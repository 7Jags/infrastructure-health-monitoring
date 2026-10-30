
"""Software-only vehicle clients for the I2V prototype."""

from dataclasses import dataclass
from datetime import datetime, timezone
from math import cos, sin, pi
from threading import Lock
from time import monotonic

from ..schemas import VehicleState, VehicleType


# Virtual road network.
BRIDGE_ROUTE = ("BR-001", "BR-002", "BR-003")

# Distance between consecutive bridges.
SEGMENT_LENGTH_M = 1200.0

# Original speed variation.
SPEED_PERIOD_SECONDS = 120.0
ANGULAR_FREQUENCY = 2.0 * pi / SPEED_PERIOD_SECONDS

# BR-003 demonstration speed.
BR003_TARGET_SPEED_KPH = 30.0
BR003_TARGET_SPEED_MPS = BR003_TARGET_SPEED_KPH / 3.6

# Smaller steps improve the numerical movement calculation.
SIMULATION_STEP_SECONDS = 0.1


@dataclass(frozen=True)
class VehicleConfig:
    """Static configuration for a virtual vehicle."""

    vehicle_type: VehicleType
    base_speed: float
    speed_range: float
    mass_kg: float
    road_friction: float
    reaction_time_s: float
    phase_offset: float
    initial_route_index: int
    initial_distance_to_bridge_m: float


@dataclass
class VehicleRuntime:
    """Mutable simulation state for an individual vehicle."""

    route_position_m: float
    last_update_time: float
    speed_mps: float
    segment_index: int
    approach_deceleration_mps2: float = 0.0


class VehicleSimulator:
    """Simulate vehicles moving continuously around a virtual route."""

    _vehicles: dict[str, VehicleConfig] = {
        "V-001": VehicleConfig(
            vehicle_type=VehicleType.CAR,
            base_speed=48.0,
            speed_range=16.0,
            mass_kg=1400.0,
            road_friction=0.72,
            reaction_time_s=1.2,
            phase_offset=0.0,
            initial_route_index=0,
            initial_distance_to_bridge_m=250.0,
        ),
        "V-002": VehicleConfig(
            vehicle_type=VehicleType.TRUCK,
            base_speed=55.0,
            speed_range=24.0,
            mass_kg=14500.0,
            road_friction=0.58,
            reaction_time_s=1.6,
            phase_offset=1.1,
            initial_route_index=1,
            initial_distance_to_bridge_m=180.0,
        ),
        "V-003": VehicleConfig(
            vehicle_type=VehicleType.BUS,
            base_speed=42.0,
            speed_range=12.0,
            mass_kg=8200.0,
            road_friction=0.64,
            reaction_time_s=1.4,
            phase_offset=2.2,
            initial_route_index=2,
            initial_distance_to_bridge_m=300.0,
        ),
    }

    def __init__(self) -> None:
        self._lock = Lock()
        self._simulation_start = monotonic()
        self._initial_route_positions: dict[str, float] = {}

        for vehicle_id, config in self._vehicles.items():
            bridge_position = (
                config.initial_route_index * SEGMENT_LENGTH_M
            )

            route_position = (
                bridge_position
                - config.initial_distance_to_bridge_m
            )

            self._initial_route_positions[vehicle_id] = (
                route_position % self.route_length_m
            )

        self._runtime = self._create_runtime_states(
            self._simulation_start
        )

    @property
    def route_length_m(self) -> float:
        return len(BRIDGE_ROUTE) * SEGMENT_LENGTH_M

    @property
    def vehicle_ids(self) -> set[str]:
        return set(self._vehicles.keys())

    @staticmethod
    def _smoothstep(value: float) -> float:
        """Return a smooth transition value between zero and one."""

        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)

    def _speed_at_time(
        self,
        vehicle: VehicleConfig,
        elapsed_seconds: float,
    ) -> float:
        """Return the original sinusoidal speed in metres per second."""

        phase = (
            ANGULAR_FREQUENCY * elapsed_seconds
            + vehicle.phase_offset
        )

        speed_kph = (
            vehicle.base_speed
            + vehicle.speed_range * sin(phase)
        )

        return speed_kph / 3.6

    def _distance_between_times(
        self,
        vehicle: VehicleConfig,
        start_seconds: float,
        end_seconds: float,
    ) -> float:
        """Integrate the original sinusoidal speed between two times."""

        start_phase = (
            ANGULAR_FREQUENCY * start_seconds
            + vehicle.phase_offset
        )

        end_phase = (
            ANGULAR_FREQUENCY * end_seconds
            + vehicle.phase_offset
        )

        base_distance = (
            vehicle.base_speed / 3.6
        ) * (end_seconds - start_seconds)

        variable_distance = (
            (vehicle.speed_range / 3.6)
            / ANGULAR_FREQUENCY
        ) * (
            cos(start_phase) - cos(end_phase)
        )

        return base_distance + variable_distance

    def _recovery_speed(
        self,
        vehicle: VehicleConfig,
        elapsed_seconds: float,
        distance_from_br003_m: float,
    ) -> float:
        """Smoothly restore normal speed after crossing BR-003."""

        progress = (
            distance_from_br003_m / SEGMENT_LENGTH_M
        )

        blend = self._smoothstep(progress)

        normal_speed = self._speed_at_time(
            vehicle,
            elapsed_seconds,
        )

        return (
            BR003_TARGET_SPEED_MPS
            + (normal_speed - BR003_TARGET_SPEED_MPS) * blend
        )

    def _approach_deceleration(
        self,
        entry_speed_mps: float,
        remaining_distance_m: float,
    ) -> float:
        """Calculate constant deceleration to reach 30 km/h at BR-003."""

        if remaining_distance_m <= 0:
            return 0.0

        if entry_speed_mps <= BR003_TARGET_SPEED_MPS:
            return 0.0

        return (
            entry_speed_mps**2
            - BR003_TARGET_SPEED_MPS**2
        ) / (2.0 * remaining_distance_m)

    def _create_runtime_states(
        self,
        start_time: float,
    ) -> dict[str, VehicleRuntime]:
        """Initialize independent runtime states for all vehicles."""

        runtime_states = {}

        for vehicle_id, vehicle in self._vehicles.items():
            position = self._initial_route_positions[vehicle_id]

            segment_index = int(
                position // SEGMENT_LENGTH_M
            )

            initial_speed = self._speed_at_time(
                vehicle,
                0.0,
            )

            approach_deceleration = 0.0

            if segment_index == 1:
                # V-003 starts on the BR-002 -> BR-003 segment.
                remaining_distance = (
                    SEGMENT_LENGTH_M
                    - (position % SEGMENT_LENGTH_M)
                )

                approach_deceleration = (
                    self._approach_deceleration(
                        initial_speed,
                        remaining_distance,
                    )
                )

            elif segment_index == 2:
                # V-001 starts partway through the BR-003 -> BR-001
                # recovery segment.
                initial_speed = self._recovery_speed(
                    vehicle,
                    0.0,
                    position % SEGMENT_LENGTH_M,
                )

            runtime_states[vehicle_id] = VehicleRuntime(
                route_position_m=position,
                last_update_time=start_time,
                speed_mps=initial_speed,
                segment_index=segment_index,
                approach_deceleration_mps2=approach_deceleration,
            )

        return runtime_states

    def _handle_segment_transition(
        self,
        vehicle: VehicleConfig,
        runtime: VehicleRuntime,
        new_segment_index: int,
        elapsed_seconds: float,
    ) -> None:
        """Apply the appropriate speed behaviour on entering a segment."""

        previous_segment = runtime.segment_index
        runtime.segment_index = new_segment_index

        if new_segment_index == 1:
            # Entering BR-002 -> BR-003:
            # calculate deceleration to reach 30 km/h at BR-003.
            remaining_distance = (
                SEGMENT_LENGTH_M
                - (runtime.route_position_m % SEGMENT_LENGTH_M)
            )

            runtime.approach_deceleration_mps2 = (
                self._approach_deceleration(
                    runtime.speed_mps,
                    remaining_distance,
                )
            )

        elif new_segment_index == 2 and previous_segment == 1:
            # The vehicle has crossed BR-003.
            runtime.speed_mps = BR003_TARGET_SPEED_MPS
            runtime.approach_deceleration_mps2 = 0.0

        elif new_segment_index == 0:
            # Normal sinusoidal speed resumes after the recovery segment.
            runtime.speed_mps = self._speed_at_time(
                vehicle,
                elapsed_seconds,
            )

    def _advance_vehicle(
        self,
        vehicle_id: str,
        current_time: float,
    ) -> None:
        """Advance one vehicle independently of API request frequency."""

        vehicle = self._vehicles[vehicle_id]
        runtime = self._runtime[vehicle_id]

        while runtime.last_update_time < current_time:
            elapsed_seconds = (
                runtime.last_update_time - self._simulation_start
            )

            segment_index = int(
                (
                    runtime.route_position_m % self.route_length_m
                ) // SEGMENT_LENGTH_M
            )

            if segment_index != runtime.segment_index:
                self._handle_segment_transition(
                    vehicle,
                    runtime,
                    segment_index,
                    elapsed_seconds,
                )

            step = min(
                SIMULATION_STEP_SECONDS,
                current_time - runtime.last_update_time,
            )

            if segment_index == 0:
                # BR-001 -> BR-002: original sinusoidal movement.
                next_elapsed = elapsed_seconds + step

                distance = self._distance_between_times(
                    vehicle,
                    elapsed_seconds,
                    next_elapsed,
                )

                runtime.speed_mps = self._speed_at_time(
                    vehicle,
                    next_elapsed,
                )

            elif segment_index == 1:
                # BR-002 -> BR-003: gradual deceleration.
                speed = runtime.speed_mps
                deceleration = runtime.approach_deceleration_mps2

                if (
                    deceleration > 0.0
                    and speed > BR003_TARGET_SPEED_MPS
                ):
                    time_to_target = (
                        speed - BR003_TARGET_SPEED_MPS
                    ) / deceleration

                    if time_to_target <= step:
                        # Reach the bridge at exactly the target speed.
                        distance = (
                            SEGMENT_LENGTH_M
                            - (
                                runtime.route_position_m
                                % SEGMENT_LENGTH_M
                            )
                        )

                        runtime.speed_mps = (
                            BR003_TARGET_SPEED_MPS
                        )

                        runtime.route_position_m = (
                            runtime.route_position_m + distance
                        ) % self.route_length_m

                        runtime.last_update_time += time_to_target
                        continue

                    distance = (
                        speed * step
                        - 0.5 * deceleration * step**2
                    )

                    runtime.speed_mps = max(
                        BR003_TARGET_SPEED_MPS,
                        speed - deceleration * step,
                    )

                else:
                    # If already at the target, continue moving.
                    distance = speed * step

            else:
                # BR-003 -> BR-001: smoothly restore normal speed.
                distance_from_bridge = (
                    runtime.route_position_m % SEGMENT_LENGTH_M
                )

                start_speed = self._recovery_speed(
                    vehicle,
                    elapsed_seconds,
                    distance_from_bridge,
                )

                estimated_position = (
                    runtime.route_position_m + start_speed * step
                ) % self.route_length_m

                estimated_segment = int(
                    estimated_position // SEGMENT_LENGTH_M
                )

                next_elapsed = elapsed_seconds + step

                if estimated_segment == 2:
                    end_distance_from_bridge = (
                        estimated_position % SEGMENT_LENGTH_M
                    )

                    end_speed = self._recovery_speed(
                        vehicle,
                        next_elapsed,
                        end_distance_from_bridge,
                    )
                else:
                    # The vehicle is leaving the recovery segment.
                    end_speed = self._speed_at_time(
                        vehicle,
                        next_elapsed,
                    )

                distance = (
                    (start_speed + end_speed) / 2.0
                ) * step

                runtime.speed_mps = end_speed

            runtime.route_position_m = (
                runtime.route_position_m + distance
            ) % self.route_length_m

            runtime.last_update_time += step

    def next_state(self, vehicle_id: str) -> VehicleState:
        """Calculate and return the current state of a vehicle."""

        vehicle = self._vehicles.get(vehicle_id)

        if vehicle is None:
            raise ValueError(f"Unknown vehicle ID: {vehicle_id}")

        current_time = monotonic()

        with self._lock:
            self._advance_vehicle(
                vehicle_id,
                current_time,
            )

            runtime = self._runtime[vehicle_id]

            route_position = (
                runtime.route_position_m % self.route_length_m
            )

            segment_index = int(
                route_position // SEGMENT_LENGTH_M
            )

            distance_into_segment = (
                route_position % SEGMENT_LENGTH_M
            )

            approaching_index = (
                segment_index + 1
            ) % len(BRIDGE_ROUTE)

            approaching_node_id = BRIDGE_ROUTE[
                approaching_index
            ]

            previous_node_id = BRIDGE_ROUTE[
                segment_index
            ]

            current_segment_id = (
                f"SEG-{previous_node_id}-{approaching_node_id}"
            )

            distance_to_bridge = (
                SEGMENT_LENGTH_M - distance_into_segment
            )

            speed_kph = round(
                runtime.speed_mps * 3.6,
                1,
            )

        return VehicleState(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle.vehicle_type,
            timestamp=datetime.now(timezone.utc),
            approaching_node_id=approaching_node_id,
            current_segment_id=current_segment_id,
            distance_to_bridge_m=round(
                distance_to_bridge,
                1,
            ),
            speed_kph=speed_kph,
            mass_kg=vehicle.mass_kg,
            road_friction=vehicle.road_friction,
            reaction_time_s=vehicle.reaction_time_s,
        )

    def reset(self) -> None:
        """Restart the virtual network simulation."""

        with self._lock:
            self._simulation_start = monotonic()
            self._runtime = self._create_runtime_states(
                self._simulation_start
            )


vehicle_simulator = VehicleSimulator()
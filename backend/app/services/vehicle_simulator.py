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

# Speed variation completes one cycle every 120 seconds.
SPEED_PERIOD_SECONDS = 120.0
ANGULAR_FREQUENCY = 2.0 * pi / SPEED_PERIOD_SECONDS


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


class VehicleSimulator:
    """Simulate vehicle movement using elapsed simulation time."""

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

        # Each vehicle has its own starting position along the route.
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

    @property
    def route_length_m(self) -> float:
        return len(BRIDGE_ROUTE) * SEGMENT_LENGTH_M

    @property
    def vehicle_ids(self) -> set[str]:
        return set(self._vehicles.keys())

    def _speed_at_time(
        self,
        vehicle: VehicleConfig,
        elapsed_seconds: float,
    ) -> float:
        """Return instantaneous speed in metres per second."""

        phase = (
            ANGULAR_FREQUENCY * elapsed_seconds
            + vehicle.phase_offset
        )

        speed_kph = (
            vehicle.base_speed
            + vehicle.speed_range * sin(phase)
        )

        return speed_kph / 3.6

    def _distance_travelled(
        self,
        vehicle: VehicleConfig,
        elapsed_seconds: float,
    ) -> float:
        """Integrate the speed function over elapsed time."""

        phase = (
            ANGULAR_FREQUENCY * elapsed_seconds
            + vehicle.phase_offset
        )

        initial_phase = vehicle.phase_offset

        base_distance = (
            vehicle.base_speed / 3.6
        ) * elapsed_seconds

        variable_distance = (
            (vehicle.speed_range / 3.6)
            / ANGULAR_FREQUENCY
        ) * (
            cos(initial_phase) - cos(phase)
        )

        return base_distance + variable_distance

    def next_state(self, vehicle_id: str) -> VehicleState:
        """Calculate a vehicle's current state from simulation time."""

        vehicle = self._vehicles.get(vehicle_id)

        if vehicle is None:
            raise ValueError(f"Unknown vehicle ID: {vehicle_id}")

        current_time = monotonic()

        with self._lock:
            elapsed_seconds = max(
                0.0,
                current_time - self._simulation_start,
            )

            initial_position = self._initial_route_positions[
                vehicle_id
            ]

            distance_travelled = self._distance_travelled(
                vehicle,
                elapsed_seconds,
            )

            route_position = (
                initial_position + distance_travelled
            ) % self.route_length_m

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

            speed_mps = self._speed_at_time(
                vehicle,
                elapsed_seconds,
            )

            speed_kph = round(speed_mps * 3.6, 1)

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


vehicle_simulator = VehicleSimulator()
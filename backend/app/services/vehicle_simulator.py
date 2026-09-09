"""Software-only vehicle clients for the I2V prototype."""

from datetime import datetime, timezone
from math import sin
from threading import Lock

from ..schemas import VehicleState, VehicleType


class VehicleSimulator:
    """Generate deterministic telemetry for three virtual approaching vehicles."""

    _vehicles = {
        "V-001": {
            "vehicle_type": VehicleType.CAR,
            "base_speed": 48.0,
            "speed_range": 16.0,
            "mass_kg": 1_400.0,
            "road_friction": 0.72,
            "reaction_time_s": 1.2,
            "phase_offset": 0.0,
        },
        "V-002": {
            "vehicle_type": VehicleType.TRUCK,
            "base_speed": 55.0,
            "speed_range": 24.0,
            "mass_kg": 14_500.0,
            "road_friction": 0.58,
            "reaction_time_s": 1.6,
            "phase_offset": 1.1,
        },
        "V-003": {
            "vehicle_type": VehicleType.BUS,
            "base_speed": 42.0,
            "speed_range": 12.0,
            "mass_kg": 8_200.0,
            "road_friction": 0.64,
            "reaction_time_s": 1.4,
            "phase_offset": 2.2,
        },
    }

    def __init__(self) -> None:
        self._tick = 0
        self._lock = Lock()

    @property
    def vehicle_ids(self) -> set[str]:
        return set(self._vehicles)

    def next_state(self, vehicle_id: str) -> VehicleState:
        """Advance one vehicle by a reading and return its current state."""

        vehicle = self._vehicles[vehicle_id]
        with self._lock:
            self._tick += 1
            phase = self._tick * 0.36 + vehicle["phase_offset"]

        speed_kph = round(vehicle["base_speed"] + vehicle["speed_range"] * sin(phase), 1)
        return VehicleState(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle["vehicle_type"],
            timestamp=datetime.now(timezone.utc),
            approaching_node_id="BR-001",
            speed_kph=max(0.0, speed_kph),
            mass_kg=vehicle["mass_kg"],
            road_friction=vehicle["road_friction"],
            reaction_time_s=vehicle["reaction_time_s"],
        )

    def reset(self) -> None:
        with self._lock:
            self._tick = 0


vehicle_simulator = VehicleSimulator()

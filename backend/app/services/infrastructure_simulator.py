"""A software-only Smart Node that produces realistic bridge telemetry."""

from datetime import datetime, timezone
from math import sin
from threading import Lock

from ..schemas import InfrastructureState
from .health_service import assess_structural_health


class BridgeSimulator:
    """Generate deterministic, changing data for the BR-001 virtual bridge."""

    node_id = "BR-001"
    name = "Bagmati River Bridge"

    def __init__(self) -> None:
        self._tick = 0
        self._lock = Lock()

    def next_state(self) -> InfrastructureState:
        """Advance the virtual Smart Node by one reading and return its state."""

        with self._lock:
            self._tick += 1
            phase = self._tick * 0.42

        load_percent = round(60.0 + 35.0 * sin(phase), 1)
        load_pressure = max(0.0, sin(phase))
        vibration_hz = round(2.1 + 6.2 * load_pressure, 2)
        strain = round(0.0012 + 0.0038 * load_pressure, 5)
        temperature_c = round(24.0 + 10.0 * sin(self._tick * 0.12), 1)
        traffic = round(900 + 700 * max(0.0, sin(self._tick * 0.27)))

        return InfrastructureState(
            node_id=self.node_id,
            name=self.name,
            infrastructure_type="bridge",
            timestamp=datetime.now(timezone.utc),
            load_percent=load_percent,
            vibration_hz=vibration_hz,
            strain=strain,
            temperature_c=temperature_c,
            traffic_vehicles_per_hour=traffic,
            health=assess_structural_health(
                load_percent=load_percent,
                vibration_hz=vibration_hz,
                strain=strain,
                temperature_c=temperature_c,
            ),
        )

    def reset(self) -> None:
        """Reset the simulation for repeatable demos and tests."""

        with self._lock:
            self._tick = 0


bridge_simulator = BridgeSimulator()

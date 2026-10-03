"""Software-only infrastructure simulation."""

from datetime import datetime, timezone
from math import sin
from threading import Lock

from ..schemas import (
    HealthAssessment,
    InfrastructureState,
    StructuralHealthCategory,
)


class BridgeSimulator:
    """Generate realistic virtual telemetry and structural health."""

    def __init__(
        self,
        *,
        node_id: str,
        name: str,
        condition: str,
    ):
        self._tick = 0
        self._lock = Lock()

        self.node_id = node_id
        self.name = name
        self.condition = condition

        if condition == "normal":
            self._structural_health = 96.0

        elif condition == "stress":
            self._structural_health = 65.0

        elif condition == "critical":
            self._structural_health = 40.0

        else:
            raise ValueError(
                f"Unknown bridge condition: {condition}"
            )

    def next_state(self) -> InfrastructureState:
        """Generate the next virtual bridge telemetry state."""

        with self._lock:
            self._tick += 1
            tick = self._tick

        # ---------------------------------------------------------
        # 1. CURRENT OPERATING CONDITIONS
        # ---------------------------------------------------------

        if self.condition == "normal":

            traffic = round(
                900
                + 700 * max(
                    0.0,
                    sin(tick * 0.27),
                )
            )

            load_percent = round(
                45.0
                + 40.0 * max(
                    0.0,
                    sin(tick * 0.18),
                ),
                1,
            )

            load_pressure = max(
                0.0,
                sin(tick * 0.18),
            )

            vibration_hz = round(
                2.1 + 5.0 * load_pressure,
                2,
            )

            strain = round(
                0.0012 + 0.0030 * load_pressure,
                5,
            )

            temperature_c = round(
                24.0 + 2.5 * sin(tick * 0.002),
                1,
            )

        elif self.condition == "stress":

            traffic = round(
                1200
                + 500 * max(
                    0.0,
                    sin(tick * 0.22),
                )
            )

            load_percent = round(
                65.0
                + 18.0 * max(
                    0.0,
                    sin(tick * 0.16),
                ),
                1,
            )

            load_pressure = max(
                0.0,
                sin(tick * 0.16),
            )

            vibration_hz = round(
                4.5 + 3.0 * load_pressure,
                2,
            )

            strain = round(
                0.0025 + 0.0018 * load_pressure,
                5,
            )

            temperature_c = round(
                27.0 + 2.0 * sin(tick * 0.002),
                1,
            )

        else:
            # Critical infrastructure condition.

            traffic = round(
                1500
                + 400 * max(
                    0.0,
                    sin(tick * 0.20),
                )
            )

            load_percent = round(
                80.0
                + 15.0 * max(
                    0.0,
                    sin(tick * 0.14),
                ),
                1,
            )

            load_pressure = max(
                0.0,
                sin(tick * 0.14),
            )

            vibration_hz = round(
                6.0 + 3.0 * load_pressure,
                2,
            )

            strain = round(
                0.0035 + 0.0015 * load_pressure,
                5,
            )

            temperature_c = round(
                30.0 + 2.5 * sin(tick * 0.002),
                1,
            )

        # ---------------------------------------------------------
        # 2. STRUCTURAL HEALTH
        # ---------------------------------------------------------

        self._update_structural_health(
            load_percent=load_percent,
            vibration_hz=vibration_hz,
            strain=strain,
        )

        health = self._build_health_assessment()

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
            health=health,
        )

    def _update_structural_health(
        self,
        *,
        load_percent: float,
        vibration_hz: float,
        strain: float,
    ) -> None:
        """Gradually move structural health according to current conditions."""

        load_stress = max(
            0.0,
            min(
                1.0,
                (load_percent - 40.0) / 50.0,
            ),
        )

        vibration_stress = max(
            0.0,
            min(
                1.0,
                (vibration_hz - 2.0) / 5.0,
            ),
        )

        strain_stress = max(
            0.0,
            min(
                1.0,
                (strain - 0.0010) / 0.0030,
            ),
        )

        stress_level = (
            load_stress * 0.40
            + vibration_stress * 0.30
            + strain_stress * 0.30
        )

        # Normal bridge:
        #     low stress -> health near 100%
        #
        # Stress bridge:
        #     health remains around the caution range
        #
        # Critical bridge:
        #     health remains around the high-risk range

        if self.condition == "normal":

            target_health = 100.0 - (
                stress_level * 10.0
            )

            minimum_health = 90.0
            maximum_health = 100.0

        elif self.condition == "stress":

            target_health = 65.0 - (
                stress_level * 3.0
            )

            minimum_health = 60.0
            maximum_health = 70.0

        else:

            target_health = 40.0 - (
                stress_level * 3.0
            )

            minimum_health = 35.0
            maximum_health = 45.0

        smoothing_factor = 0.08

        self._structural_health += (
            target_health - self._structural_health
        ) * smoothing_factor

        self._structural_health = max(
            minimum_health,
            min(
                maximum_health,
                self._structural_health,
            ),
        )

    def _build_health_assessment(self) -> HealthAssessment:
        """Convert structural health into the API health model."""

        health_percentage = round(
            self._structural_health,
            1,
        )

        risk_score = round(
            1.0 - (health_percentage / 100.0),
            3,
        )

        if health_percentage >= 70.0:
            category = StructuralHealthCategory.NORMAL

        elif health_percentage >= 45.0:
            category = StructuralHealthCategory.CAUTION

        else:
            category = StructuralHealthCategory.HIGH_RISK

        return HealthAssessment(
            health_percentage=health_percentage,
            risk_score=risk_score,
            category=category,
        )

    def reset(self) -> None:
        """Reset the simulation clock and structural condition."""

        with self._lock:
            self._tick = 0

            if self.condition == "normal":
                self._structural_health = 96.0

            elif self.condition == "stress":
                self._structural_health = 65.0

            else:
                self._structural_health = 40.0


# -------------------------------------------------------------
# VIRTUAL INFRASTRUCTURE NETWORK
# -------------------------------------------------------------

bridge_simulators = {
    "BR-001": BridgeSimulator(
        node_id="BR-001",
        name="Bagmati River Bridge",
        condition="normal",
    ),

    "BR-002": BridgeSimulator(
        node_id="BR-002",
        name="Stress Bridge",
        condition="stress",
    ),

    "BR-003": BridgeSimulator(
        node_id="BR-003",
        name="Critical Bridge",
        condition="critical",
    ),
}


# Keep the original variable for compatibility with
# existing routes that currently use BR-001.

bridge_simulator = bridge_simulators["BR-001"]


def get_bridge_simulator(node_id: str) -> BridgeSimulator:
    """Return the simulator for a specific infrastructure node."""

    try:
        return bridge_simulators[node_id]

    except KeyError:
        raise KeyError(
            f"Infrastructure node {node_id} not found."
        )
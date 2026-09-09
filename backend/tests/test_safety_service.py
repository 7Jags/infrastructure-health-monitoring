from datetime import datetime, timezone

from app.schemas import (
    HealthAssessment,
    InfrastructureState,
    SafetyDecision,
    StructuralHealthCategory,
    VehicleState,
    VehicleType,
)
from app.services.safety_service import assess_vehicle_safety, calculate_stopping_distance_m


def make_vehicle(speed_kph: float) -> VehicleState:
    return VehicleState(
        vehicle_id="V-001",
        vehicle_type=VehicleType.CAR,
        timestamp=datetime.now(timezone.utc),
        approaching_node_id="BR-001",
        speed_kph=speed_kph,
        mass_kg=1_400,
        road_friction=0.72,
        reaction_time_s=1.2,
    )


def make_infrastructure(category: StructuralHealthCategory, health: float) -> InfrastructureState:
    return InfrastructureState(
        node_id="BR-001",
        name="Bagmati River Bridge",
        infrastructure_type="bridge",
        timestamp=datetime.now(timezone.utc),
        load_percent=60,
        vibration_hz=2.5,
        strain=0.0012,
        temperature_c=24,
        traffic_vehicles_per_hour=900,
        health=HealthAssessment(
            health_percentage=health,
            risk_score=1 - health / 100,
            category=category,
        ),
    )


def test_stopping_distance_increases_with_speed() -> None:
    assert calculate_stopping_distance_m(make_vehicle(80)) > calculate_stopping_distance_m(
        make_vehicle(40)
    )


def test_high_risk_infrastructure_produces_red_decision() -> None:
    assessment = assess_vehicle_safety(
        make_vehicle(40),
        make_infrastructure(StructuralHealthCategory.HIGH_RISK, 30),
    )

    assert assessment.decision is SafetyDecision.RED
    assert assessment.recommended_speed_kph == 25

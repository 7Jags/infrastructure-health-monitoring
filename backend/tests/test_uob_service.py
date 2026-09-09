from datetime import datetime, timezone

from app.schemas import (
    HealthAssessment,
    InfrastructureState,
    SafetyDecision,
    StructuralHealthCategory,
    VehicleSafetyAssessment,
    VehicleState,
    VehicleType,
)
from app.services.uob_service import create_uob_packet


def test_uob_packet_encodes_safety_decision() -> None:
    vehicle = VehicleState(
        vehicle_id="V-001",
        vehicle_type=VehicleType.CAR,
        timestamp=datetime.now(timezone.utc),
        approaching_node_id="BR-001",
        speed_kph=40,
        mass_kg=1_400,
        road_friction=0.72,
        reaction_time_s=1.2,
    )
    infrastructure = InfrastructureState(
        node_id="BR-001",
        name="Bagmati River Bridge",
        infrastructure_type="bridge",
        timestamp=datetime.now(timezone.utc),
        load_percent=90,
        vibration_hz=7.5,
        strain=0.004,
        temperature_c=32,
        traffic_vehicles_per_hour=1_400,
        health=HealthAssessment(
            health_percentage=40,
            risk_score=0.6,
            category=StructuralHealthCategory.HIGH_RISK,
        ),
    )
    assessment = VehicleSafetyAssessment(
        decision=SafetyDecision.RED,
        recommended_speed_kph=25,
        stopping_distance_m=35,
        available_stopping_distance_m=56,
        safety_margin_m=21,
        message="Slow immediately.",
    )

    packet = create_uob_packet(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )

    assert packet.packet_id.startswith("UOB-")
    assert packet.hazard_code == "0x03"
    assert packet.target_vehicle_id == "V-001"

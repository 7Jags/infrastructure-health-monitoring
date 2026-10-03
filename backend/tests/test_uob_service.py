
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
        distance_to_bridge_m=100,
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
        recommended_speed_kph=0,
        approach_speed_limit_kph=50,
        crossing_speed_limit_kph=0,
        reaction_distance_m=13.3,
        braking_distance_m=8.7,
        stopping_distance_m=22.0,
        safety_buffer_m=10,
        available_stopping_distance_m=90,
        safety_margin_m=68,
        kinetic_energy_j=86419.8,
        can_stop_before_bridge=True,
        message="Stop before entering the high-risk bridge.",
    )

    packet = create_uob_packet(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )

    assert packet.packet_id.startswith("UOB-")
    assert packet.hazard_code == "0x03"
    assert packet.decision is SafetyDecision.RED
    assert packet.target_vehicle_id == "V-001"
    assert packet.source_node_id == "BR-001"
    assert packet.recommended_speed_kph == 0
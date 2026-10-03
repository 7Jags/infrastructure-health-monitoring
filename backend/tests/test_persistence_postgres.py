
"""PostgreSQL integration tests for persistence_service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    InfrastructureTelemetryRecord,
    SafetyDecisionRecord,
    UobPacketRecord,
    VehicleTelemetryRecord,
)
from app.schemas import (
    HealthAssessment,
    InfrastructureState,
    StructuralHealthCategory,
    SafetyDecision,
    UobPacket,
    VehicleSafetyAssessment,
    VehicleState,
    VehicleType,
)
from app.services.persistence_service import (
    get_latest_infrastructure_state,
    record_infrastructure_state,
    record_safety_event,
    record_vehicle_state,
)


def make_infrastructure() -> InfrastructureState:
    return InfrastructureState(
        node_id="TEST-BR-001",
        name="Test Bridge",
        infrastructure_type="bridge",
        timestamp=datetime.now(timezone.utc),
        load_percent=45.0,
        vibration_hz=3.2,
        strain=120.0,
        temperature_c=28.0,
        traffic_vehicles_per_hour=500,
        health=HealthAssessment(
            health_percentage=95.0,
            risk_score=0.05,
            category=StructuralHealthCategory.NORMAL,
        ),
    )


def make_vehicle() -> VehicleState:
    return VehicleState(
        vehicle_id="TEST-V-001",
        vehicle_type=VehicleType.CAR,
        timestamp=datetime.now(timezone.utc),
        approaching_node_id="TEST-BR-001",
        current_segment_id="TEST-SEGMENT",
        distance_to_bridge_m=200.0,
        speed_kph=40.0,
        mass_kg=1400.0,
        road_friction=0.72,
        reaction_time_s=1.2,
    )


def make_assessment() -> VehicleSafetyAssessment:
    return VehicleSafetyAssessment(
        decision=SafetyDecision.GREEN,
        recommended_speed_kph=40.0,
        approach_speed_limit_kph=50.0,
        crossing_speed_limit_kph=60.0,
        reaction_distance_m=13.33,
        braking_distance_m=8.75,
        stopping_distance_m=22.08,
        safety_buffer_m=10.0,
        available_stopping_distance_m=190.0,
        safety_margin_m=167.92,
        kinetic_energy_j=86419.75,
        can_stop_before_bridge=True,
        message="Safe to approach the bridge.",
    )


def test_infrastructure_record_is_saved_and_retrieved(
    db_session: Session,
) -> None:
    infrastructure = make_infrastructure()

    record_infrastructure_state(db_session, infrastructure)

    saved = get_latest_infrastructure_state(
        db_session,
        "TEST-BR-001",
    )

    assert saved is not None
    assert saved.node_id == "TEST-BR-001"
    assert saved.health_percentage == 95.0
    assert saved.health_category == "normal"


def test_vehicle_record_is_saved(db_session: Session) -> None:
    vehicle = make_vehicle()

    record_vehicle_state(db_session, vehicle)

    saved = (
        db_session.query(VehicleTelemetryRecord)
        .filter(
            VehicleTelemetryRecord.vehicle_id == "TEST-V-001"
        )
        .one()
    )

    assert saved.vehicle_id == "TEST-V-001"
    assert saved.speed_kph == 40.0
    assert saved.mass_kg == 1400.0


def test_safety_event_and_uob_packet_are_saved(
    db_session: Session,
) -> None:
    infrastructure = make_infrastructure()
    vehicle = make_vehicle()
    assessment = make_assessment()

    packet = UobPacket(
        packet_id="UOB-TEST-001",
        format_version="1.0",
        timestamp=datetime.now(timezone.utc),
        source_node_id="TEST-BR-001",
        target_vehicle_id="TEST-V-001",
        hazard_code="0x00",
        decision=SafetyDecision.GREEN,
        bridge_health_percentage=95.0,
        recommended_speed_kph=40.0,
        message="Safe to approach the bridge.",
    )

    record_safety_event(
        db_session,
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
        packet=packet,
    )

    safety_record = (
        db_session.query(SafetyDecisionRecord)
        .filter(
            SafetyDecisionRecord.vehicle_id == "TEST-V-001"
        )
        .one()
    )

    packet_record = (
        db_session.query(UobPacketRecord)
        .filter(
            UobPacketRecord.packet_id == "UOB-TEST-001"
        )
        .one()
    )

    assert safety_record.decision == "green"
    assert safety_record.node_id == "TEST-BR-001"
    assert packet_record.target_vehicle_id == "TEST-V-001"
    assert packet_record.hazard_code == "0x00"

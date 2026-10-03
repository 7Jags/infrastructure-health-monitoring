"""Routes exposing the virtual infrastructure-to-vehicle broadcast layer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import InfrastructureTelemetryRecord
from ..schemas import (
    InfrastructureState,
    UobPacket,
    VehicleSafetyAssessment,
    VehicleState,
)
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.uob_service import create_uob_packet
from ..services.vehicle_simulator import vehicle_simulator

router = APIRouter(
    prefix="/api/uob",
    tags=["uob broadcast"],
)


def _get_latest_infrastructure(
    session: Session,
) -> InfrastructureState:
    """Return the latest stored infrastructure state."""

    latest_record = (
        session.query(InfrastructureTelemetryRecord)
        .filter(
            InfrastructureTelemetryRecord.node_id == "BR-001"
        )
        .order_by(
            InfrastructureTelemetryRecord.recorded_at.desc()
        )
        .first()
    )

    if latest_record is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No current infrastructure state is available.",
        )

    health_percentage = latest_record.health_percentage

    risk_score = round(
        1.0 - (health_percentage / 100.0),
        3,
    )

    return InfrastructureState(
        node_id=latest_record.node_id,
        name="Bagmati River Bridge",
        infrastructure_type="bridge",
        timestamp=latest_record.recorded_at,
        load_percent=latest_record.load_percent,
        vibration_hz=latest_record.vibration_hz,
        strain=latest_record.strain,
        temperature_c=latest_record.temperature_c,
        traffic_vehicles_per_hour=latest_record.traffic_vehicles_per_hour,
        health={
            "health_percentage": health_percentage,
            "risk_score": risk_score,
            "category": latest_record.health_category,
        },  # type: ignore
    )


def _generate_uob_packet(
    vehicle_id: str,
    session: Session,
) -> tuple[
    UobPacket,
    VehicleState,
    InfrastructureState,
    VehicleSafetyAssessment,
]:
    """Generate the current UOB packet and safety assessment."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' was not found",
        )

    vehicle = vehicle_simulator.next_state(vehicle_id)

    infrastructure = _get_latest_infrastructure(session)

    assessment = assess_vehicle_safety(
        vehicle,
        infrastructure,
    )

    packet = create_uob_packet(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )

    return (
        packet,
        vehicle,
        infrastructure,
        assessment,
    )


@router.get(
    "/vehicles/{vehicle_id}/current",
    response_model=UobPacket,
)
def get_current_uob_packet(
    vehicle_id: str,
    session: Session = Depends(get_session),
) -> UobPacket:
    """Return the current UOB packet without recording a safety event."""

    packet, _, _, _ = _generate_uob_packet(
        vehicle_id,
        session,
    )

    return packet


@router.get(
    "/vehicles/{vehicle_id}/latest",
    response_model=UobPacket,
)
def get_latest_uob_packet(
    vehicle_id: str,
    session: Session = Depends(get_session),
) -> UobPacket:
    """Generate and record the UOB packet for a virtual vehicle."""

    packet, vehicle, infrastructure, assessment = _generate_uob_packet(
        vehicle_id,
        session,
    )

    record_safety_event(
        session,
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
        packet=packet,
    )

    return packet
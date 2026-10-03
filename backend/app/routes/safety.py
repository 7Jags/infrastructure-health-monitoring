"""Routes that produce vehicle-specific infrastructure safety decisions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import InfrastructureTelemetryRecord
from ..schemas import (
    InfrastructureState,
    SafetyDecisionResponse,
)
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/safety",
    tags=["safety"],
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


def _calculate_current_safety(
    vehicle_id: str,
    session: Session,
) -> SafetyDecisionResponse:
    """Calculate current safety without recording a history event."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown vehicle: {vehicle_id}",
        )

    vehicle = vehicle_simulator.next_state(vehicle_id)

    infrastructure = _get_latest_infrastructure(session)

    assessment = assess_vehicle_safety(
        vehicle,
        infrastructure,
    )

    return SafetyDecisionResponse(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )


@router.get(
    "/vehicles/{vehicle_id}/current",
    response_model=SafetyDecisionResponse,
)
def get_current_safety(
    vehicle_id: str,
    session: Session = Depends(get_session),
) -> SafetyDecisionResponse:
    """Return the current safety condition without creating a history event."""

    return _calculate_current_safety(
        vehicle_id,
        session,
    )


@router.get(
    "/vehicles/{vehicle_id}/decision",
    response_model=SafetyDecisionResponse,
)
def get_safety_decision(
    vehicle_id: str,
    session: Session = Depends(get_session),
) -> SafetyDecisionResponse:
    """Calculate safety and record it as a safety event."""

    result = _calculate_current_safety(
        vehicle_id,
        session,
    )

    record_safety_event(
        session,
        vehicle=result.vehicle,
        infrastructure=result.infrastructure,
        assessment=result.assessment,
    )

    return result
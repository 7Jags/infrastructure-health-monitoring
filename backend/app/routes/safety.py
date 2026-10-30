"""Routes that produce vehicle-specific infrastructure safety decisions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import SafetyDecisionResponse
from ..services.infrastructure_state_service import (
    get_current_infrastructure_state,
)
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/safety",
    tags=["safety"],
)


def _calculate_current_safety(
    vehicle_id: str,
    session: Session,
) -> SafetyDecisionResponse:
    """Calculate safety using the vehicle's actual approaching bridge."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown vehicle: {vehicle_id}",
        )

    vehicle = vehicle_simulator.next_state(vehicle_id)

    try:
        infrastructure = get_current_infrastructure_state(
            session,
            vehicle.approaching_node_id,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Unknown approaching infrastructure node: "
                f"{vehicle.approaching_node_id}"
            ),
        )

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
    """Return current safety without recording a history event."""

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
    """Calculate safety and record the complete safety event."""

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
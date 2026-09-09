"""Routes that produce vehicle-specific infrastructure safety decisions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import SafetyDecisionResponse
from ..services.infrastructure_simulator import bridge_simulator
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.vehicle_simulator import vehicle_simulator

router = APIRouter(prefix="/api/safety", tags=["safety"])


@router.get("/vehicles/{vehicle_id}/decision", response_model=SafetyDecisionResponse)
def get_safety_decision(
    vehicle_id: str, session: Session = Depends(get_session)
) -> SafetyDecisionResponse:
    """Generate an I2V safety decision for an approaching virtual vehicle."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' was not found",
        )

    vehicle = vehicle_simulator.next_state(vehicle_id)
    infrastructure = bridge_simulator.next_state()
    assessment = assess_vehicle_safety(vehicle, infrastructure)
    record_safety_event(
        session,
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )
    return SafetyDecisionResponse(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )

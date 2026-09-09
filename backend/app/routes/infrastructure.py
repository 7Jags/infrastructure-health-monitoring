"""Monitoring routes for the initial infrastructure prototype."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import InfrastructureState, SimulationResetResponse
from ..services.infrastructure_simulator import bridge_simulator
from ..services.persistence_service import record_infrastructure_state
from ..services.vehicle_simulator import vehicle_simulator

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])


@router.get("/bridges/{bridge_id}/state", response_model=InfrastructureState)
def get_bridge_state(
    bridge_id: str, session: Session = Depends(get_session)
) -> InfrastructureState:
    """Return the next virtual Smart Node reading for the requested bridge."""

    if bridge_id != bridge_simulator.node_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infrastructure node '{bridge_id}' was not found",
        )
    state = bridge_simulator.next_state()
    record_infrastructure_state(session, state)
    return state


@router.post("/simulation/reset", response_model=SimulationResetResponse)
def reset_simulation() -> SimulationResetResponse:
    """Reset all virtual infrastructure and vehicle readings for a repeatable demo."""

    bridge_simulator.reset()
    vehicle_simulator.reset()
    return SimulationResetResponse(
        message="Infrastructure and vehicle simulation reset",
        node_id=bridge_simulator.node_id,
    )

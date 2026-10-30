"""Monitoring routes for the virtual infrastructure network."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import (
    InfrastructureState,
    SimulationResetResponse,
)
from ..services.infrastructure_simulator import (
    bridge_simulators,
    get_bridge_simulator,
)
from ..services.infrastructure_state_service import (
    get_current_infrastructure_state,
)
from ..services.persistence_service import record_infrastructure_state
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/infrastructure",
    tags=["infrastructure"],
)


@router.get(
    "/bridges/{bridge_id}/state",
    response_model=InfrastructureState,
)
def get_bridge_state(
    bridge_id: str,
    session: Session = Depends(get_session),
) -> InfrastructureState:
    """Generate and persist a new reading for a specific bridge."""

    try:
        simulator = get_bridge_simulator(bridge_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infrastructure node '{bridge_id}' was not found.",
        )

    state = simulator.next_state()
    record_infrastructure_state(session, state)

    return state


@router.get(
    "/bridges/{bridge_id}/latest",
    response_model=InfrastructureState,
)
def get_latest_bridge_state(
    bridge_id: str,
    session: Session = Depends(get_session),
) -> InfrastructureState:
    """Return the latest persisted reading for a specific bridge."""

    try:
        return get_current_infrastructure_state(
            session,
            bridge_id,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infrastructure node '{bridge_id}' was not found.",
        )


@router.post(
    "/simulation/reset",
    response_model=SimulationResetResponse,
)
def reset_simulation() -> SimulationResetResponse:
    """Reset all virtual infrastructure and vehicle simulations."""

    for simulator in bridge_simulators.values():
        simulator.reset()

    vehicle_simulator.reset()

    return SimulationResetResponse(
        message="Infrastructure network and vehicle simulation reset.",
        node_id="NETWORK",
    )
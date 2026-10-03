"""Monitoring routes for the initial infrastructure prototype."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import (
    InfrastructureState,
    SimulationResetResponse,
    HealthAssessment,
    StructuralHealthCategory,
)
from ..services.infrastructure_simulator import bridge_simulator
from ..services.persistence_service import (
    get_latest_infrastructure_state,
    record_infrastructure_state,
)
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
    """Return the next virtual Smart Node reading."""

    if bridge_id != bridge_simulator.node_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infrastructure node '{bridge_id}' was not found",
        )

    state = bridge_simulator.next_state()

    record_infrastructure_state(
        session,
        state,
    )

    return state


@router.get(
    "/bridges/{bridge_id}/latest",
    response_model=InfrastructureState,
)
def get_latest_bridge_state(
    bridge_id: str,
    session: Session = Depends(get_session),
) -> InfrastructureState:
    """Return the latest persisted Smart Node reading."""

    if bridge_id != bridge_simulator.node_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infrastructure node '{bridge_id}' was not found",
        )

    record = get_latest_infrastructure_state(
        session,
        bridge_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for infrastructure node '{bridge_id}'",
        )

    return InfrastructureState(
        node_id=record.node_id,
        name=bridge_simulator.name,
        infrastructure_type="bridge",
        timestamp=record.recorded_at,
        load_percent=record.load_percent,
        vibration_hz=record.vibration_hz,
        strain=record.strain,
        temperature_c=record.temperature_c,
        traffic_vehicles_per_hour=record.traffic_vehicles_per_hour,
        health=HealthAssessment(
            health_percentage=record.health_percentage,
            risk_score=round(
                1 - (record.health_percentage / 100),
                3,
            ),
            category=StructuralHealthCategory(
                record.health_category
            ),
        ),
    )


@router.post(
    "/simulation/reset",
    response_model=SimulationResetResponse,
)
def reset_simulation() -> SimulationResetResponse:
    """Reset all virtual infrastructure and vehicle readings."""

    bridge_simulator.reset()
    vehicle_simulator.reset()

    return SimulationResetResponse(
        message="Infrastructure and vehicle simulation reset",
        node_id=bridge_simulator.node_id,
    )
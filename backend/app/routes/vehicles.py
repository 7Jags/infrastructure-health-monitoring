"""Routes exposing virtual vehicle telemetry."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import VehicleState
from ..services.persistence_service import record_vehicle_state
from ..services.vehicle_simulator import vehicle_simulator

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("/{vehicle_id}/state", response_model=VehicleState)
def get_vehicle_state(
    vehicle_id: str, session: Session = Depends(get_session)
) -> VehicleState:
    """Return the next simulated reading for a known vehicle."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' was not found",
        )
    state = vehicle_simulator.next_state(vehicle_id)
    record_vehicle_state(session, state)
    return state

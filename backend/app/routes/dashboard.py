"""Unified dashboard snapshot endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..services.infrastructure_state_service import (
    get_current_infrastructure_state,
)
from ..services.safety_service import assess_vehicle_safety
from ..services.uob_service import create_uob_packet
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/current/{vehicle_id}")
def get_current_dashboard_snapshot(
    vehicle_id: str,
    session: Session = Depends(get_session),
) -> dict:
    """Return one snapshot using the vehicle's approaching bridge."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found.",
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
        vehicle=vehicle,
        infrastructure=infrastructure,
    )

    uob = create_uob_packet(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )

    return {
        "infrastructure": infrastructure,
        "vehicle": vehicle,
        "safety": assessment,
        "uob": uob,
    }
"""Unified dashboard snapshot endpoint."""

from fastapi import APIRouter, HTTPException

from ..services.infrastructure_simulator import bridge_simulator
from ..services.safety_service import assess_vehicle_safety
from ..services.uob_service import create_uob_packet
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/current/{vehicle_id}")
def get_current_dashboard_snapshot(vehicle_id: str) -> dict:
    """Return one consistent infrastructure-to-vehicle snapshot."""

    try:
        vehicle = vehicle_simulator.next_state(vehicle_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle {vehicle_id} not found.",
        )

    infrastructure = bridge_simulator.next_state()

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
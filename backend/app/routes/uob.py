"""Routes exposing the virtual infrastructure-to-vehicle broadcast layer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import (
    InfrastructureState,
    UobPacket,
    VehicleSafetyAssessment,
    VehicleState,
)
from ..services.infrastructure_state_service import (
    get_current_infrastructure_state,
)
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.uob_service import create_uob_packet
from ..services.vehicle_simulator import vehicle_simulator


router = APIRouter(
    prefix="/api/uob",
    tags=["uob broadcast"],
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
    """Generate a UOB packet for the bridge the vehicle is approaching."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' was not found.",
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
    """Return the current UOB packet without recording a history event."""

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
    """Generate and persist the UOB packet and its associated safety event."""

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
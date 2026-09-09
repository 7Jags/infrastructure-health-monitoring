"""Routes exposing the virtual infrastructure-to-vehicle broadcast layer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import UobPacket
from ..services.infrastructure_simulator import bridge_simulator
from ..services.persistence_service import record_safety_event
from ..services.safety_service import assess_vehicle_safety
from ..services.uob_service import create_uob_packet
from ..services.vehicle_simulator import vehicle_simulator

router = APIRouter(prefix="/api/uob", tags=["uob broadcast"])


@router.get("/vehicles/{vehicle_id}/latest", response_model=UobPacket)
def get_latest_uob_packet(
    vehicle_id: str, session: Session = Depends(get_session)
) -> UobPacket:
    """Generate the I2V packet currently broadcast to one virtual vehicle."""

    if vehicle_id not in vehicle_simulator.vehicle_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' was not found",
        )

    vehicle = vehicle_simulator.next_state(vehicle_id)
    infrastructure = bridge_simulator.next_state()
    assessment = assess_vehicle_safety(vehicle, infrastructure)
    packet = create_uob_packet(
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
    )
    record_safety_event(
        session,
        vehicle=vehicle,
        infrastructure=infrastructure,
        assessment=assessment,
        packet=packet,
    )
    return packet

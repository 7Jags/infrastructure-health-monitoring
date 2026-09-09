"""Creates virtual I2V Unified On-board Broadcast (UOB) packets."""

from datetime import datetime, timezone
from uuid import uuid4

from ..schemas import (
    InfrastructureState,
    SafetyDecision,
    UobPacket,
    VehicleSafetyAssessment,
    VehicleState,
)

HAZARD_CODES = {
    SafetyDecision.GREEN: "0x00",
    SafetyDecision.AMBER: "0x02",
    SafetyDecision.RED: "0x03",
}


def create_uob_packet(
    *,
    vehicle: VehicleState,
    infrastructure: InfrastructureState,
    assessment: VehicleSafetyAssessment,
) -> UobPacket:
    """Encode the current safety decision as a virtual I2V broadcast packet."""

    return UobPacket(
        packet_id=f"UOB-{uuid4().hex[:12].upper()}",
        format_version="1.0",
        timestamp=datetime.now(timezone.utc),
        source_node_id=infrastructure.node_id,
        target_vehicle_id=vehicle.vehicle_id,
        hazard_code=HAZARD_CODES[assessment.decision],
        decision=assessment.decision,
        bridge_health_percentage=infrastructure.health.health_percentage,
        recommended_speed_kph=assessment.recommended_speed_kph,
        message=assessment.message,
    )

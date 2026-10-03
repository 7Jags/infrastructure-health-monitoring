"""Persists simulation events without coupling routes to SQLAlchemy models."""

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models import (
    InfrastructureTelemetryRecord,
    SafetyDecisionRecord,
    UobPacketRecord,
    VehicleTelemetryRecord,
)
from ..schemas import (
    InfrastructureState,
    UobPacket,
    VehicleSafetyAssessment,
    VehicleState,
)


def record_infrastructure_state(
    session: Session,
    state: InfrastructureState,
) -> None:
    session.add(
        InfrastructureTelemetryRecord(
            node_id=state.node_id,
            recorded_at=state.timestamp,
            load_percent=state.load_percent,
            vibration_hz=state.vibration_hz,
            strain=state.strain,
            temperature_c=state.temperature_c,
            traffic_vehicles_per_hour=state.traffic_vehicles_per_hour,
            health_percentage=state.health.health_percentage,
            health_category=state.health.category.value,
        )
    )

    session.commit()


def get_latest_infrastructure_state(
    session: Session,
    node_id: str,
) -> InfrastructureTelemetryRecord | None:
    """Return the latest persisted infrastructure telemetry record."""

    return (
        session.query(InfrastructureTelemetryRecord)
        .filter(
            InfrastructureTelemetryRecord.node_id == node_id
        )
        .order_by(
            desc(InfrastructureTelemetryRecord.recorded_at)
        )
        .first()
    )


def record_vehicle_state(
    session: Session,
    state: VehicleState,
) -> None:
    session.add(
        VehicleTelemetryRecord(
            vehicle_id=state.vehicle_id,
            recorded_at=state.timestamp,
            speed_kph=state.speed_kph,
            mass_kg=state.mass_kg,
            road_friction=state.road_friction,
            reaction_time_s=state.reaction_time_s,
        )
    )

    session.commit()


def record_safety_event(
    session: Session,
    *,
    vehicle: VehicleState,
    infrastructure: InfrastructureState,
    assessment: VehicleSafetyAssessment,
    packet: UobPacket | None = None,
) -> None:
    """Persist the readings and decision that together form an I2V event."""

    session.add_all(
        [
            InfrastructureTelemetryRecord(
                node_id=infrastructure.node_id,
                recorded_at=infrastructure.timestamp,
                load_percent=infrastructure.load_percent,
                vibration_hz=infrastructure.vibration_hz,
                strain=infrastructure.strain,
                temperature_c=infrastructure.temperature_c,
                traffic_vehicles_per_hour=infrastructure.traffic_vehicles_per_hour,
                health_percentage=infrastructure.health.health_percentage,
                health_category=infrastructure.health.category.value,
            ),
            VehicleTelemetryRecord(
                vehicle_id=vehicle.vehicle_id,
                recorded_at=vehicle.timestamp,
                speed_kph=vehicle.speed_kph,
                mass_kg=vehicle.mass_kg,
                road_friction=vehicle.road_friction,
                reaction_time_s=vehicle.reaction_time_s,
            ),
            SafetyDecisionRecord(
                vehicle_id=vehicle.vehicle_id,
                node_id=infrastructure.node_id,
                recorded_at=infrastructure.timestamp,
                decision=assessment.decision.value,
                recommended_speed_kph=assessment.recommended_speed_kph,
                stopping_distance_m=assessment.stopping_distance_m,
                available_stopping_distance_m=assessment.available_stopping_distance_m,
                safety_margin_m=assessment.safety_margin_m,
                message=assessment.message,
            ),
        ]
    )

    if packet is not None:
        session.add(
            UobPacketRecord(
                packet_id=packet.packet_id,
                target_vehicle_id=packet.target_vehicle_id,
                source_node_id=packet.source_node_id,
                recorded_at=packet.timestamp,
                hazard_code=packet.hazard_code,
                decision=packet.decision.value,
                recommended_speed_kph=packet.recommended_speed_kph,
                message=packet.message,
            )
        )

    session.commit()
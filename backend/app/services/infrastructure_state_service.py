"""Load the latest persisted state for a specific bridge."""

from sqlalchemy.orm import Session

from ..schemas import (
    HealthAssessment,
    InfrastructureState,
    StructuralHealthCategory,
)
from .infrastructure_simulator import get_bridge_simulator
from .persistence_service import (
    get_latest_infrastructure_state,
    record_infrastructure_state,
)


def get_current_infrastructure_state(
    session: Session,
    node_id: str,
) -> InfrastructureState:
    """Return the latest state for a bridge, creating one if necessary."""

    simulator = get_bridge_simulator(node_id)

    record = get_latest_infrastructure_state(
        session,
        node_id,
    )

    if record is None:
        state = simulator.next_state()
        record_infrastructure_state(session, state)
        return state

    health_percentage = record.health_percentage

    return InfrastructureState(
        node_id=record.node_id,
        name=simulator.name,
        infrastructure_type="bridge",
        timestamp=record.recorded_at,
        load_percent=record.load_percent,
        vibration_hz=record.vibration_hz,
        strain=record.strain,
        temperature_c=record.temperature_c,
        traffic_vehicles_per_hour=record.traffic_vehicles_per_hour,
        health=HealthAssessment(
            health_percentage=health_percentage,
            risk_score=round(1.0 - health_percentage / 100.0, 3),
            category=StructuralHealthCategory(record.health_category),
        ),
    )
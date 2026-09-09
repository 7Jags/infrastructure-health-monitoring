"""Read-only historical data routes for the dashboard."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import (
    InfrastructureTelemetryRecord,
    SafetyDecisionRecord,
    UobPacketRecord,
    VehicleTelemetryRecord,
)
from ..schemas import (
    InfrastructureTelemetryHistory,
    SafetyDecisionHistory,
    UobPacketHistory,
    VehicleTelemetryHistory,
)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/infrastructure/{node_id}", response_model=list[InfrastructureTelemetryHistory])
def get_infrastructure_history(
    node_id: str,
    limit: int = Query(default=50, ge=1, le=250),
    session: Session = Depends(get_session),
) -> list[InfrastructureTelemetryRecord]:
    return list(
        session.scalars(
            select(InfrastructureTelemetryRecord)
            .where(InfrastructureTelemetryRecord.node_id == node_id)
            .order_by(InfrastructureTelemetryRecord.recorded_at.desc())
            .limit(limit)
        )
    )


@router.get("/vehicles/{vehicle_id}", response_model=list[VehicleTelemetryHistory])
def get_vehicle_history(
    vehicle_id: str,
    limit: int = Query(default=50, ge=1, le=250),
    session: Session = Depends(get_session),
) -> list[VehicleTelemetryRecord]:
    return list(
        session.scalars(
            select(VehicleTelemetryRecord)
            .where(VehicleTelemetryRecord.vehicle_id == vehicle_id)
            .order_by(VehicleTelemetryRecord.recorded_at.desc())
            .limit(limit)
        )
    )


@router.get("/safety/vehicles/{vehicle_id}", response_model=list[SafetyDecisionHistory])
def get_safety_history(
    vehicle_id: str,
    limit: int = Query(default=50, ge=1, le=250),
    session: Session = Depends(get_session),
) -> list[SafetyDecisionRecord]:
    return list(
        session.scalars(
            select(SafetyDecisionRecord)
            .where(SafetyDecisionRecord.vehicle_id == vehicle_id)
            .order_by(SafetyDecisionRecord.recorded_at.desc())
            .limit(limit)
        )
    )


@router.get("/uob/vehicles/{vehicle_id}", response_model=list[UobPacketHistory])
def get_uob_history(
    vehicle_id: str,
    limit: int = Query(default=50, ge=1, le=250),
    session: Session = Depends(get_session),
) -> list[UobPacketRecord]:
    return list(
        session.scalars(
            select(UobPacketRecord)
            .where(UobPacketRecord.target_vehicle_id == vehicle_id)
            .order_by(UobPacketRecord.recorded_at.desc())
            .limit(limit)
        )
    )

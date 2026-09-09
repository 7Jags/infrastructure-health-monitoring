"""SQLAlchemy models for recorded platform events."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class InfrastructureTelemetryRecord(Base):
    __tablename__ = "infrastructure_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[str] = mapped_column(String(32), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    load_percent: Mapped[float] = mapped_column(Float)
    vibration_hz: Mapped[float] = mapped_column(Float)
    strain: Mapped[float] = mapped_column(Float)
    temperature_c: Mapped[float] = mapped_column(Float)
    traffic_vehicles_per_hour: Mapped[int] = mapped_column(Integer)
    health_percentage: Mapped[float] = mapped_column(Float)
    health_category: Mapped[str] = mapped_column(String(20))


class VehicleTelemetryRecord(Base):
    __tablename__ = "vehicle_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(32), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    speed_kph: Mapped[float] = mapped_column(Float)
    mass_kg: Mapped[float] = mapped_column(Float)
    road_friction: Mapped[float] = mapped_column(Float)
    reaction_time_s: Mapped[float] = mapped_column(Float)


class SafetyDecisionRecord(Base):
    __tablename__ = "safety_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(32), index=True)
    node_id: Mapped[str] = mapped_column(String(32), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    decision: Mapped[str] = mapped_column(String(10))
    recommended_speed_kph: Mapped[float] = mapped_column(Float)
    stopping_distance_m: Mapped[float] = mapped_column(Float)
    available_stopping_distance_m: Mapped[float] = mapped_column(Float)
    safety_margin_m: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text)


class UobPacketRecord(Base):
    __tablename__ = "uob_packets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    packet_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    target_vehicle_id: Mapped[str] = mapped_column(String(32), index=True)
    source_node_id: Mapped[str] = mapped_column(String(32), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    hazard_code: Mapped[str] = mapped_column(String(8))
    decision: Mapped[str] = mapped_column(String(10))
    recommended_speed_kph: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text)

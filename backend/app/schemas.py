
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StructuralHealthCategory(StrEnum):
    NORMAL = "normal"
    CAUTION = "caution"
    HIGH_RISK = "high_risk"


class HealthAssessment(BaseModel):
    """The health result calculated from a structure's latest telemetry."""

    health_percentage: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=1)
    category: StructuralHealthCategory


class InfrastructureState(BaseModel):
    """A complete state snapshot for one monitored piece of infrastructure."""

    node_id: str
    name: str
    infrastructure_type: str
    timestamp: datetime
    load_percent: float = Field(ge=0, le=100)
    vibration_hz: float = Field(ge=0)
    strain: float = Field(ge=0)
    temperature_c: float
    traffic_vehicles_per_hour: int = Field(ge=0)
    health: HealthAssessment


class SimulationResetResponse(BaseModel):
    message: str
    node_id: str


class VehicleType(StrEnum):
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"


class VehicleState(BaseModel):
    """A current reading from one simulated vehicle approaching a bridge."""

    vehicle_id: str
    vehicle_type: VehicleType
    timestamp: datetime

    approaching_node_id: str
    current_segment_id: str = "unknown"
    distance_to_bridge_m: float = Field(default=0, ge=0)

    speed_kph: float = Field(ge=0)
    mass_kg: float = Field(gt=0)
    road_friction: float = Field(gt=0, le=1)
    reaction_time_s: float = Field(gt=0)


class SafetyDecision(StrEnum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class VehicleSafetyAssessment(BaseModel):
    """Vehicle-specific safety calculations and recommendation."""

    decision: SafetyDecision

    # Speed recommendations.
    recommended_speed_kph: float = Field(ge=0)
    approach_speed_limit_kph: float = Field(ge=0)
    crossing_speed_limit_kph: float = Field(ge=0)

    # Stopping-distance calculations.
    reaction_distance_m: float = Field(ge=0)
    braking_distance_m: float = Field(ge=0)
    stopping_distance_m: float = Field(ge=0)
    safety_buffer_m: float = Field(ge=0)
    available_stopping_distance_m: float = Field(ge=0)
    safety_margin_m: float

    # Vehicle physics.
    kinetic_energy_j: float = Field(ge=0)

    # Whether the vehicle can stop before the reserved boundary.
    can_stop_before_bridge: bool

    message: str


class SafetyDecisionResponse(BaseModel):
    vehicle: VehicleState
    infrastructure: InfrastructureState
    assessment: VehicleSafetyAssessment


class UobPacket(BaseModel):
    """A virtual Unified On-board Broadcast from a Smart Node to a vehicle."""

    packet_id: str
    format_version: str
    timestamp: datetime
    source_node_id: str
    target_vehicle_id: str
    hazard_code: str
    decision: SafetyDecision
    bridge_health_percentage: float = Field(ge=0, le=100)
    recommended_speed_kph: float = Field(ge=0)
    message: str


class InfrastructureTelemetryHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    node_id: str
    recorded_at: datetime
    load_percent: float
    vibration_hz: float
    strain: float
    temperature_c: float
    traffic_vehicles_per_hour: int
    health_percentage: float
    health_category: StructuralHealthCategory


class VehicleTelemetryHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: str
    recorded_at: datetime
    speed_kph: float
    mass_kg: float
    road_friction: float
    reaction_time_s: float


class SafetyDecisionHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: str
    node_id: str
    recorded_at: datetime
    decision: SafetyDecision
    recommended_speed_kph: float
    stopping_distance_m: float
    available_stopping_distance_m: float
    safety_margin_m: float
    message: str


class UobPacketHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    packet_id: str
    target_vehicle_id: str
    source_node_id: str
    recorded_at: datetime
    hazard_code: str
    decision: SafetyDecision
    recommended_speed_kph: float
    message: str
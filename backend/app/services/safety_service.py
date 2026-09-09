"""Explainable safety logic joining vehicle and infrastructure conditions."""

from ..schemas import (
    InfrastructureState,
    SafetyDecision,
    VehicleSafetyAssessment,
    VehicleState,
)

GRAVITY_M_PER_S2 = 9.81
FULL_HEALTH_STOPPING_DISTANCE_M = 140.0


def calculate_stopping_distance_m(vehicle: VehicleState) -> float:
    """Calculate reaction plus braking distance on the current road surface."""

    speed_mps = vehicle.speed_kph / 3.6
    reaction_distance = speed_mps * vehicle.reaction_time_s
    braking_distance = speed_mps**2 / (2 * GRAVITY_M_PER_S2 * vehicle.road_friction)
    return round(reaction_distance + braking_distance, 1)


def assess_vehicle_safety(
    vehicle: VehicleState, infrastructure: InfrastructureState
) -> VehicleSafetyAssessment:
    """Return the current I2V decision for a vehicle approaching a bridge."""

    stopping_distance = calculate_stopping_distance_m(vehicle)
    available_distance = round(
        FULL_HEALTH_STOPPING_DISTANCE_M * infrastructure.health.health_percentage / 100,
        1,
    )
    safety_margin = round(available_distance - stopping_distance, 1)

    if infrastructure.health.category.value == "high_risk" or safety_margin < 0:
        decision = SafetyDecision.RED
        recommended_speed = 25.0
        message = (
            f"Stop or slow immediately: {infrastructure.node_id} has elevated risk. "
            "Recommended speed: 25 km/h."
        )
    elif infrastructure.health.category.value == "caution" or safety_margin < 20:
        decision = SafetyDecision.AMBER
        recommended_speed = 40.0
        message = (
            f"Caution at {infrastructure.node_id}: reduce speed and maintain distance. "
            "Recommended speed: 40 km/h."
        )
    else:
        decision = SafetyDecision.GREEN
        recommended_speed = 60.0
        message = f"{infrastructure.node_id} is operating normally. Proceed with care."

    return VehicleSafetyAssessment(
        decision=decision,
        recommended_speed_kph=recommended_speed,
        stopping_distance_m=stopping_distance,
        available_stopping_distance_m=available_distance,
        safety_margin_m=safety_margin,
        message=message,
    )

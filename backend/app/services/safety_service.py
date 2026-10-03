
"""Explainable safety logic joining vehicle and infrastructure conditions."""

from math import sqrt

from ..schemas import (
    InfrastructureState,
    SafetyDecision,
    VehicleSafetyAssessment,
    VehicleState,
)

GRAVITY_M_PER_S2 = 9.81
SAFETY_BUFFER_M = 10.0
LOW_MARGIN_THRESHOLD_M = 20.0

# Provisional demonstration policy.
# These values should eventually be configurable.
CROSSING_SPEED_LIMITS = {
    "normal": 60.0,
    "caution": 30.0,
    "high_risk": 0.0,
}


def _calculate_stopping_components(
    vehicle: VehicleState,
) -> tuple[float, float]:
    """Calculate reaction distance and braking distance."""

    speed_mps = vehicle.speed_kph / 3.6

    reaction_distance = speed_mps * vehicle.reaction_time_s

    braking_distance = (
        speed_mps**2
        / (2 * GRAVITY_M_PER_S2 * vehicle.road_friction)
    )

    return reaction_distance, braking_distance


def calculate_stopping_distance_m(vehicle: VehicleState) -> float:
    """Calculate total stopping distance."""

    reaction_distance, braking_distance = (
        _calculate_stopping_components(vehicle)
    )

    return round(reaction_distance + braking_distance, 1)


def calculate_kinetic_energy_j(vehicle: VehicleState) -> float:
    """Calculate the vehicle's kinetic energy in joules."""

    speed_mps = vehicle.speed_kph / 3.6

    kinetic_energy = 0.5 * vehicle.mass_kg * speed_mps**2

    return round(kinetic_energy, 1)


def calculate_approach_speed_limit_kph(
    available_distance_m: float,
    reaction_time_s: float,
    road_friction: float,
) -> float:
    """
    Calculate the maximum theoretical approach speed that allows
    the vehicle to stop within the available distance.

    Formula:
        D = v*t + v²/(2*mu*g)
    """

    if available_distance_m <= 0:
        return 0.0

    friction_acceleration = road_friction * GRAVITY_M_PER_S2

    speed_mps = (
        -friction_acceleration * reaction_time_s
        + sqrt(
            (friction_acceleration * reaction_time_s) ** 2
            + 2 * friction_acceleration * available_distance_m
        )
    )

    return round(max(0.0, speed_mps * 3.6), 1)


def assess_vehicle_safety(
    vehicle: VehicleState,
    infrastructure: InfrastructureState,
) -> VehicleSafetyAssessment:
    """Return the current I2V safety assessment for an approaching vehicle."""

    # 1. Calculate the vehicle's stopping requirements.
    reaction_distance, braking_distance = (
        _calculate_stopping_components(vehicle)
    )

    stopping_distance = round(
        reaction_distance + braking_distance, 1
    )

    # 2. Calculate the usable distance before the bridge.
    # Keep a fixed buffer between the stopping point and the bridge.
    available_distance = round(
        max(0.0, vehicle.distance_to_bridge_m - SAFETY_BUFFER_M),
        1,
    )

    safety_margin = round(
        available_distance - stopping_distance, 1
    )

    can_stop_before_bridge = safety_margin >= 0

    # 3. Calculate the theoretical approach speed limit.
    approach_speed_limit = calculate_approach_speed_limit_kph(
        available_distance_m=available_distance,
        reaction_time_s=vehicle.reaction_time_s,
        road_friction=vehicle.road_friction,
    )

    # 4. Determine the structural condition and crossing speed limit.
    health_category = infrastructure.health.category.value

    crossing_speed_limit = CROSSING_SPEED_LIMITS.get(
        health_category,
        0.0,
    )

    # 5. The recommended speed cannot exceed either limit.
    recommended_speed = min(
        approach_speed_limit,
        crossing_speed_limit,
    )

    # 6. Calculate kinetic energy.
    kinetic_energy = calculate_kinetic_energy_j(vehicle)

    # 7. Determine the safety decision.
    if health_category == "high_risk":
        decision = SafetyDecision.RED

        if can_stop_before_bridge:
            message = (
                f"STOP: {infrastructure.node_id} is in a high-risk "
                "condition. Stop before entering the bridge."
            )
        else:
            message = (
                f"EMERGENCY: {infrastructure.node_id} is in a high-risk "
                "condition, and the vehicle cannot stop within the "
                "available distance. Take immediate emergency action."
            )

    elif not can_stop_before_bridge:
        decision = SafetyDecision.RED
        message = (
            f"EMERGENCY: The vehicle cannot stop before "
            f"{infrastructure.node_id}. Immediate action is required."
        )

    elif (
        health_category == "caution"
        or safety_margin < LOW_MARGIN_THRESHOLD_M
        or vehicle.speed_kph > recommended_speed + 0.5
    ):
        decision = SafetyDecision.AMBER
        message = (
            f"CAUTION: Reduce speed while approaching "
            f"{infrastructure.node_id}. "
            f"Recommended speed: {recommended_speed:.1f} km/h."
        )

    else:
        decision = SafetyDecision.GREEN
        message = (
            f"{infrastructure.node_id} is operating normally. "
            "Maintain a safe approach speed."
        )

    # 8. Return the complete assessment.
    return VehicleSafetyAssessment(
        decision=decision,
        recommended_speed_kph=round(recommended_speed, 1),
        approach_speed_limit_kph=approach_speed_limit,
        crossing_speed_limit_kph=crossing_speed_limit,
        reaction_distance_m=round(reaction_distance, 1),
        braking_distance_m=round(braking_distance, 1),
        stopping_distance_m=stopping_distance,
        safety_buffer_m=SAFETY_BUFFER_M,
        available_stopping_distance_m=available_distance,
        safety_margin_m=safety_margin,
        kinetic_energy_j=kinetic_energy,
        can_stop_before_bridge=can_stop_before_bridge,
        message=message,
    )
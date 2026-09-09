"""Deterministic structural-health calculations for the first prototype."""

from ..schemas import HealthAssessment, StructuralHealthCategory


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def assess_structural_health(
    *,
    load_percent: float,
    vibration_hz: float,
    strain: float,
    temperature_c: float,
) -> HealthAssessment:
    """Return a transparent rule-based health assessment.

    Version one uses explainable rules. A future predictive model can replace
    these factors without changing the API contract.
    """

    load_risk = _clamp((load_percent - 50.0) / 50.0)
    vibration_risk = _clamp((vibration_hz - 3.0) / 6.0)
    strain_risk = _clamp((strain - 0.0015) / 0.0035)
    temperature_risk = _clamp((abs(temperature_c - 24.0) - 8.0) / 18.0)

    risk_score = (
        load_risk * 0.30
        + vibration_risk * 0.30
        + strain_risk * 0.25
        + temperature_risk * 0.15
    )
    health_percentage = round((1.0 - risk_score) * 100.0, 1)

    if health_percentage >= 70:
        category = StructuralHealthCategory.NORMAL
    elif health_percentage >= 45:
        category = StructuralHealthCategory.CAUTION
    else:
        category = StructuralHealthCategory.HIGH_RISK

    return HealthAssessment(
        health_percentage=health_percentage,
        risk_score=round(risk_score, 3),
        category=category,
    )

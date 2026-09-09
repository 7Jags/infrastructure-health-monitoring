from app.schemas import StructuralHealthCategory
from app.services.health_service import assess_structural_health


def test_low_risk_telemetry_is_normal() -> None:
    assessment = assess_structural_health(
        load_percent=55,
        vibration_hz=2.4,
        strain=0.0012,
        temperature_c=24,
    )

    assert assessment.category is StructuralHealthCategory.NORMAL
    assert assessment.health_percentage > 90


def test_extreme_telemetry_is_high_risk() -> None:
    assessment = assess_structural_health(
        load_percent=100,
        vibration_hz=10,
        strain=0.006,
        temperature_c=50,
    )

    assert assessment.category is StructuralHealthCategory.HIGH_RISK
    assert assessment.health_percentage == 0

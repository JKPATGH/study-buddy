"""Percentage-to-GPA conversion helpers (standard US 4.0 scale, with weighted bonuses)."""

WEIGHT_BONUS = {
    "Regular": 0.0,
    "Honors": 0.5,
    "AP/IB": 1.0,
}


def percentage_to_base_gpa(percentage: float) -> float:
    """Convert a 0-100 percentage grade to an unweighted 4.0-scale GPA point value."""
    if percentage >= 93:
        return 4.0
    if percentage >= 90:
        return 3.7
    if percentage >= 87:
        return 3.3
    if percentage >= 83:
        return 3.0
    if percentage >= 80:
        return 2.7
    if percentage >= 77:
        return 2.3
    if percentage >= 73:
        return 2.0
    if percentage >= 70:
        return 1.7
    if percentage >= 67:
        return 1.3
    if percentage >= 63:
        return 1.0
    if percentage >= 60:
        return 0.7
    return 0.0


def class_gpa(percentage: float, weight: str) -> float:
    """GPA point value for one class, including a bonus for Honors/AP/IB weighting."""
    return percentage_to_base_gpa(percentage) + WEIGHT_BONUS.get(weight, 0.0)


def overall_gpa(classes: list[dict]) -> float:
    """Average weighted GPA across a list of {"percentage": float, "weight": str} entries."""
    if not classes:
        return 0.0
    total = sum(class_gpa(c["percentage"], c.get("weight", "Regular")) for c in classes)
    return round(total / len(classes), 3)

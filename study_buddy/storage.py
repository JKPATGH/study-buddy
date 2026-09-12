"""Simple JSON-backed local storage for Study Buddy app data (calendar, periods, GPA, planner)."""
import json
from pathlib import Path

DATA_DIR = Path.home() / "Library" / "Application Support" / "StudyBuddy"
DATA_FILE = DATA_DIR / "data.json"

DEFAULT_DATA = {
    "calendar": [],       # [{"date": "2026-09-15", "title": "Chemistry test"}]
    "periods": [],        # [{"period": "1", "class_name": "Algebra II", "teacher": "", "time": "8:00-8:50"}]
    "gpa_classes": [],    # [{"name": "Algebra II", "percentage": 94, "weight": "Regular"}]
    "plan": [],           # [{"year": "Freshman", "note": "Take Biology + Geometry"}]
}


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            loaded = json.loads(DATA_FILE.read_text())
            return {**DEFAULT_DATA, **loaded}
        except (json.JSONDecodeError, OSError):
            pass
    return {key: list(value) for key, value in DEFAULT_DATA.items()}


def save_data(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2))

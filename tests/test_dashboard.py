"""Smoke-test the actual Streamlit dashboard, not just its HTTP health endpoint."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_dashboard_renders_seeded_data():
    script = Path(__file__).resolve().parents[1] / "dashboard.py"
    at = AppTest.from_file(str(script), default_timeout=45).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]
    assert len(at.metric) == 3
    assert at.title[0].value == "Cohort Retention Lab"


def test_dashboard_age_control_rerenders_without_errors():
    script = Path(__file__).resolve().parents[1] / "dashboard.py"
    at = AppTest.from_file(str(script), default_timeout=45).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]
    at.slider[0].set_value(6).run()
    assert len(at.exception) == 0, [str(e.message) for e in at.exception]

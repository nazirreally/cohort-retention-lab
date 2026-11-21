"""Regression tests for invalid CSV values and timezone normalization."""
import pandas as pd
import pytest
from cohortlab.core import prepare, monthly_metrics


def sample(**changes):
    row = {"customer_id": "cust-1", "event_date": "2024-01-02", "revenue": 10.0}
    row.update(changes)
    return pd.DataFrame([row])


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_customer_id_rejected(value):
    with pytest.raises(ValueError, match="Customer IDs"):
        prepare(sample(customer_id=value))


@pytest.mark.parametrize("value", [None, pd.NaT])
def test_missing_event_date_rejected(value):
    with pytest.raises(ValueError, match="Event dates"):
        prepare(sample(event_date=value))


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan"), -0.01])
def test_invalid_revenue_rejected(value):
    with pytest.raises(ValueError, match="Revenue"):
        prepare(sample(revenue=value))


def test_timezone_aware_events_normalized_to_utc_month():
    events = sample(event_date="2024-02-01T00:30:00+02:00")
    assert str(prepare(events).iloc[0]["month"]) == "2024-01"
    assert monthly_metrics(events).iloc[0]["month"] == "2024-01"


def test_valid_data_unchanged():
    assert prepare(sample()).iloc[0]["revenue"] == 10.0

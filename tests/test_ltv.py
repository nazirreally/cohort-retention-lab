"""Regression coverage for maturity-aware observed revenue per original customer."""
import pandas as pd
import pytest

from cohortlab.ltv import cohort_ltv


@pytest.fixture
def events():
    return pd.DataFrame(
        [
            ("a", "2024-01-05", 10),
            ("b", "2024-01-06", 20),
            ("a", "2024-03-01", 30),
            ("c", "2024-03-01", 8),
            ("c", "2024-04-01", 2),
        ],
        columns=["customer_id", "event_date", "revenue"],
    )


def test_zero_month_and_cumulative_revenue(events):
    result = cohort_ltv(events, max_age=3, as_of="2024-04")
    january = result[result.cohort == "2024-01"].reset_index(drop=True)
    assert january.age.tolist() == [0, 1, 2, 3]
    assert january.revenue.tolist() == [30, 0, 30, 0]
    assert january.cumulative_revenue.tolist() == [30, 30, 60, 60]
    assert january.revenue_per_original_customer.tolist() == [15, 15, 30, 30]


def test_future_cohort_ages_not_reported(events):
    result = cohort_ltv(events, max_age=12, as_of="2024-04")
    assert result[result.cohort == "2024-03"].age.tolist() == [0, 1]


def test_cutoff_excludes_later_revenue(events):
    result = cohort_ltv(events, max_age=3, as_of="2024-03")
    assert result[result.cohort == "2024-03"].revenue.tolist() == [8]


def test_invalid_horizon_rejected(events):
    with pytest.raises(ValueError, match="max_age"):
        cohort_ltv(events, max_age=-1)

import pandas as pd
import pytest
from cohortlab.maturity import retention_matrix, retention_summary


@pytest.fixture
def events():
    return pd.DataFrame([
        ("A", "2024-01-01", 1), ("B", "2024-01-03", 1),
        ("A", "2024-03-02", 1), ("C", "2024-03-10", 1),
        ("C", "2024-04-01", 1),
    ], columns=["customer_id", "event_date", "revenue"])


def test_zero_activity_month_included(events):
    m = retention_matrix(events)
    jan = m[m.cohort == "2024-01"].set_index("age")
    assert jan.loc[1, "active_users"] == 0
    assert jan.loc[1, "retention_rate"] == 0
    assert jan.loc[2, "active_users"] == 1


def test_immature_cohort_excluded(events):
    m = retention_matrix(events)
    assert set(m[m.cohort == "2024-03"].age) == {0, 1}
    assert len(m[m.cohort == "2024-01"]) == 4


def test_as_of_excludes_future_events(events):
    m = retention_matrix(events, as_of="2024-03")
    assert m.as_of.unique().tolist() == ["2024-03"]
    assert set(m[m.cohort == "2024-03"].age) == {0}


def test_weighted_summary(events):
    s = retention_summary(retention_matrix(events))
    age1 = s[s.age == 1].iloc[0]
    assert age1.eligible_users == 3
    assert age1.active_users == 1
    assert age1.weighted_retention == pytest.approx(1 / 3)


def test_max_age(events):
    assert retention_matrix(events, max_age=0).age.max() == 0
    with pytest.raises(ValueError, match="max_age"):
        retention_matrix(events, max_age=-1)


def test_future_cutoff_rejected(events):
    with pytest.raises(ValueError, match="as_of"):
        retention_matrix(events, as_of="2024-05")


def test_empty_summary():
    assert retention_summary(pd.DataFrame()).empty

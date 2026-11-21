import pandas as pd
import pytest
from cohortlab.core import prepare, retention, revenue_by_cohort, monthly_metrics
from cohortlab.generate import generate

@pytest.fixture
def sample():
    return pd.DataFrame([
        ("A", "2024-01-01", 10),
        ("A", "2024-01-15", 5),
        ("B", "2024-01-20", 20),
        ("A", "2024-02-01", 10),
        ("C", "2024-02-03", 40),
        ("B", "2024-03-05", 20),
    ], columns=["customer_id", "event_date", "revenue"])

def test_dedup_active_customers(sample):
    r = retention(sample)
    assert r.loc[(r.cohort == "2024-01") & (r.age == 0), "active_users"].item() == 2

def test_cohort_retention(sample):
    r = retention(sample)
    assert r.loc[(r.cohort == "2024-01") & (r.age == 1), "retention_rate"].item() == .5
    assert r.loc[(r.cohort == "2024-01") & (r.age == 2), "retention_rate"].item() == .5

def test_cohort_revenue(sample):
    r = revenue_by_cohort(sample)
    assert r.loc[(r.cohort == "2024-01") & (r.age == 0), "revenue"].item() == 35

def test_monthly_arpu(sample):
    m = monthly_metrics(sample)
    assert m.loc[m.month == "2024-01", "arpu"].item() == 17.5

def test_bad_columns(sample):
    with pytest.raises(ValueError, match="Missing columns"):
        prepare(sample.drop(columns=["revenue"]))

def test_negative_revenue(sample):
    sample.loc[0, "revenue"] = -1
    with pytest.raises(ValueError, match="nonnegative"):
        prepare(sample)

def test_bad_date(sample):
    sample.loc[0, "event_date"] = "not-a-date"
    with pytest.raises(ValueError):
        prepare(sample)

def test_null_customer(sample):
    sample.loc[0, "customer_id"] = None
    with pytest.raises(ValueError, match="Customer IDs must be nonempty"):
        prepare(sample)

def test_empty():
    with pytest.raises(ValueError, match="No events"):
        prepare(pd.DataFrame(columns=["customer_id", "event_date", "revenue"]))

def test_seed_reproducible():
    pd.testing.assert_frame_equal(generate(seed=8, customers=20), generate(seed=8, customers=20))

def test_synthetic_revenue_positive():
    d = generate(customers=20, months=4)
    assert (d.revenue > 0).all()
    assert d.customer_id.nunique() == 20

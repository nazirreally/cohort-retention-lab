"""Censoring-aware cumulative revenue per acquired customer (observed LTV proxy)."""
import pandas as pd
from .core import prepare
from .maturity import retention_matrix


def cohort_ltv(events: pd.DataFrame, max_age: int = 12, as_of=None) -> pd.DataFrame:
    """Revenue by cohort age, including zero-revenue mature months.

    Cumulative revenue is divided by original cohort size (not active users).
    Future cohort ages are excluded. This is observed revenue, not predicted LTV.
    """
    grid = retention_matrix(events, max_age=max_age, as_of=as_of)
    df = prepare(events)
    cutoff = pd.Period(grid["as_of"].iloc[0], freq="M")
    observed = df.loc[df["month"] <= cutoff]
    revenue = observed.groupby(["cohort", "age"])["revenue"].sum()
    result = grid[["cohort", "age", "cohort_size", "as_of"]].copy()
    result["revenue"] = [
        float(revenue.get((pd.Period(cohort, freq="M"), int(age)), 0.0))
        for cohort, age in zip(result["cohort"], result["age"])
    ]
    result["cumulative_revenue"] = result.groupby("cohort", sort=False)["revenue"].cumsum()
    result["revenue_per_original_customer"] = (
        result["cumulative_revenue"] / result["cohort_size"]
    )
    return result

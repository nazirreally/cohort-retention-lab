"""Censoring-aware cohort retention with explicit zero-activity periods."""
import pandas as pd
from .core import prepare


def retention_matrix(events: pd.DataFrame, max_age: int = 12, as_of=None) -> pd.DataFrame:
    """Return one row per observed cohort and mature age.

    A missing mature age is zero retention, while an immature age is omitted.
    as_of is an observation cutoff month, never a forecast date.
    """
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 0:
        raise ValueError("max_age must be a nonnegative integer")
    df = prepare(events)
    observed = df["month"].max()
    cutoff = pd.Period(as_of, freq="M") if as_of is not None else observed
    if cutoff > observed:
        raise ValueError("as_of cannot exceed the latest observed event month")
    df = df.loc[df["month"] <= cutoff]
    if df.empty:
        raise ValueError("No events at or before as_of")
    cohort_size = df.groupby("cohort")["customer_id"].nunique()
    active = df.groupby(["cohort", "age"])["customer_id"].nunique()
    rows = []
    for cohort, size in cohort_size.items():
        mature_age = min(max_age, (cutoff.year - cohort.year) * 12 + cutoff.month - cohort.month)
        for age in range(mature_age + 1):
            count = int(active.get((cohort, age), 0))
            rows.append({"cohort": str(cohort), "age": age,
                         "cohort_size": int(size), "active_users": count,
                         "retention_rate": count / int(size), "as_of": str(cutoff)})
    return pd.DataFrame(rows, columns=["cohort", "age", "cohort_size",
                                      "active_users", "retention_rate", "as_of"])


def retention_summary(matrix: pd.DataFrame) -> pd.DataFrame:
    """Cohort-size-weighted retention for each age, excluding immature cohorts."""
    if matrix.empty:
        return pd.DataFrame(columns=["age", "eligible_cohorts", "eligible_users",
                                     "active_users", "weighted_retention"])
    grouped = matrix.groupby("age", as_index=False).agg(
        eligible_cohorts=("cohort", "nunique"),
        eligible_users=("cohort_size", "sum"), active_users=("active_users", "sum"))
    grouped["weighted_retention"] = grouped.active_users / grouped.eligible_users
    return grouped

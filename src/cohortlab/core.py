import pandas as pd


REQUIRED = {"customer_id", "event_date", "revenue"}


def prepare(events: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(events.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if events.empty:
        raise ValueError("No events")
    df = events.copy()
    if df["customer_id"].isna().any():
        raise ValueError("Null customer IDs")
    df["event_date"] = pd.to_datetime(df["event_date"], errors="raise")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="raise")
    if df["revenue"].isna().any() or (df["revenue"] < 0).any():
        raise ValueError("Revenue must be nonnegative")
    df["month"] = df["event_date"].dt.to_period("M")
    first = df.groupby("customer_id")["month"].min().rename("cohort")
    df = df.join(first, on="customer_id")
    df["age"] = (df["month"].dt.year - df["cohort"].dt.year) * 12 + (df["month"].dt.month - df["cohort"].dt.month)
    return df


def retention(events: pd.DataFrame) -> pd.DataFrame:
    df = prepare(events)
    active = df.groupby(["cohort", "age"])["customer_id"].nunique().rename("active_users").reset_index()
    sizes = active.loc[active["age"] == 0, ["cohort", "active_users"]].rename(columns={"active_users": "cohort_size"})
    result = active.merge(sizes, on="cohort")
    result["retention_rate"] = result["active_users"] / result["cohort_size"]
    result["cohort"] = result["cohort"].astype(str)
    return result.sort_values(["cohort", "age"]).reset_index(drop=True)


def revenue_by_cohort(events: pd.DataFrame) -> pd.DataFrame:
    df = prepare(events)
    result = df.groupby(["cohort", "age"], as_index=False)["revenue"].sum()
    result["cohort"] = result["cohort"].astype(str)
    return result.sort_values(["cohort", "age"]).reset_index(drop=True)


def monthly_metrics(events: pd.DataFrame) -> pd.DataFrame:
    df = prepare(events)
    result = df.groupby("month").agg(active_customers=("customer_id", "nunique"), revenue=("revenue", "sum")).reset_index()
    result["arpu"] = result["revenue"] / result["active_customers"]
    result["month"] = result["month"].astype(str)
    return result

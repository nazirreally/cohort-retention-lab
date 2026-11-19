"""Deterministic synthetic SaaS billing activity; no real customer data."""
import numpy as np
import pandas as pd


def generate(seed: int = 42, customers: int = 800, months: int = 18) -> pd.DataFrame:
    if customers < 1 or months < 1:
        raise ValueError("customers and months must be positive")
    rng = np.random.default_rng(seed)
    start = pd.Period("2024-01", freq="M")
    rows = []
    for cid in range(1, customers + 1):
        joined = int(rng.integers(0, months))
        plan = float(rng.choice([19, 49, 99], p=[0.55, 0.35, 0.10]))
        for m in range(joined, months):
            age = m - joined
            probability = 1.0 if age == 0 else max(0.15, 0.88 ** age)
            if rng.random() <= probability:
                date = (start + m).to_timestamp() + pd.Timedelta(days=int(rng.integers(0, 27)))
                rows.append((f"C{cid:05d}", date.strftime("%Y-%m-%d"), plan))
    return pd.DataFrame(rows, columns=["customer_id", "event_date", "revenue"])

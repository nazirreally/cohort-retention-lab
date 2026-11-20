import argparse
from pathlib import Path
import pandas as pd
from .core import retention, revenue_by_cohort, monthly_metrics
from .generate import generate
from .maturity import retention_matrix, retention_summary


def main():
    parser = argparse.ArgumentParser(description="SaaS cohort retention analytics")
    parser.add_argument("--input", type=Path, help="CSV with customer_id,event_date,revenue; default synthetic data")
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-age", type=int, default=12, help="Maximum age for maturity-aware retention")
    parser.add_argument("--as-of", help="Observation cutoff month (YYYY-MM)")
    args = parser.parse_args()
    events = pd.read_csv(args.input) if args.input else generate(seed=args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    events.to_csv(args.out / "events.csv", index=False)
    retention(events).to_csv(args.out / "retention.csv", index=False)
    revenue_by_cohort(events).to_csv(args.out / "cohort_revenue.csv", index=False)
    monthly_metrics(events).to_csv(args.out / "monthly_metrics.csv", index=False)
    mature = retention_matrix(events, max_age=args.max_age, as_of=args.as_of)
    mature.to_csv(args.out / "mature_retention.csv", index=False)
    retention_summary(mature).to_csv(args.out / "weighted_retention.csv", index=False)
    print(f"Created six CSV files in {args.out}")

if __name__ == "__main__":
    main()

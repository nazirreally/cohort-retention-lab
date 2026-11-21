# Cohort Retention Lab 📈

[![CI](https://github.com/nazirreally/cohort-retention-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/nazirreally/cohort-retention-lab/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Data](https://img.shields.io/badge/Data-synthetic-64748b)

**Reproducible SaaS activity analytics with censoring-aware cohort retention, cohort revenue, weighted retention, and an interactive dashboard.** All default data is synthetic; no credentials or proprietary software required.

## Business problem

Raw cohort tables frequently confuse **zero retention** with **not yet observable**. This project explicitly fills zero-activity months only when a cohort has matured to that age, and excludes immature cohorts from age-level comparisons. It also reports monthly recognized revenue and ARPU, rather than mislabeling activity as contractual churn.

## Architecture

```mermaid
flowchart LR
    A[CSV events or seeded generator] --> B[Schema validation + monthly cohorts]
    B --> C[Activity retention + revenue]
    B --> D[Maturity-aware cohort grid]
    D --> H[Observed cohort revenue per original customer]
    D --> E[Size-weighted age summary]
    C --> F[CSV exports]
    E --> F
    C --> G[Streamlit / Plotly dashboard]
```

## Technology stack

| Layer | Implementation |
|---|---|
| Analytics | Python, pandas, NumPy |
| CLI | argparse, installed `cohortlab` command |
| Visualization | Streamlit, Plotly |
| Testing | pytest, synthetic deterministic fixtures |
| Automation | GitHub Actions, Python 3.10 / 3.12 |

## Implemented features

- Seeded synthetic customer activity and custom CSV ingestion.
- Input validation for required columns, nonblank identifiers, nonnull dates, and finite nonnegative revenue. Timezone-aware event timestamps are converted to UTC before monthly grouping.
- Unique-customer cohort activity retention (reactivation permitted).
- Cohort revenue, monthly recognized revenue, and ARPU.
- **Maturity-aware retention grid:** missing mature months count as zero, future/unobserved months are omitted.
- **Cohort-size-weighted retention** by age, using only eligible cohorts.
- Optional `--as-of` observation cutoff and `--max-age` horizon.
- **Observed cohort revenue per original customer** via the Python API, with zero-revenue mature months and cumulative revenue by age. This is a historical revenue proxy, not predicted lifetime value.
- CSV exports and a Streamlit dashboard with maturity-aware heatmap, cohort-size-weighted retention curve, observed cumulative revenue per original customer, observation cutoff, age horizon, and revenue views.

## Dashboard walkthrough

Upload an events CSV or use the seeded sample, select an observation cutoff, and adjust the maximum cohort age (0–24 months). The heatmap distinguishes mature zero-activity months from future cells, while the weighted curve uses only eligible cohorts at each age. Revenue and customer KPIs respect the selected cutoff. The observed revenue panel plots cumulative recognized revenue per original customer by cohort and offers a CSV download. Download the maturity grid, weighted summary, observed cohort revenue, or monthly revenue from the dashboard. These charts measure observed activity, not subscription cancellation.

## Setup and reproducible demo

Requires Python 3.10+. On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dashboard,test]'
python -m pytest -q
cohortlab --seed 42 --max-age 6 --out outputs
streamlit run dashboard.py
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`. For your own events:

```bash
cohortlab --input data/your_events.csv --as-of 2024-06 --max-age 3 --out outputs
```

Input columns: `customer_id,event_date,revenue`; revenue is a nonnegative numeric amount. `--as-of` must not be later than the latest observed event month.

Six generated CSV files: `events.csv`, `retention.csv`, `cohort_revenue.csv`, `monthly_metrics.csv`, `mature_retention.csv`, and `weighted_retention.csv`.

### Interpreting the new outputs

`mature_retention.csv` includes `cohort,age,cohort_size,active_users,retention_rate,as_of`. Example: if a January cohort has no February events but March events exist, February is **zero**, not missing. A cohort first seen in March cannot contribute an age-2 observation to a dataset ending in April.

`weighted_retention.csv` includes `age,eligible_cohorts,eligible_users,active_users,weighted_retention`. Each age uses the eligible customer population as its denominator; the average is **not** an unweighted mean of cohort percentages.

## Repository structure

```text
src/cohortlab/
  core.py         # validated cohort and revenue calculations
  maturity.py     # maturity-aware retention and weighted summaries
  ltv.py          # observed cohort cumulative revenue per original customer
  generate.py     # synthetic events
  cli.py          # six CSV exports
dashboard.py      # Streamlit visualization
tests/            # pytest regression tests
.github/workflows/ci.yml
```

## Observed cohort revenue example

```python
from cohortlab.generate import generate
from cohortlab.ltv import cohort_ltv

result = cohort_ltv(generate(seed=42), max_age=6)
print(result[['cohort', 'age', 'revenue', 'cumulative_revenue',
              'revenue_per_original_customer']].head())
```

The original cohort size remains the denominator at every age. Missing mature months contribute zero revenue, and future months are omitted. This feature is available through the Python API and dashboard (including a CSV download). CLI integration is not yet implemented.

## Verification

The [21 November 2026 GitHub Actions run](https://github.com/nazirreally/cohort-retention-lab/actions/runs/44906306722) passed on **Python 3.10 and 3.12**. Its jobs ran the full pytest suite, a CLI smoke test verifying six nonempty CSV exports, Python compilation, and a Streamlit HTTP health check.

**Remaining verification gap:** Streamlit startup health does not guarantee that the full dashboard (including the observed-revenue chart) renders without exceptions after interaction. No automated browser or `streamlit.testing.v1.AppTest` regression is yet included; no screenshot or performance benchmark is claimed.

## Engineering trade-offs and limitations

- A cohort is the month of **first observed event**, not necessarily signup or acquisition.
- Retention measures observed activity; it is **not** subscription survival or contractual churn.
- The latest observed event month is the default observation boundary. Sparse late data can make some apparently mature months zero; supply a deliberate `--as-of` for controlled reporting.
- The dashboard presents maturity-aware heatmap, weighted retention, and observed cumulative revenue panels; CI checks HTTP startup but does not yet browser-test the rendered UI.
- Input events are not deduplicated by event ID; revenue assumes events represent recognized amounts, without refunds, FX, or tax handling.
- Timezone-aware timestamps are normalized to UTC before month bucketing; this can move events near month boundaries into the previous or next month relative to their source timezone.
- pandas in-memory processing is suitable for portfolio/demo datasets, not massive streaming workloads.

## Roadmap

- Add rendered Streamlit AppTest/browser smoke tests and visual regression checks.
- Add data-quality diagnostics, explicit event IDs, and duplicate detection.
- Expose observed cohort revenue per customer in CLI exports.
- Add DuckDB/Parquet input for larger reproducible workloads.
- Add integration tests for dashboard startup and CSV schema contracts.

**License:** Check repository license metadata before reuse; no license is implied by this README.

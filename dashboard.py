"""Interactive cohort analytics; launch with `streamlit run dashboard.py`."""
import pandas as pd
import plotly.express as px
import streamlit as st

from cohortlab.core import monthly_metrics, revenue_by_cohort, retention, prepare
from cohortlab.generate import generate
from cohortlab.maturity import retention_matrix, retention_summary

st.set_page_config(page_title="Cohort Retention Lab", layout="wide")
st.title("Cohort Retention Lab")
st.caption("Activity-based retention and recognized revenue. Default data is synthetic; these metrics do not estimate contractual churn.")
upload = st.file_uploader("Events CSV: customer_id, event_date, revenue", type="csv")

try:
    events = pd.read_csv(upload) if upload is not None else generate(seed=42)
    prepared = prepare(events)
    months = sorted(prepared["month"].astype(str).unique().tolist())
    cutoff = st.selectbox("Observation cutoff (inclusive)", months, index=len(months) - 1)
    max_age = st.slider("Maximum cohort age (months)", min_value=0, max_value=24, value=12)
    observed_events = events.loc[prepared["month"].astype(str) <= cutoff].copy()
    m = monthly_metrics(observed_events)
    rev = revenue_by_cohort(observed_events)
    mature = retention_matrix(events, max_age=max_age, as_of=cutoff)
    weighted = retention_summary(mature)
except (ValueError, KeyError, TypeError, pd.errors.ParserError) as exc:
    st.error(f"Invalid dataset: {exc}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Unique customers", f"{observed_events.customer_id.nunique():,}")
c2.metric("Recognized revenue", f"${pd.to_numeric(observed_events.revenue).sum():,.0f}")
c3.metric("Observed months", f"{len(m)}")

st.subheader("Maturity-aware retention")
st.caption("Blank cells are not yet observable; 0% cells represent mature months with no active customers. Reactivation is allowed.")
heat = mature.pivot(index="cohort", columns="age", values="retention_rate")
st.plotly_chart(px.imshow(heat, aspect="auto", color_continuous_scale="Blues",
                          zmin=0, zmax=1,
                          labels={"x": "Months since first activity", "y": "First activity cohort", "color": "Retention"}),
                use_container_width=True)
st.subheader("Cohort-size-weighted retention by age")
st.caption("Each point includes only cohorts old enough to have reached that age; denominators change with age.")
st.plotly_chart(px.line(weighted, x="age", y="weighted_retention", markers=True,
                        hover_data=["eligible_cohorts", "eligible_users", "active_users"],
                        labels={"age": "Cohort age (months)", "weighted_retention": "Weighted retention"}),
                use_container_width=True)

st.subheader("Monthly recognized revenue")
st.plotly_chart(px.line(m, x="month", y="revenue", markers=True), use_container_width=True)
st.subheader("Cohort revenue")
st.dataframe(rev, use_container_width=True)

st.download_button("Download maturity-aware retention CSV", mature.to_csv(index=False),
                   "mature_retention.csv", "text/csv")
st.download_button("Download weighted retention CSV", weighted.to_csv(index=False),
                   "weighted_retention.csv", "text/csv")
st.download_button("Download monthly revenue CSV", m.to_csv(index=False),
                   "monthly_metrics.csv", "text/csv")

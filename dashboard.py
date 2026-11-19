import pandas as pd
import plotly.express as px
import streamlit as st
from cohortlab.core import retention, monthly_metrics, revenue_by_cohort
from cohortlab.generate import generate

st.set_page_config(page_title="Cohort Retention Lab", layout="wide")
st.title("Cohort Retention Lab")
st.caption("Monthly activity retention and recognized revenue. Synthetic sample by default; not a subscription churn estimator.")
upload = st.file_uploader("Optional events CSV (customer_id, event_date, revenue)", type="csv")
try:
    events = pd.read_csv(upload) if upload else generate()
    r = retention(events)
    m = monthly_metrics(events)
    rev = revenue_by_cohort(events)
except (ValueError, KeyError, pd.errors.ParserError) as exc:
    st.error(f"Invalid dataset: {exc}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Unique customers", f"{events.customer_id.nunique():,}")
c2.metric("Recognized revenue", f"${events.revenue.sum():,.0f}")
c3.metric("Observed months", f"{len(m)}")
st.subheader("Retention heatmap")
heat = r.pivot(index="cohort", columns="age", values="retention_rate")
st.plotly_chart(px.imshow(heat, aspect="auto", color_continuous_scale="Blues", labels={"x":"Months since first activity", "y":"Acquisition cohort", "color":"Retention"}), use_container_width=True)
st.subheader("Monthly revenue")
st.plotly_chart(px.line(m, x="month", y="revenue", markers=True), use_container_width=True)
st.subheader("Cohort revenue")
st.dataframe(rev, use_container_width=True)
st.download_button("Download retention CSV", r.to_csv(index=False), "retention.csv", "text/csv")

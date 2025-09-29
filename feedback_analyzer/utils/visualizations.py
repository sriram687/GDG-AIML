from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt


def render_metrics_row(df: pd.DataFrame):
	total = len(df)
	avg_sent = round(df.get("sentiment_score", pd.Series([0]*total)).mean(), 3)
	urgent = int((df.get("is_urgent", False) == True).sum())

	col1, col2, col3 = st.columns(3)
	with col1:
		st.markdown('<div class="metric-card priority-med">', unsafe_allow_html=True)
		st.markdown('<div class="metric-title">Total Feedback</div>', unsafe_allow_html=True)
		st.markdown(f'<div class="metric-value">{total}</div>', unsafe_allow_html=True)
		st.markdown('</div>', unsafe_allow_html=True)
	with col2:
		st.markdown('<div class="metric-card priority-low">', unsafe_allow_html=True)
		st.markdown('<div class="metric-title">Avg Sentiment</div>', unsafe_allow_html=True)
		st.markdown(f'<div class="metric-value">{avg_sent}</div>', unsafe_allow_html=True)
		st.markdown('</div>', unsafe_allow_html=True)
	with col3:
		st.markdown('<div class="metric-card priority-urgent">', unsafe_allow_html=True)
		st.markdown('<div class="metric-title">Urgent Items</div>', unsafe_allow_html=True)
		st.markdown(f'<div class="metric-value">{urgent}</div>', unsafe_allow_html=True)
		st.markdown('</div>', unsafe_allow_html=True)


def render_sentiment_trend(df: pd.DataFrame):
	if "date" not in df.columns:
		st.info("No date column available for trend plot.")
		return
	grp = (
		df.dropna(subset=["date"]).assign(date=lambda d: d["date"].dt.to_period("W").dt.start_time)
		.groupby("date")["sentiment_score"].mean().reset_index()
	)
	fig = px.line(grp, x="date", y="sentiment_score", title="Sentiment Trend (Weekly)")
	fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
	st.plotly_chart(fig, use_container_width=True)


def render_priority_donut(df: pd.DataFrame):
	bins = [
		("Urgent", (df.get("priority", 0) >= 0.85)),
		("High", (df.get("priority", 0).between(0.65, 0.85, inclusive="left"))),
		("Medium", (df.get("priority", 0).between(0.4, 0.65, inclusive="left"))),
		("Low", (df.get("priority", 0) < 0.4)),
	]
	data = {name: int(mask.sum()) for name, mask in bins}
	donut_df = pd.DataFrame({"priority": list(data.keys()), "count": list(data.values())})
	fig = px.pie(donut_df, values="count", names="priority", hole=0.6, title="Priority Distribution")
	fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
	st.plotly_chart(fig, use_container_width=True)


def render_weekly_volume(counts: pd.DataFrame):
	if counts.empty:
		st.info("No weekly data yet.")
		return
	fig = px.bar(counts, x="date", y="count", title="Weekly Volume")
	fig.update_layout(height=260, margin=dict(l=10, r=10, t=40, b=10))
	st.plotly_chart(fig, use_container_width=True)


def render_clusters(scatter_df: pd.DataFrame):
	if scatter_df.empty:
		st.info("Not enough data to form clusters.")
		return
	chart = (
		alt.Chart(scatter_df)
		.mark_circle(size=80)
		.encode(
			x="pca_x",
			y="pca_y",
			color=alt.Color("cluster:N", legend=None),
			tooltip=["cluster"]
		)
		.properties(height=340)
	)
	st.altair_chart(chart, use_container_width=True)



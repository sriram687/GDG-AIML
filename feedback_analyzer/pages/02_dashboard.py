import streamlit as st
import pandas as pd
from utils.visualizations import (
	render_metrics_row,
	render_sentiment_trend,
	render_priority_donut,
	render_weekly_volume,
	render_clusters,
)
from core.analyzer import Analyzer
from core.prioritizer import Prioritizer
from core.insights import Insights


def page():
	st.title("📊 Dashboard")

	df: pd.DataFrame | None = st.session_state.get("processed_df")
	if df is None or df.empty:
		st.info("No data found. Please upload data first.")
		st.page_link("pages/01_upload.py", label="Upload Data", icon="📤")
		return

	with st.spinner("Running analysis (sentiment, topics)..."):
		analyzer = Analyzer()
		results = analyzer.analyze(df)
		st.session_state["analysis_results"] = results

	prioritizer = Prioritizer()
	with st.spinner("Scoring priorities..."):
		df_scored = prioritizer.score(results)
		st.session_state["processed_df"] = df_scored

	render_metrics_row(df_scored)
	col1, col2 = st.columns([2,1])
	with col1:
		render_sentiment_trend(df_scored)
	with col2:
		render_priority_donut(df_scored)

	insights = Insights()
	with st.expander("Key Insights", expanded=True):
		bullets = insights.generate_key_bullets(df_scored)
		for b in bullets:
			st.markdown(f"- {b}")

	counts, sents = insights.weekly_trends(df_scored)
	col3, col4 = st.columns([1,1])
	with col3:
		render_weekly_volume(counts)
	with col4:
		st.write("Weekly Sentiment")
		st.dataframe(sents, use_container_width=True, height=260)

	with st.expander("Clusters", expanded=False):
		scatter_df = insights.build_text_clusters(df_scored)
		render_clusters(scatter_df)

	st.page_link("pages/03_explorer.py", label="Open Explorer", icon="🔎")


if __name__ == "__main__":
	page()



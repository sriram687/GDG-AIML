import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder


def page():
	st.title("🔎 Explorer")
	df: pd.DataFrame | None = st.session_state.get("processed_df")
	if df is None or df.empty:
		st.info("No data found. Please upload data first.")
		st.page_link("pages/01_upload.py", label="Upload Data", icon="📤")
		return

	with st.expander("Filters", expanded=True):
		col1, col2, col3 = st.columns(3)
		with col1:
			topic = st.selectbox("Topic", options=["All"] + sorted(df.get("topic", pd.Series(["other"])) .astype(str).unique().tolist()))
		with col2:
			priority_min = st.slider("Min Priority", 0.0, 1.0, 0.0, 0.05)
		with col3:
			urgent_only = st.checkbox("Urgent only")

	mask = (df.get("priority", 0) >= priority_min)
	if topic != "All":
		mask &= (df.get("topic", "other").astype(str) == topic)
	if urgent_only:
		mask &= (df.get("is_urgent", False) == True)

	df_view = df.loc[mask].copy()

	gob = GridOptionsBuilder.from_dataframe(df_view)
	gob.configure_default_column(resizable=True, filter=True, sortable=True)
	gob.configure_selection("single")
	AgGrid(df_view, gridOptions=gob.build(), height=500, theme="streamlit")


if __name__ == "__main__":
	page()



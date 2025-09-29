import io
import streamlit as st
import pandas as pd
from utils.exports import export_pdf_summary, export_csv


def page():
	st.title("📄 Reports & Exports")
	df: pd.DataFrame | None = st.session_state.get("processed_df")
	if df is None or df.empty:
		st.info("No data found. Please upload data first.")
		st.page_link("pages/01_upload.py", label="Upload Data", icon="📤")
		return

	col1, col2 = st.columns(2)
	with col1:
		csv_bytes = export_csv(df)
		st.download_button("Download CSV", data=csv_bytes, file_name="feedback_export.csv", mime="text/csv")
	with col2:
		pdf_bytes = export_pdf_summary(df)
		st.download_button("Download PDF Summary", data=pdf_bytes, file_name="feedback_report.pdf", mime="application/pdf")


if __name__ == "__main__":
	page()



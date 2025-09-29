import io
from pathlib import Path
import pandas as pd
import streamlit as st

from core.data_processor import DataProcessor


def _load_sample() -> pd.DataFrame:
	sample_path = Path(__file__).resolve().parents[1] / "assets" / "sample_data" / "sample_feedback.csv"
	return pd.read_csv(sample_path)


def page():
	st.title("📤 Upload Feedback Data")
	st.caption("CSV, Excel, JSON supported. We'll handle cleaning and normalization.")

	with st.expander("Upload Options", expanded=True):
		file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls", "json"])
		use_sample = st.checkbox("Use sample dataset", value=not bool(file))

		if use_sample and not file:
			df = _load_sample()
		else:
			if file is None:
				st.info("Upload a file or use the sample dataset.")
				return
			# Parse by extension
			ext = Path(file.name).suffix.lower()
			if ext == ".csv":
				df = pd.read_csv(file)
			elif ext in (".xlsx", ".xls"):
				df = pd.read_excel(file)
			elif ext == ".json":
				df = pd.read_json(io.BytesIO(file.read()))
			else:
				st.error("Unsupported file type")
				return

	processor = DataProcessor()
	with st.spinner("Processing data..."):
		processed = processor.process_dataframe(df)

	st.session_state["uploaded_df"] = df
	st.session_state["processed_df"] = processed

	st.success(f"Loaded {len(processed)} feedback items.")
	st.dataframe(processed.head(20), use_container_width=True)

	st.page_link("pages/02_dashboard.py", label="Go to Dashboard", icon="➡️")


if __name__ == "__main__":
	page()



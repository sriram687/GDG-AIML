import streamlit as st
from pathlib import Path

from config import AppConfig


def inject_styles():
	styles_path = Path(__file__).parent / "assets" / "styles.css"
	if styles_path.exists():
		st.markdown(f"<style>{styles_path.read_text()}</style>", unsafe_allow_html=True)


def init_session_state():
	defaults = {
		"uploaded_df": None,
		"processed_df": None,
		"analysis_results": None,
		"entities": None,
		"embeddings": None,
		"topics": None,
		"db_uri": AppConfig().DATABASE_URL,
	}
	for k, v in defaults.items():
		if k not in st.session_state:
			st.session_state[k] = v


def sidebar_branding():
	st.sidebar.image("https://avatars.githubusercontent.com/u/1342004?s=200&v=4", use_container_width=True)
	st.sidebar.markdown("**Customer Feedback Analyzer**")
	st.sidebar.caption("AI-driven insights & responses")


def main():
	st.set_page_config(
		title="Feedback Analyzer",
		page_icon="💬",
		layout="wide",
		initial_sidebar_state="expanded",
	)
	inject_styles()
	init_session_state()
	sidebar_branding()

	st.markdown(
		"""
		<div class="header">
			<h1>AI-Driven Customer Feedback Analyzer</h1>
			<p class="subtitle">Transform feedback into insights and high-quality responses</p>
		</div>
		""",
		unsafe_allow_html=True,
	)

	st.markdown(
		"""
		Use the sidebar to navigate pages:
		- Upload data
		- Dashboard insights
		- Explorer
		- Responses
		- Reports
		"""
	)

	cta1, cta2, cta3 = st.columns(3)
	with cta1:
		st.page_link("pages/01_upload.py", label="Upload Data", icon="📤")
	with cta2:
		st.page_link("pages/02_dashboard.py", label="Dashboard", icon="📊")
	with cta3:
		st.page_link("pages/04_responses.py", label="Responses", icon="✍️")

	st.info("Tip: Try the sample dataset from the Upload page to explore features quickly.")


if __name__ == "__main__":
	main()



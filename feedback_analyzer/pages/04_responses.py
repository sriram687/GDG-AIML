import streamlit as st
import pandas as pd
from core.response_gen import ResponseGenerator, ResponseOptions
from config import AppConfig


def page():
	st.title("✍️ Response Generator")
	df: pd.DataFrame | None = st.session_state.get("processed_df")
	if df is None or df.empty:
		st.info("No data found. Please upload data first.")
		st.page_link("pages/01_upload.py", label="Upload Data", icon="📤")
		return

	row_idx = st.number_input("Select row index", min_value=0, max_value=len(df)-1, value=0, step=1)
	row = df.iloc[int(row_idx)]

	col1, col2 = st.columns(2)
	with col1:
		st.markdown("**Feedback**")
		st.write(row.get("text", ""))
	with col2:
		st.markdown("**Context**")
		st.json({
			"date": str(row.get("date", "")),
			"topic": row.get("topic", ""),
			"sentiment_score": float(row.get("sentiment_score", 0)),
			"priority": float(row.get("priority", 0)),
		})

	st.divider()
	st.subheader("Options")
	col3, col4, col5 = st.columns([1,1,1])
	with col3:
		tone = st.selectbox("Tone", options=["professional", "warm", "concise", "apologetic"], index=0)
	with col4:
		length = st.selectbox("Length", options=["short", "medium", "long"], index=1)
	with col5:
		offer_credit = st.checkbox("Offer credit/goodwill", value=False)

    gen = ResponseGenerator()
    opts = ResponseOptions(tone=tone, length=length, offer_credit=offer_credit)
    cfg = AppConfig()
    api_available = bool(cfg.GOOGLE_API_KEY or cfg.OPENAI_API_KEY or cfg.ANTHROPIC_API_KEY)
    use_api = st.toggle("Use API provider (if available)", value=api_available)
    provider = st.selectbox("Provider", options=["auto", "gemini", "openai", "anthropic"], index=0, help="auto tries Gemini→OpenAI→Anthropic")

    if st.button("Generate Response", type="primary"):
        reply, used = gen.generate(
            feedback_text=str(row.get("text", "")),
            sentiment=float(row.get("sentiment_score", 0)) if "sentiment_score" in row else None,
            topic=str(row.get("topic", "")) if "topic" in row else None,
            opts=opts,
            use_api=use_api,
            provider=None if provider == "auto" else provider,
        )
        st.text_area("AI Response", value=reply, height=200)
        st.caption(f"Provider: {used}")


if __name__ == "__main__":
	page()



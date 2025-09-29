from __future__ import annotations

import pandas as pd
from utils.helpers import URGENCY_KEYWORDS, CHURN_KEYWORDS, contains_keywords


class Prioritizer:
	def score(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		out["is_urgent"] = out["text"].astype(str).apply(lambda t: contains_keywords(t, URGENCY_KEYWORDS))
		out["is_churn_risk"] = out["text"].astype(str).apply(lambda t: contains_keywords(t, CHURN_KEYWORDS))

		# Priority = sigmoid-like from components
		sent = out.get("sentiment_score", 0).fillna(0)
		urg = out["is_urgent"].astype(int)
		churn = out["is_churn_risk"].astype(int)
		text_len = out.get("word_count", 10).fillna(10)

		priority = (
			(1 - (sent + 1) / 2) * 0.45 +  # negative sentiment increases priority
			urg * 0.35 +
			churn * 0.15 +
			(text_len.clip(0, 80) / 80.0) * 0.05
		)
		out["priority"] = priority.clip(0, 1)
		return out



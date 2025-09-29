from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, Any


class Analyzer:
	"""Lightweight placeholder analyzer with fast heuristics.

	Replaces with transformers/BERTopic when models are available to keep
	initial UX snappy (<5s for ~1000 rows)."""

	positive_words = {"great", "love", "fast", "awesome", "improve", "thanks"}
	negative_words = {"slow", "bug", "fail", "crash", "cancel", "duplicate", "error"}

	def _heuristic_sentiment(self, text: str) -> float:
		text_l = text.lower()
		pos = sum(w in text_l for w in self.positive_words)
		neg = sum(w in text_l for w in self.negative_words)
		if pos == 0 and neg == 0:
			return 0.0
		return (pos - neg) / max(pos + neg, 1)

	def _simple_topics(self, df: pd.DataFrame) -> pd.Series:
		keywords = {
			"login": ["login", "sign in", "auth"],
			"billing": ["billing", "invoice", "charge", "refund"],
			"performance": ["slow", "fast", "performance"],
			"checkout": ["checkout", "cart", "coupon"],
			"support": ["support", "reply", "help"],
			"ui": ["ui", "design", "dark mode"],
		}
		def map_topic(text: str) -> str:
			t = text.lower()
			for name, kws in keywords.items():
				if any(k in t for k in kws):
					return name
			return "other"
		return df["text"].astype(str).apply(map_topic)

	def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		out["sentiment_score"] = out["text"].astype(str).apply(self._heuristic_sentiment)
		out["topic"] = self._simple_topics(out)
		return out



from __future__ import annotations

from typing import Iterable
import re
import pandas as pd
from sqlalchemy import create_engine
from config import AppConfig


def get_db_engine():
	return create_engine(AppConfig().DATABASE_URL, future=True)


def normalize_feedback_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	columns_map = {
		"feedback": "text",
		"comment": "text",
		"message": "text",
	}
	for c, tgt in columns_map.items():
		if c in df.columns and "text" not in df.columns:
			df = df.rename(columns={c: tgt})
	
	if "text" not in df.columns:
		raise ValueError("Input must contain a 'text' column or equivalent")

	if "date" in df.columns:
		df["date"] = pd.to_datetime(df["date"], errors="coerce")

	# Basic cleaning
	df["text"] = (
		df["text"].astype(str).str.replace("\s+", " ", regex=True).str.strip()
	)

	# Ensure required cols
	for col in ["id", "source", "customer_id"]:
		if col not in df.columns:
			df[col] = None

	return df


URGENCY_KEYWORDS = [
	"urgent", "asap", "immediately", "now", "critical", "crash", "down"
]
CHURN_KEYWORDS = [
	"cancel", "cancelling", "churn", "switch", "refund", "chargeback"
]


def contains_keywords(text: str, keywords: Iterable[str]) -> bool:
	pattern = r"\b(" + "|".join(map(re.escape, keywords)) + r")\b"
	return bool(re.search(pattern, text.lower()))



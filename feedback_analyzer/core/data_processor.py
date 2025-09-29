from __future__ import annotations

import pandas as pd
from utils.helpers import normalize_feedback_dataframe


class DataProcessor:
	def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
		clean = normalize_feedback_dataframe(df.copy())
		# Basic features
		clean["text_len"] = clean["text"].str.len()
		clean["word_count"] = clean["text"].str.split().apply(len)
		return clean



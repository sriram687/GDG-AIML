from __future__ import annotations

import math
from typing import Dict, Any, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class Insights:
	def generate_key_bullets(self, df: pd.DataFrame) -> list[str]:
		bullets: list[str] = []
		if "topic" in df.columns:
			by_topic = df.groupby("topic").size().sort_values(ascending=False).head(3)
			topics = ", ".join(f"{k} ({v})" for k, v in by_topic.items())
			bullets.append(f"Top topics by volume: {topics}.")

		if "sentiment_score" in df.columns:
			avg = df["sentiment_score"].mean()
			bullets.append(f"Average sentiment score is {avg:.2f} (higher is better).")

		if "priority" in df.columns:
			pct_urgent = (df["priority"] >= 0.85).mean() * 100
			bullets.append(f"{pct_urgent:.1f}% of feedback is urgent.")

		return bullets

	def compute_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
		kpis: Dict[str, Any] = {
			"total": int(len(df)),
			"avg_sentiment": float(df.get("sentiment_score", 0).mean() if "sentiment_score" in df.columns else 0.0),
			"urgent": int((df.get("priority", 0) >= 0.85).sum() if "priority" in df.columns else 0),
			"churn_risk": int((df.get("is_churn_risk", False) == True).sum() if "is_churn_risk" in df.columns else 0),
		}
		if "topic" in df.columns and not df.empty:
			kpis["top_topic"] = df.groupby("topic").size().idxmax()
		else:
			kpis["top_topic"] = "n/a"
		return kpis

	def weekly_trends(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
		if "date" not in df.columns:
			return pd.DataFrame(columns=["date", "count"]), pd.DataFrame(columns=["date", "sentiment_score"])
		df_w = df.dropna(subset=["date"]).copy()
		df_w["week"] = df_w["date"].dt.to_period("W").dt.start_time
		by_count = df_w.groupby("week").size().reset_index(name="count").rename(columns={"week": "date"})
		by_sent = df_w.groupby("week")["sentiment_score"].mean().reset_index().rename(columns={"week": "date"})
		return by_count, by_sent

	def weekly_summary_bullets(self, df: pd.DataFrame) -> list[str]:
		counts, sents = self.weekly_trends(df)
		bullets: list[str] = []
		if not counts.empty:
			last = counts.sort_values("date").tail(2)
			if len(last) == 2:
				prev, curr = last.iloc[0], last.iloc[1]
				chg = (curr["count"] - prev["count"]) / max(prev["count"], 1) * 100
				bullets.append(f"Feedback volume changed {chg:+.1f}% week-over-week.")
		if not sents.empty:
			last = sents.sort_values("date").tail(2)
			if len(last) == 2:
				prev, curr = last.iloc[0], last.iloc[1]
				chg = curr["sentiment_score"] - prev["sentiment_score"]
				bullets.append(f"Average sentiment moved {chg:+.2f} vs last week.")
		return bullets

	def build_text_clusters(self, df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
		texts = df["text"].astype(str).tolist()
		if len(texts) < 5:
			return pd.DataFrame({"pca_x": [], "pca_y": [], "cluster": []})
		vec = TfidfVectorizer(max_features=2000, ngram_range=(1,2))
		X = vec.fit_transform(texts)
		k = min(n_clusters, max(2, int(math.sqrt(len(texts)//2))))
		model = KMeans(n_clusters=k, n_init=10, random_state=42)
		labels = model.fit_predict(X)
		pca = PCA(n_components=2, random_state=42)
		coords = pca.fit_transform(X.toarray())
		out = pd.DataFrame({
			"pca_x": coords[:,0],
			"pca_y": coords[:,1],
			"cluster": labels,
		})
		return out



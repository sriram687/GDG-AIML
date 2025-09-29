from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import re
import pandas as pd


@dataclass
class EntityConfig:
	custom_products: tuple[str, ...] = ()
	feature_patterns: tuple[str, ...] = (
		"login|authentication|auth",
		"billing|invoice|subscription|payment",
		"checkout|cart|coupon",
		"mobile|android|ios",
		"performance|latency|speed",
		"ui|design|dark mode",
	)


class EntityExtractor:
	def __init__(self, config: EntityConfig | None = None) -> None:
		self.config = config or EntityConfig()
		self._nlp = None

	def _ensure_spacy(self):
		if self._nlp is not None:
			return
		try:
			import spacy  # type: ignore
			self._nlp = spacy.load("en_core_web_sm")
		except Exception:
			self._nlp = None

	def extract(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		self._ensure_spacy()

		products: list[str] = []
		features: list[str] = []

		if self._nlp is not None:
			for text in out["text"].astype(str).tolist():
				doc = self._nlp(text)
				prods = [ent.text for ent in doc.ents if ent.label_ in {"PRODUCT", "ORG"}]
				products.append(", ".join(sorted(set(prods + list(self.config.custom_products)))))
				feat_hits = []
				for pat in self.config.feature_patterns:
					if re.search(pat, text, flags=re.I):
						feat_hits.append(pat.split("|")[0])
				features.append(", ".join(sorted(set(feat_hits))))
		else:
			for text in out["text"].astype(str).tolist():
				feat_hits = []
				for pat in self.config.feature_patterns:
					if re.search(pat, text, flags=re.I):
						feat_hits.append(pat.split("|")[0])
				features.append(", ".join(sorted(set(feat_hits))))
				products.append("")

		out["entities_products"] = products
		out["entities_features"] = features
		return out



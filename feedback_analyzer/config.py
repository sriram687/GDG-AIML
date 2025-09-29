import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
	OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
	ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
	GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
	DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///feedback.db")
	MODEL_SENTIMENT: str = os.getenv("MODEL_SENTIMENT", "cardiffnlp/twitter-roberta-base-sentiment-latest")
	MODEL_EMBEDDINGS: str = os.getenv("MODEL_EMBEDDINGS", "sentence-transformers/all-MiniLM-L6-v2")
	THEME_PRIMARY: str = os.getenv("THEME_PRIMARY", "#2B6CB0")
	THEME_ACCENT: str = os.getenv("THEME_ACCENT", "#00B5D8")
	THEME_POSITIVE: str = os.getenv("THEME_POSITIVE", "#38A169")
	THEME_NEGATIVE: str = os.getenv("THEME_NEGATIVE", "#E53E3E")
	THEME_WARNING: str = os.getenv("THEME_WARNING", "#DD6B20")
	ORG_NAME: str = os.getenv("ORG_NAME", "Acme Corp")



from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
from config import AppConfig


Tone = Literal["professional", "warm", "concise", "apologetic"]


@dataclass
class ResponseOptions:
	tone: Tone = "professional"
	length: Literal["short", "medium", "long"] = "medium"
	offer_credit: bool = False


class ResponseGenerator:
    def __init__(self) -> None:
        self.cfg = AppConfig()

	def build_prompt(self, feedback_text: str, sentiment: float | None, topic: str | None, opts: ResponseOptions) -> str:
		len_hint = {
			"short": "80-120 characters",
			"medium": "3-5 sentences",
			"long": "6-10 sentences",
		}[opts.length]

		return (
			"You are a senior customer support agent. Write a reply that:\n"
			"- acknowledges the customer's feedback succinctly\n"
			"- addresses the core issue with clear next steps\n"
			"- matches the requested tone\n"
			"- avoids making promises that cannot be kept\n\n"
			f"Tone: {opts.tone}. Target length: {len_hint}.\n"
			f"Topic: {topic or 'general'}. Sentiment score: {sentiment if sentiment is not None else 'n/a'}.\n\n"
			f"Customer feedback: \"{feedback_text}\"\n"
			+ ("If appropriate, offer a small goodwill credit.\n" if opts.offer_credit else "")
		)

	def generate_local(self, feedback_text: str, sentiment: float | None, topic: str | None, opts: ResponseOptions) -> str:
		# Placeholder deterministic template for offline use
		ack = "Thank you for sharing this."
		if sentiment is not None and sentiment < -0.2:
			ack = "We're sorry for the trouble you've experienced."
		elif sentiment is not None and sentiment > 0.2:
			ack = "We appreciate your positive feedback!"

		body = "We've noted your comments and are working to address this promptly."
		if topic == "billing":
			body = "Our billing team is reviewing this and will correct any charges."
		elif topic == "login":
			body = "Our engineers are investigating the login performance on mobile."
		elif topic == "checkout":
			body = "We're fixing the checkout issue and will release a patch shortly."

		closing = "Please let us know if there's anything else we can assist with."
		if opts.offer_credit and topic in {"billing", "checkout"}:
			closing = closing + " We've added a small goodwill credit to your account."

		return f"{ack} {body} {closing}"

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        if not self.cfg.OPENAI_API_KEY:
            return None
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI(api_key=self.cfg.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=400,
            )
            return resp.choices[0].message.content if resp and resp.choices else None
        except Exception:
            return None

    def _generate_with_anthropic(self, prompt: str) -> Optional[str]:
        if not self.cfg.ANTHROPIC_API_KEY:
            return None
        try:
            import anthropic  # type: ignore
            client = anthropic.Anthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=400,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}],
            )
            if getattr(resp, "content", None):
                return resp.content[0].text  # type: ignore[index]
            return None
        except Exception:
            return None

    def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        if not self.cfg.GOOGLE_API_KEY:
            return None
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=self.cfg.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            return getattr(resp, "text", None)
        except Exception:
            return None

    def generate(self, feedback_text: str, sentiment: float | None, topic: str | None, opts: ResponseOptions, use_api: bool = True, provider: Optional[str] = None) -> tuple[str, str]:
        prompt = self.build_prompt(feedback_text, sentiment, topic, opts)
        if use_api:
            providers = [provider] if provider else ["gemini", "openai", "anthropic"]
            for prov in providers:
                if prov == "gemini":
                    txt = self._generate_with_gemini(prompt)
                    if txt:
                        return txt, "gemini"
                if prov == "openai":
                    txt = self._generate_with_openai(prompt)
                    if txt:
                        return txt, "openai"
                if prov == "anthropic":
                    txt = self._generate_with_anthropic(prompt)
                    if txt:
                        return txt, "anthropic"
        return self.generate_local(feedback_text, sentiment, topic, opts), "local"



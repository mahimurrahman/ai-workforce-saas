from __future__ import annotations

from typing import Any

try:
    import groq
except ImportError:  # pragma: no cover
    groq = None

from app.core.config import settings


class BaseAgent:
    agent_type = "assistant"
    system_prompt = ""
    model = "llama-3.3-70b-versatile"
    max_tokens = 300
    temperature = 0.2

    def __init__(self):
        self.client = None
        if groq is not None and self._has_live_model():
            self.client = groq.Groq(api_key=settings.GROQ_API_KEY)

    def _has_live_model(self) -> bool:
        api_key = settings.GROQ_API_KEY.strip()
        return bool(api_key and not api_key.startswith("your_") and len(api_key) >= 20)

    def _build_messages(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        for item in (history or [])[-12:]:
            role = item.get("role")
            content = item.get("content", "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})
        return messages

    def _last_user_context(self, history: list[dict[str, Any]] | None = None) -> str:
        for item in reversed(history or []):
            if item.get("role") == "user" and item.get("content"):
                return item["content"]
        return ""

    def _dry_run_response(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str:
        raise NotImplementedError

    async def process_message(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str:
        if self.client is None:
            return self._dry_run_response(message, history)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(message, history),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content or ""
            return content.strip() or self._dry_run_response(message, history)
        except Exception:
            return self._dry_run_response(message, history)

from __future__ import annotations

from typing import Any

from app.agents.ops.agent import OpsAgent
from app.agents.sales.agent import SalesAgent
from app.agents.support.agent import SupportAgent
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.services.redis_service import RedisService


class AgentOrchestrator:
    SUPPORT_KEYWORDS = {
        "support",
        "help",
        "refund",
        "issue",
        "problem",
        "broken",
        "error",
        "login",
        "account",
        "ticket",
        "trouble",
        "cancel",
        "return",
    }
    SALES_KEYWORDS = {
        "price",
        "pricing",
        "buy",
        "purchase",
        "demo",
        "trial",
        "quote",
        "cost",
        "plan",
        "subscription",
        "upgrade",
        "invoice",
    }
    OPS_KEYWORDS = {
        "workflow",
        "admin",
        "operations",
        "ops",
        "data",
        "process",
        "update",
        "automation",
        "integration",
        "dashboard",
        "report",
        "reporting",
        "crm",
    }

    def __init__(self):
        self.agents = {
            "support": SupportAgent(),
            "sales": SalesAgent(),
            "ops": OpsAgent(),
        }
        self.redis_service = RedisService()

    def _normalize_history(
        self,
        history: list[ChatMessage | dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in history or []:
            if isinstance(item, ChatMessage):
                data = item.model_dump()
            else:
                data = dict(item)
            role = data.get("role")
            content = str(data.get("content", "")).strip()
            if role in {"user", "assistant"} and content:
                normalized.append(
                    {
                        "role": role,
                        "content": content,
                        "agent_type": data.get("agent_type"),
                    }
                )
        return normalized[-50:]

    def _score_message(self, text: str) -> dict[str, int]:
        return {
            "support": sum(1 for keyword in self.SUPPORT_KEYWORDS if keyword in text),
            "sales": sum(1 for keyword in self.SALES_KEYWORDS if keyword in text),
            "ops": sum(1 for keyword in self.OPS_KEYWORDS if keyword in text),
        }

    def _last_assistant_agent(self, history: list[dict[str, Any]]) -> str | None:
        for item in reversed(history):
            if item.get("role") == "assistant" and item.get("agent_type") in self.agents:
                return item["agent_type"]
        return None

    def select_agent(
        self,
        message: str,
        history: list[ChatMessage | dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        normalized_history = self._normalize_history(history)
        scores = self._score_message(message.lower())
        highest_score = max(scores.values())

        if highest_score > 0:
            tied_agents = [
                agent_type for agent_type, score in scores.items() if score == highest_score
            ]
            last_agent = self._last_assistant_agent(normalized_history)
            agent_type = last_agent if last_agent in tied_agents else tied_agents[0]
            confidence = min(0.98, 0.7 + highest_score * 0.12)
        else:
            agent_type = self._last_assistant_agent(normalized_history) or "support"
            confidence = 0.58 if agent_type != "support" else 0.45

        return {
            "agent": self.agents[agent_type],
            "agent_type": agent_type,
            "confidence": round(confidence, 2),
        }

    async def route_message(self, request: ChatRequest) -> ChatResponse:
        source_history = (
            self._normalize_history(request.history)
            if request.history is not None
            else self.redis_service.get_conversation_history(request.user_id)
        )

        if (
            source_history
            and source_history[-1].get("role") == "user"
            and source_history[-1].get("content", "").strip() == request.message.strip()
        ):
            prior_history = source_history[:-1]
        else:
            prior_history = source_history

        routing = self.select_agent(request.message, prior_history)
        response_text = await routing["agent"].process_message(request.message, prior_history)

        user_message = {"role": "user", "content": request.message}
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "agent_type": routing["agent_type"],
        }

        full_history = [*prior_history, user_message, assistant_message]
        self.redis_service.save_conversation_history(request.user_id, full_history)

        return ChatResponse(
            response=response_text,
            agent_type=routing["agent_type"],
            confidence=routing["confidence"],
        )

from typing import Any

from app.agents.base import BaseAgent
from app.agents.support.prompts import SUPPORT_SYSTEM_PROMPT

class SupportAgent(BaseAgent):
    agent_type = "support"
    system_prompt = SUPPORT_SYSTEM_PROMPT
    max_tokens = 300
    temperature = 0.2

    def _dry_run_response(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str:
        previous_issue = self._last_user_context(history)
        if "refund" in message.lower():
            return (
                "Support here. I can help with the refund request. "
                "Please share the order or subscription email, confirm whether the charge is duplicate or unwanted, "
                "and I will guide the next step."
            )
        if previous_issue and previous_issue.lower() != message.lower():
            return (
                f"Support here. I still have the earlier issue in context: \"{previous_issue}\". "
                f"For this follow-up, my next step would be to verify the account details and resolve: {message}."
            )
        return (
            "Support here. I can help with account issues, refunds, login problems, and troubleshooting. "
            f"Based on your message, I would start by confirming the affected account and the exact problem: {message}."
        )

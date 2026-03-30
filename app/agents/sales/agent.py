from typing import Any

from app.agents.base import BaseAgent
from app.agents.sales.prompts import SALES_SYSTEM_PROMPT

class SalesAgent(BaseAgent):
    agent_type = "sales"
    system_prompt = SALES_SYSTEM_PROMPT
    max_tokens = 250
    temperature = 0.3

    def _dry_run_response(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str:
        previous_interest = self._last_user_context(history)
        if "pricing" in message.lower() or "price" in message.lower():
            return (
                "Sales here. We can walk through pricing, plan fit, and rollout scope. "
                "If you tell me team size, monthly volume, and whether you need support, sales, or ops coverage first, "
                "I can point you to the right plan."
            )
        if "demo" in message.lower():
            return (
                "Sales here. A useful demo should be tailored to your workflow. "
                "Send your team size and top use case, and I will structure the demo around the highest-value path."
            )
        if previous_interest and previous_interest.lower() != message.lower():
            return (
                f"Sales here. I still have your earlier buying context in mind: \"{previous_interest}\". "
                f"For this step, I would position the offer around: {message}."
            )
        return (
            "Sales here. I can help with pricing, demos, trials, and buying questions. "
            f"From your message, the next step is to qualify scope and recommend a plan: {message}."
        )

from typing import Any

from app.agents.base import BaseAgent
from app.agents.ops.prompts import OPS_SYSTEM_PROMPT

class OpsAgent(BaseAgent):
    agent_type = "ops"
    system_prompt = OPS_SYSTEM_PROMPT
    max_tokens = 250
    temperature = 0.25

    def _dry_run_response(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> str:
        previous_context = self._last_user_context(history)
        if "workflow" in message.lower() or "process" in message.lower():
            return (
                "Ops here. I can help update the workflow. "
                "Tell me the current steps, the bottleneck, and the desired handoff, and I will turn that into an operational sequence."
            )
        if "admin" in message.lower() or "data" in message.lower():
            return (
                "Ops here. I can handle admin and data operations. "
                "Share the record source, the fields that need to change, and the target system so I can map the update flow."
            )
        if previous_context and previous_context.lower() != message.lower():
            return (
                f"Ops here. I still have the prior operating context in mind: \"{previous_context}\". "
                f"My next action for this follow-up would be to update the process around: {message}."
            )
        return (
            "Ops here. I can help with workflows, admin requests, integrations, and data operations. "
            f"From your message, I would start by mapping the current process and the requested change: {message}."
        )

from app.agents.support.agent import SupportAgent
from app.agents.sales.agent import SalesAgent
from app.agents.ops.agent import OpsAgent
from app.schemas.chat import ChatRequest, ChatResponse

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "support": SupportAgent(),
            "sales": SalesAgent(),
            "ops": OpsAgent(),
        }

    def _choose_agent(self, message: str):
        text = message.lower()

        support_keywords = ["support", "help", "refund", "login", "account", "ticket", "angry", "issue"]
        sales_keywords = ["price", "pricing", "buy", "purchase", "demo", "lead", "interest", "trial", "quote"]
        ops_keywords = ["workflow", "admin", "operations", "data", "process", "crm", "task", "update"]

        if any(word in text for word in support_keywords):
            return "support", 0.92
        if any(word in text for word in sales_keywords):
            return "sales", 0.89
        if any(word in text for word in ops_keywords):
            return "ops", 0.87

        return "support", 0.70

    async def route_message(self, request: ChatRequest) -> ChatResponse:
        agent_type, confidence = self._choose_agent(request.message)
        agent = self.agents.get(agent_type, self.agents["support"])

        response_text = await agent.process_message(request.message)

        return ChatResponse(
            response=response_text,
            agent_type=agent_type,
            confidence=confidence,
        )
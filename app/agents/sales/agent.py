import groq
from app.core.config import settings
from app.agents.sales.prompts import SALES_SYSTEM_PROMPT

class SalesAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)

    async def process_message(self, message: str) -> str:
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("your_") or len(settings.GROQ_API_KEY) < 50:
            return "[SalesAgent] Dry-run mode: mock response for testing. Set GROQ_API_KEY in .env to enable real responses."

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SALES_SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I cannot process your request right now. Error: {str(e)}"
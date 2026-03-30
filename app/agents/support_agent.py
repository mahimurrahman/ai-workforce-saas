from app.agents.support.agent import SupportAgent as NewSupportAgent

# Compatibility shim to avoid breaking imports.
class SupportAgent(NewSupportAgent):
    pass
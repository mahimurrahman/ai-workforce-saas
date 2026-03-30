from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router
from app.core.config import settings
from app.agents.orchestrator import AgentOrchestrator

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Workforce SaaS - Intelligent agent orchestration"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(api_router, prefix="/api")

orchestrator = AgentOrchestrator()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@app.get("/dashboard")
async def dashboard(request: Request):
    # In-memory samples; extend for DB-backed logs
    recent_activity = []
    status_items = {
        "support": "ready",
        "sales": "ready",
        "ops": "ready",
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "project_name": settings.PROJECT_NAME,
            "status_items": status_items,
            "recent_activity": recent_activity,
        },
    )

@app.get("/chat")
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
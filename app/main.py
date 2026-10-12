from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.api.routes.customers import router as customers_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.health import router as health_router
from app.api.routes.interactions import router as interactions_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.orders import router as orders_router
from app.core.config import settings
from app.db.database import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered customer operations backend for order support and workflow automation.",
    docs_url="/docs",
    redoc_url="/redoc",
)

for router in (
    health_router,
    customers_router,
    orders_router,
    agent_router,
    knowledge_router,
    evaluation_router,
    interactions_router,
):
    app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}

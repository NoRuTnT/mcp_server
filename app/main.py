from fastapi import FastAPI

from app.config import get_settings
from app.core.logging import configure_logging
from app.mcp.router import router as mcp_router

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.include_router(mcp_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Moonhub MCP server is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db
from app.api.routes import (
    auth,
    projects,
    uploads,
    characters,
    story,
    manga,
    jobs,
    exports,
    settings as settings_route,
    assets
)

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI Manga Studio database tables...")
    await init_db()
    logger.info("AI Manga Studio backend startup complete.")
    yield
    logger.info("AI Manga Studio backend shutting down.")

app = FastAPI(
    title="AI Manga Studio API",
    version="1.0.0",
    description="Agentic AI Manga Generation Platform API with LangGraph and Cloudflare Workers AI",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    if settings.APP_ENV == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal Server Error: {str(exc)}"}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Mount API v1 Routers
api_v1 = FastAPI(title="AI Manga Studio API v1")
api_v1.include_router(auth.router)
api_v1.include_router(projects.router)
api_v1.include_router(uploads.router)
api_v1.include_router(characters.router)
api_v1.include_router(story.router)
api_v1.include_router(manga.router)
api_v1.include_router(jobs.router)
api_v1.include_router(exports.router)
api_v1.include_router(settings_route.router)
api_v1.include_router(assets.router)

app.mount("/api/v1", api_v1)

@app.get("/")
async def root():
    return {
        "name": "AI Manga Studio API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": "/api/v1"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "env": settings.APP_ENV,
        "llm_configured": settings.is_llm_configured,
        "image_provider_configured": settings.is_image_provider_configured
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

"""Application entrypoint: creates tables, wires CORS, security headers, routers."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine
from .routers import analytics, auth, generate, history

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # for real migrations, use Alembic
    yield


app = FastAPI(
    title="AI Communication Copilot",
    version="1.0.0",
    description="Rewrite, reply, email, LinkedIn, and dating assistants with personas, "
                "caching, rate limiting, and analytics.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Basic hardening headers on every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.include_router(auth.router)
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AI Communication Copilot",
        "llm_mode": "mock" if settings.use_mock_llm else "live",
        "cache": "redis" if settings.redis_url else "memory",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

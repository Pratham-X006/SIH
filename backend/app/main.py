from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    allocations,
    audit_routes,
    auth,
    blockchain,
    data_sources,
    deliveries,
    hazards,
    impact,
    prediction,
    priorities,
    resources,
    system,
)
from app.db.init_db import init_db

app = FastAPI(
    title="Disaster Early Warning, Impact Assessment & Relief Management API",
    description="SIH 2026 · IHSIH027 · Team Optimistic Braincells (product name: SETU)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup() -> None:
    init_db()


app.include_router(hazards.router)
app.include_router(prediction.router)
app.include_router(impact.router)
app.include_router(blockchain.router)
app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(priorities.router)
app.include_router(allocations.router)
app.include_router(deliveries.router)
app.include_router(audit_routes.router)
app.include_router(system.router)
app.include_router(data_sources.router)


@app.get("/health")
def health():
    return {"status": "ok"}

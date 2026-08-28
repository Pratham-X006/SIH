"""SQLAlchemy engine/session. Uses SQLite for this prototype (DATABASE_URL in .env) — the
schema below is written close enough to standard SQL that migrating to PostgreSQL/PostGIS
(the architecturally correct production choice, see ARCHITECTURE.md) mainly means swapping
DATABASE_URL and adding geometry columns, not a redesign. See LIMITATIONS.md for why SQLite
was used here instead of PostGIS (no local Postgres/Docker daemon available in this build
environment).
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

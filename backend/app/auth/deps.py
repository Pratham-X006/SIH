"""RBAC dependencies. Every protected route declares `Depends(require_role(...))` explicitly
— there is no implicit "admin can do everything" bypass, because Section 52 requires that an
NGO cannot perform administrator-only operations and a warehouse manager cannot self-approve
their own high-level allocation, not merely that *some* auth check exists.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

ROLES = [
    "SUPER_ADMIN",
    "DISTRICT_OFFICER",
    "NGO",
    "WAREHOUSE_MANAGER",
    "RELIEF_CENTRE",
    "AUDITOR",
    "PUBLIC",
]


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User | None:
    """Returns None for anonymous/public access — routes that allow PUBLIC must handle that
    explicitly rather than assuming a user object always exists."""
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.query(User).filter(User.username == payload["sub"]).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


def require_role(*allowed_roles: str):
    """Dependency factory. `Depends(require_role("PUBLIC"))` allows anonymous access;
    any other role list requires a valid, matching authenticated user."""

    def _dependency(user: User | None = Depends(get_current_user)) -> User | None:
        if "PUBLIC" in allowed_roles and user is None:
            return None
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role!r} is not permitted to perform this action "
                f"(requires one of {list(allowed_roles)}).",
            )
        return user

    return _dependency

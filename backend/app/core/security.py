"""
Admin auth utilities — Section 15. Only the admin panel needs this;
patients remain anonymous/session-based (Section 1.4 non-goal).
"""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from uuid import UUID

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_report_token(session_id: UUID) -> str:
    """Create a short-lived, session-bound token for anonymous report access."""
    expire = datetime.utcnow() + timedelta(minutes=settings.REPORT_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(session_id), "purpose": "triage-report", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_report_token(token: str, session_id: UUID) -> bool:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("purpose") == "triage-report" and payload.get("sub") == str(session_id)
    except JWTError:
        return False


def get_current_admin_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """FastAPI dependency — protects every /api/admin/* route (except login)."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

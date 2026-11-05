import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt 
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from stage3_systems.database import get_db
from stage3_systems.models import User

JWT_SECRET = os.getenv("SMARTLOGISTICS_JWT_SECRET")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    # Fail closed: do not start an API with a predictable development secret.
    raise RuntimeError(
        "Set SMARTLOGISTICS_JWT_SECRET to a random secret of at least 32 characters."
    )
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "20"))
password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return password_hash.verify(password, stored_hash)
    except Exception:
        return False

def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: DbSession,
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat"]},
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise unauthorized
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise unauthorized
    return user

def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return user

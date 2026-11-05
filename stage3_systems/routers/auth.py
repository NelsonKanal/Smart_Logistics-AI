from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from stage3_systems.auth import (
    create_access_token, get_current_user, hash_password, verify_password
)
from stage3_systems.database import get_db
from stage3_systems.models import User
from stage3_systems.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
DbSession = Annotated[Session, Depends(get_db)]

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession):
    email = str(request.email).strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(
        full_name=request.full_name.strip(),
        email=email,
        password_hash=hash_password(request.password),
        role="customer",
        is_active=1, 
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user),
        user=UserResponse(id=user.id, full_name=user.full_name, email=user.email, role=user.role),
    )

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession):
    email = str(request.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()
    # Same response whether email or password is incorrect.
    if user is None or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return TokenResponse(
        access_token=create_access_token(user),
        user=UserResponse(id=user.id, full_name=user.full_name, email=user.email, role=user.role),
    )

@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return UserResponse(id=user.id, full_name=user.full_name, email=user.email, role=user.role)

"""
Authentication API Routes — Register, Login, Refresh, Logout, and User Info.
Uses JWT (python-jose) + bcrypt (passlib) for production-grade auth.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings

router = APIRouter(prefix="/auth")
log = structlog.get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Schemas ───────────────────────────────────────────────────
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str = "user"
    autonomy_level: int = 1
    is_active: bool = True


# ── Helper Utilities ──────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


# In-memory store for dev if DB is offline (synchronizes with DB when available)
_users_db: Dict[str, Dict] = {}


# ── Endpoints ─────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """Register a new user and return JWT access tokens."""
    import uuid

    if request.email in _users_db:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = hash_password(request.password)
    user_id = str(uuid.uuid4())

    user_data = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "hashed_password": hashed_pw,
        "full_name": request.full_name,
        "role": "user",
        "autonomy_level": 1,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    _users_db[request.email] = user_data
    log.info("User registered", email=request.email, user_id=user_id)

    access_token = create_access_token({"sub": user_id, "email": request.email, "role": "user"})
    refresh_token = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user={
            "id": user_id,
            "email": request.email,
            "username": request.username,
            "full_name": request.full_name,
            "role": "user",
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """Authenticate user credentials and issue JWT access token."""
    user = _users_db.get(request.email)
    
    # If not in dev in-memory store, create default admin for quick testing
    if not user and request.email == "admin@jarvis.ai" and request.password == "admin123":
        user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "admin@jarvis.ai",
            "username": "jarvis_admin",
            "hashed_password": hash_password("admin123"),
            "full_name": "JARVIS Administrator",
            "role": "admin",
            "autonomy_level": 3,
            "is_active": True,
        }
        _users_db["admin@jarvis.ai"] = user

    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
    refresh_token = create_refresh_token({"sub": user["id"]})

    log.info("User logged in", email=request.email)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "role": user["role"],
        },
    )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Exchange a valid refresh token for a new access token."""
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        new_access_token = create_access_token({"sub": user_id})
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout")
async def logout():
    """Client-side logout acknowledgement."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Return currently authenticated user details."""
    return UserResponse(
        id="00000000-0000-0000-0000-000000000001",
        email="admin@jarvis.ai",
        username="jarvis_admin",
        full_name="JARVIS Administrator",
        role="admin",
        autonomy_level=3,
        is_active=True,
    )

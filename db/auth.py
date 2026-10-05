import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from .models import Token, User, UserCreate, UserRead
from .session import BASE_DIR, get_session

ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=int(os.getenv("TOKEN_TTL_HOURS", "24")))
ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "true").lower() == "true"


def _load_secret() -> str:
    """SECRET_KEY env var, else a random key persisted in .secret_key (git-ignored)."""
    env = os.getenv("SECRET_KEY")
    if env:
        return env
    path = Path(BASE_DIR) / ".secret_key"
    if not path.exists():
        path.write_text(secrets.token_urlsafe(48))
        path.chmod(0o600)
    return path.read_text().strip()


SECRET_KEY = _load_secret()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user: User) -> str:
    payload = {"sub": str(user.id), "exp": datetime.now(timezone.utc) + TOKEN_TTL}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _user_from_token(token: str, session: Session) -> User:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    user = session.get(User, user_id)
    if user is None:
        raise unauthorized
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    return _user_from_token(token, session)


def get_optional_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    session: Session = Depends(get_session),
) -> Optional[User]:
    """None when no token is sent; 401 when a token is sent but invalid/expired."""
    if token is None:
        return None
    return _user_from_token(token, session)


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, session: Session = Depends(get_session)):
    if not ALLOW_REGISTRATION:
        raise HTTPException(403, "Registration is disabled")
    username = data.username.strip().lower()
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(409, "Username already taken")
    user = User(username=username, password_hash=hash_password(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.username == form.username.strip().lower())
    ).first()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_token(user))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user

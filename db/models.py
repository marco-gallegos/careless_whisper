from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=72)


class UserRead(SQLModel):
    id: int
    username: str
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TranscriptBase(SQLModel):
    filename: Optional[str] = None
    text: str
    language: str = "unknown"
    model_used: str = "base"
    processing_time: float = 0.0


class Transcript(TranscriptBase, table=True):
    __tablename__ = "transcripts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    segments: list = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class TranscriptCreate(TranscriptBase):
    segments: list = Field(default_factory=list)


class TranscriptUpdate(SQLModel):
    filename: Optional[str] = None
    text: Optional[str] = None
    language: Optional[str] = None


class TranscriptRead(TranscriptBase):
    id: int
    user_id: Optional[int] = None
    segments: list
    created_at: datetime

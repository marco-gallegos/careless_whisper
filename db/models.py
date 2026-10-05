from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TranscriptBase(SQLModel):
    filename: Optional[str] = None
    text: str
    language: str = "unknown"
    model_used: str = "base"
    processing_time: float = 0.0


class Transcript(TranscriptBase, table=True):
    __tablename__ = "transcripts"

    id: Optional[int] = Field(default=None, primary_key=True)
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
    segments: list
    created_at: datetime

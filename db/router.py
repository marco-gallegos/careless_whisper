from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from . import crud
from .auth import get_current_user
from .models import TranscriptCreate, TranscriptRead, TranscriptUpdate, User
from .session import get_session

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("", response_model=TranscriptRead, status_code=201)
def create(
    data: TranscriptCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return crud.create_transcript(session, data, user.id)


@router.get("", response_model=List[TranscriptRead])
def list_all(
    offset: int = 0,
    limit: int = Query(50, le=200),
    language: Optional[str] = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return crud.list_transcripts(session, user.id, offset, limit, language)


@router.get("/{transcript_id}", response_model=TranscriptRead)
def read(
    transcript_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    transcript = crud.get_transcript(session, transcript_id, user.id)
    if transcript is None:
        raise HTTPException(404, "Transcript not found")
    return transcript


@router.patch("/{transcript_id}", response_model=TranscriptRead)
def update(
    transcript_id: int,
    data: TranscriptUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    transcript = crud.update_transcript(session, transcript_id, user.id, data)
    if transcript is None:
        raise HTTPException(404, "Transcript not found")
    return transcript


@router.delete("/{transcript_id}", status_code=204)
def delete(
    transcript_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if not crud.delete_transcript(session, transcript_id, user.id):
        raise HTTPException(404, "Transcript not found")
    return Response(status_code=204)

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from . import crud
from .models import TranscriptCreate, TranscriptRead, TranscriptUpdate
from .session import get_session

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("", response_model=TranscriptRead, status_code=201)
def create(data: TranscriptCreate, session: Session = Depends(get_session)):
    return crud.create_transcript(session, data)


@router.get("", response_model=List[TranscriptRead])
def list_all(
    offset: int = 0,
    limit: int = Query(50, le=200),
    language: Optional[str] = None,
    session: Session = Depends(get_session),
):
    return crud.list_transcripts(session, offset, limit, language)


@router.get("/{transcript_id}", response_model=TranscriptRead)
def read(transcript_id: int, session: Session = Depends(get_session)):
    transcript = crud.get_transcript(session, transcript_id)
    if transcript is None:
        raise HTTPException(404, "Transcript not found")
    return transcript


@router.patch("/{transcript_id}", response_model=TranscriptRead)
def update(
    transcript_id: int, data: TranscriptUpdate, session: Session = Depends(get_session)
):
    transcript = crud.update_transcript(session, transcript_id, data)
    if transcript is None:
        raise HTTPException(404, "Transcript not found")
    return transcript


@router.delete("/{transcript_id}", status_code=204)
def delete(transcript_id: int, session: Session = Depends(get_session)):
    if not crud.delete_transcript(session, transcript_id):
        raise HTTPException(404, "Transcript not found")
    return Response(status_code=204)

from typing import Optional, Sequence

from sqlmodel import Session, select

from .models import Transcript, TranscriptCreate, TranscriptUpdate


def create_transcript(session: Session, data: TranscriptCreate, user_id: int) -> Transcript:
    transcript = Transcript.model_validate(data, update={"user_id": user_id})
    session.add(transcript)
    session.commit()
    session.refresh(transcript)
    return transcript


def get_transcript(session: Session, transcript_id: int, user_id: int) -> Optional[Transcript]:
    transcript = session.get(Transcript, transcript_id)
    if transcript is None or transcript.user_id != user_id:
        return None
    return transcript


def list_transcripts(
    session: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 50,
    language: Optional[str] = None,
) -> Sequence[Transcript]:
    stmt = (
        select(Transcript)
        .where(Transcript.user_id == user_id)
        .order_by(Transcript.created_at.desc())
    )
    if language:
        stmt = stmt.where(Transcript.language == language)
    return session.exec(stmt.offset(offset).limit(limit)).all()


def update_transcript(
    session: Session, transcript_id: int, user_id: int, data: TranscriptUpdate
) -> Optional[Transcript]:
    transcript = get_transcript(session, transcript_id, user_id)
    if transcript is None:
        return None
    transcript.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(transcript)
    session.commit()
    session.refresh(transcript)
    return transcript


def delete_transcript(session: Session, transcript_id: int, user_id: int) -> bool:
    transcript = get_transcript(session, transcript_id, user_id)
    if transcript is None:
        return False
    session.delete(transcript)
    session.commit()
    return True

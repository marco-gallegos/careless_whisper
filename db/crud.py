from typing import Optional, Sequence

from sqlmodel import Session, select

from .models import Transcript, TranscriptCreate, TranscriptUpdate


def create_transcript(session: Session, data: TranscriptCreate) -> Transcript:
    transcript = Transcript.model_validate(data)
    session.add(transcript)
    session.commit()
    session.refresh(transcript)
    return transcript


def get_transcript(session: Session, transcript_id: int) -> Optional[Transcript]:
    return session.get(Transcript, transcript_id)


def list_transcripts(
    session: Session, offset: int = 0, limit: int = 50, language: Optional[str] = None
) -> Sequence[Transcript]:
    stmt = select(Transcript).order_by(Transcript.created_at.desc())
    if language:
        stmt = stmt.where(Transcript.language == language)
    return session.exec(stmt.offset(offset).limit(limit)).all()


def update_transcript(
    session: Session, transcript_id: int, data: TranscriptUpdate
) -> Optional[Transcript]:
    transcript = session.get(Transcript, transcript_id)
    if transcript is None:
        return None
    transcript.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(transcript)
    session.commit()
    session.refresh(transcript)
    return transcript


def delete_transcript(session: Session, transcript_id: int) -> bool:
    transcript = session.get(Transcript, transcript_id)
    if transcript is None:
        return False
    session.delete(transcript)
    session.commit()
    return True

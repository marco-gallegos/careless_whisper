import os
from pathlib import Path

from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'transcripts.sqlite'}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session

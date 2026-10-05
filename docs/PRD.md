# PRD: Careless Whisper - Local Transcription API

Status: reflects the current implementation (api.py + db/). Last updated 2026-10-05.

## 1. Overview
A locally hosted FastAPI service that transcribes audio with OpenAI Whisper and
stores every transcript in a local SQLite database, exposing it through a CRUD API.
It runs as a macOS launchd service on the owner's machine; no data leaves the machine.

## 2. Goals
- Transcribe audio files via a simple HTTP call (curl / browser fetch).
- Keep results: persist every transcript so it can be listed, corrected and deleted later.
- Run fully local, with no external services or API keys.

## 3. Non-goals (current version)
- Authentication/authorization (CORS is open; service intended for trusted local use).
- Multi-user, multi-tenant or remote deployment.
- Storing the audio files (they are deleted after transcription).
- Full-text search, speaker diarization, streaming/real-time transcription.
- Job queue: requests are processed synchronously per request (thread pool of 4).

## 4. Users
Single developer/owner using the API from scripts and a browser test client (`test_client.html`).

## 5. Functional requirements

### 5.1 Transcription
| ID | Requirement | Status |
|----|-------------|--------|
| T1 | `POST /transcribe?model=` accepts a multipart audio file | Done |
| T2 | Supported formats: mp3, wav, m4a, ogg, flac, webm, mp4; others -> 400 | Done |
| T3 | Models: tiny, base, small, medium, large, turbo (default base); invalid -> 400 | Done |
| T4 | Empty file -> 400; internal failure -> 500 | Done |
| T5 | Response: id, status, transcription, language, segments (id/start/end/text), processing_time, model_used | Done |
| T6 | `POST /transcribe-text-only` returns text, language, processing_time | Done |
| T7 | Temp files cleaned after each request | Done |
| T8 | Each successful transcription is saved to the DB; a save failure is logged and does not fail the request (id is null) | Done |
| T9 | `GET /`, `/health`, `/models` informational endpoints | Done |

Note: `/transcribe-text-only` calls the same handler, so it is also persisted.

### 5.2 Transcript storage (CRUD)
| ID | Requirement | Status |
|----|-------------|--------|
| S1 | `POST /transcripts` create manually (201) | Done |
| S2 | `GET /transcripts` list, newest first; `offset`, `limit` (default 50, max 200), `language` filter | Done |
| S3 | `GET /transcripts/{id}` -> 404 if missing | Done |
| S4 | `PATCH /transcripts/{id}` partial update of filename, text, language -> 404 if missing | Done |
| S5 | `DELETE /transcripts/{id}` (204) -> 404 if missing | Done |

### 5.3 Data model: `transcripts`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | autoincrement |
| filename | text, nullable | original upload name |
| text | text, required | full transcription |
| language | text | default "unknown" |
| model_used | text | Whisper model name |
| processing_time | float | seconds |
| segments | JSON, required | list of {id,start,end,text} |
| created_at | UTC datetime | set on insert |

### 5.4 Persistence and migrations
- ORM: SQLModel (SQLAlchemy). Migrations: Alembic (`migrations/`, autogenerate, batch mode for SQLite).
- DB file: `transcripts.sqlite` in project root (git-ignored); override with `DATABASE_URL`.
- Schema changes require a new migration: `make migration m="..."`; apply with `make migrate`.
- The app does not run migrations on startup; `make migrate` must be run on each environment.

## 6. Non-functional requirements
- Runs locally on macOS (CPU, fp16 disabled); service on port 8765, 15 min keep-alive for long audio.
- Managed with uv (Python >=3.10, `package = false`); numba/numpy are constrained in `pyproject.toml` to avoid a bad resolution and a yanked numpy.
- Whisper model is loaded per request (cache is commented out), trading memory for latency.
- Operation: launchd plist + `make install|load|unload|logs`.

## 7. Architecture
```
client -> FastAPI (api.py) -> thread pool -> whisper.transcribe
                 |                                  |
                 +-> db/router.py -> db/crud.py -> SQLModel -> SQLite
```
Files: `api.py` (app + transcription), `db/models.py`, `db/session.py`, `db/crud.py`,
`db/router.py`, `migrations/`, `alembic.ini`, `makefile`.
`apifasterwhisper.py` and `apimlxwhisper.py` are standalone experiments, not integrated with the DB.

## 8. Known gaps / risks
- No auth; binds to 0.0.0.0 with wildcard CORS, so anyone on the network can read/delete transcripts.
- No tests for the DB layer; `test_api.py` predates storage.
- The launchd plist runs `/usr/bin/python3`, which lacks the uv-managed dependencies; it needs updating to use `uv run` or the `.venv` interpreter.
- Model reloaded on every request (slow); no request queue or concurrency limit beyond the thread pool.
- Existing docs (readme.md, QUICKSTART.md, LEEME.md, etc.) do not yet describe the storage endpoints.

## 9. Open questions / possible next steps
1. Restrict host/CORS and add an API key?
2. Re-enable model caching?
3. Run migrations automatically on startup?
4. Add search over transcript text and export (txt/srt/vtt)?
5. Integrate the MLX/faster-whisper backends behind a selectable engine?

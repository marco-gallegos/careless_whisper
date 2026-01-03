"""
FastAPI application for audio transcription using OpenAI Whisper (local model).

Features:
- Async processing with threading support
- Long-running request handling with streaming responses
- Easy consumption via curl or fetch
- Managed with uv
"""

import asyncio
import os
import shutil
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure thread pool for CPU-bound tasks
# Use more threads if Python 3.14t (free-threaded) is available
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
    title="Whisper Transcription API",
    description="Local OpenAI Whisper transcription service",
    version="1.0.0"
)

# Enable CORS for browser fetch requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
_model_cache = {}

class TranscriptionResponse(BaseModel):
    status: str
    transcription: str
    language: str
    segments: list
    processing_time: float
    model_used: str


def get_whisper_model(model_name: str = "base"):
    """
    Load and cache Whisper model.
    
    Available models: tiny, base, small, medium, large
    """
    if model_name not in _model_cache:
        print(f"Loading Whisper model: {model_name}")
        _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]


def transcribe_audio_sync(file_path: str, model_name: str = "base") -> dict:
    """
    Synchronous transcription function to run in thread pool.
    This is CPU-bound work, so we run it in a separate thread.
    """
    model = get_whisper_model(model_name)
    result = model.transcribe(file_path, fp16=False)
    return result


async def transcribe_audio_async(file_path: str, model_name: str = "base") -> dict:
    """
    Async wrapper for transcription using thread pool.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        transcribe_audio_sync,
        file_path,
        model_name
    )
    return result


def cleanup_temp_file(file_path: str):
    """Clean up temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # Remove parent directory if it's a temp directory
            parent_dir = os.path.dirname(file_path)
            if parent_dir and os.path.exists(parent_dir) and tempfile.gettempdir() in parent_dir:
                shutil.rmtree(parent_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")


@app.get("/")
async def root():
    """API root endpoint with usage information."""
    return {
        "message": "Whisper Transcription API",
        "endpoints": {
            "/transcribe": "POST - Upload audio file for transcription",
            "/health": "GET - Check API health",
            "/models": "GET - List available models"
        },
        "usage": {
            "curl": "curl -X POST -F 'file=@audio.mp3' http://localhost:8000/transcribe",
            "fetch": "fetch('http://localhost:8000/transcribe', {method: 'POST', body: formData})"
        }
    }


@app.get("/health")
async def health_check():
    """Check API health and model availability."""
    try:
        import whisper
        return {
            "status": "healthy",
            "whisper_available": True,
            "cached_models": list(_model_cache.keys())
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/models")
async def list_models():
    """List available Whisper models."""
    return {
        "available_models": ["tiny", "base", "small", "medium", "large"],
        "description": {
            "tiny": "Fastest, lowest accuracy (~1GB)",
            "base": "Fast, good for most uses (~1GB)",
            "small": "Balanced speed/accuracy (~2GB)",
            "medium": "High accuracy, slower (~5GB)",
            "large": "Highest accuracy, slowest (~10GB)"
        },
        "default": "base"
    }


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = "base"
):
    """
    Transcribe an audio file using OpenAI Whisper.
    
    Parameters:
    - file: Audio file (mp3, wav, m4a, ogg, flac, etc.)
    - model: Whisper model to use (default: base)
    
    Returns:
    - Full transcription with segments and timing information
    
    Example curl usage:
    ```bash
    curl -X POST "http://localhost:8000/transcribe?model=base" \\
         -F "file=@audio.mp3" \\
         -H "accept: application/json"
    ```
    
    Example JavaScript fetch:
    ```javascript
    const formData = new FormData();
    formData.append('file', audioFile);
    
    const response = await fetch('http://localhost:8000/transcribe?model=base', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    ```
    """
    start_time = time.time()
    temp_dir = None
    file_path = None
    
    try:
        # Validate model
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model. Choose from: {', '.join(valid_models)}"
            )
        
        # Validate file extension
        allowed_extensions = ["mp3", "wav", "m4a", "ogg", "flac", "webm", "mp4"]
        file_extension = file.filename.split(".")[-1].lower() if file.filename else "unknown"
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create temporary directory and save file
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.{file_extension}")
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            f.write(content)
        
        # Transcribe asynchronously using thread pool
        print(f"Starting transcription with model '{model}' for file: {file.filename}")
        result = await transcribe_audio_async(file_path, model)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Format segments
        segments = [
            {
                "id": segment["id"],
                "start": round(segment["start"], 2),
                "end": round(segment["end"], 2),
                "text": segment["text"].strip()
            }
            for segment in result.get("segments", [])
        ]
        
        # Schedule cleanup in background
        background_tasks.add_task(cleanup_temp_file, file_path)
        
        # Prepare response
        response_data = TranscriptionResponse(
            status="success",
            transcription=result["text"].strip(),
            language=result.get("language", "unknown"),
            segments=segments,
            processing_time=round(processing_time, 2),
            model_used=model
        )
        
        print(f"Transcription completed in {processing_time:.2f}s")
        return response_data
    
    except HTTPException:
        # Re-raise HTTP exceptions
        if file_path:
            cleanup_temp_file(file_path)
        raise
    
    except Exception as e:
        # Clean up and return error
        if file_path:
            cleanup_temp_file(file_path)
        
        print(f"Transcription error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@app.post("/transcribe-text-only")
async def transcribe_text_only(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = "base"
):
    """
    Simplified endpoint that returns only the transcribed text.
    Faster response with minimal data.
    """
    result = await transcribe(background_tasks, file, model)
    return {
        "text": result.transcription,
        "language": result.language,
        "processing_time": result.processing_time
    }


if __name__ == "__main__":
    # Configure uvicorn for long-running requests
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=300,  # 5 minutes keep-alive
        timeout_graceful_shutdown=30,
        log_level="info"
    )

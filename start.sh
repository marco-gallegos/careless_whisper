#!/bin/bash

# Startup script for Whisper Transcription API

echo "🚀 Starting Whisper Transcription API..."
echo ""

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg is not installed!"
    echo "   Install it with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
    echo ""
fi

PYTHON=/usr/bin/python3

# Install dependencies if needed (user site-packages, no sudo required)
if ! $PYTHON -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    $PYTHON -m pip install --user -r requirements.txt
    echo ""
fi

# Apply database migrations
$PYTHON -m alembic upgrade head

# Start the server
echo "✅ Starting server on http://localhost:8765"
echo "   Press Ctrl+C to stop"
echo ""

exec $PYTHON api.py


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

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo ""
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
    echo ""
fi

# Start the server
echo "✅ Starting server on http://localhost:8765"
echo "   Press Ctrl+C to stop"
echo ""

python api.py


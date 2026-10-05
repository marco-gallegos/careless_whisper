# Example curl commands for testing the Whisper API

# 1. Check API health
curl http://localhost:8765/health

# 2. Get API information
curl http://localhost:8765/

# 3. List available models
curl http://localhost:8765/models

# 4. Transcribe audio file (replace audio.mp3 with your file)
# Using the base model (default)
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"

# 5. Transcribe with tiny model (fastest)
curl -X POST "http://localhost:8765/transcribe?model=tiny" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"

# 6. Transcribe and get only text (no segments)
curl -X POST "http://localhost:8765/transcribe-text-only?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"

# 7. Transcribe with large model (most accurate)
curl -X POST "http://localhost:8765/transcribe?model=large" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"

# 8. Save response to file
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json" \
     -o transcription_result.json

# 9. Pretty print JSON response (requires jq)
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json" | jq .


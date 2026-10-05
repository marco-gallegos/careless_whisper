# 🚀 Quick Reference - Whisper API

## Start Server
```bash
./start.sh
# or: python api.py
```

## Test
```bash
# Health check
curl http://localhost:8765/health

# Transcribe
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@audio.mp3"

# Or use web UI
open test_client.html
```

## JavaScript Example
```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('http://localhost:8765/transcribe', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.transcription);
```

## Python Example
```python
import requests

with open("audio.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8765/transcribe",
        files={"file": f}
    )

print(response.json()["transcription"])
```

## Available Models
- `tiny` - Fastest (testing)
- `base` - Recommended (production) ⭐
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy

## Endpoints
- `GET /` - API info
- `GET /health` - Health check
- `GET /models` - List models
- `POST /transcribe` - Full transcription
- `POST /transcribe-text-only` - Text only
- `GET /docs` - Interactive docs

## Files
- 📖 `LEEME.md` - Full docs (Spanish)
- 📖 `readme.md` - Full docs (English)
- ⚡ `QUICKSTART.md` - Quick start guide
- 🧪 `test_client.html` - Web UI
- 📝 `examples.sh` - curl examples

## Troubleshooting
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux

# Install dependencies
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Check server
curl http://localhost:8765/health
```

---
**Full documentation:** See `LEEME.md` (Spanish) or `readme.md` (English)


# Whisper Transcription API

FastAPI service for audio transcription using OpenAI Whisper (local model).

## Features

- ✅ **Asynchronous processing** with ThreadPoolExecutor
- ✅ **Local Whisper models** (no external API calls)
- ✅ **Long-running request support** (no premature timeouts)
- ✅ **Easy to consume** via curl or JavaScript fetch
- ✅ **Python 3.14t ready** (free-threaded Python support)
- ✅ **Managed with uv** (modern Python package manager)
- ✅ **CORS enabled** for browser requests
- ✅ **Background task cleanup** for temp files

## Requirements

- Python 3.10+ (3.14t recommended for better threading)
- uv package manager
- FFmpeg (for audio processing)

## Installation

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create virtual environment and install dependencies

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using traditional pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install FFmpeg (required by Whisper)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Usage

### Start the server

```bash
# Using uv
uv run python api.py

# Or directly with Python
python api.py

# Or with uvicorn
uvicorn api:app --host 0.0.0.0 --port 8765 --timeout-keep-alive 300
```

The API will be available at `http://localhost:8765`

### Run as a background service (macOS launchd)

The repo ships `com.marcogallegos.translateapi.plist`, which runs `api.py` at login and restarts it if it crashes
(`RunAtLoad` + `KeepAlive`). Use the makefile:

```bash
make load      # copy plist to ~/Library/LaunchAgents/ and load it
make status    # launchd state, PID, exit code and recent logs
make logs      # last 30 lines of stdout/stderr (logs/stdout.log, logs/stderr.log)
make reload    # unload + load (after editing api.py or the plist)
make unload    # stop the service
make uninstall # unload and remove the plist
```

Notes:

- The plist hardcodes `/usr/bin/python3` and the absolute project path, so the packages in `requirements.txt` must be importable by that interpreter. Edit `ProgramArguments`/`WorkingDirectory` if you move the project or want to use a venv.
- `launchd` has a minimal `PATH`; the plist sets it to include `/opt/homebrew/bin` so Whisper can find `ffmpeg`.
- The service listens on port **8765** on all interfaces (`0.0.0.0`) with CORS open to any origin. Fine on a trusted network; restrict `host`/`allow_origins` in `api.py` otherwise.

### Web UI

The companion React app in `~/code/js/careless_whisper_ui` records audio in the browser and calls
`POST /transcribe-text-only` on this service. See its README for configuration (`VITE_TRANSCRIPTION_API_URL`, `VITE_WHISPER_MODEL`).

### API Endpoints

#### 1. Root endpoint - API info
```bash
curl http://localhost:8765/
```

#### 2. Health check
```bash
curl http://localhost:8765/health
```

#### 3. List available models
```bash
curl http://localhost:8765/models
```

#### 4. Transcribe audio (full response with segments)
```bash
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"
```

#### 5. Transcribe audio (text only)
```bash
curl -X POST "http://localhost:8765/transcribe-text-only?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"
```

### Available Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~1GB | Fastest | Lowest |
| `base` | ~1GB | Fast | Good (default) |
| `small` | ~2GB | Medium | Better |
| `medium` | ~5GB | Slow | High |
| `large` | ~10GB | Slowest | Highest |

### JavaScript Example

```javascript
// Using fetch API
const transcribeAudio = async (audioFile) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    
    try {
        const response = await fetch('http://localhost:8765/transcribe?model=base', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Transcription:', result.transcription);
        console.log('Language:', result.language);
        console.log('Processing time:', result.processing_time, 'seconds');
        
        return result;
    } catch (error) {
        console.error('Error:', error);
    }
};

// Usage
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await transcribeAudio(file);
        console.log(result);
    }
});
```

### Python Example

```python
import requests

def transcribe_audio(file_path: str, model: str = "base"):
    url = f"http://localhost:8765/transcribe?model={model}"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Transcription: {result['transcription']}")
        print(f"Language: {result['language']}")
        print(f"Processing time: {result['processing_time']}s")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Usage
transcribe_audio("audio.mp3", model="base")
```

## Response Format

### Full Transcription Response

```json
{
    "status": "success",
    "transcription": "Full transcription text here...",
    "language": "en",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 5.5,
            "text": "First segment text"
        },
        {
            "id": 1,
            "start": 5.5,
            "end": 12.3,
            "text": "Second segment text"
        }
    ],
    "processing_time": 15.42,
    "model_used": "base"
}
```

### Text-Only Response

```json
{
    "text": "Full transcription text here...",
    "language": "en",
    "processing_time": 15.42
}
```

## Supported Audio Formats

- MP3
- WAV
- M4A
- OGG
- FLAC
- WEBM
- MP4

## Configuration

### Timeout Settings

The server is configured with long timeouts to handle large audio files:
- Keep-alive timeout: 300 seconds (5 minutes)
- Graceful shutdown: 30 seconds

### Thread Pool

The API uses a `ThreadPoolExecutor` with 4 workers by default. This can be adjusted in `api.py`:

```python
executor = ThreadPoolExecutor(max_workers=4)
```

For Python 3.14t (free-threaded), you can increase this number for better performance.

## Performance Tips

1. **Choose the right model**: Use `base` for most cases, `tiny` for speed, `large` for accuracy
2. **Use Python 3.14t**: Better threading performance with the free-threaded build
3. **Adjust workers**: Increase `max_workers` based on your CPU cores
4. **Pre-load models**: The first request will be slower as it loads the model

## Troubleshooting

### "ModuleNotFoundError: No module named 'whisper'"
```bash
uv pip install openai-whisper
```

### "FFmpeg not found"
Install FFmpeg using the instructions in the Installation section.

### "Request timeout"
Increase the timeout in your client or use the `--timeout-keep-alive` flag when starting uvicorn.

### Out of memory
Use a smaller model (`tiny` or `base`) or close other applications.

## Development

### Running tests
```bash
uv pip install pytest httpx pytest-asyncio
pytest
```

### Project structure
```
apitranslate/
├── api.py              # Main FastAPI application
├── pyproject.toml      # Project configuration
├── requirements.txt    # Dependencies
├── .python-version     # Python version
└── readme.md          # This file
```

## License

MIT License - feel free to use this in your projects!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Uvicorn](https://www.uvicorn.org/)
- [uv](https://github.com/astral-sh/uv)

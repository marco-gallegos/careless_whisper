# Quick Setup Guide

## 🚀 Quick Start (3 steps)

### 1. Install uv (if not installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Install FFmpeg
**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

## 🎯 Running the Server

### Option 1: Using the start script (easiest)
```bash
./start.sh
```

### Option 2: Directly with Python
```bash
python api.py
```

### Option 3: With uvicorn
```bash
uvicorn api:app --host 0.0.0.0 --port 8765 --timeout-keep-alive 300
```

The API will be available at http://localhost:8765

## 📝 Quick Test

### Using curl
```bash
# Health check
curl http://localhost:8765/health

# Transcribe an audio file
curl -X POST "http://localhost:8765/transcribe?model=base" \
     -F "file=@your_audio.mp3"
```

### Using the web interface
Open `test_client.html` in your browser for a beautiful UI to test the API.

### Using the test script
```bash
python test_api.py
```

## 🔧 Python 3.14t Setup (Optional - for better performance)

If you want to use Python 3.14t (free-threaded):

```bash
# Install Python 3.14t using uv
uv python install 3.14t

# Create virtual environment with 3.14t
uv venv --python 3.14t

# Activate and install
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 📚 More Examples

See `examples.sh` for more curl examples or check `readme.md` for the full documentation.

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'whisper'"**
```bash
uv pip install openai-whisper
```

**"FFmpeg not found"**
Install FFmpeg (see step 3 above)

**"Cannot connect to API"**
Make sure the server is running: `python api.py`

**Model takes too long to load**
Use a smaller model like `tiny` or `base` for faster loading

## 💡 Tips

- First transcription will be slow (model loading)
- Use `tiny` model for testing (fastest)
- Use `base` model for production (good balance)
- Use `large` model for best accuracy (slowest)
- The model is cached after first load


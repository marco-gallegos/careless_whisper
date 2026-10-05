#!/bin/bash

# Simple test script to verify the API works with your audio file

echo "🧪 Testing Whisper API with existing audio file"
echo ""

# Check if server is running
echo "1️⃣ Checking if server is running..."
if curl -s http://localhost:8765/health > /dev/null 2>&1; then
    echo "   ✅ Server is running"
else
    echo "   ❌ Server is not running!"
    echo "   Start it with: ./start.sh"
    exit 1
fi

echo ""
echo "2️⃣ Testing with Why_and_When_ReactJS.mp3..."
echo "   Model: tiny (for quick testing)"
echo "   ⏳ This will take about 30-60 seconds..."
echo ""

# Run transcription with the existing audio file
curl -X POST "http://localhost:8765/transcribe?model=tiny" \
     -F "file=@Why_and_When_ReactJS.mp3" \
     -H "accept: application/json" \
     -o test_result.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Transcription completed!"
    echo ""
    echo "📄 Result saved to test_result.json"
    echo ""
    
    # Try to pretty print with jq if available
    if command -v jq &> /dev/null; then
        echo "Preview:"
        echo "--------"
        jq -r '.transcription[:200] + "..."' test_result.json 2>/dev/null || cat test_result.json
    else
        echo "Install 'jq' for pretty JSON output: brew install jq"
    fi
else
    echo ""
    echo "❌ Transcription failed"
fi


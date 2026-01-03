"""
Simple test script for the Whisper Transcription API
"""

import asyncio
import os
from pathlib import Path

import httpx


async def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Whisper Transcription API\n")
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
    
    # Test 2: List models
    print("2️⃣ Testing models endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/models")
        print(f"   Status: {response.status_code}")
        models = response.json()
        print(f"   Available models: {models['available_models']}\n")
    
    # Test 3: Transcription (if audio file exists)
    audio_files = list(Path(".").glob("*.mp3")) + list(Path(".").glob("*.wav"))
    
    if audio_files:
        audio_file = audio_files[0]
        print(f"3️⃣ Testing transcription with {audio_file.name}...")
        print("   ⏳ This may take a minute...")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            with open(audio_file, "rb") as f:
                files = {"file": (audio_file.name, f, "audio/mpeg")}
                response = await client.post(
                    f"{base_url}/transcribe",
                    params={"model": "tiny"},  # Using tiny model for faster testing
                    files=files
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Language: {result['language']}")
                print(f"   Processing time: {result['processing_time']}s")
                print(f"   Transcription preview: {result['transcription'][:100]}...")
                print(f"   Number of segments: {len(result['segments'])}\n")
            else:
                print(f"   Error: {response.text}\n")
    else:
        print("3️⃣ Skipping transcription test (no audio files found)")
        print("   Add an .mp3 or .wav file to test transcription\n")
    
    print("✅ Tests completed!")


if __name__ == "__main__":
    print("Make sure the API server is running (python api.py)\n")
    asyncio.run(test_api())


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
import uuid
import shutil
import time

# Importar mlx_whisper
try:
    import mlx_whisper
except ImportError:
    raise ImportError("mlx_whisper no está instalado. Instálalo siguiendo las instrucciones en "
                     "https://github.com/ml-explore/mlx-examples/tree/main/whisper")

app = FastAPI(title="MLX-Whisper Transcription API")

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an audio file using MLX-Whisper with the default model.
    
    Parameters:
    - file: Audio file to transcribe
    """
    try:
        # Verificar que es un archivo de audio
        allowed_extensions = ["mp3", "wav", "m4a", "ogg", "flac"]
        file_extension = file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado")
        
        # Crear un directorio temporal
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.{file_extension}")
        
        # Guardar el archivo en el directorio temporal
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Cargar el modelo (usando el valor por defecto)
        start_time = time.time()
        model = mlx_whisper
        
        # Transcribir el audio usando la API de mlx_whisper
        result = model.transcribe(file_path)
        end_time = time.time()
        
        # Preparar la respuesta
        response_data = {
            "status": "success",
            "transcription": result["text"],
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "id": i,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                } for i, segment in enumerate(result.get("segments", []))
            ],
            "processing_time": end_time - start_time
        }
        
        # Eliminar archivos temporales
        shutil.rmtree(temp_dir)
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        # Limpiar si hay error
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    try:
        # Verificar que mlx_whisper esté disponible
        import mlx_whisper
        return {"status": "healthy", "mlx_whisper_version": getattr(mlx_whisper, "__version__", "unknown")}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🎙️ API de Transcripción con Whisper

## 📋 Resumen del Proyecto

API profesional desarrollada con FastAPI que transcribe archivos de audio usando el modelo Whisper de OpenAI de forma **completamente local** (sin necesidad de API keys ni conexión a internet).

### ✅ Requisitos Cumplidos

| Requisito | Estado | Implementación |
|-----------|--------|----------------|
| API con FastAPI | ✅ | Implementado completamente |
| Archivo como entrada | ✅ | Upload de archivos con validación |
| Modelo local de Whisper | ✅ | `openai-whisper` instalado localmente |
| Fácil consumo (curl/fetch) | ✅ | Endpoints REST simples |
| Sin timeout prematuro | ✅ | `timeout-keep-alive=300` segundos |
| Asíncrono | ✅ | `async/await` + ThreadPoolExecutor |
| Soporte threads Python 3.14t | ✅ | ThreadPoolExecutor configurado |
| Gestionado con uv | ✅ | `pyproject.toml` + `.python-version` |

## 🚀 Inicio Rápido

### Instalación en 3 Pasos

```bash
# 1. Instalar uv (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependencias
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 3. Instalar FFmpeg
brew install ffmpeg  # macOS
# sudo apt install ffmpeg  # Linux
```

### Iniciar Servidor

```bash
# Opción 1: Script automático (recomendado)
./start.sh

# Opción 2: Directo con Python
python api.py

# Opción 3: Con uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300
```

Servidor disponible en: **http://localhost:8000**

## 📡 Uso de la API

### 1. Con curl (Terminal)

```bash
# Transcripción completa
curl -X POST "http://localhost:8000/transcribe?model=base" \
     -F "file=@audio.mp3" \
     -H "accept: application/json"

# Solo texto (más rápido)
curl -X POST "http://localhost:8000/transcribe-text-only?model=base" \
     -F "file=@audio.mp3"

# Con diferentes modelos
curl -X POST "http://localhost:8000/transcribe?model=tiny" \
     -F "file=@audio.mp3"  # Rápido

curl -X POST "http://localhost:8000/transcribe?model=large" \
     -F "file=@audio.mp3"  # Preciso
```

### 2. Con JavaScript (Frontend)

```javascript
// Función para transcribir audio
async function transcribirAudio(archivo) {
    const formData = new FormData();
    formData.append('file', archivo);
    
    const respuesta = await fetch('http://localhost:8000/transcribe?model=base', {
        method: 'POST',
        body: formData
    });
    
    const resultado = await respuesta.json();
    return resultado;
}

// Uso con input file
document.getElementById('audioInput').addEventListener('change', async (e) => {
    const archivo = e.target.files[0];
    const resultado = await transcribirAudio(archivo);
    console.log('Transcripción:', resultado.transcription);
});
```

### 3. Con Python (Backend)

```python
import requests

def transcribir(ruta_audio: str, modelo: str = "base"):
    url = f"http://localhost:8000/transcribe?model={modelo}"
    
    with open(ruta_audio, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    return response.json()

# Uso
resultado = transcribir("audio.mp3", modelo="base")
print(resultado['transcription'])
```

### 4. Con Interface Web

Abre el archivo `test_client.html` en tu navegador para una interface gráfica completa con:
- Drag & drop de archivos
- Selección de modelos
- Visualización de resultados
- Segmentos con timestamps

## 🎯 Endpoints Disponibles

### GET `/` - Información de la API
```bash
curl http://localhost:8000/
```

### GET `/health` - Estado del servicio
```bash
curl http://localhost:8000/health
```
Respuesta:
```json
{
    "status": "healthy",
    "whisper_available": true,
    "cached_models": ["base"]
}
```

### GET `/models` - Modelos disponibles
```bash
curl http://localhost:8000/models
```

### POST `/transcribe` - Transcripción completa
Parámetros:
- `file` (form-data): Archivo de audio
- `model` (query): Modelo a usar (default: `base`)

Respuesta:
```json
{
    "status": "success",
    "transcription": "Texto completo...",
    "language": "es",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 5.5,
            "text": "Primer segmento"
        }
    ],
    "processing_time": 15.42,
    "model_used": "base"
}
```

### POST `/transcribe-text-only` - Solo texto
Igual que `/transcribe` pero retorna solo el texto, más rápido.

## 🤖 Modelos Disponibles

| Modelo | Tamaño | Velocidad | Precisión | Uso Recomendado |
|--------|--------|-----------|-----------|-----------------|
| `tiny` | ~1GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Pruebas rápidas |
| `base` | ~1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | **Producción general** ⭐ |
| `small` | ~2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Mejor balance |
| `medium` | ~5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Alta precisión |
| `large` | ~10GB | ⚡ | ⭐⭐⭐⭐⭐ | Máxima precisión |

### Recomendaciones:
- **Desarrollo/Testing**: Usa `tiny` (carga rápida)
- **Producción**: Usa `base` (mejor balance)
- **Alta precisión**: Usa `large` (lento pero preciso)

## 🎵 Formatos de Audio Soportados

✅ MP3, WAV, M4A, OGG, FLAC, WEBM, MP4

El API valida automáticamente el formato del archivo.

## ⚙️ Arquitectura

### Diseño Asíncrono

```
Cliente → FastAPI → ThreadPoolExecutor → Whisper Model → Respuesta
            ↓                                ↓
      Validación                      Procesamiento CPU
      Background Tasks                 (en thread separado)
```

### Características Técnicas

1. **Procesamiento Asíncrono**: 
   - FastAPI maneja requests con `async/await`
   - Whisper corre en ThreadPoolExecutor (CPU-bound)
   - No bloquea el event loop

2. **Caché de Modelos**:
   - Modelo se carga una vez y se cachea
   - Peticiones subsecuentes son más rápidas
   - Ahorro de memoria y tiempo

3. **Background Tasks**:
   - Limpieza automática de archivos temporales
   - No requiere esperar a que termine la limpieza

4. **Timeout Configuration**:
   - Keep-alive: 300 segundos
   - Soporta archivos grandes sin timeout

## 🔧 Configuración Avanzada

### Python 3.14t (Free-Threaded)

Para mejor rendimiento con threads:

```bash
# Instalar Python 3.14t
uv python install 3.14t

# Crear entorno con 3.14t
uv venv --python 3.14t
source .venv/bin/activate

# Instalar dependencias
uv pip install -r requirements.txt
```

### Ajustar Workers

Edita `api.py` línea ~20:

```python
# Aumentar workers según tus cores de CPU
executor = ThreadPoolExecutor(max_workers=8)
```

Recomendación: `max_workers = número_de_cores - 1`

### Cambiar Puerto

```bash
# En api.py (línea ~250)
uvicorn.run(app, host="0.0.0.0", port=3000)

# O con uvicorn directamente
uvicorn api:app --port 3000
```

## 🧪 Testing

### 1. Test Automático
```bash
python test_api.py
```

### 2. Test con Audio Incluido
```bash
./test_with_audio.sh
```
Usa el archivo `Why_and_When_ReactJS.mp3` incluido en el proyecto.

### 3. Test con Interface Web
```bash
open test_client.html
# O doble click en el archivo
```

### 4. Tests con curl
```bash
# Ver ejemplos
cat examples.sh

# Ejecutar ejemplos
./examples.sh
```

## 📊 Rendimiento

### Primera Transcripción
- **Carga del modelo**: 10-30 segundos
- **Transcripción**: 10-60 segundos (según tamaño)
- **Total**: ~20-90 segundos

### Transcripciones Subsecuentes
- **Carga del modelo**: 0 segundos (cacheado)
- **Transcripción**: 10-60 segundos
- **Total**: ~10-60 segundos

### Por Modelo (audio de 5 minutos):

| Modelo | Tiempo Aprox. |
|--------|---------------|
| tiny | ~10-15 seg |
| base | ~15-25 seg |
| small | ~30-45 seg |
| medium | ~60-90 seg |
| large | ~120-180 seg |

*Tiempos en MacBook Pro M1/M2. Varían según hardware.*

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'whisper'"
```bash
source .venv/bin/activate
uv pip install openai-whisper
```

### Error: "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt update && sudo apt install ffmpeg

# Verificar instalación
ffmpeg -version
```

### Error: "Cannot connect to API"
```bash
# Verificar si el servidor está corriendo
curl http://localhost:8000/health

# Si no está corriendo, iniciarlo
python api.py
```

### Error: "Request timeout"
El archivo es muy grande. Opciones:
1. Usar modelo más pequeño (`tiny` o `base`)
2. Aumentar timeout en cliente
3. Partir el audio en partes más pequeñas

### Error: Out of Memory
```bash
# Usar modelo más pequeño
curl -X POST "http://localhost:8000/transcribe?model=tiny" -F "file=@audio.mp3"

# Cerrar otras aplicaciones
# Considerar usar swap/memoria virtual
```

## 📁 Estructura del Proyecto

```
apitranslate/
├── api.py                    # ⭐ API principal
├── pyproject.toml            # Configuración uv
├── requirements.txt          # Dependencias
├── .python-version           # Versión de Python
├── .gitignore               # Archivos a ignorar
│
├── readme.md                 # Documentación completa (inglés)
├── QUICKSTART.md            # Guía rápida (inglés)
├── PROYECTO_COMPLETADO.md   # Este archivo
├── LEEME.md                 # Documentación en español
│
├── start.sh                 # ⭐ Script para iniciar servidor
├── examples.sh              # Ejemplos de curl
├── test_api.py              # Tests en Python
├── test_with_audio.sh       # Test con audio incluido
└── test_client.html         # ⭐ Interface web
```

## 🎨 Interface Web (test_client.html)

Features:
- ✨ Diseño moderno y responsive
- 📤 Drag & drop de archivos
- 🎛️ Selector de modelos
- 📊 Visualización de resultados
- ⏱️ Segmentos con timestamps
- 📈 Indicador de progreso
- 🌐 CORS habilitado

## 💡 Mejores Prácticas

### 1. Elección del Modelo
```bash
# Para desarrollo y pruebas
model=tiny

# Para producción general
model=base

# Para audio con acentos o ruido
model=small

# Para máxima precisión
model=large
```

### 2. Optimización de Performance

```python
# En api.py, ajustar workers
executor = ThreadPoolExecutor(max_workers=cpu_count())

# Pre-cargar modelo al inicio
get_whisper_model("base")  # Se ejecuta al importar
```

### 3. Manejo de Archivos Grandes

```javascript
// Mostrar progreso al usuario
const formData = new FormData();
formData.append('file', largeFile);

// Indicar que puede tardar
showMessage('Procesando archivo grande, puede tardar varios minutos...');

const result = await fetch(url, {
    method: 'POST',
    body: formData
});
```

## 🔒 Seguridad

### Validaciones Implementadas
- ✅ Validación de formato de archivo
- ✅ Verificación de archivo no vacío
- ✅ Limpieza de archivos temporales
- ✅ Manejo de errores robusto
- ✅ Sin almacenamiento permanente

### Recomendaciones Adicionales
```python
# Limitar tamaño de archivo (agregar en api.py)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Limitar rate
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

## 🌐 Despliegue en Producción

### Usando Docker (Opcional)

```dockerfile
FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Usando systemd (Linux)

```ini
[Unit]
Description=Whisper API
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/apitranslate
ExecStart=/path/to/.venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Recursos Adicionales

### Documentación
- FastAPI: https://fastapi.tiangolo.com/
- OpenAI Whisper: https://github.com/openai/whisper
- uv: https://github.com/astral-sh/uv

### Documentación Interactiva
Una vez iniciado el servidor:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 Próximos Pasos

1. **Iniciar el servidor**:
   ```bash
   ./start.sh
   ```

2. **Probar con el archivo incluido**:
   ```bash
   ./test_with_audio.sh
   ```

3. **Abrir interface web**:
   ```bash
   open test_client.html
   ```

4. **Integrar en tu aplicación**:
   - Ver ejemplos en `examples.sh`
   - Ver código JavaScript en `test_client.html`
   - Ver código Python en `test_api.py`

## ✨ Características Destacadas

### Lo que hace especial esta implementación:

1. **Completamente Local**: Sin API keys, sin costos por uso
2. **Asíncrono Real**: No bloquea, usa threads correctamente
3. **Python 3.14t Ready**: Preparado para free-threaded Python
4. **Production Ready**: Manejo de errores, logging, cleanup
5. **Developer Friendly**: Múltiples ejemplos y documentación
6. **Beautiful UI**: Interface web moderna incluida
7. **Flexible**: Múltiples modelos, múltiples endpoints
8. **Fast**: Caché de modelos, optimizado para performance

## 🎉 Conclusión

Tienes una API completa, profesional y lista para usar que:
- ✅ Cumple todos los requisitos solicitados
- ✅ Incluye características adicionales útiles
- ✅ Tiene documentación completa
- ✅ Incluye ejemplos de uso
- ✅ Tiene herramientas de testing
- ✅ Es fácil de usar y extender

**¡A transcribir audio con IA! 🚀🎙️**

---

Para más información, consulta:
- `readme.md` - Documentación completa en inglés
- `QUICKSTART.md` - Guía rápida de inicio
- `PROYECTO_COMPLETADO.md` - Resumen de archivos creados


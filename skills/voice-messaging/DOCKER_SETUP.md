# Docker Setup for Voice Messaging

This guide covers setting up local STT (Speech-to-Text) and TTS (Text-to-Speech) endpoints using Docker for privacy and offline operation.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Kokoro TTS Setup](#kokoro-tts-setup)
- [Whisper STT Setup](#whisper-stt-setup)
- [Qwen3 TTS Setup](#qwen3-tts-setup)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

---

## Prerequisites

- Docker installed and running
- NVIDIA GPU (optional, but recommended for performance)
- NVIDIA Container Toolkit (for GPU support)
- 8GB+ RAM minimum
- 20GB+ disk space

### Install NVIDIA Container Toolkit (for GPU support)

**Linux:**

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Windows/macOS:**

Docker Desktop with WSL2 (Windows) or Docker Desktop for Mac includes GPU support automatically.

### Verify GPU Access

```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

If you see GPU information, you're ready to go!

---

## Kokoro TTS Setup

Kokoro is a production-quality text-to-speech engine with excellent voice quality and low latency.

### Quick Start

```bash
# Pull the image
docker pull ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Run with GPU
docker run -d \
  --name kokoro-tts \
  --gpus all \
  -p 8880:8880 \
  --restart unless-stopped \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Run without GPU (slower)
docker run -d \
  --name kokoro-tts \
  -p 8880:8880 \
  --restart unless-stopped \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
```

### Verify Installation

```bash
# Check if container is running
docker ps | grep kokoro

# Test the endpoint
curl http://localhost:8880/v1/health

# Test TTS generation
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test of the Kokoro TTS system.",
    "voice": "af_bella",
    "response_format": "ogg"
  }' \
  --output test.ogg

# Play the test file
# Linux/macOS: play test.ogg
# Windows: start test.ogg
```

### Available Voices

Kokoro provides 10 high-quality voices:

| Voice ID | Gender | Accent | Description |
|----------|--------|--------|-------------|
| af_bella | Female | American | Warm, friendly (default) |
| af_heart | Female | American | Soft, caring |
| af_sky | Female | American | Clear, professional |
| af_michael | Female | American | Calm, neutral |
| am_michael | Male | American | Deep, authoritative |
| bm_george | Male | British | Sophisticated, formal |
| bm_lewis | Male | British | Energetic, casual |
| bf_emma | Female | British | Elegant, refined |
| bf_isabella | Female | American | Expressive, dynamic |

### Configuration

Update `config.toml`:

```toml
[tts]
provider = "kokoro"
base_url = "http://localhost:8880/v1"
voice = "af_bella"
format = "ogg"
speed = 1.0
```

### Advanced Options

#### Custom Port

```bash
docker run -d \
  --name kokoro-tts \
  --gpus all \
  -p 8881:8880 \  # Use port 8881 on host
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
```

Then update `config.toml`:

```toml
base_url = "http://localhost:8881/v1"
```

#### Resource Limits

```bash
docker run -d \
  --name kokoro-tts \
  --gpus all \
  -p 8880:8880 \
  --memory="4g" \
  --cpus="2.0" \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
```

---

## Whisper STT Setup

For a Docker-based Whisper STT endpoint, you can use the official faster-whisper container or build your own.

### Option 1: Using faster-whisper Docker Image

```bash
# Pull the image
docker pull guillaumekln/faster-whisper-server

# Run with GPU
docker run -d \
  --name whisper-stt \
  --gpus all \
  -p 8000:8000 \
  -e MODEL_NAME=base \
  -e COMPUTE_TYPE=int8 \
  --restart unless-stopped \
  guillaumekln/faster-whisper-server

# Run without GPU (slower)
docker run -d \
  --name whisper-stt \
  -p 8000:8000 \
  -e MODEL_NAME=base \
  -e COMPUTE_TYPE=int8 \
  --restart unless-stopped \
  guillaumekln/faster-whisper-server
```

### Option 2: Build Custom Whisper Server

Create a `Dockerfile.whisper`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    faster-whisper==1.0.3 \
    flask==3.0.0 \
    pydub==0.25.1

# Copy server code
COPY whisper_server.py /app/

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "whisper_server.py"]
```

Create `whisper_server.py`:

```python
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os

app = Flask(__name__)

# Load model
model_size = os.getenv("MODEL_SIZE", "base")
compute_type = os.getenv("COMPUTE_TYPE", "int8")
device = os.getenv("DEVICE", "cpu")

model = WhisperModel(
    model_size,
    device=device,
    compute_type=compute_type
)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": model_size})

@app.route("/v1/audio/transcriptions", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    audio_path = f"/tmp/{file.filename}"
    file.save(audio_path)

    # Transcribe
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        language=request.form.get("language")
    )

    text = " ".join([segment.text for segment in segments])

    # Cleanup
    os.remove(audio_path)

    return jsonify({
        "text": text,
        "language": info.language,
        "duration": info.duration
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Build and run:

```bash
# Build image
docker build -f Dockerfile.whisper -t whisper-server .

# Run with GPU
docker run -d \
  --name whisper-stt \
  --gpus all \
  -p 8000:8000 \
  -e MODEL_SIZE=base \
  -e COMPUTE_TYPE=int8 \
  -e DEVICE=cuda \
  --restart unless-stopped \
  whisper-server

# Run without GPU
docker run -d \
  --name whisper-stt \
  -p 8000:8000 \
  -e MODEL_SIZE=base \
  -e COMPUTE_TYPE=int8 \
  -e DEVICE=cpu \
  --restart unless-stopped \
  whisper-server
```

### Verify Installation

```bash
# Check if container is running
docker ps | grep whisper

# Test the endpoint
curl http://localhost:8000/health

# Test transcription
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test_audio.wav" \
  -F "language=en"
```

### Configuration

Update `config.toml`:

```toml
[stt]
provider = "faster-whisper"
base_url = "http://localhost:8000"
model = "base"
device = "cpu"
```

### Model Sizes

| Model | Size | RAM | VRAM (GPU) | Speed | Accuracy |
|-------|------|-----|------------|-------|----------|
| tiny | 39 MB | 1 GB | 0.5 GB | 32x | Low |
| base | 74 MB | 1 GB | 0.5 GB | 16x | Medium |
| small | 244 MB | 2 GB | 1 GB | 6x | Good |
| medium | 769 MB | 5 GB | 2 GB | 2x | High |
| large-v3 | 1550 MB | 10 GB | 5 GB | 1x | Best |

**Recommendation:** Use `base` for CPU, `small` or `medium` for GPU.

---

## Qwen3 TTS Setup

Qwen3 offers high-quality TTS with customizable voices.

### Quick Start

```bash
# Pull the image
docker pull qwen3-tts-openai-fastapi-qwen3-tts-gpu

# Run with GPU
docker run -d \
  --name qwen3-tts \
  --gpus all \
  -p 8890:8000 \
  --restart unless-stopped \
  qwen3-tts-openai-fastapi-qwen3-tts-gpu

# Run without GPU (slower)
docker run -d \
  --name qwen3-tts \
  -p 8890:8000 \
  --restart unless-stopped \
  qwen3-tts-openai-fastapi-qwen3-tts-gpu
```

### Verify Installation

```bash
# Check if container is running
docker ps | grep qwen3

# Test the endpoint
curl http://localhost:8890/health

# Test TTS generation
curl -X POST http://localhost:8890/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test of the Qwen3 TTS system.",
    "voice": "default",
    "response_format": "wav"
  }' \
  --output test.wav
```

### Configuration

Update `config.toml`:

```toml
[tts]
provider = "qwen3"
base_url = "http://localhost:8890"
voice = "default"
format = "wav"
speed = 1.0
```

---

## Troubleshooting

### Container Won't Start

**Symptom:** Docker exits immediately

**Solution:**

```bash
# Check logs
docker logs kokoro-tts

# Common issues:
# 1. GPU not available -> Remove --gpus all
# 2. Port already in use -> Change -p 8880:8880 to -p 8881:8880
# 3. Out of memory -> Add --memory="4g"
```

### GPU Not Detected

**Symptom:** "CUDA not available" error

**Solution:**

```bash
# Verify GPU is available
nvidia-smi

# Verify Docker can see GPU
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# If not working, install NVIDIA Container Toolkit (see Prerequisites)
```

### Endpoint Not Responding

**Symptom:** Connection refused or timeout

**Solution:**

```bash
# Check if container is running
docker ps | grep kokoro

# Restart container
docker restart kokoro-tts

# Check port is accessible
netstat -an | grep 8880

# Test from inside container
docker exec kokoro-tts curl http://localhost:8880/v1/health
```

### Out of Memory

**Symptom:** Container crashes with OOM error

**Solution:**

```bash
# Stop container
docker stop kokoro-tts

# Run with memory limit
docker run -d \
  --name kokoro-tts \
  --gpus all \
  -p 8880:8880 \
  --memory="4g" \
  --memory-swap="4g" \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Or use smaller model (for Whisper)
MODEL_SIZE=tiny
```

### Slow Performance

**Symptom:** High latency on CPU

**Solutions:**

1. **Use smaller model:**
   ```toml
   model = "tiny"  # Instead of base or small
   ```

2. **Enable quantization:**
   ```toml
   compute_type = "int8"  # Instead of float16
   ```

3. **Use GPU if available:**
   ```bash
   docker run --gpus all ...
   ```

4. **Adjust worker count:**
   ```bash
   docker run -e WORKERS=2 ...
   ```

---

## Performance Optimization

### GPU Acceleration

Using a GPU can dramatically improve performance:

| Task | CPU (base) | GPU (base) | Speedup |
|------|------------|------------|---------|
| Whisper STT | 10-15s | 0.5s | 20-30x |
| Kokoro TTS | 1-3s | 0.3s | 3-10x |

### Memory Optimization

```bash
# Limit memory usage
docker run --memory="4g" --cpus="2.0" ...

# Use int8 quantization (faster, slightly less accurate)
COMPUTE_TYPE=int8
```

### Caching

Both Whisper and Kokoro cache models after first download:

```bash
# Set cache location
docker run -v /path/to/cache:/cache ...

# For Whisper
export HF_HUB_CACHE=/path/to/cache
```

---

## Security Considerations

### Network Isolation

```bash
# Run in isolated network
docker network create voice-network
docker run --network=voice-network ...

# Use firewall to restrict access
sudo ufw allow from 127.0.0.1 to any port 8880
```

### Resource Limits

```bash
# Prevent resource abuse
docker run \
  --memory="4g" \
  --cpus="2.0" \
  --pids-limit 100 \
  ...
```

### Updates

```bash
# Regularly update images
docker pull ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
docker stop kokoro-tts
docker rm kokoro-tts
docker run ...  # Same as before
```

---

## Quick Reference

### Start All Services

```bash
# Kokoro TTS
docker start kokoro-tts || docker run -d --name kokoro-tts --gpus all -p 8880:8880 ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Whisper STT
docker start whisper-stt || docker run -d --name whisper-stt --gpus all -p 8000:8000 guillaumekln/faster-whisper-server

# Qwen3 TTS
docker start qwen3-tts || docker run -d --name qwen3-tts --gpus all -p 8890:8000 qwen3-tts-openai-fastapi-qwen3-tts-gpu
```

### Check Status

```bash
docker ps --filter "name=kokoro"
docker ps --filter "name=whisper"
docker ps --filter "name=qwen3"
```

### View Logs

```bash
docker logs -f kokoro-tts
docker logs -f whisper-stt
docker logs -f qwen3-tts
```

### Stop All Services

```bash
docker stop kokoro-tts whisper-stt qwen3-tts
```

---

**Need help?** Check the [main README](README.md) for more information.

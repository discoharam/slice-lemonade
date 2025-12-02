# runpod/Dockerfile - SIMPLE VERSION
FROM pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    demucs==4.0.0 \
    runpod==0.10.0 \
    soundfile==0.12.1 \
    numpy==1.24.3 \
    scipy==1.11.4

# Copy handler
COPY handler.py .

# Run the handler
CMD ["python", "-u", "handler.py"]

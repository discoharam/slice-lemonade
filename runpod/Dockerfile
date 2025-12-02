# Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set Python version
ENV PYTHON_VERSION=3.10
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific versions
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir \
    runpod==0.10.0 \
    torch==2.0.1 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install Demucs and audio processing libraries
RUN pip3 install --no-cache-dir \
    demucs==4.0.0 \
    soundfile \
    numpy \
    scipy

# Copy handler
COPY handler.py .

# Test that Demucs loads
RUN python3 -c "import demucs.api; import torch; print('✅ Demucs loaded successfully'); print(f'✅ CUDA available: {torch.cuda.is_available()}')"

# Start the handler
CMD ["python3", "-u", "handler.py"]

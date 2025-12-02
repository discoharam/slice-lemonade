# Optimized Dockerfile for Demucs + RunPod
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies with cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    git \
    wget \
    ffmpeg \
    libsndfile1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies with specific versions
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch with CUDA 11.8
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Test PyTorch import (without CUDA check during build)
RUN python3 -c "import torch; print('✅ PyTorch', torch.__version__, 'imported successfully')"

# Install Demucs and other dependencies
RUN pip3 install --no-cache-dir \
    demucs==4.0.0 \
    soundfile==0.12.1 \
    numpy==1.24.3 \
    scipy==1.11.4 \
    runpod==0.10.0

# Copy handler
COPY handler.py .

# Test that Demucs loads (without GPU during build)
RUN python3 -c "import demucs.api; print('✅ Demucs loaded successfully')"

# Expose port (optional for RunPod serverless)
EXPOSE 8000

# Run the handler
CMD ["python3", "-u", "handler.py"]

# Dockerfile - SIMPLIFIED WORKING VERSION
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    libsndfile1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch with CUDA 11.8
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies first
RUN pip3 install --no-cache-dir \
    numpy==1.24.3 \
    scipy==1.11.4 \
    soundfile==0.12.1

# Install Demucs from GitHub (latest stable)
RUN pip3 install --no-cache-dir \
    demucs

# Install RunPod
RUN pip3 install --no-cache-dir runpod==0.10.0

# Copy handler
COPY handler.py .

# Simple test - just check Python works
RUN python3 -c "print('✅ Python environment ready')"

# Run the handler
CMD ["python3", "-u", "handler.py"]

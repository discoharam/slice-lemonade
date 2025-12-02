# runpod/Dockerfile
FROM runpod/base:0.4.0-cuda11.8.0

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --upgrade pip

# Install PyTorch with CUDA 11.8 (compatible with RunPod)
RUN pip3 install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118

# Install Demucs and dependencies
RUN pip3 install \
    demucs==4.0.0 \
    numpy==1.24.3 \
    scipy==1.11.4 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    requests==2.31.0

# Create directory for models
RUN mkdir -p /workspace/models

# Copy handler
COPY handler.py /workspace/handler.py

# Set environment variables
ENV PYTHONPATH=/workspace
ENV DEMUCS_MODELS=/workspace/models
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Run the handler
CMD ["python3", "/workspace/handler.py"]

# runpod/Dockerfile - OPTIMIZED VERSION
FROM runpod/base:0.4.0-cuda11.8.0

# Set working directory
WORKDIR /workspace

# Clean up any unnecessary files first
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with NO CACHE to save space
RUN pip3 install --no-cache-dir --upgrade pip

# Install PyTorch with CUDA 11.8 - MINIMAL VERSION
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Install only essential Demucs dependencies
RUN pip3 install --no-cache-dir \
    demucs==4.0.0 \
    numpy==1.24.3 \
    soundfile==0.12.1

# Clean up pip cache
RUN rm -rf ~/.cache/pip/*

# Create directory for models
RUN mkdir -p /workspace/models

# Copy handler
COPY handler.py /workspace/handler.py

# Set environment variables
ENV PYTHONPATH=/workspace
ENV DEMUCS_MODELS=/workspace/models
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ENV PYTHONUNBUFFERED=1

# Run the handler
CMD ["python3", "/workspace/handler.py"]

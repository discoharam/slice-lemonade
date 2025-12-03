FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    libsox-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir \
    runpod==1.4.0 \
    demucs==4.0.0 \
    scipy==1.11.4 \
    numpy==1.24.3 \
    torchaudio==2.1.0 \
    sox==1.4.1

# Verify demucs installation
RUN python -c "import demucs; print(f'Demucs version: {demucs.__version__}')"

# Copy handler code
COPY handler.py .

# Set working directory
WORKDIR /workspace

# Run the handler
CMD ["python", "-u", "handler.py"]
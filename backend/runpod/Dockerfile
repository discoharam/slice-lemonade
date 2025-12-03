FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Install dependencies in one go to avoid prompts
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    libsox-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    runpod==1.4.0 \
    demucs==4.0.0 \
    scipy==1.11.4 \
    numpy==1.24.3

# Copy handler
COPY handler.py .

# Run
CMD ["python", "-u", "handler.py"]

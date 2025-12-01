FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python 3.10 and dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-venv \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy handler
COPY handler.py .

# Set environment variable for Demucs to use CUDA
ENV DEMUCS_CUDA=1

CMD ["python", "-u", "handler.py"]

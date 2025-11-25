FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler code
COPY handler.py .

# Pre-download Demucs models
RUN python -c "import demucs.api; print('Pre-loading Demucs model...'); demucs.api.Separator(model='htdemucs', device='cuda')"

CMD ["python", "-u", "handler.py"]
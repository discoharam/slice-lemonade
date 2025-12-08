FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC PYTHONUNBUFFERED=1 TRANSFORMERS_CACHE=/root/.cache/huggingface
WORKDIR /workspace
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl git libsox-dev sox libavcodec-extra python3-dev build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge
RUN mkdir -p /tmp/audio_processing /root/.cache/torch/hub/checkpoints
COPY handler.py .
RUN useradd -m -u 1000 worker && chown -R worker:worker /tmp/audio_processing /root/.cache
USER worker
EXPOSE 8000
CMD ["python", "-u", "handler.py"]
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface
ENV TORCH_HOME=/root/.cache/torch
WORKDIR /workspace
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl git libsox-dev sox libavcodec-extra python3-dev build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge
RUN mkdir -p /root/.cache/torch/hub/checkpoints /root/.cache/huggingface
COPY handler.py .
RUN useradd -m -u 1000 worker && chown -R worker:worker /workspace /root/.cache
USER worker
EXPOSE 8000
CMD ["python", "-u", "handler.py"]

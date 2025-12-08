# File: runpod/Dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface
ENV TORCH_HOME=/tmp/torch
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
WORKDIR /workspace
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl git libsox-dev sox libavcodec-extra python3-dev build-essential ca-certificates && apt-get clean && rm -rf /var/lib/apt/lists/* && update-ca-certificates
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt certifi && pip cache purge
RUN mkdir -p /tmp/torch/hub/checkpoints /tmp/huggingface
COPY handler.py .
RUN useradd -m -u 1000 worker && chown -R worker:worker /workspace
USER worker
EXPOSE 8000
CMD ["python", "-u", "handler.py"]
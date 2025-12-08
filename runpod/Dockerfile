# runpod/Dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/workspace/huggingface \
    TORCH_HOME=/workspace/models \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 git curl libsox-dev sox ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge

RUN mkdir -p /workspace/models /workspace/huggingface

COPY download_model.py .
RUN python download_model.py

COPY handler.py .

RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /workspace

USER worker

EXPOSE 8000
CMD ["python", "-u", "handler.py"]

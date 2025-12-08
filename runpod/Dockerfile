FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface
ENV TORCH_HOME=/root/.cache/torch
WORKDIR /workspace
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl git libsox-dev sox libavcodec-extra python3-dev build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge
RUN mkdir -p /root/.cache/torch/hub/checkpoints /root/.cache/huggingface
# PRE-DOWNLOAD AND CACHE THE MODEL
RUN python -c "
import torch
from demucs.pretrained import get_model
print('Pre-downloading Demucs model...')
try:
    model = get_model('htdemucs')
    print('? Model pre-downloaded successfully')
    # Test model loading
    if torch.cuda.is_available():
        model.cuda().eval()
        print('? GPU available, model moved to GPU')
    else:
        model.cpu().eval()
        print('? Using CPU')
except Exception as e:
    print(f'?? Pre-download failed: {e}')
    print('Model will download at runtime')
"
COPY handler.py .
RUN useradd -m -u 1000 worker && chown -R worker:worker /workspace /root/.cache
USER worker
EXPOSE 8000
CMD ["python", "-u", "handler.py"]

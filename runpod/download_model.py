# runpod/download_model.py
import torch,os
print("--- Pre-caching Demucs htdemucs model ---")
os.environ['TORCH_HOME']='/tmp/torch'
try:
    torch.hub.load_extended('facebookresearch/demucs', 'htdemucs')
    print("✅ Model downloaded and cached successfully.")
except Exception as e:
    print(f"❌ Failed to download model: {e}")
    exit(1)

# runpod/download_model.py
import os
import sys

# Explicitly set cache to workspace
os.environ['TORCH_HOME'] = '/workspace/models'

print(f"🏗️ STARTING MODEL PRE-CACHE to {os.environ['TORCH_HOME']}...")

try:
    from demucs.pretrained import get_model
    
    print("⬇️ Downloading htdemucs model...")
    model = get_model('htdemucs')
    
    print("✅ Model downloaded and cached successfully.")
    
except Exception as e:
    print(f"❌ FATAL: Model download failed: {e}")
    sys.exit(1)

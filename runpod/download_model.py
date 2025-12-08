# runpod/download_model.py
import os
import sys

# Ensure cache directory matches handler and Dockerfile
os.environ['TORCH_HOME'] = '/tmp/torch'

print("🏗️ STARTING MODEL PRE-CACHE...")

try:
    # Use the official Demucs API to trigger the download
    # This ensures the model is cached exactly where the handler expects it
    from demucs.pretrained import get_model
    
    print("⬇️ Downloading htdemucs model...")
    # This call downloads the model files to /tmp/torch/hub/checkpoints
    model = get_model('htdemucs')
    
    print("✅ Model downloaded and cached successfully.")
    
except Exception as e:
    print(f"❌ FATAL: Model download failed: {e}")
    # Print full traceback to see exactly what went wrong in the build logs
    import traceback
    traceback.print_exc()
    sys.exit(1)

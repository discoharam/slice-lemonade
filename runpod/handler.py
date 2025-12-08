# runpod/handler.py
import sys, traceback, os

try:
    import runpod, torch, base64, tempfile, subprocess
    import soundfile as sf, numpy as np
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
except Exception as e:
    print(f"❌ IMPORTS FAILED: {e}")
    sys.exit(1)

# --- Global State ---
model = None
device = None
CACHE_DIR = '/workspace/models'

def load_model_safe():
    """Attempts to load the model with explicit pathing and error logging."""
    global model, device
    print(f"🏗️ Attempting to load model from {CACHE_DIR}...")
    
    # Force environment variable
    os.environ['TORCH_HOME'] = CACHE_DIR
    
    # Debug: Check if files exist
    try:
        if os.path.exists(CACHE_DIR):
            print(f"📂 Cache contents: {os.listdir(CACHE_DIR)}")
            hub_dir = os.path.join(CACHE_DIR, 'hub')
            if os.path.exists(hub_dir):
                print(f"📂 Hub contents: {os.listdir(hub_dir)}")
        else:
            print("⚠️ Cache directory not found!")
    except: pass

    try:
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Loading htdemucs on {dev}...")
        
        # Load model
        loaded_model = get_model('htdemucs')
        loaded_model.to(dev).eval()
        
        print("✅ Model successfully loaded into memory.")
        return loaded_model, dev
    except Exception as e:
        print(f"❌ FATAL: Model load failed: {e}")
        traceback.print_exc()
        return None, None

def init():
    """Called by RunPod on cold start."""
    global model, device
    model, device = load_model_safe()
    if model is None:
        return {"status": "error", "details": "Model failed to load in init"}
    return {"status": "ready"}

def handler(job):
    """Handle separation job with fallback loading."""
    global model, device
    
    # --- Fallback: Lazy load if init failed ---
    if model is None:
        print("⚠️ Model was None in handler. Attempting lazy load...")
        model, device = load_model_safe()
        
    if model is None:
        print("❌ Error: Model is still None after fallback.")
        return {"error": "RunPod failed: Model could not be loaded on worker."}

    print(f"--> Processing Job: {job.get('id')}")
    tmpdir = None
    
    try:
        job_input = job.get("input", {})
        audio_base64 = job_input.get("audio_data", "")
        if not audio_base64: return {"error": "No audio_data provided"}

        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, "input.wav")
        
        with open(input_path, 'wb') as f:
            f.write(base64.b64decode(audio_base64))
            
        audio, sr = sf.read(input_path)
        if len(audio.shape) == 1: audio = np.stack([audio, audio], axis=0)
        audio = torch.from_numpy(audio).float()
        
        if sr != 44100:
            import torchaudio
            audio = torchaudio.functional.resample(audio, sr, 44100)
            
        # Processing
        with torch.no_grad():
            stems = apply_model(model, audio[None], device=device, shifts=1, split=True, overlap=0.25)[0]
            
        stems_dict = {}
        for i, name in enumerate(['vocals', 'drums', 'bass', 'other']):
            if i < len(stems):
                stem_path = os.path.join(tmpdir, f"{name}.wav")
                sf.write(stem_path, stems[i].cpu().numpy().T, 44100)
                mp3_path = os.path.join(tmpdir, f"{name}.mp3")
                subprocess.run(['ffmpeg', '-y', '-i', stem_path, '-codec:a', 'libmp3lame', '-b:a', '320k', '-q:a', '0', mp3_path], check=True, capture_output=True)
                with open(mp3_path, 'rb') as f:
                    stems_dict[name] = base64.b64encode(f.read()).decode()
                    
        return {"stems": stems_dict, "status": "completed"}
        
    except Exception as e:
        print(f"❌ Handler Error: {e}")
        traceback.print_exc()
        return {"error": f"Processing exception: {str(e)}"}
    finally:
        if tmpdir and os.path.exists(tmpdir):
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler, "init": init})

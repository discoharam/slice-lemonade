# runpod/handler.py
import runpod,torch,base64,tempfile,os,subprocess,time,json,sys
import soundfile as sf,numpy as np
from demucs.pretrained import get_model
from demucs.apply import apply_model

# Global model variable
model = None
device = None

def init():
    """Initialize worker and load pre-cached model."""
    global model, device
    print("===> Slice Lemonade Worker: Initializing...")
    
    os.environ['TORCH_HOME'] = '/tmp/torch'
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading htdemucs on {device}...")
    try:
        # This will now load instantly from the Docker image cache
        model = get_model('htdemucs')
        model.to(device).eval()
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Init failed: {e}")
        return {"error": str(e)}
        
    return {"status": "ready"}

def handler(job):
    global model, device
    if model is None: return {"error": "Model not loaded"}
    
    print(f"--> Job: {job.get('id')}")
    tmpdir = None
    try:
        job_input = job.get("input", {})
        audio_base64 = job_input.get("audio_data", "")
        if not audio_base64: return {"error": "No audio_data"}

        tmpdir = tempfile.mkdtemp(dir="/tmp")
        input_path = os.path.join(tmpdir, "input.wav")
        
        with open(input_path, 'wb') as f:
            f.write(base64.b64decode(audio_base64))
            
        audio, sr = sf.read(input_path)
        if len(audio.shape) == 1: audio = np.stack([audio, audio], axis=0)
        audio = torch.from_numpy(audio).float()
        
        if sr != 44100:
            import torchaudio
            audio = torchaudio.functional.resample(audio, sr, 44100)
            
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
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        if tmpdir and os.path.exists(tmpdir):
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler, "init": init})

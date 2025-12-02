import runpod
import torch
import base64
import tempfile
import os
import io
import json
import numpy as np
from scipy.io import wavfile

print("🚀 Slice Lemonade Demucs Handler - REAL GPU SEPARATION")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Import Demucs with error handling
try:
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import torchaudio
    DEMUCS_AVAILABLE = True
    print("✅ Demucs imported successfully")
except ImportError as e:
    print(f"❌ Demucs import error: {e}")
    DEMUCS_AVAILABLE = False

def handler(job):
    """Audio separation handler"""
    if not DEMUCS_AVAILABLE:
        return {
            "error": "Demucs not installed properly",
            "status": "error",
            "debug": "Check demucs installation in Dockerfile"
        }
    
    try:
        job_input = job.get("input", {})
        
        # Get audio data
        audio_base64 = job_input.get("audio_data", "")
        filename = job_input.get("file_name", "audio.wav")
        
        if not audio_base64:
            return {"error": "No audio data", "status": "error"}
        
        print(f"📦 Processing {filename}")
        
        # Decode
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            input_path = tmp.name
        
        try:
            print("🤖 Loading Demucs model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            model = get_model('htdemucs')
            model.to(device)
            model.eval()
            
            # Load audio
            wav, sr = torchaudio.load(input_path)
            
            # Convert to mono if stereo
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
            
            # Resample to 44100 Hz
            if sr != 44100:
                wav = torchaudio.functional.resample(wav, sr, 44100)
            
            # Normalize
            max_val = wav.abs().max()
            if max_val > 0:
                wav = wav / max_val
            
            # Separate
            print("⚡ Separating audio...")
            with torch.no_grad():
                sources = apply_model(model, wav[None], device=device)[0]
            
            # Prepare results
            stems = ['drums', 'bass', 'other', 'vocals']
            results = {}
            
            for idx, stem_name in enumerate(stems):
                if idx < sources.shape[0]:
                    stem_wav = sources[idx].cpu().numpy()
                    stem_wav_int16 = np.clip(stem_wav * 32767, -32768, 32767).astype(np.int16)
                    
                    bytes_io = io.BytesIO()
                    wavfile.write(bytes_io, 44100, stem_wav_int16.T)
                    audio_bytes = bytes_io.getvalue()
                    
                    results[stem_name] = base64.b64encode(audio_bytes).decode('utf-8')
                    print(f"✅ {stem_name}: {len(results[stem_name])} chars")
            
            # Clean up
            os.unlink(input_path)
            
            if not results:
                return {"error": "No stems generated", "status": "error"}
            
            print(f"🎉 Success! {len(results)} stems")
            return {
                "status": "success",
                "message": "Demucs separation completed",
                "stems": list(results.keys()),
                **results
            }
            
        except Exception as e:
            print(f"❌ Separation error: {str(e)}")
            return {"error": f"Separation failed: {str(e)}", "status": "error"}
            
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")
        return {"error": f"Handler error: {str(e)}", "status": "error"}

# Start handler
if __name__ == "__main__":
    if DEMUCS_AVAILABLE:
        print("✅ Handler ready for GPU separation")
        runpod.serverless.start({"handler": handler})
    else:
        print("❌ Demucs not available")
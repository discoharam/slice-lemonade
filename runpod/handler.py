# runpod/handler.py
import runpod
import tempfile
import base64
import traceback

print("🚀 Slice Lemonade Handler")

# Load Demucs
try:
    import torch
    print(f"✅ PyTorch {torch.__version__}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"✅ Using device: {device}")
    
    import demucs.api
    separator = demucs.api.Separator(device=device)
    print("✅ Demucs loaded")
except Exception as e:
    print(f"❌ Error: {e}")
    separator = None

def handler(job):
    print(f"\n🎯 Processing job")
    
    try:
        input_data = job.get("input", {})
        audio_data = input_data.get("audio_data")
        
        if not audio_data:
            return {"error": "No audio_data", "status": "error"}
        
        if separator is None:
            return {"error": "Demucs not loaded", "status": "error"}
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_data)
        print(f"📊 Audio size: {len(audio_bytes)} bytes")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            print("🔬 Separating...")
            _, separated = separator.separate_audio_file(temp_path)
            
            results = {}
            for source, audio in separated.items():
                try:
                    import io
                    from scipy.io.wavfile import write
                    import numpy as np
                    
                    # Convert and save
                    audio_np = audio.numpy()
                    buffer = io.BytesIO()
                    write(buffer, separator.samplerate, audio_np.T)
                    buffer.seek(0)
                    
                    stem_bytes = buffer.read()
                    results[source] = base64.b64encode(stem_bytes).decode('utf-8')
                    print(f"✅ {source}: {len(stem_bytes)} bytes")
                except Exception as e:
                    print(f"⚠️ {source} error: {e}")
                    continue
            
            if results:
                return {
                    "status": "success",
                    "results": results,
                    "message": f"Separated {len(results)} stems"
                }
            else:
                return {"error": "No stems", "status": "error"}
                
        finally:
            import os
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"❌ Handler error: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("\n🍋 Handler ready")
    runpod.serverless.start({"handler": handler})

# handler.py - OPTIMIZED FOR RUNPOD
import runpod
import os
import tempfile
import base64
import traceback
import sys

print("=" * 60)
print("🚀 Slice Lemonade - Real Demucs Handler")
print(f"🐍 Python {sys.version}")
print("=" * 60)

# Try to load Demucs
separator = None
try:
    print("🎵 Loading PyTorch...")
    import torch
    print(f"✅ PyTorch {torch.__version__} loaded")
    
    if torch.cuda.is_available():
        print(f"🎮 CUDA available on {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️ CUDA not available, using CPU")
        device = "cpu"
    
    print("🎵 Loading Demucs...")
    import demucs.api
    
    separator = demucs.api.Separator(
        model="htdemucs", 
        device=device,
        progress=True,
        shifts=1,
        split=True,
        overlap=0.25
    )
    print("✅ Demucs loaded successfully!")
    
except Exception as e:
    print(f"❌ Failed to load Demucs: {str(e)}")
    traceback.print_exc()

def handler(job):
    """Handle audio separation"""
    print(f"\n🎯 Processing job")
    
    try:
        input_data = job.get("input", {})
        audio_data = input_data.get("audio_data")
        file_name = input_data.get("file_name", "audio.wav")
        
        if not audio_data:
            return {"error": "No audio_data provided", "status": "error"}
        
        print(f"📁 File: {file_name}")
        
        # Decode base64
        try:
            audio_bytes = base64.b64decode(audio_data)
            print(f"📦 Audio size: {len(audio_bytes)} bytes")
        except:
            return {"error": "Invalid base64 audio", "status": "error"}
        
        if separator is None:
            return {"error": "Demucs not loaded", "status": "error"}
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            print("🔬 Separating audio...")
            _, separated = separator.separate_audio_file(temp_path)
            print(f"✅ Got {len(separated)} stems")
            
            # Process stems
            results = {}
            import io
            import numpy as np
            from scipy.io.wavfile import write as write_wav
            
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                # Convert to numpy
                audio_np = audio.numpy()
                
                # Handle shape
                if audio_np.ndim == 1:
                    audio_np = audio_np.reshape(1, -1)
                
                # Save to buffer
                buffer = io.BytesIO()
                write_wav(buffer, separator.samplerate, audio_np.T)
                buffer.seek(0)
                
                stem_bytes = buffer.read()
                results[source] = base64.b64encode(stem_bytes).decode('utf-8')
                print(f"✅ {source}: {len(stem_bytes)} bytes")
            
            return {
                "status": "success",
                "results": results,
                "message": f"Separated {len(results)} stems"
            }
            
        finally:
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"status": "error", "error": error_msg}

if __name__ == "__main__":
    print(f"\n🍋 Slice Lemonade Handler Ready")
    print(f"📊 Demucs loaded: {separator is not None}")
    if separator is not None:
        print(f"⚡ Device: {separator.device}")
    print("📡 Waiting for jobs...")
    runpod.serverless.start({"handler": handler})

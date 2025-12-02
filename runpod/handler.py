# handler.py - SIMPLIFIED VERSION
import runpod
import os
import tempfile
import base64
import traceback
import sys

print("=" * 60)
print("🚀 Slice Lemonade - Demucs Handler")
print("=" * 60)

# Import torch first
try:
    import torch
    print(f"✅ PyTorch {torch.__version__} loaded")
    if torch.cuda.is_available():
        print(f"🎮 CUDA available: {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️ CUDA not available, using CPU")
        device = "cpu"
except Exception as e:
    print(f"❌ Failed to load PyTorch: {e}")
    device = "cpu"

# Try to load Demucs
separator = None
try:
    import demucs.api
    print("🎵 Loading Demucs...")
    
    separator = demucs.api.Separator(
        model="htdemucs", 
        device=device,
        progress=True
    )
    print("✅ Demucs loaded successfully!")
    
    # Quick test
    import torch
    test_audio = torch.randn(2, 44100)  # 1 second of audio
    _ = separator.separate(test_audio)
    print("✅ Demucs test passed!")
    
except Exception as e:
    print(f"❌ Failed to initialize Demucs: {e}")
    traceback.print_exc()

def handler(job):
    """Handle audio separation"""
    print(f"\n🎯 Starting job: {job.get('id', 'unknown')}")
    
    try:
        input_data = job.get("input", {})
        audio_data = input_data.get("audio_data")
        file_name = input_data.get("file_name", "audio.wav")
        
        if not audio_data:
            return {"error": "No audio_data provided", "status": "error"}
        
        print(f"📁 File: {file_name}")
        
        # Decode audio
        try:
            audio_bytes = base64.b64decode(audio_data)
            print(f"📊 Size: {len(audio_bytes)} bytes")
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
            for source, audio in separated.items():
                try:
                    import io
                    from scipy.io.wavfile import write as write_wav
                    import numpy as np
                    
                    # Convert to numpy
                    audio_np = audio.numpy()
                    
                    # Ensure correct shape
                    if audio_np.ndim == 1:
                        audio_np = audio_np.reshape(1, -1)
                    
                    # Scale to int16
                    audio_np = (audio_np * 32767).astype(np.int16)
                    
                    # Save to buffer
                    buffer = io.BytesIO()
                    write_wav(buffer, separator.samplerate, audio_np.T)
                    buffer.seek(0)
                    
                    # Encode
                    stem_bytes = buffer.read()
                    results[source] = base64.b64encode(stem_bytes).decode('utf-8')
                    
                    print(f"✅ {source}: {len(stem_bytes)} bytes")
                    
                except Exception as e:
                    print(f"⚠️ Skipping {source}: {e}")
                    continue
            
            if results:
                return {
                    "status": "success",
                    "results": results,
                    "message": f"Separated {len(results)} stems"
                }
            else:
                return {"error": "No stems processed", "status": "error"}
                
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
    print(f"\n🍋 Handler Ready - Demucs: {separator is not None}")
    print("⚡ Waiting for jobs...")
    runpod.serverless.start({"handler": handler})

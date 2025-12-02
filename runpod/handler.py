# handler.py - SIMPLIFIED ROBUST VERSION
import runpod
import os
import tempfile
import base64
import traceback
import sys
import json

print("=" * 60)
print("🚀 Slice Lemonade Demucs Handler")
print(f"🐍 Python {sys.version}")
print("=" * 60)

# Try to load Demucs with better error handling
separator = None
model_loaded = False

try:
    print("🎵 Loading PyTorch...")
    import torch
    print(f"✅ PyTorch {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"🎮 CUDA: {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️ CUDA not available")
        device = "cpu"
    
    print("🎵 Loading Demucs...")
    # Try different import approaches
    try:
        from demucs import separate
        print("✅ Demucs import method 1 successful")
    except:
        try:
            import demucs.api
            print("✅ Demucs import method 2 successful")
        except Exception as e:
            print(f"❌ Demucs import failed: {e}")
            raise
    
    # Initialize separator
    import demucs.api
    separator = demucs.api.Separator(
        model="htdemucs",
        device=device,
        progress=True
    )
    
    model_loaded = True
    print("✅ Demucs initialized successfully!")
    
except Exception as e:
    print(f"❌ Initialization error: {str(e)}")
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
        
        if not model_loaded or separator is None:
            return {"error": "Demucs model not loaded", "status": "error"}
        
        # Save to temp file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file_name)
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print("🔬 Separating audio...")
            _, separated = separator.separate_audio_file(temp_path)
            print(f"✅ Separation complete: {len(separated)} stems")
            
            # Process stems
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                import io
                from scipy.io.wavfile import write as write_wav
                import numpy as np
                
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
                "message": f"Separated {len(results)} stems",
                "stems": list(results.keys())
            }
            
        finally:
            # Clean up
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"status": "error", "error": error_msg}

if __name__ == "__main__":
    print(f"\n🍋 Slice Lemonade Handler Ready")
    print(f"📊 Demucs loaded: {model_loaded}")
    print(f"⚡ Device: {device if 'device' in locals() else 'unknown'}")
    print("📡 Waiting for jobs...")
    
    runpod.serverless.start({"handler": handler})

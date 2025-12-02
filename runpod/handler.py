# handler.py - UPDATED VERSION
import runpod
import os
import tempfile
import base64
import traceback
import json
from pathlib import Path
import sys

print("🚀 Slice Lemonade - Real Demucs Handler")
print(f"Python: {sys.version}")

# Try to load Demucs
separator = None
try:
    print("🎵 Loading Demucs and dependencies...")
    
    # Import torch first to check CUDA
    import torch
    print(f"✅ PyTorch {torch.__version__} loaded")
    
    if torch.cuda.is_available():
        print(f"✅ CUDA available on {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        device = "cuda"
    else:
        print("⚠️ CUDA not available, using CPU")
        device = "cpu"
    
    # Now import demucs
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
    
    # Test with a tiny audio to ensure it works
    print("🧪 Testing Demucs with dummy audio...")
    test_audio = torch.randn(2, 44100)  # 1 second stereo
    _ = separator.separate(test_audio)
    print("✅ Demucs test passed!")
    
except Exception as e:
    print(f"❌ Failed to load Demucs: {str(e)}")
    traceback.print_exc()
    print("\n🔍 Debug info:")
    import importlib
    try:
        import demucs
        print(f"Demucs version: {demucs.__version__}")
    except:
        print("Demucs import failed")
    
    try:
        print(f"Torch CUDA: {torch.cuda.is_available()}")
    except:
        pass

def handler(job):
    """Handle audio separation - COMPATIBLE VERSION"""
    print(f"\n🎯 Starting job {job.get('id', 'unknown')}")
    
    try:
        input_data = job.get("input", {})
        
        # Check for both possible field names
        audio_data = input_data.get("audio_data") or input_data.get("audio")
        file_name = input_data.get("file_name") or input_data.get("filename", "audio.wav")
        
        if not audio_data:
            error_msg = "No audio data provided. Expected 'audio_data' or 'audio' field"
            print(f"❌ {error_msg}")
            print(f"📊 Input keys: {list(input_data.keys())}")
            return {"error": error_msg, "status": "error"}
        
        print(f"📁 Processing: {file_name}")
        
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            error_msg = f"Failed to decode base64 audio: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "status": "error"}
        
        print(f"📦 Audio size: {len(audio_bytes)} bytes")
        
        if separator is None:
            error_msg = "Demucs not available - model failed to load"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "status": "error",
                "fallback_available": True
            }
        
        # Save to temp file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file_name)
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print("🔬 Separating audio with Demucs...")
            
            # Get separation
            origin, separated = separator.separate_audio_file(temp_path)
            
            print(f"✅ Separation complete, got {len(separated)} stems: {list(separated.keys())}")
            
            # Process each stem
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                try:
                    # Save to bytes
                    import io
                    from scipy.io.wavfile import write as write_wav
                    import numpy as np
                    
                    # Convert to numpy and ensure proper format
                    audio_np = audio.numpy()
                    
                    # Handle mono/stereo
                    if audio_np.ndim == 1:
                        audio_np = audio_np.reshape(1, -1)
                    elif audio_np.ndim == 2 and audio_np.shape[0] > 2:
                        audio_np = audio_np.T
                    
                    # Scale to int16
                    audio_np = (audio_np * 32767).astype(np.int16)
                    
                    # Write to buffer
                    buffer = io.BytesIO()
                    write_wav(buffer, separator.samplerate, audio_np)
                    buffer.seek(0)
                    
                    # Encode as base64
                    stem_bytes = buffer.read()
                    stem_base64 = base64.b64encode(stem_bytes).decode('utf-8')
                    results[source] = stem_base64
                    print(f"✅ {source}: {len(stem_bytes)} bytes")
                    
                except Exception as e:
                    print(f"⚠️ Error processing {source}: {str(e)}")
                    continue
            
            if not results:
                return {"error": "Failed to process any stems", "status": "error"}
            
            return {
                "status": "success",
                "results": results,
                "message": f"Separated {len(results)} stems",
                "stems": list(results.keys())
            }
            
        finally:
            # Clean up temp files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": error_msg,
            "traceback": traceback.format_exc()
        }

# Warmup function
def warmup():
    """Warm up the model"""
    print("\n🔥 Warming up Demucs...")
    if separator is not None:
        try:
            # Create dummy audio
            dummy_audio = torch.randn(2, 44100 * 2)  # 2 seconds
            _ = separator.separate(dummy_audio)
            print("✅ Warmup successful!")
        except Exception as e:
            print(f"⚠️ Warmup failed: {e}")

if __name__ == "__main__":
    print(f"\n🍋 Slice Lemonade Handler Ready")
    print(f"📊 Demucs loaded: {separator is not None}")
    
    # Warm up on startup
    warmup()
    
    print("⚡ Waiting for jobs...")
    runpod.serverless.start({"handler": handler})

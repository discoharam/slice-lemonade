# handler.py - OPTIMIZED FOR RUNPOD
import runpod
import os
import tempfile
import base64
import traceback
import json
import sys
import time

print("=" * 60)
print("🚀 Slice Lemonade - Real Demucs Handler")
print(f"🐍 Python {sys.version}")
print("=" * 60)

# Try to load Demucs with detailed logging
separator = None
model_loaded = False

try:
    print("🎵 Loading PyTorch...")
    import torch
    print(f"✅ PyTorch {torch.__version__} loaded")
    
    if torch.cuda.is_available():
        print(f"🎮 CUDA available on {torch.cuda.get_device_name(0)}")
        print(f"🎮 CUDA version: {torch.version.cuda}")
        print(f"🎮 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        device = "cuda"
    else:
        print("⚠️ CUDA not available, using CPU")
        device = "cpu"
    
    print("🎵 Loading Demucs...")
    import demucs.api
    
    print("🎵 Initializing Demucs separator...")
    separator = demucs.api.Separator(
        model="htdemucs", 
        device=device,
        progress=True,
        shifts=1,
        split=True,
        overlap=0.25
    )
    
    model_loaded = True
    print("✅ Demucs loaded successfully!")
    
    # Quick warmup
    print("🔥 Warming up model...")
    warmup_audio = torch.randn(1, 44100 * 2)  # 2 seconds mono
    _ = separator.separate(warmup_audio)
    print("✅ Model warmup complete!")
    
except Exception as e:
    print(f"❌ Failed to initialize Demucs: {str(e)}")
    traceback.print_exc()
    print("\n🔍 Debug info:")
    print(f"Model loaded: {model_loaded}")
    print(f"Separator object: {separator}")

def handler(job):
    """Handle audio separation"""
    print(f"\n" + "=" * 50)
    print(f"🎯 Starting job: {job.get('id', 'unknown')}")
    print("=" * 50)
    
    try:
        input_data = job.get("input", {})
        print(f"📦 Input keys: {list(input_data.keys())}")
        
        # Check for audio data
        audio_data = input_data.get("audio_data")
        file_name = input_data.get("file_name", "audio.wav")
        
        if not audio_data:
            error_msg = "No audio_data provided in input"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "status": "error"}
        
        print(f"📁 Processing: {file_name}")
        
        # Decode base64
        try:
            audio_bytes = base64.b64decode(audio_data)
            print(f"📊 Audio size: {len(audio_bytes)} bytes")
        except Exception as e:
            error_msg = f"Failed to decode base64 audio: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "status": "error"}
        
        # Check if Demucs is available
        if not model_loaded or separator is None:
            error_msg = "Demucs model failed to load on worker"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "status": "error"}
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file_name)
        
        try:
            # Save audio to file
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print("🔬 Starting Demucs separation...")
            start_time = time.time()
            
            # Separate audio
            _, separated = separator.separate_audio_file(temp_path)
            
            elapsed = time.time() - start_time
            print(f"✅ Separation completed in {elapsed:.2f} seconds")
            print(f"🎵 Got {len(separated)} stems: {list(separated.keys())}")
            
            # Process each stem
            results = {}
            for source, audio in separated.items():
                try:
                    print(f"💾 Processing {source}...")
                    
                    # Convert to numpy and save as WAV
                    import io
                    import numpy as np
                    from scipy.io.wavfile import write as write_wav
                    
                    # Convert tensor to numpy
                    audio_np = audio.numpy()
                    
                    # Ensure proper shape (channels x samples)
                    if audio_np.ndim == 1:
                        audio_np = audio_np.reshape(1, -1)
                    elif audio_np.ndim == 2 and audio_np.shape[0] > 2:
                        # Transpose if needed
                        audio_np = audio_np.T
                    
                    # Scale to 16-bit PCM
                    if audio_np.dtype != np.int16:
                        audio_np = (audio_np * 32767).astype(np.int16)
                    
                    # Write to buffer
                    buffer = io.BytesIO()
                    write_wav(buffer, separator.samplerate, audio_np.T)
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
            
            response = {
                "status": "success",
                "results": results,
                "message": f"Separated {len(results)} stems in {elapsed:.2f}s",
                "stems": list(results.keys()),
                "processing_time": elapsed
            }
            
            print(f"📤 Response: {len(results)} stems ready")
            return response
            
        finally:
            # Cleanup
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
            "error": error_msg
        }

if __name__ == "__main__":
    print(f"\n🍋 Slice Lemonade Handler Ready!")
    print(f"📊 Demucs loaded: {model_loaded}")
    print(f"⚡ Device: {device if 'device' in locals() else 'unknown'}")
    print(f"📡 Waiting for jobs...\n")
    
    # Test endpoint
    test_input = {
        "input": {
            "audio_data": "test",
            "file_name": "test.wav"
        }
    }
    
    runpod.serverless.start({"handler": handler})

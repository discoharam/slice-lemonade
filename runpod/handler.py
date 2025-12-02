# handler.py - REAL VERSION FOR RUNPOD
import runpod
import os
import tempfile
import base64
import traceback
from pathlib import Path

print("🚀 Slice Lemonade - Real Demucs Handler")

# Try to load Demucs
separator = None
try:
    print("🎵 Loading Demucs...")
    import demucs.api
    
    # Check CUDA
    import torch
    if torch.cuda.is_available():
        print(f"✅ CUDA available on {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️ CUDA not available, using CPU")
        device = "cpu"
    
    separator = demucs.api.Separator(
        model="htdemucs", 
        device=device,
        progress=False,
        shifts=1
    )
    print("✅ Demucs loaded successfully!")
    
except Exception as e:
    print(f"❌ Failed to load Demucs: {str(e)}")
    traceback.print_exc()

def handler(job):
    """Handle audio separation"""
    print(f"\n🎯 Processing job: {job.get('id')}")
    
    try:
        input_data = job.get("input", {})
        audio_data = input_data.get("audio_data")
        file_name = input_data.get("file_name", "audio.wav")
        
        if not audio_data:
            return {"error": "No audio data provided"}
        
        print(f"📁 File: {file_name}")
        audio_bytes = base64.b64decode(audio_data)
        print(f"📦 Audio size: {len(audio_bytes)} bytes")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            if separator is None:
                print("❌ Demucs not loaded")
                return {
                    "error": "Demucs model not loaded on worker",
                    "status": "error"
                }
            
            print("🔬 Separating audio...")
            _, separated = separator.separate_audio_file(temp_path)
            print(f"✅ Separation complete, got {len(separated)} stems")
            
            # Process each stem
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                # Save to bytes
                import io
                buffer = io.BytesIO()
                separator.save_audio(
                    audio, 
                    buffer, 
                    samplerate=separator.samplerate,
                    format="wav"
                )
                buffer.seek(0)
                
                # Encode as base64
                stem_bytes = buffer.read()
                stem_base64 = base64.b64encode(stem_bytes).decode('utf-8')
                results[source] = stem_base64
                print(f"✅ {source}: {len(stem_bytes)} bytes -> {len(stem_base64)} chars base64")
            
            return {
                "status": "success",
                "results": results,
                "message": f"Separated {len(results)} stems"
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
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
    print(f"\n🍋 Slice Lemonade Handler Ready")
    print(f"📊 Demucs loaded: {separator is not None}")
    print("⚡ Waiting for jobs...")
    
    runpod.serverless.start({"handler": handler})

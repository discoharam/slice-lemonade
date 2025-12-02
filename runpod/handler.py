# handler.py - UPDATED VERSION
import runpod
import os
import tempfile
import base64
from pathlib import Path
import traceback

print("🚀 Starting Slice Lemonade RunPod Handler...")

def init_separator():
    """Lazy load Demucs to avoid startup issues"""
    try:
        print("🎵 Attempting to load Demucs...")
        import demucs.api
        
        separator = demucs.api.Separator(
            model="htdemucs", 
            device="cuda",
            progress=False
        )
        print("✅ Demucs loaded successfully!")
        return separator
    except Exception as e:
        print(f"❌ Failed to load Demucs: {str(e)}")
        print("⚠️ Using fallback mode")
        return None

separator = init_separator()

def separate_audio(job):
    """Handle audio separation"""
    job_id = job.get('id', 'unknown')
    print(f"🎯 Starting job {job_id}")
    
    try:
        job_input = job['input']
        audio_data = job_input.get('audio_data')
        file_name = job_input.get('file_name', 'audio.wav')
        
        if not audio_data:
            return {"error": "No audio data provided"}
        
        print(f"📁 Processing: {file_name}")
        audio_bytes = base64.b64decode(audio_data)
        print(f"📦 Audio size: {len(audio_bytes)} bytes")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            if separator is None:
                print("⚠️ Demucs not available, using fallback")
                return {
                    "status": "error",
                    "error": "Demucs not loaded on worker",
                    "message": "GPU worker initialization failed"
                }
            
            print("🔬 Separating with Demucs...")
            _, separated = separator.separate_audio_file(temp_path)
            print(f"✅ Separation complete, got {len(separated)} sources")
            
            # Process each stem
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                # Convert to bytes
                import io
                buffer = io.BytesIO()
                separator.save_audio(audio, buffer, samplerate=separator.samplerate)
                buffer.seek(0)
                
                # Encode as base64
                audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                results[source] = audio_base64
                print(f"✅ {source} encoded: {len(audio_base64)} chars")
            
            return {
                "status": "success",
                "job_id": job_id,
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
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": error_msg,
            "job_id": job_id
        }

if __name__ == "__main__":
    print("🍋 Slice Lemonade Handler Ready!")
    print(f"📊 Demucs loaded: {separator is not None}")
    print("⚡ Waiting for jobs...")
    runpod.serverless.start({"handler": separate_audio})

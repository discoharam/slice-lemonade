import runpod
import os
import tempfile
import base64
from pathlib import Path
import demucs.api
from io import BytesIO
import torch

print("🚀 Starting Slice Lemonade RunPod Handler...")

separator = None

def init_separator():
    global separator
    if separator is None:
        print("🎵 Loading Demucs model on GPU...")
        try:
            separator = demucs.api.Separator(
                model="htdemucs", 
                device="cuda",
                progress=True
            )
            print("✅ Demucs model loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load Demucs: {str(e)}")
            raise e

def separate_audio(job):
    try:
        print(f"🎯 Starting job: {job.get('id', 'unknown')}")
        init_separator()
        
        job_input = job['input']
        audio_data = job_input.get('audio_data')
        file_name = job_input.get('file_name', 'audio.mp3')
        
        if not audio_data:
            return {"error": "No audio data provided"}
        
        print(f"📁 Processing: {file_name}")
        audio_bytes = base64.b64decode(audio_data)
        print(f"📦 Audio size: {len(audio_bytes)} bytes")
        
        with tempfile.NamedTemporaryFile(suffix=Path(file_name).suffix, delete=False) as input_file:
            input_file.write(audio_bytes)
            input_path = input_file.name
        
        try:
            print("🔬 Separating audio stems...")
            origin, separated = separator.separate_audio_file(input_path)
            print("✅ Separation completed!")
            
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing stem: {source}")
                buffer = BytesIO()
                demucs.api.save_audio(audio, buffer, samplerate=separator.samplerate)
                buffer.seek(0)
                audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                results[source] = audio_base64
                print(f"✅ Saved {source}: {len(audio_base64)} bytes")
            
            print("🎉 All stems processed successfully!")
            return {
                "status": "success",
                "job_id": job.get('id', 'unknown'),
                "results": results,
                "stems": list(results.keys()),
                "message": f"Separated {len(results)} stems"
            }
        finally:
            Path(input_path).unlink(missing_ok=True)
    except Exception as e:
        error_msg = f"❌ Error during audio separation: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "job_id": job.get('id', 'unknown')
        }

if __name__ == "__main__":
    print("🍋 Slice Lemonade RunPod Handler Ready!")
    print("⚡ Waiting for jobs...")
    runpod.serverless.start({"handler": separate_audio})
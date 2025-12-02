import runpod
import torch
import base64
import tempfile
import os
import io
import json
import numpy as np
from scipy.io import wavfile
import subprocess

print("🚀 Slice Lemonade Demucs Handler - REAL GPU SEPARATION")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

def handler(job):
    """Audio separation handler using Demucs command line"""
    job_id = job.get('id', 'unknown')
    print(f"🎯 Processing job {job_id} - REAL DEMUCS")
    
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
        
        # Create a temporary directory for input and output
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, filename)
            with open(input_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Run Demucs command line - SIMPLEST APPROACH
            print("🤖 Running Demucs separation...")
            
            # Use command line demucs (most stable)
            cmd = [
                "demucs",
                "--device", "cuda" if torch.cuda.is_available() else "cpu",
                "--two-stems=vocals",
                "-o", tmpdir,
                input_path
            ]
            
            print(f"📝 Command: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"❌ Demucs command failed: {result.stderr}")
                    # Fall back to Python API
                    print("🔄 Trying Python API...")
                    return python_demucs_separation(audio_bytes, tmpdir, filename)
                
                print("✅ Demucs command completed")
                
            except subprocess.TimeoutExpired:
                print("⏰ Demucs command timed out, trying Python API...")
                return python_demucs_separation(audio_bytes, tmpdir, filename)
            
            # Find output files
            output_dir = os.path.join(tmpdir, "htdemucs")
            if not os.path.exists(output_dir):
                # Try to find any directory
                for item in os.listdir(tmpdir):
                    item_path = os.path.join(tmpdir, item)
                    if os.path.isdir(item_path):
                        output_dir = item_path
                        break
            
            # Look for separated files
            stems = ['drums', 'bass', 'other', 'vocals']
            results = {}
            
            for stem in stems:
                # Look for the file in the expected structure
                stem_path = os.path.join(output_dir, os.path.splitext(filename)[0], f"{stem}.wav")
                
                if not os.path.exists(stem_path):
                    # Try alternative location
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            if file.endswith('.wav') and stem in file.lower():
                                stem_path = os.path.join(root, file)
                                break
                
                if os.path.exists(stem_path):
                    with open(stem_path, 'rb') as f:
                        stem_bytes = f.read()
                    results[stem] = base64.b64encode(stem_bytes).decode('utf-8')
                    print(f"✅ {stem}: {len(results[stem])} chars")
                else:
                    print(f"⚠️ {stem} not found in output")
            
            if not results:
                print("🔄 No stems found, trying Python API...")
                return python_demucs_separation(audio_bytes, tmpdir, filename)
            
            print(f"🎉 Success! {len(results)} stems")
            return {
                "status": "success",
                "message": "Demucs separation completed",
                "stems": list(results.keys()),
                **results
            }
            
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Handler error: {str(e)}", "status": "error"}

def python_demucs_separation(audio_bytes, tmpdir, filename):
    """Fallback using Python API"""
    try:
        print("🤖 Trying Python API fallback...")
        
        # Save audio to file
        input_path = os.path.join(tmpdir, filename)
        with open(input_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Try to import and use Demucs Python API
        try:
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            import torchaudio
        except ImportError as e:
            return {"error": f"Demucs Python API not available: {e}", "status": "error"}
        
        # Load model
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
        with torch.no_grad():
            sources = apply_model(model, wav[None], device=device)[0]
        
        # Prepare results
        stems = ['drums', 'bass', 'other', 'vocals']
        results = {}
        
        for idx, stem in enumerate(stems):
            if idx < sources.shape[0]:
                stem_wav = sources[idx].cpu().numpy()
                stem_wav_int16 = np.clip(stem_wav * 32767, -32768, 32767).astype(np.int16)
                
                bytes_io = io.BytesIO()
                wavfile.write(bytes_io, 44100, stem_wav_int16.T)
                stem_bytes = bytes_io.getvalue()
                
                results[stem] = base64.b64encode(stem_bytes).decode('utf-8')
                print(f"✅ {stem}: {len(results[stem])} chars")
        
        if not results:
            return {"error": "No stems generated", "status": "error"}
        
        return {
            "status": "success",
            "message": "Demucs Python API separation completed",
            "stems": list(results.keys()),
            **results
        }
        
    except Exception as e:
        print(f"❌ Python API error: {str(e)}")
        return {"error": f"Python API failed: {str(e)}", "status": "error"}

# Start handler
if __name__ == "__main__":
    print("✅ Handler ready for GPU separation")
    runpod.serverless.start({"handler": handler})

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
import sys

print("🚀 Slice Lemonade Demucs Handler - REAL GPU SEPARATION v4.0.0")
print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

def handler(job):
    """Audio separation handler using Demucs v4.0.0"""
    job_id = job.get('id', 'unknown')
    print(f"🎯 Processing job {job_id} - REAL DEMUCS v4.0.0")
    
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
            
            print("🤖 Starting Demucs v4.0.0 separation...")
            
            # METHOD 1: Try command-line first (most reliable)
            try:
                print("📝 Running Demucs command line...")
                cmd = [
                    "demucs",
                    "--device", "cuda" if torch.cuda.is_available() else "cpu",
                    "-o", tmpdir,  # Output directory
                    input_path
                ]
                
                print(f"Command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
                
                if result.returncode != 0:
                    print(f"⚠️ Command failed: {result.stderr}")
                    raise Exception("Command-line demucs failed")
                    
                print("✅ Command-line demucs completed")
                
                # Find output files - Demucs v4.0.0 structure
                model_dir = "htdemucs"  # Default model
                output_dir = os.path.join(tmpdir, model_dir)
                
                if not os.path.exists(output_dir):
                    # Look for any directory
                    items = os.listdir(tmpdir)
                    for item in items:
                        item_path = os.path.join(tmpdir, item)
                        if os.path.isdir(item_path) and not item.startswith('.'):
                            output_dir = item_path
                            break
                
                print(f"Looking for output in: {output_dir}")
                
                # Get the track name (without extension)
                track_name = os.path.splitext(filename)[0]
                
                # Look for stems in the expected structure
                stems = {}
                for stem in ['vocals', 'drums', 'bass', 'other']:
                    # Try different possible locations
                    possible_paths = [
                        os.path.join(output_dir, track_name, f"{stem}.wav"),
                        os.path.join(output_dir, track_name, f"{stem}.mp3"),
                        os.path.join(output_dir, track_name, stem, "audio.wav"),
                    ]
                    
                    found = False
                    for path in possible_paths:
                        if os.path.exists(path):
                            with open(path, 'rb') as f:
                                stems[stem] = base64.b64encode(f.read()).decode('utf-8')
                            print(f"✅ Found {stem}: {len(stems[stem])} chars")
                            found = True
                            break
                    
                    if not found:
                        print(f"⚠️ {stem} not found in output")
                
                if stems:
                    print(f"🎉 Command-line success! Found {len(stems)} stems")
                    return {
                        "status": "success",
                        "message": "Demucs separation completed",
                        "stems": list(stems.keys()),
                        **stems
                    }
                else:
                    print("❌ No stems found in command-line output")
                    raise Exception("No output from command-line demucs")
                    
            except Exception as e:
                print(f"🔄 Command-line failed, trying Python API: {str(e)}")
                return python_demucs_separation(audio_bytes, tmpdir, filename)
            
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Handler error: {str(e)}", 
            "status": "error",
            "debug": {
                "cuda": torch.cuda.is_available(),
                "torch_version": torch.__version__
            }
        }

def python_demucs_separation(audio_bytes, tmpdir, filename):
    """Fallback using Python API for Demucs v4.0.0"""
    try:
        print("🤖 Trying Demucs Python API...")
        
        # Save audio to file
        input_path = os.path.join(tmpdir, filename)
        with open(input_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Import Demucs v4.0.0 API
        try:
            # First try the new API
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            import torchaudio
        except ImportError as e:
            print(f"❌ Import error: {str(e)}")
            # Try alternative imports
            try:
                from demucs import pretrained
                from demucs import apply
                get_model = pretrained.get_model
                apply_model = apply.apply_model
                import torchaudio
            except ImportError as e2:
                return {"error": f"Demucs Python API not available: {e2}", "status": "error"}
        
        print("✅ Imports successful")
        
        # Load model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📦 Loading model on {device}...")
        
        try:
            model = get_model('htdemucs')
            model.to(device)
            model.eval()
        except Exception as e:
            return {"error": f"Failed to load model: {str(e)}", "status": "error"}
        
        print("✅ Model loaded")
        
        # Load audio
        try:
            wav, sr = torchaudio.load(input_path)
            print(f"📊 Audio loaded: {wav.shape}, {sr}Hz")
        except Exception as e:
            return {"error": f"Failed to load audio: {str(e)}", "status": "error"}
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
            print("✅ Converted to mono")
        
        # Resample to 44100 Hz if needed
        if sr != 44100:
            resample = torchaudio.transforms.Resample(sr, 44100)
            wav = resample(wav)
            print(f"✅ Resampled to 44100Hz")
        
        # Normalize
        max_val = wav.abs().max()
        if max_val > 0:
            wav = wav / max_val
        
        # Separate
        print("⚡ Starting separation...")
        with torch.no_grad():
            sources = apply_model(model, wav[None], device=device)[0]
        
        print(f"✅ Separation complete: {sources.shape}")
        
        # Prepare results
        stems = ['drums', 'bass', 'other', 'vocals']
        results = {}
        
        for idx, stem in enumerate(stems):
            if idx < sources.shape[0]:
                # Get the stem audio
                stem_wav = sources[idx].cpu().numpy()
                
                # Convert to int16
                stem_wav_int16 = np.clip(stem_wav * 32767, -32768, 32767).astype(np.int16)
                
                # Save to bytes
                bytes_io = io.BytesIO()
                wavfile.write(bytes_io, 44100, stem_wav_int16.T)
                stem_bytes = bytes_io.getvalue()
                
                # Encode to base64
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
        import traceback
        traceback.print_exc()
        return {
            "error": f"Python API failed: {str(e)}", 
            "status": "error",
            "python_error": str(e)
        }

# Start handler
if __name__ == "__main__":
    print("✅ Slice Lemonade Handler ready!")
    print("📡 Waiting for jobs...")
    runpod.serverless.start({"handler": handler})
import runpod
import torch
import base64
import tempfile
import os
import io
import json
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torchaudio
from scipy.io import wavfile
import numpy as np

print("🚀 Slice Lemonade Demucs Handler - REAL GPU SEPARATION")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

def handler(job):
    """REAL Demucs audio separation - NO TEST MODE"""
    job_id = job.get('id', 'unknown')
    print(f"🎯 Processing job {job_id} - REAL DEMUCS")
    
    try:
        job_input = job.get("input", {})
        
        # Get audio data
        audio_base64 = job_input.get("audio_data", job_input.get("audio", ""))
        filename = job_input.get("file_name", job_input.get("filename", "audio.wav"))
        
        if not audio_base64:
            return {
                "error": "No audio data provided",
                "status": "error",
                "message": "Send audio_data in base64 format"
            }
        
        print(f"📦 Processing {filename} ({len(audio_base64)} chars)")
        
        # Decode base64
        try:
            audio_bytes = base64.b64decode(audio_base64)
            print(f"🎵 Decoded to {len(audio_bytes)} bytes")
        except Exception as e:
            return {"error": f"Base64 decode failed: {str(e)}", "status": "error"}
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            input_path = tmp.name
        
        try:
            print("🤖 Loading Demucs model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"⚡ Using device: {device}")
            
            # Load Demucs model
            model = get_model('htdemucs')
            model.to(device)
            model.eval()
            
            # Load audio file
            print("🎧 Loading audio...")
            wav, sr = torchaudio.load(input_path)
            print(f"📊 Input shape: {wav.shape}, Sample rate: {sr}Hz")
            
            # Convert to mono if stereo
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
                print("🔄 Converted stereo to mono")
            
            # Resample to 44100 Hz if needed
            if sr != 44100:
                wav = torchaudio.functional.resample(wav, sr, 44100)
                print(f"🎚️ Resampled from {sr}Hz to 44100Hz")
            
            # Normalize
            max_val = wav.abs().max()
            if max_val > 0:
                wav = wav / max_val
            print(f"📏 Normalized (max: {wav.abs().max():.3f})")
            
            duration = wav.shape[1] / 44100
            print(f"⏱️ Duration: {duration:.2f}s")
            
            # REAL GPU SEPARATION
            print("⚡ Starting Demucs separation on GPU...")
            with torch.no_grad():
                # Apply model
                sources = apply_model(
                    model, 
                    wav[None],  # Add batch dimension
                    device=device,
                    shifts=1,
                    split=True,
                    overlap=0.25,
                    progress=True
                )[0]  # Remove batch dimension
            
            print(f"✅ Separation complete! Output shape: {sources.shape}")
            
            # Prepare results
            print("💾 Encoding stems...")
            stems = ['drums', 'bass', 'other', 'vocals']
            results = {}
            
            for idx, stem_name in enumerate(stems):
                if idx < sources.shape[0]:
                    # Get stem audio
                    stem_wav = sources[idx].cpu().numpy()
                    
                    # Convert to 16-bit PCM for WAV
                    stem_wav_int16 = np.clip(stem_wav * 32767, -32768, 32767).astype(np.int16)
                    
                    # Save to bytes
                    bytes_io = io.BytesIO()
                    wavfile.write(bytes_io, 44100, stem_wav_int16.T)
                    audio_bytes = bytes_io.getvalue()
                    
                    # Encode to base64
                    results[stem_name] = base64.b64encode(audio_bytes).decode('utf-8')
                    print(f"✅ {stem_name}: {len(results[stem_name])} chars")
            
            # Clean up
            os.unlink(input_path)
            
            if not results:
                return {
                    "error": "No stems generated",
                    "status": "error",
                    "debug": "Demucs returned empty results"
                }
            
            print(f"🎉 Success! Separated {len(results)} stems")
            return {
                "status": "success",
                "message": f"Real Demucs GPU separation completed",
                "duration": f"{duration:.2f}s",
                "stems": list(results.keys()),
                **results  # This adds vocals, drums, bass, other keys
            }
            
        except Exception as e:
            print(f"❌ Separation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Demucs separation failed: {str(e)}",
                "status": "error"
            }
            
    except Exception as e:
        print(f"❌ Handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Handler error: {str(e)}",
            "status": "error"
        }

# Start the serverless handler
if __name__ == "__main__":
    print("✅ Real Demucs Handler - READY FOR GPU SEPARATION")
    print("👂 Listening for jobs...")
    runpod.serverless.start({"handler": handler})

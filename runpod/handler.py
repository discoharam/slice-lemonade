# handler.py for RunPod
import runpod
import torch
import base64
import io
import os
from pathlib import Path
import tempfile
from demucs import separate
from demucs.pretrained import get_model

def handler(job):
    """Demucs audio separation handler"""
    job_input = job.get("input", {})
    
    # Check for test mode
    if job_input.get("test", False):
        return {
            "message": "Demucs handler is working!",
            "ready_for_demucs": True,
            "status": "success",
            "test": True
        }
    
    # Get audio data
    audio_base64 = job_input.get("audio", job_input.get("audio_data", ""))
    if not audio_base64:
        return {"error": "No audio data provided"}
    
    try:
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            input_path = tmp.name
        
        # Create output directory
        output_dir = tempfile.mkdtemp()
        
        # Run Demucs
        model = get_model('htdemucs')
        model.cpu()
        
        # Separate
        separate.demucs.separate_audio(
            model,
            input_path,
            output_dir,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        # Read separated tracks
        results = {}
        stem_names = ['vocals', 'drums', 'bass', 'other']
        
        for stem in stem_names:
            stem_path = Path(output_dir) / 'htdemucs' / Path(input_path).stem / f"{stem}.wav"
            if stem_path.exists():
                with open(stem_path, 'rb') as f:
                    stem_bytes = f.read()
                    results[stem] = base64.b64encode(stem_bytes).decode('utf-8')
        
        # Cleanup
        os.unlink(input_path)
        
        return {
            "status": "success",
            "stems": list(results.keys()),
            **results
        }
        
    except Exception as e:
        return {"error": str(e)}

# Start the handler
runpod.serverless.start({"handler": handler})

import os
import uuid
from datetime import datetime
from flask import current_app
from .runpod_client import runpod_client

class AudioSeparator:
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.aac']
    
    def separate_audio(self, input_path, job_id):
        try:
            output_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            result = runpod_client.separate_audio(input_path, job_id)
            
            if result.get('status') == 'error':
                raise Exception(result.get('error', 'Unknown RunPod error'))
            
            results_data = self._save_separated_tracks(result['results'], output_dir)
            
            return {
                "job_id": job_id,
                "status": "completed",
                "results": results_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Separation failed: {str(e)}")
    
    def _save_separated_tracks(self, tracks_data, output_dir):
        results = {}
        
        for stem_name, base64_data in tracks_data.items():
            try:
                audio_bytes = base64.b64decode(base64_data)
                output_path = os.path.join(output_dir, f"{stem_name}.wav")
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                results[stem_name] = f"/api/download/{os.path.basename(output_dir)}/{stem_name}"
            except Exception as e:
                print(f"Error saving {stem_name}: {str(e)}")
                continue
        
        return results
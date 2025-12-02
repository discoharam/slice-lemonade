import math
import os
import uuid
import base64
import json
import wave
import struct
from datetime import datetime
from flask import current_app
from .runpod_client import runpod_client

class AudioSeparator:
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.aac']
        self.expected_stems = ['vocals', 'drums', 'bass', 'other']
    
    def separate_audio(self, input_path, job_id):
        try:
            output_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🎯 Processing job {job_id} with file: {os.path.basename(input_path)}")
            
            # Get file info
            file_size = os.path.getsize(input_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Call RunPod client for REAL separation
            result = runpod_client.separate_audio(input_path, job_id)
            
            # Check for errors
            if 'error' in result:
                print(f"❌ RunPod error: {result['error']}")
                raise Exception(f"RunPod error: {result['error']}")
            
            # Save REAL tracks from Demucs
            if 'output' in result:
                output_data = result['output']
                
                # Check if we have real audio tracks
                has_audio_tracks = any(stem in output_data for stem in self.expected_stems)
                
                if has_audio_tracks:
                    print("✅ REAL Demucs output detected!")
                    results_data = self._save_real_tracks(output_data, output_dir, job_id)
                    note = "Real Demucs GPU separation completed successfully!"
                    is_real = True
                else:
                    # No audio tracks - might be error message
                    print(f"⚠️ No audio tracks in output. Output: {output_data}")
                    
                    # Check if it's an error
                    if 'error' in output_data:
                        error_msg = output_data['error']
                        raise Exception(f"Demucs error: {error_msg}")
                    else:
                        raise Exception(f"Unexpected output: {output_data}")
            else:
                raise Exception("No output from RunPod")
            
            # Return results
            return {
                "job_id": job_id,
                "status": "completed",
                "results": results_data,
                "timestamp": datetime.utcnow().isoformat(),
                "note": note,
                "is_real": is_real
            }
            
        except Exception as e:
            print(f"❌ Separation error: {str(e)}")
            raise Exception(f"Separation failed: {str(e)}")
    
    def _save_real_tracks(self, tracks_data, output_dir, job_id):
        """Save real Demucs separated tracks"""
        results = {}
        print(f"💾 Saving real tracks to {output_dir}")
        
        for stem_name in self.expected_stems:
            if stem_name in tracks_data:
                try:
                    audio_base64 = tracks_data[stem_name]
                    
                    # Handle different base64 formats
                    if audio_base64.startswith('data:audio/wav;base64,'):
                        audio_base64 = audio_base64[22:]  # Remove prefix
                    
                    # Fix padding
                    missing_padding = len(audio_base64) % 4
                    if missing_padding:
                        audio_base64 += '=' * (4 - missing_padding)
                    
                    # Decode
                    audio_bytes = base64.b64decode(audio_base64)
                    
                    # Save to file
                    output_path = os.path.join(output_dir, f"{stem_name}.wav")
                    with open(output_path, 'wb') as f:
                        f.write(audio_bytes)
                    
                    file_size = os.path.getsize(output_path)
                    results[stem_name] = f"/api/download/{job_id}/{stem_name}"
                    print(f"✅ Saved REAL {stem_name}.wav ({file_size} bytes)")
                    
                except Exception as e:
                    print(f"⚠️ Error saving {stem_name}: {str(e)}")
                    # Don't create placeholder - fail fast
                    raise Exception(f"Failed to save {stem_name}: {str(e)}")
        
        # If we got some tracks but not all
        if results:
            return results
        else:
            raise Exception("No tracks were saved")

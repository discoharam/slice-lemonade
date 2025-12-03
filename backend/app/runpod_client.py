import os
import time
import base64
import requests
import json

class RunPodClient:
    def __init__(self):
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        
        if not self.api_key:
            print("❌ RUNPOD_API_KEY not found in environment")
        if not self.endpoint_id:
            print("❌ RUNPOD_ENDPOINT_ID not found in environment")
        
        if self.api_key and self.endpoint_id:
            print(f"✅ RunPod Client Configured")
            print(f"   Endpoint ID: {self.endpoint_id}")
            print(f"   Mode: REAL DEMUCS GPU SEPARATION")
        else:
            print("❌ RunPod not configured - check .env file")
    
    def separate_audio(self, file_path, job_id):
        """Send audio to RunPod for REAL Demucs separation"""
        try:
            print(f"🚀 Sending to RunPod for REAL separation: {file_path}")
            
            # Read and encode audio
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            filename = os.path.basename(file_path)
            
            # Payload for REAL Demucs v4.0.0
            payload = {
                "input": {
                    "audio_data": audio_base64,
                    "file_name": filename
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Submit job via REST API
            run_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/run"
            print(f"📤 Sending {len(audio_bytes)} bytes to RunPod...")
            print("⚡ This will perform REAL GPU Demucs separation (1-3 minutes)")
            
            response = requests.post(run_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_msg = f"RunPod error {response.status_code}: {response.text[:200]}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
            runpod_job = response.json()
            runpod_job_id = runpod_job.get("id")
            
            if not runpod_job_id:
                error_msg = f"No job ID returned from RunPod: {runpod_job}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
            print(f"✅ RunPod job submitted: {runpod_job_id}")
            return self._poll_job_status(runpod_job_id)
            
        except Exception as e:
            error_msg = f"RunPod connection error: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _poll_job_status(self, runpod_job_id):
        """Poll RunPod for completion"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        status_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status/{runpod_job_id}"
        
        print(f"⏳ Polling RunPod job {runpod_job_id}...")
        print("⏰ Real Demucs takes 1-3 minutes on GPU...")
        
        for poll_num in range(50):  # 5 minutes max (50 * 6s = 300s)
            time.sleep(6)  # Check every 6 seconds
            
            try:
                response = requests.get(status_url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"⚠️ Poll {poll_num+1}: HTTP {response.status_code} - {response.text[:100]}")
                    continue
                
                status_data = response.json()
                status = status_data.get("status")
                
                print(f"📊 Poll {poll_num+1}: Status = {status}")
                
                if status == "COMPLETED":
                    output = status_data.get("output", {})
                    
                    print("\n" + "="*50)
                    print("✅ RunPod job completed!")
                    print("="*50)
                    
                    # Check if this is REAL Demucs output
                    if isinstance(output, dict):
                        if "error" in output:
                            error_msg = output.get("error", "Unknown error")
                            print(f"❌ RunPod returned error: {error_msg}")
                            return {"error": error_msg}
                        
                        # Check for audio stems
                        has_audio_tracks = any(key in output for key in ['vocals', 'drums', 'bass', 'other'])
                        
                        if has_audio_tracks:
                            print("🎯 REAL Demucs tracks detected!")
                            for key in ['vocals', 'drums', 'bass', 'other']:
                                if key in output:
                                    char_count = len(output[key])
                                    size_kb = char_count * 3 / 4 / 1024
                                    print(f"   {key}: {char_count:,} chars (~{size_kb:.1f} KB)")
                            return {"output": output, "runpod_job_id": runpod_job_id}
                        elif "stems" in output:
                            print(f"✅ Got stems: {output.get('stems', [])}")
                            return {"output": output, "runpod_job_id": runpod_job_id}
                        else:
                            print(f"⚠️ Unexpected output format")
                            print(f"Output keys: {list(output.keys())}")
                            return {"error": "No audio tracks returned from RunPod"}
                    
                    return {"output": output, "runpod_job_id": runpod_job_id}
                
                elif status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ RunPod failed: {error}")
                    return {"error": f"RunPod failed: {error}"}
                
                elif status == "IN_QUEUE":
                    if poll_num % 5 == 0:  # Every 30 seconds
                        print("⏰ Job in queue (GPU might be warming up)")
                
                elif status == "IN_PROGRESS":
                    if poll_num % 3 == 0:  # Every 18 seconds
                        print("⚡ GPU is processing...")
                
            except Exception as e:
                print(f"⚠️ Poll error: {str(e)}")
                continue
        
        return {"error": f"RunPod timeout after 5 minutes"}

# Create a global instance for import
runpod_client = RunPodClient()
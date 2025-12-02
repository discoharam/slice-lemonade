import os
import time
import base64
import requests
import json

class RunPodClient:
    def __init__(self):
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        
        print(f"🔧 RunPod Client: {'✅ Configured' if self.api_key and self.endpoint_id else '❌ Not configured'}")
        if self.api_key and self.endpoint_id:
            print(f"   Endpoint ID: {self.endpoint_id}")
            print(f"   API Key: {self.api_key[:10]}...")
            print(f"   Mode: REAL DEMUCS GPU SEPARATION")
    
    def separate_audio(self, file_path, job_id):
        """Send audio to RunPod for REAL Demucs separation"""
        try:
            print(f"🚀 Sending to RunPod for REAL separation: {file_path}")
            
            # Read and encode audio
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            filename = os.path.basename(file_path)
            
            # Payload for REAL Demucs - NO TEST PARAMETER
            payload = {
                "input": {
                    "audio_data": audio_base64,
                    "file_name": filename
                    # NO "test" parameter - always real processing
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
                return {"error": "No job ID returned from RunPod"}
            
            print(f"✅ RunPod job submitted: {runpod_job_id}")
            return self._poll_job_status(runpod_job_id)
            
        except Exception as e:
            error_msg = f"RunPod error: {str(e)}"
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
                    print(f"⚠️ Poll {poll_num+1}: HTTP {response.status_code}")
                    continue
                
                status_data = response.json()
                status = status_data.get("status")
                
                print(f"📊 Poll {poll_num+1}: Status = {status}")
                
                if status == "COMPLETED":
                    output = status_data.get("output", {})
                    
                    # Check if this is REAL Demucs output
                    print(f"✅ RunPod job completed!")
                    
                    if isinstance(output, dict):
                        has_audio_tracks = any(key in output for key in ['vocals', 'drums', 'bass', 'other'])
                        
                        if has_audio_tracks:
                            print("🎯 REAL Demucs tracks detected!")
                            for key in ['vocals', 'drums', 'bass', 'other']:
                                if key in output:
                                    print(f"   {key}: {len(output[key])} chars")
                            return {"output": output, "runpod_job_id": runpod_job_id}
                        else:
                            print(f"⚠️ No audio tracks in output. Keys: {list(output.keys())}")
                            return {"output": output, "runpod_job_id": runpod_job_id, "error": "No audio tracks returned"}
                    
                    return {"output": output, "runpod_job_id": runpod_job_id}
                
                elif status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ RunPod failed: {error}")
                    return {"error": f"RunPod failed: {error}"}
                
                elif status == "IN_QUEUE":
                    if poll_num >= 10:  # After 60 seconds in queue
                        print("⏰ Job in queue (GPU might be warming up)")
                
                elif status == "IN_PROGRESS":
                    print("⚡ GPU is processing...")
                
            except Exception as e:
                print(f"⚠️ Poll error: {str(e)}")
                continue
        
        return {"error": f"RunPod timeout after 5 minutes"}

# Create a global instance for import
runpod_client = RunPodClient()

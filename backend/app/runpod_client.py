import runpod
import base64
import os
import time
import requests

class RunPodClient:
    def __init__(self):
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
        
        if self.api_key:
            runpod.api_key = self.api_key
    
    def separate_audio(self, file_path, job_id):
        try:
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            job_input = {
                "audio_data": audio_base64,
                "file_name": os.path.basename(file_path)
            }
            
            if not self.endpoint_id:
                raise Exception("RunPod endpoint ID not configured")
            
            print(f"🚀 Submitting job to RunPod endpoint: {self.endpoint_id}")
            job = runpod.submit(self.endpoint_id, job_input)
            
            timeout = 300
            start_time = time.time()
            
            while True:
                job_status = runpod.get_job_status(job['id'])
                status = job_status.get('status', 'UNKNOWN')
                
                if status == 'COMPLETED':
                    output = job_status.get('output', {})
                    if output.get('status') == 'error':
                        raise Exception(f"RunPod error: {output.get('error')}")
                    return output
                elif status in ['FAILED', 'CANCELLED']:
                    raise Exception(f"RunPod job failed with status: {status}")
                elif time.time() - start_time > timeout:
                    raise Exception("RunPod job timeout")
                
                print(f"⏳ Job status: {status}, waiting...")
                time.sleep(3)
                
        except Exception as e:
            raise Exception(f"RunPod separation failed: {str(e)}")

runpod_client = RunPodClient()
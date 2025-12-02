import os
import base64
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def quick_test():
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = "whast4iifdcn9r"  # Your endpoint ID
    
    print("🚀 Testing REAL Demucs endpoint...")
    
    # Very small silent WAV file (base64 encoded)
    silent_wav = "UklGRnoAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoAAAB="
    
    payload = {
        "input": {
            "audio_data": silent_wav,
            "file_name": "test_silence.wav"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Submit job
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    print("📤 Sending test job...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            job = response.json()
            job_id = job.get("id")
            print(f"✅ Job submitted: {job_id}")
            
            # Check status
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
            
            for i in range(10):  # Check for 1 minute
                time.sleep(6)
                status_resp = requests.get(status_url, headers=headers)
                status_data = status_resp.json()
                status = status_data.get("status")
                
                print(f"📊 Poll {i+1}: {status}")
                
                if status == "COMPLETED":
                    output = status_data.get("output", {})
                    print("\n🎉 RESPONSE RECEIVED!")
                    print(f"Output keys: {list(output.keys())}")
                    
                    if "vocals" in output or "drums" in output:
                        print("✅ REAL DEMUCS WORKING! Found audio stems.")
                        for key in ["vocals", "drums", "bass", "other"]:
                            if key in output:
                                print(f"  {key}: {len(output[key])} chars")
                    else:
                        print(f"Output: {output}")
                    break
                elif status == "FAILED":
                    print(f"❌ Failed: {status_data.get('error')}")
                    break
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    quick_test()

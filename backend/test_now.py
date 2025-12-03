import os
import base64
import requests
import time
import wave
import struct
from dotenv import load_dotenv

load_dotenv()

def create_silent_wav(duration=1.0, sample_rate=44100):
    """Create a silent WAV file in memory"""
    n_samples = int(duration * sample_rate)
    
    # Create WAV bytes
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Create silent frames (16-bit, stereo)
            silent_data = struct.pack('<h', 0) * n_samples * 2
            wav_file.writeframes(silent_data)
        
        wav_bytes = wav_io.getvalue()
    
    return base64.b64encode(wav_bytes).decode('utf-8')

def quick_test():
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = "whast4iifdcn9r"
    
    print("🚀 Testing REAL Demucs endpoint...")
    print(f"📡 Endpoint: {endpoint_id}")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # Create a test audio file (1 second of silence)
    import io
    silent_wav = create_silent_wav(duration=1.0)
    
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
            
            max_polls = 20  # 2 minutes max
            for i in range(max_polls):
                time.sleep(6)
                
                try:
                    status_resp = requests.get(status_url, headers=headers, timeout=30)
                    status_data = status_resp.json()
                    status = status_data.get("status")
                    
                    print(f"📊 Poll {i+1}/{max_polls}: {status}")
                    
                    if status == "COMPLETED":
                        output = status_data.get("output", {})
                        print("\n" + "="*50)
                        print("🎉 RESPONSE RECEIVED!")
                        print("="*50)
                        
                        if "error" in output:
                            print(f"❌ Error: {output['error']}")
                        elif "vocals" in output or "drums" in output:
                            print("✅ REAL DEMUCS WORKING!")
                            print(f"Output keys: {list(output.keys())}")
                            
                            stems = ['vocals', 'drums', 'bass', 'other']
                            found = []
                            for stem in stems:
                                if stem in output:
                                    char_count = len(output[stem])
                                    size_kb = char_count * 3 / 4 / 1024
                                    print(f"  {stem}: {char_count:,} chars (~{size_kb:.1f} KB)")
                                    found.append(stem)
                            
                            if found:
                                print(f"\n✅ Found {len(found)} stems: {', '.join(found)}")
                            else:
                                print("⚠️ No audio stems found in output")
                        else:
                            print(f"⚠️ Unexpected output format")
                            print(f"Output keys: {list(output.keys())}")
                            if "message" in output:
                                print(f"Message: {output['message']}")
                        break
                        
                    elif status == "FAILED":
                        error = status_data.get("error", "Unknown error")
                        print(f"❌ Job failed: {error}")
                        break
                        
                    elif status == "IN_PROGRESS":
                        if i % 3 == 0:  # Every 3rd poll
                            print("⚡ GPU is processing...")
                    
                except Exception as e:
                    print(f"⚠️ Poll error: {str(e)}")
            
            if i == max_polls - 1:
                print("⏰ Timeout: Job took too long to complete")
                
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
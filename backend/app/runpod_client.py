# File: backend/app/runpod_client.py
import os,time,base64,requests,json
from dotenv import load_dotenv
class RunPodClient:
 def __init__(self):
  load_dotenv();self.api_key=os.getenv('RUNPOD_API_KEY');self.endpoint_id=os.getenv('RUNPOD_ENDPOINT_ID')
  if not self.api_key:raise ValueError("RUNPOD_API_KEY not found in environment")
  if not self.endpoint_id:raise ValueError("RUNPOD_ENDPOINT_ID not found in environment")
  print(f"✅ RunPod Client: Endpoint {self.endpoint_id[:8]}...")
 def separate_audio(self,file_path,job_id,output_format='mp3',quality='high'):
  try:
   with open(file_path,'rb')as f:audio_bytes=f.read()
   audio_base64=base64.b64encode(audio_bytes).decode('utf-8');filename=os.path.basename(file_path)
   payload={"input":{"audio_data":audio_base64,"file_name":filename,"quality":quality}}
   headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"}
   run_url=f"https://api.runpod.ai/v2/{self.endpoint_id}/run";print(f"🚀 Sending to RunPod: {len(audio_bytes)} bytes")
   response=requests.post(run_url,json=payload,headers=headers,timeout=60)
   if response.status_code!=200:
    print(f"❌ RunPod API error {response.status_code}: {response.text[:200] if response.text else 'No error message'}")
    return {"error": f"RunPod API error {response.status_code}: {response.text[:200] if response.text else 'No error message'}"}
   runpod_job=response.json()
   if isinstance(runpod_job,dict)and'id'in runpod_job:runpod_job_id=runpod_job.get("id")
   elif isinstance(runpod_job,dict)and'output'in runpod_job:return runpod_job
   else:return {"error": "Invalid RunPod response format"}
   if not runpod_job_id:return {"error": "No job ID returned from RunPod"}
   return self._poll_job_status(runpod_job_id)
  except requests.exceptions.Timeout:
   print(f"❌ RunPod timeout after 60 seconds")
   return {"error": "RunPod connection timeout (60s)"}
  except Exception as e:
   print(f"❌ RunPod connection error: {str(e)}")
   return {"error": f"RunPod connection error: {str(e)}"}
 def _poll_job_status(self,runpod_job_id):
  headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"};status_url=f"https://api.runpod.ai/v2/{self.endpoint_id}/status/{runpod_job_id}";max_attempts=30;print(f"⏳ Polling job: {runpod_job_id}")
  for attempt in range(max_attempts):
   time.sleep(5)
   try:
    response=requests.get(status_url,headers=headers,timeout=15)
    if response.status_code!=200:continue
    status_data=response.json();status=status_data.get("status")
    if status=="COMPLETED":
     output=status_data.get("output",{})
     if isinstance(output,str):
      try:output=json.loads(output)
      except:output={"output":output}
     if isinstance(output,dict):
      if"error"in output:return {"error": f"Handler error: {output['error']}"}
      if"stems"in output:return output
      elif"output"in output and isinstance(output["output"],dict)and"stems"in output["output"]:return output["output"]
      else:
       stems={key:output[key] for key in['vocals','drums','bass','other']if key in output}
       if stems:return {"stems":stems}
       return output
    elif status=="FAILED":return {"error": f"RunPod failed: {status_data.get('error','Unknown error')}"}
   except Exception as e:continue
  return {"error": f"RunPod timeout after {max_attempts*5} seconds"}
# File: runpod/handler.py
import runpod,torch,base64,tempfile,os,subprocess,time,json,sys,ssl
import soundfile as sf,numpy as np
print("=== SLICE LEMONADE WORKER ===")
print(f"PyTorch:{torch.__version__} CUDA:{torch.cuda.is_available()}")
os.environ['HF_HOME']='/tmp/huggingface'
os.environ['TORCH_HOME']='/tmp/torch'
os.environ['REQUESTS_CA_BUNDLE']='/etc/ssl/certs/ca-certificates.crt'
os.environ['SSL_CERT_FILE']='/etc/ssl/certs/ca-certificates.crt'
os.makedirs('/tmp/huggingface',exist_ok=True)
os.makedirs('/tmp/torch/hub/checkpoints',exist_ok=True)
os.chmod('/tmp/torch',0o777)
os.chmod('/tmp/torch/hub',0o777)
os.chmod('/tmp/torch/hub/checkpoints',0o777)
os.chmod('/tmp/huggingface',0o777)
import certifi
ssl._create_default_https_context=ssl._create_unverified_context
def init():return{"status":"ready"}
def handler(job):
    tmpdir=None
    try:
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        device="cuda"if torch.cuda.is_available()else"cpu"
        print(f"Loading model on {device}...")
        model=get_model('htdemucs')
        model.to(device).eval()
        print("? Model loaded")
        job_input=job.get("input",{})
        audio_base64=job_input.get("audio_data","")
        if not audio_base64:return{"error":"No audio data"}
        tmpdir=tempfile.mkdtemp()
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb')as f:f.write(base64.b64decode(audio_base64))
        audio,sr=sf.read(input_path)
        if len(audio.shape)==1:audio=np.stack([audio,audio],axis=0)
        audio=torch.from_numpy(audio).float()
        import torchaudio
        if sr!=44100:audio=torchaudio.functional.resample(audio,sr,44100)
        with torch.no_grad():
            stems=apply_model(model,audio[None],device=device,shifts=1,split=True,overlap=0.25)[0]
        stems_dict={}
        for i,name in enumerate(['vocals','drums','bass','other']):
            if i<len(stems):
                stem_path=os.path.join(tmpdir,f"{name}.wav")
                sf.write(stem_path,stems[i].cpu().numpy().T,44100)
                mp3_path=os.path.join(tmpdir,f"{name}.mp3")
                subprocess.run(['ffmpeg','-y','-i',stem_path,'-codec:a','libmp3lame','-b:a','320k','-q:a','0',mp3_path],capture_output=True,check=True)
                with open(mp3_path,'rb')as f:
                    stems_dict[name]=base64.b64encode(f.read()).decode()
        return{"stems":stems_dict,"status":"completed"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return{"error":f"Processing failed:{str(e)}"}
    finally:
        if tmpdir:
            import shutil
            shutil.rmtree(tmpdir,ignore_errors=True)
if __name__=="__main__":
    runpod.serverless.start({"handler":handler})
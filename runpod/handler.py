import runpod,torch,torchaudio,base64,tempfile,os,subprocess,time,json,gc
import soundfile as sf,numpy as np
print("=== SLICE LEMONADE SIMPLE FIX ===")
print(f"PyTorch:{torch.__version__} CUDA:{torch.cuda.is_available()}")
model,device=None,None
def load_model_simple():
    global model,device
    if model is not None:return True
    try:
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        device="cuda"if torch.cuda.is_available()else"cpu"
        print(f"Loading model on {device}...")
        model=get_model('htdemucs')
        model.to(device).eval()
        print(f"? Model loaded")
        return True
    except Exception as e:
        print(f"? Model load failed:{e}")
        return False
def init():
    if load_model_simple():
        return{"status":"loaded"}
    return{"status":"failed_will_retry"}
def handler(job):
    print("Handler called")
    if not load_model_simple():
        return{"error":"Model failed to load"}
    job_input=job.get("input",{})
    audio_base64=job_input.get("audio_data","")
    if not audio_base64:return{"error":"No audio"}
    tmpdir=tempfile.mkdtemp()
    try:
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb')as f:f.write(base64.b64decode(audio_base64))
        from demucs.apply import apply_model
        import soundfile as sf
        audio,sr=sf.read(input_path)
        if len(audio.shape)==1:audio=np.stack([audio,audio],axis=0)
        audio=torch.from_numpy(audio).float()
        if sr!=44100:audio=torchaudio.functional.resample(audio,sr,44100)
        with torch.no_grad():
            stems=apply_model(model,audio[None],device=device)[0]
        stems_dict={}
        for i,name in enumerate(['vocals','drums','bass','other']):
            if i<len(stems):
                stem_path=os.path.join(tmpdir,f"{name}.wav")
                sf.write(stem_path,stems[i].cpu().numpy().T,44100)
                mp3_path=os.path.join(tmpdir,f"{name}.mp3")
                subprocess.run(['ffmpeg','-y','-i',stem_path,'-codec:a','libmp3lame','-b:a','320k',mp3_path],capture_output=True)
                with open(mp3_path,'rb')as f:
                    stems_dict[name]=base64.b64encode(f.read()).decode()
        return{"stems":stems_dict,"status":"completed"}
    except Exception as e:
        return{"error":f"Processing failed:{str(e)}"}
    finally:
        import shutil
        shutil.rmtree(tmpdir,ignore_errors=True)
if __name__=="__main__":
    runpod.serverless.start({"handler":handler,"init":init})

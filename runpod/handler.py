import runpod,torch,torchaudio,base64,tempfile,os,subprocess,time,json,gc,warnings,requests
from demucs.pretrained import get_model as demucs_get_model
from demucs.apply import apply_model
import soundfile as sf,numpy as np
warnings.filterwarnings("ignore")
print("=== SLICE LEMONADE HDEMUCS WORKER FINAL FIX ===")
print(f"PyTorch:{torch.__version__} CUDA:{torch.cuda.is_available()}")
if torch.cuda.is_available():print(f"GPU:{torch.cuda.get_device_name(0)} Memory:{torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")
model,device=None,None
def load_model_with_retry(max_retries=3):
    global model,device
    if model is not None:return{"status":"already_loaded","device":str(device)}
    for attempt in range(max_retries):
        try:
            device="cuda"if torch.cuda.is_available()else"cpu"
            print(f"[Attempt {attempt+1}/{max_retries}] Loading htdemucs on {device}...")
            model=demucs_get_model('htdemucs')
            model.to(device).eval()
            print(f"? Model loaded on {device}")
            if torch.cuda.is_available():torch.cuda.empty_cache()
            return{"status":"loaded","device":str(device)}
        except Exception as e:
            print(f"? Attempt {attempt+1} failed:{str(e)}")
            if attempt<max_retries-1:
                time.sleep(5)
                gc.collect()
                if torch.cuda.is_available():torch.cuda.empty_cache()
    return{"status":"error","error":"All retries failed"}
def init():
    result=load_model_with_retry()
    if result["status"]=="error":
        print("?? Model failed during init, will retry in handler")
        return{"status":"will_retry"}
    return result
def load_audio(file_path,sr=44100):
    try:
        audio,sr_orig=sf.read(file_path)
        if len(audio.shape)==1:audio=np.stack([audio,audio],axis=0)
        elif audio.shape[0]>2:audio=audio[:2]
        audio=torch.from_numpy(audio).float()
        if sr_orig!=sr:audio=torchaudio.functional.resample(audio,sr_orig,sr)
        return audio
    except Exception as e:
        print(f"Audio load failed:{e}")
        waveform,sample_rate=torchaudio.load(file_path)
        if waveform.shape[0]>2:waveform=waveform[:2]
        if waveform.shape[0]==1:waveform=torch.cat([waveform,waveform])
        if sample_rate!=sr:
            resampler=torchaudio.transforms.Resample(sample_rate,sr)
            waveform=resampler(waveform)
        return waveform
def compress_to_mp3(input_path,output_path,quality='high'):
    quality_map={'high':['-codec:a','libmp3lame','-b:a','320k','-q:a','0'],'medium':['-codec:a','libmp3lame','-b:a','192k','-q:a','2'],'low':['-codec:a','libmp3lame','-b:a','128k','-q:a','4']}
    if quality not in quality_map:quality='high'
    cmd=['ffmpeg','-y','-i',input_path]+quality_map[quality]+[output_path]
    try:
        subprocess.run(cmd,capture_output=True,text=True,timeout=60,check=True)
        return True
    except Exception as e:raise Exception(f"MP3 conversion failed:{str(e)}")
def handler(job):
    print("\n"+"="*60)
    print("?? AUDIO SEPARATION REQUEST")
    print("="*60)
    start_time=time.time()
    job_input=job.get("input",{})
    audio_base64=job_input.get("audio_data","")
    filename=job_input.get("file_name","audio.wav")
    quality=job_input.get("quality","high").lower()
    if not audio_base64:return{"error":"No audio data"}
    print(f"File:{filename} Quality:{quality}")
    audio_bytes=base64.b64decode(audio_base64)
    print(f"Size:{len(audio_bytes):,} bytes ({len(audio_bytes)/1024/1024:.1f} MB)")
    tmpdir=tempfile.mkdtemp(prefix="slice_")
    print(f"Temp dir:{tmpdir}")
    try:
        if model is None:
            print("Loading model...")
            load_result=load_model_with_retry()
            if load_result["status"]!="loaded"and load_result["status"]!="already_loaded":
                return{"error":"Model failed to load","details":load_result.get("error","Unknown")}
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb')as f:f.write(audio_bytes)
        print(f"Processing on {device}...")
        demucs_start=time.time()
        mix=load_audio(input_path,sr=44100)
        if torch.cuda.is_available():torch.cuda.empty_cache()
        with torch.no_grad():
            stems=apply_model(model,mix[None],device=device,shifts=1,split=True,overlap=0.25,progress=False)[0]
        demucs_time=time.time()-demucs_start
        print(f"Demucs completed in {demucs_time:.1f}s")
        stem_names=['vocals','drums','bass','other']
        final_stems={}
        for i,stem_name in enumerate(stem_names):
            if i<len(stems):
                try:
                    stem_audio=stems[i]
                    stem_wav_path=os.path.join(tmpdir,f"{stem_name}.wav")
                    sf.write(stem_wav_path,stem_audio.cpu().numpy().T,44100)
                    mp3_path=os.path.join(tmpdir,f"{stem_name}.mp3")
                    if compress_to_mp3(stem_wav_path,mp3_path,quality):
                        with open(mp3_path,'rb')as f:mp3_bytes=f.read()
                        final_stems[stem_name]=base64.b64encode(mp3_bytes).decode('utf-8')
                        print(f"? {stem_name}:{len(mp3_bytes):,} bytes")
                except Exception as e:print(f"?? {stem_name} failed:{str(e)}")
        if not final_stems:return{"error":"No stems generated","stems_count":len(stems)}
        total_time=time.time()-start_time
        response={"stems":final_stems,"status":"completed","format":"mp3","quality":quality,"processing_time":round(total_time,1),"stems_count":len(final_stems)}
        print(f"\n? Success:{total_time:.1f}s,{len(final_stems)} stems")
        return response
    except Exception as e:
        error_msg=f"Handler error:{str(e)}"
        print(f"? {error_msg}")
        import traceback;traceback.print_exc()
        return{"error":error_msg}
    finally:
        try:
            import shutil
            shutil.rmtree(tmpdir,ignore_errors=True)
            if torch.cuda.is_available():torch.cuda.empty_cache()
            gc.collect()
        except:pass
if __name__=="__main__":
    print("?? Starting worker...")
    load_model_with_retry()
    runpod.serverless.start({"handler":handler})

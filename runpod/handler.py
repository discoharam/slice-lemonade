import runpod,torch,torchaudio,base64,tempfile,os,subprocess,time,json,gc,warnings
from demucs.pretrained import get_model as demucs_get_model
from demucs.apply import apply_model
import soundfile as sf,numpy as np
warnings.filterwarnings("ignore")
print("=== SLICE LEMONADE HDEMUCS WORKER v2 ===")
print(f"PyTorch:{torch.__version__} CUDA:{torch.cuda.is_available()}")
if torch.cuda.is_available():print(f"GPU:{torch.cuda.get_device_name(0)} Memory:{torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")
model,device=None,None
def load_model():
    global model,device
    if model is not None:return{"status":"already_loaded","device":str(device)}
    try:
        device="cuda"if torch.cuda.is_available()else"cpu"
        print(f"Loading htdemucs model on {device}...")
        model=demucs_get_model('htdemucs')
        model.to(device).eval()
        print(f"? Model loaded successfully on {device}")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print(f"GPU Memory allocated:{torch.cuda.memory_allocated()/1024**3:.1f}GB")
        return{"status":"loaded","device":str(device)}
    except Exception as e:
        error_msg=f"Model loading failed:{str(e)}"
        print(f"? {error_msg}")
        import traceback;traceback.print_exc()
        return{"status":"error","error":error_msg}
def init():
    result=load_model()
    if result["status"]=="error":
        print("?? Model failed to load during init - will retry during handler")
        return{"status":"will_retry","device":device}
    return result
def load_audio(file_path,sr=44100):
    try:
        waveform,sample_rate=torchaudio.load(file_path)
        if waveform.shape[0]>2:waveform=waveform[:2]
        if sample_rate!=sr:
            resampler=torchaudio.transforms.Resample(sample_rate,sr)
            waveform=resampler(waveform)
        if waveform.shape[0]==1:waveform=torch.cat([waveform,waveform])
        return waveform
    except Exception as e:
        print(f"TorchAudio failed:{e}, trying soundfile")
        try:
            audio,sr_orig=sf.read(file_path)
            if len(audio.shape)==1:audio=np.stack([audio,audio],axis=0)
            elif audio.shape[0]>2:audio=audio[:2]
            audio=torch.from_numpy(audio).float()
            if sr_orig!=sr:
                audio=torchaudio.functional.resample(audio,sr_orig,sr)
            return audio
        except Exception as e2:
            raise Exception(f"Audio loading failed:{e},{e2}")
def compress_audio_to_mp3(input_path,output_path,quality='high'):
    quality_map={'high':['-codec:a','libmp3lame','-b:a','320k','-q:a','0'],'medium':['-codec:a','libmp3lame','-b:a','192k','-q:a','2'],'low':['-codec:a','libmp3lame','-b:a','128k','-q:a','4']}
    if quality not in quality_map:quality='high'
    cmd=['ffmpeg','-y','-i',input_path]+quality_map[quality]+[output_path]
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        if result.returncode!=0:raise Exception(f"FFmpeg failed:{result.stderr[:200]}")
        return True
    except subprocess.TimeoutExpired:raise Exception("FFmpeg timeout")
    except Exception as e:raise Exception(f"Compression error:{str(e)}")
def handler(job):
    print("\n"+"="*60)
    print("?? AUDIO SEPARATION REQUEST RECEIVED")
    print("="*60)
    start_time=time.time()
    job_input=job.get("input",{})
    audio_base64=job_input.get("audio_data","")
    filename=job_input.get("file_name","audio.wav")
    quality=job_input.get("quality","high").lower()
    if not audio_base64:return{"error":"No audio data provided"}
    print(f"Processing:{filename} Quality:{quality}")
    audio_bytes=base64.b64decode(audio_base64)
    print(f"Input:{len(audio_bytes):,} bytes ({len(audio_bytes)/1024/1024:.1f} MB)")
    tmpdir=tempfile.mkdtemp(prefix="slice_")
    print(f"Temp dir:{tmpdir}")
    try:
        if model is None:
            print("Model not loaded, attempting to load now...")
            load_result=load_model()
            if load_result["status"]!="loaded"and load_result["status"]!="already_loaded":
                return{"error":"Failed to load model","details":load_result.get("error","Unknown")}
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb')as f:f.write(audio_bytes)
        print(f"Running Demucs on {device}...")
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
                    if compress_audio_to_mp3(stem_wav_path,mp3_path,quality):
                        with open(mp3_path,'rb')as f:mp3_bytes=f.read()
                        final_stems[stem_name]=base64.b64encode(mp3_bytes).decode('utf-8')
                        print(f"? {stem_name}:{len(mp3_bytes):,} bytes")
                    else:
                        print(f"?? {stem_name}:MP3 compression failed")
                except Exception as e:print(f"? Error processing {stem_name}:{str(e)}")
        if not final_stems:
            return{"error":"No audio stems generated","stems_generated":len(stems)}
        total_time=time.time()-start_time
        response={"stems":final_stems,"status":"completed","format":"mp3","quality":quality,"processing_time":round(total_time,1),"stems_count":len(final_stems)}
        print(f"\n? Processing complete:{total_time:.1f}s,{len(final_stems)} stems")
        print("="*60)
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
    print("?? Worker starting...")
    load_model()
    runpod.serverless.start({"handler":handler})

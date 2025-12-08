import runpod,torch,torchaudio,base64,tempfile,os,subprocess,time,json,gc,warnings
from demucs.pretrained import get_model
from demucs.apply import apply_model
import soundfile as sf,numpy as np
warnings.filterwarnings("ignore")
print("=== SLICE LEMONADE HDEMUCS WORKER ===")
print(f"PyTorch:{torch.__version__} CUDA:{torch.cuda.is_available()}")
if torch.cuda.is_available():print(f"GPU:{torch.cuda.get_device_name(0)}")
model,device=None,"cuda"if torch.cuda.is_available()else"cpu"
def init():
    global model
    print("Loading htdemucs model...")
    try:
        model=get_model('htdemucs')
        model.to(device).eval()
        print(f"Model loaded on {device}")
        if torch.cuda.is_available():print(f"GPU Memory:{torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")
        return{"status":"ready","device":device}
    except Exception as e:
        print(f"Model loading failed:{e}")
        return{"status":"error","error":str(e)}
def load_audio(file_path,sr=44100):
    try:
        waveform,sample_rate=torchaudio.load(file_path)
        if sample_rate!=sr:
            resampler=torchaudio.transforms.Resample(sample_rate,sr)
            waveform=resampler(waveform)
        return waveform
    except:
        audio,sr_orig=sf.read(file_path)
        audio=torch.from_numpy(audio).t().float()
        if sr_orig!=sr:
            audio=torchaudio.functional.resample(audio,sr_orig,sr)
        return audio
def compress_audio_to_mp3(input_path,output_path,quality='high'):
    quality_map={'high':['-codec:a','libmp3lame','-b:a','320k','-q:a','0'],'medium':['-codec:a','libmp3lame','-b:a','192k','-q:a','2'],'low':['-codec:a','libmp3lame','-b:a','128k','-q:a','4']}
    if quality not in quality_map:quality='high'
    cmd=['ffmpeg','-y','-i',input_path]+quality_map[quality]+[output_path]
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        if result.returncode!=0:raise Exception(f"FFmpeg failed:{result.stderr[:200]}")
        return True
    except subprocess.TimeoutExpired:raise Exception("FFmpeg timeout")
    except Exception as e:raise Exception(f"Compression error:{str(e)}")
def compress_if_too_large(mp3_path,target_size_mb=1.5):
    current_size=os.path.getsize(mp3_path)/1024/1024
    if current_size>target_size_mb:
        print(f"Optimizing large stem ({current_size:.1f}MB)...")
        temp_path=mp3_path+".temp.mp3"
        if current_size>3.0:bitrate='192k'
        elif current_size>2.0:bitrate='256k'
        elif current_size>1.5:bitrate='288k'
        else:return mp3_path
        cmd=['ffmpeg','-y','-i',mp3_path,'-codec:a','libmp3lame','-b:a',bitrate,'-q:a','2',temp_path]
        try:
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
            if result.returncode==0 and os.path.exists(temp_path):
                os.replace(temp_path,mp3_path)
                print(f"Optimized to {os.path.getsize(mp3_path)/1024/1024:.1f}MB")
        except:pass
    return mp3_path
def handler(job):
    print("Processing audio separation...")
    start_time=time.time()
    job_input=job.get("input",{})
    audio_base64=job_input.get("audio_data","")
    filename=job_input.get("file_name","audio.wav")
    quality=job_input.get("quality","high").lower()
    if not audio_base64:return{"error":"No audio data provided"}
    print(f"Processing:{filename} Quality:{quality}")
    audio_bytes=base64.b64decode(audio_base64)
    original_size=len(audio_bytes)
    print(f"Input:{original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
    tmpdir=tempfile.mkdtemp(prefix="slice_")
    print(f"Temp dir:{tmpdir}")
    try:
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb')as f:f.write(audio_bytes)
        if model is None:return{"error":"Model not loaded"}
        print(f"Running Demucs on {device}...")
        demucs_start=time.time()
        mix=load_audio(input_path,sr=44100)
        with torch.no_grad():
            stems=apply_model(model,mix[None],device=device,shifts=1,split=True,overlap=0.25,progress=False)[0]
        demucs_time=time.time()-demucs_start
        print(f"Demucs completed:{demucs_time:.1f}s")
        if torch.cuda.is_available():torch.cuda.empty_cache()
        gc.collect()
        stem_names=['vocals','drums','bass','other']
        final_stems,total_original,total_compressed={},0,0
        for i,stem_name in enumerate(stem_names):
            if i<len(stems):
                try:
                    stem_audio=stems[i]
                    stem_wav_path=os.path.join(tmpdir,f"{stem_name}.wav")
                    sf.write(stem_wav_path,stem_audio.cpu().numpy().T,44100)
                    wav_size=os.path.getsize(stem_wav_path)
                    total_original+=wav_size
                    mp3_path=os.path.join(tmpdir,f"{stem_name}.mp3")
                    if compress_audio_to_mp3(stem_wav_path,mp3_path,quality):
                        mp3_path=compress_if_too_large(mp3_path,target_size_mb=1.8)
                        with open(mp3_path,'rb')as f:mp3_bytes=f.read()
                        total_compressed+=len(mp3_bytes)
                        final_stems[stem_name]=base64.b64encode(mp3_bytes).decode('utf-8')
                        print(f"{stem_name}:{wav_size:,}→{len(mp3_bytes):,} bytes")
                except Exception as e:print(f"Error processing {stem_name}:{str(e)}")
        if not final_stems:return{"error":"No audio stems generated"}
        total_time=time.time()-start_time
        ratio=total_original/total_compressed if total_compressed>0 else 1
        response={"stems":final_stems,"status":"completed","format":"mp3","quality":quality,"processing_time":round(total_time,1),"stems_count":len(final_stems)}
        print(f"Processing summary:{total_time:.1f}s,{len(final_stems)} stems,ratio:{ratio:.1f}x")
        return response
    except Exception as e:
        error_msg=f"Handler error:{str(e)}"
        print(f"Error:{error_msg}")
        import traceback;traceback.print_exc()
        return{"error":error_msg}
    finally:
        try:
            import shutil
            shutil.rmtree(tmpdir,ignore_errors=True)
            print("Cleaned temp directory")
        except:pass
if __name__=="__main__":
    print("Worker ready")
    runpod.serverless.start({"handler":handler,"init":init})
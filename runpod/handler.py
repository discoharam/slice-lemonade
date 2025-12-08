# runpod/handler.py
import runpod,torch,base64,tempfile,os,subprocess,time,json,sys
import soundfile as sf,numpy as np
from demucs.pretrained import get_model
from demucs.apply import apply_model

# --- Global variables for the pre-loaded model and device ---
model=None
device=None

def init():
    """Initialize the worker once on cold start."""
    global model,device
    print("===> Slice Lemonade Worker: Initializing...")
    print(f"PyTorch:{torch.__version__} | CUDA Available:{torch.cuda.is_available()}")
    
    # --- Set environment variables for model caching ---
    os.environ['TORCH_HOME']='/tmp/torch'
    
    # --- Load model and move to GPU if available ---
    device="cuda" if torch.cuda.is_available() else "cpu"
    print(f"Attempting to load htdemucs model onto '{device}'...")
    try:
        model=get_model('htdemucs')
        model.to(device).eval()
        print("✅ Model loaded and ready.")
    except Exception as e:
        print(f"❌ FATAL: Could not load model in init: {e}")
        # Returning an error from init will prevent the worker from starting
        return {"error": f"Model load failed: {e}"}
    
    return {"status":"ready","model":"htdemucs"}

def handler(job):
    """Handle a single audio separation job."""
    global model,device
    
    # --- Health check for the model ---
    if model is None or device is None:
        print("❌ ERROR: Model not loaded. Worker failed to initialize.")
        return {"error":"Model is not loaded. Initialization failed."}

    print(f"--> Handling job {job.get('id', 'N/A')}")
    tmpdir=None
    try:
        job_input=job.get("input",{})
        audio_base64=job_input.get("audio_data","")
        if not audio_base64:return {"error":"No audio_data provided."}
        
        # --- Process audio data ---
        tmpdir=tempfile.mkdtemp(dir="/tmp")
        input_path=os.path.join(tmpdir,"input.wav")
        with open(input_path,'wb') as f:f.write(base64.b64decode(audio_base64))
        
        audio,sr=sf.read(input_path)
        if len(audio.shape)==1:audio=np.stack([audio,audio],axis=0) # Ensure stereo
        audio=torch.from_numpy(audio).float()
        
        if sr!=44100: # Resample if necessary
            import torchaudio
            audio=torchaudio.functional.resample(audio,sr,44100)

        # --- Apply the pre-loaded model ---
        print("Running separation...")
        with torch.no_grad():
            stems=apply_model(model,audio[None],device=device,shifts=1,split=True,overlap=0.25)[0]
        
        # --- Encode stems to MP3 and return ---
        stems_dict={}
        print("Encoding stems to MP3...")
        for i,name in enumerate(['vocals','drums','bass','other']):
            if i<len(stems):
                stem_path=os.path.join(tmpdir,f"{name}.wav")
                sf.write(stem_path,stems[i].cpu().numpy().T,44100)
                mp3_path=os.path.join(tmpdir,f"{name}.mp3")
                subprocess.run(['ffmpeg','-y','-i',stem_path,'-codec:a','libmp3lame','-b:a','320k','-q:a','0',mp3_path],capture_output=True,check=True)
                with open(mp3_path,'rb')as f:
                    stems_dict[name]=base64.b64encode(f.read()).decode()
        
        print("✅ Job complete. Returning stems.")
        return {"stems":stems_dict,"status":"completed"}

    except Exception as e:
        import traceback
        error_trace=traceback.format_exc()
        print(f"❌ PROCESSING FAILED: {e}\n{error_trace}")
        return {"error":f"Processing failed: {str(e)}"}
    finally:
        if tmpdir and os.path.exists(tmpdir):
            import shutil
            shutil.rmtree(tmpdir,ignore_errors=True)

if __name__=="__main__":
    runpod.serverless.start({"handler":handler,"init":init})

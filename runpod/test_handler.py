import runpod,torch,base64,tempfile,os,subprocess
import soundfile as sf,numpy as np
print("=== TEST WORKER ===")
os.environ["HF_HOME"]="/tmp/huggingface"
os.environ["TORCH_HOME"]="/tmp/torch"
os.makedirs("/tmp/torch/hub/checkpoints",exist_ok=True)
os.chmod("/tmp/torch/hub/checkpoints",0o777)
def handler(job):
    try:
        # Return dummy stems without model
        return {"stems":{
            "vocals":"dummy","drums":"dummy",
            "bass":"dummy","other":"dummy"
        },"status":"test"}
    except Exception as e:
        return {"error":str(e)}
if __name__=="__main__":
    runpod.serverless.start({"handler":handler})

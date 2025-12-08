import runpod

def init():
    print("=== TEST HANDLER v2.0 ===")
    print("If you see this, worker is UPDATED!")
    print("Demucs htdemucs should be available")
    return {"status": "ready", "version": "2.0-demucs"}

def handler(job):
    print("Test handler called - worker is working!")
    return {"status": "success", "message": "Worker is updated and responding", "test": True}

if __name__ == "__main__":
    print("Starting test worker...")
    runpod.serverless.start({"handler": handler, "init": init})

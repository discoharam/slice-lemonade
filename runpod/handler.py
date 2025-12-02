import runpod
import json

print("🚀 Slice Lemonade Handler Starting...")

def handler(job):
    """Simple handler for testing"""
    print(f"Processing job: {job.get('id', 'unknown')}")
    
    # Return a simple response
    return {
        "status": "success",
        "message": "Handler is working!",
        "test": True,
        "ready_for_demucs": True
    }

if __name__ == "__main__":
    print("✅ Handler initialized")
    print("📡 Starting RunPod serverless...")
    runpod.serverless.start({"handler": handler})

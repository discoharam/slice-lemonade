# handler.py - SIMPLE TEST VERSION
import runpod
import os
import sys

print("=" * 50)
print("🚀 Slice Lemonade Handler - TEST VERSION")
print("=" * 50)
print(f"Python: {sys.version}")
print(f"Current dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# Test imports
def test_imports():
    print("\n🔧 Testing imports...")
    
    imports_to_test = [
        "torch",
        "torch.cuda",
        "numpy",
        "demucs",
        "librosa",
        "soundfile"
    ]
    
    for import_name in imports_to_test:
        try:
            if import_name == "torch.cuda":
                import torch
                print(f"✅ torch.cuda: {torch.cuda.is_available()}")
            else:
                __import__(import_name)
                print(f"✅ {import_name}: OK")
        except Exception as e:
            print(f"❌ {import_name}: {str(e)}")

test_imports()

def handler(job):
    """Simple test handler"""
    print(f"\n🎯 Received job: {job.get('id')}")
    
    try:
        input_data = job.get("input", {})
        audio_data = input_data.get("audio_data", "")
        file_name = input_data.get("file_name", "test.wav")
        
        print(f"📁 File: {file_name}")
        print(f"📊 Data size: {len(audio_data)} chars")
        
        # Test if we can decode
        import base64
        if audio_data:
            try:
                decoded = base64.b64decode(audio_data[:100])  # Just first 100 chars
                print(f"✅ Can decode base64: {len(decoded)} bytes")
            except:
                print("⚠️ Cannot decode base64")
        
        # Return a simple success
        return {
            "status": "success",
            "message": "Handler is working!",
            "test_output": {
                "file": file_name,
                "data_size": len(audio_data)
            }
        }
        
    except Exception as e:
        print(f"❌ Error in handler: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("✅ Handler ready!")
    print("⚡ Waiting for jobs...")
    print("=" * 50)
    
    runpod.serverless.start({"handler": handler})

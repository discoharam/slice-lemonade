# handler.py - DEBUG VERSION
import runpod
import os
import sys
import traceback

print("🚀 Starting Slice Lemonade RunPod Handler...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

def test_imports():
    """Test if all required imports work"""
    print("\n🔧 Testing imports...")
    
    # Test basic imports
    try:
        import tempfile
        print("✅ tempfile: OK")
    except ImportError as e:
        print(f"❌ tempfile: {e}")
    
    try:
        import base64
        print("✅ base64: OK")
    except ImportError as e:
        print(f"❌ base64: {e}")
    
    try:
        from pathlib import Path
        print("✅ pathlib: OK")
    except ImportError as e:
        print(f"❌ pathlib: {e}")
    
    # Test PyTorch/CUDA
    try:
        import torch
        print(f"✅ torch: OK (version {torch.__version__})")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
    except ImportError as e:
        print(f"❌ torch: {e}")
    
    # Test Demucs
    try:
        import demucs.api
        print("✅ demucs.api: OK")
    except ImportError as e:
        print(f"❌ demucs.api: {e}")
        traceback.print_exc()

# Run import tests
test_imports()

def init_separator():
    """Try to load Demucs with detailed error reporting"""
    print("\n🎵 Attempting to load Demucs...")
    try:
        import demucs.api
        print("✅ Demucs imported successfully")
        
        # Check if CUDA is available for torch
        import torch
        if not torch.cuda.is_available():
            print("⚠️ CUDA not available, using CPU (this will be slow)")
            device = "cpu"
        else:
            print(f"✅ CUDA available on {torch.cuda.get_device_name(0)}")
            device = "cuda"
        
        print(f"🔄 Creating separator with device={device}...")
        separator = demucs.api.Separator(
            model="htdemucs", 
            device=device,
            progress=False
        )
        print("✅ Demucs separator created successfully!")
        return separator
        
    except Exception as e:
        print(f"❌ Failed to load Demucs: {str(e)}")
        traceback.print_exc()
        return None

separator = init_separator()

def separate_audio(job):
    """Handle audio separation with detailed error reporting"""
    print(f"\n🎯 Starting job: {job.get('id', 'unknown')}")
    
    try:
        job_input = job['input']
        audio_data = job_input.get('audio_data')
        file_name = job_input.get('file_name', 'audio.wav')
        
        if not audio_data:
            return {"error": "No audio data provided"}
        
        print(f"📁 Processing: {file_name}")
        print(f"📦 Audio data length: {len(audio_data)} chars")
        
        # Decode audio
        import base64
        audio_bytes = base64.b64decode(audio_data)
        print(f"📦 Audio bytes: {len(audio_bytes)} bytes")
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        print(f"📁 Saved to: {temp_path}")
        
        try:
            if separator is None:
                print("⚠️ Demucs not available, returning test data")
                # Return test data for debugging
                return {
                    "status": "test",
                    "message": "Demucs not loaded, returning test stems",
                    "results": {
                        "vocals": "test_vocals",
                        "drums": "test_drums", 
                        "bass": "test_bass",
                        "other": "test_other"
                    }
                }
            
            print("🔬 Starting Demucs separation...")
            origin, separated = separator.separate_audio_file(temp_path)
            print(f"✅ Separation complete, got {len(separated)} sources: {list(separated.keys())}")
            
            # Process each stem
            results = {}
            for source, audio in separated.items():
                print(f"💾 Processing {source}...")
                
                import io
                buffer = io.BytesIO()
                separator.save_audio(audio, buffer, samplerate=separator.samplerate)
                buffer.seek(0)
                
                audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                results[source] = audio_base64
                print(f"✅ {source}: {len(audio_base64)} chars")
            
            return {
                "status": "success",
                "results": results,
                "message": f"Separated {len(results)} stems"
            }
            
        finally:
            # Clean up
            try:
                os.unlink(temp_path)
                print(f"🧹 Cleaned up {temp_path}")
            except:
                pass
                
    except Exception as e:
        error_msg = f"❌ Job failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        return {
            "status": "error",
            "error": error_msg
        }

if __name__ == "__main__":
    print("\n🍋 Slice Lemonade Handler Status:")
    print(f"   Demucs loaded: {'✅ Yes' if separator else '❌ No'}")
    print("⚡ Waiting for jobs...")
    
    # Add error handling for serverless start
    try:
        runpod.serverless.start({"handler": separate_audio})
    except Exception as e:
        print(f"❌ Failed to start serverless: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

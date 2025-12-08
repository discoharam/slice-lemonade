import os
import sys
import tempfile
import struct

def create_test_wav(duration_sec=1, sample_rate=44100):
    """Create a proper test WAV file with actual audio data"""
    num_samples = duration_sec * sample_rate
    num_channels = 2
    bits_per_sample = 16
    
    # Generate simple sine wave
    import numpy as np
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    freq = 440  # A4 note
    sine_wave = 0.3 * np.sin(2 * np.pi * freq * t)
    
    # Convert to 16-bit PCM
    audio_data = (sine_wave * 32767).astype(np.int16)
    
    # Create stereo by duplicating
    stereo_data = np.column_stack([audio_data, audio_data])
    
    # Create WAV file
    byte_data = stereo_data.tobytes()
    
    # Build WAV header
    chunk_size = 36 + len(byte_data)
    subchunk_size = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        chunk_size,
        b'WAVE',
        b'fmt ',
        subchunk_size,
        1,  # PCM format
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        len(byte_data)
    )
    
    return wav_header + byte_data

def test_handler():
    print("Testing handler with proper audio...")
    try:
        from handler import handler, init
        
        print("Initializing...")
        init_result = init()
        print(f"Init result: {init_result}")
        
        # Create a real WAV file with actual audio
        test_wav = create_test_wav(duration_sec=2)  # 2-second test audio
        import base64
        test_audio_base64 = base64.b64encode(test_wav).decode('utf-8')
        
        test_job = {
            "input": {
                "audio_data": test_audio_base64,
                "file_name": "test.wav",
                "quality": "high"
            }
        }
        
        print("Running handler...")
        result = handler(test_job)
        
        print(f"Result keys: {list(result.keys())}")
        if "error" in result:
            print(f"❌ Test failed: {result['error']}")
            return False
        else:
            print(f"✅ Test passed - generated {result.get('stems_count', 0)} stems")
            print(f"   Stems: {list(result.get('stems', {}).keys())}")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_handler()
    sys.exit(0 if success else 1)
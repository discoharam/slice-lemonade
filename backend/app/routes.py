@main.route('/api/test-runpod', methods=['POST'])
def test_runpod():
    """Test endpoint to verify RunPod connection"""
    try:
        # Create a small test audio file
        import io
        import wave
        import struct
        import base64
        
        # Create 1 second of silence
        sample_rate = 44100
        n_samples = sample_rate
        silent_data = struct.pack('<h', 0) * n_samples * 2  # 16-bit stereo
        
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(silent_data)
            
            audio_bytes = wav_io.getvalue()
        
        # Send to RunPod
        from .runpod_client import runpod_client
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        result = runpod_client.separate_audio(tmp_path, "test-runpod")
        
        # Clean up
        os.unlink(tmp_path)
        
        return jsonify({
            "status": "test_complete",
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
#!/usr/bin/env python3
"""
Simple test for handler response format (without Demucs)
"""
import json
import base64

def test_response_format():
    """Test the response format the handler should return"""
    
    # Create mock stems with minimal base64 data
    mock_stems = {
        "vocals": base64.b64encode(b"mock_vocals_data").decode('utf-8'),
        "drums": base64.b64encode(b"mock_drums_data").decode('utf-8'),
        "bass": base64.b64encode(b"mock_bass_data").decode('utf-8'),
        "other": base64.b64encode(b"mock_other_data").decode('utf-8')
    }
    
    # Test different response formats
    
    print("🧪 Testing Response Formats")
    print("="*50)
    
    # Format 1: Direct stems (what our new handler should return)
    format1 = {
        "stems": mock_stems,
        "status": "completed",
        "format": "mp3",
        "quality": "medium",
        "processing_time": 10.5,
        "stems_count": 4
    }
    
    # Format 2: Wrapped by RunPod (what backend receives)
    format2 = {"output": format1}
    
    # Format 3: Double nesting (current bug)
    format3 = {"output": {"output": format1}}
    
    print("\n1. Direct Response (handler return):")
    print(f"   Keys: {list(format1.keys())}")
    print(f"   Has 'stems'? {'stems' in format1}")
    size1 = len(json.dumps(format1).encode('utf-8'))
    print(f"   Size: {size1:,} bytes ({size1/1024:.1f} KB)")
    
    print("\n2. Wrapped by RunPod (backend receives):")
    print(f"   Keys: {list(format2.keys())}")
    print(f"   Has 'output'? {'output' in format2}")
    size2 = len(json.dumps(format2).encode('utf-8'))
    print(f"   Size: {size2:,} bytes ({size2/1024:.1f} KB)")
    
    print("\n3. Double Nesting (current bug):")
    print(f"   Keys: {list(format3.keys())}")
    print(f"   Has 'output.output'? {'output' in format3 and isinstance(format3['output'], dict) and 'output' in format3['output']}")
    size3 = len(json.dumps(format3).encode('utf-8'))
    print(f"   Size: {size3:,} bytes ({size3/1024:.1f} KB)")
    
    print("\n📊 Size Comparison:")
    print(f"   Format 1: {size1:,} bytes")
    print(f"   Format 2: {size2:,} bytes (+{(size2-size1)/size1*100:.1f}%)")
    print(f"   Format 3: {size3:,} bytes (+{(size3-size1)/size1*100:.1f}%)")
    
    print("\n✅ Target: Handler returns Format 1")
    print("✅ Backend receives Format 2")
    print("❌ Bug: Currently getting Format 3")
    
    return format1

if __name__ == "__main__":
    test_response_format()
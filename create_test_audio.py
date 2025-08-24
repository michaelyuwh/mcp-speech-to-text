#!/usr/bin/env python3
"""
Create a sample audio file for testing transcription
"""

import sys
import os
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

def create_test_audio():
    """Create a simple test audio file."""
    
    print("🎵 Creating test audio file...")
    
    # Create a 3-second sine wave at 440Hz (A note)
    tone = Sine(440).to_audio_segment(duration=3000)  # 3 seconds
    
    # Export as WAV
    output_path = "/tmp/test_audio.wav"
    tone.export(output_path, format="wav")
    
    print(f"   ✅ Created: {output_path}")
    print(f"   📏 Duration: 3 seconds")
    print(f"   🎼 Frequency: 440Hz (A note)")
    
    return output_path

if __name__ == "__main__":
    try:
        audio_file = create_test_audio()
        print(f"\n🎉 Test audio file ready: {audio_file}")
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        sys.exit(1)

// frontend/src/utils/monoConverter.ts
export class MonoConverter {
  /**
   * Convert stereo audio to mono
   */
  static async convertToMono(audioBuffer: ArrayBuffer, sampleRate: number = 44100): Promise<ArrayBuffer> {
    return new Promise((resolve, reject) => {
      try {
        // Create AudioContext
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
          sampleRate: sampleRate
        });
        
        // Decode the audio data
        audioContext.decodeAudioData(audioBuffer.slice(0), (originalBuffer) => {
          try {
            // Get number of channels
            const numberOfChannels = originalBuffer.numberOfChannels;
            
            if (numberOfChannels === 1) {
              // Already mono, return as-is
              resolve(audioBuffer);
              audioContext.close();
              return;
            }
            
            // Create mono buffer
            const monoBuffer = audioContext.createBuffer(
              1, // mono
              originalBuffer.length,
              originalBuffer.sampleRate
            );
            
            // Mix channels to mono
            const monoData = monoBuffer.getChannelData(0);
            
            // For stereo (2 channels), mix both channels
            if (numberOfChannels === 2) {
              const leftData = originalBuffer.getChannelData(0);
              const rightData = originalBuffer.getChannelData(1);
              
              for (let i = 0; i < originalBuffer.length; i++) {
                // Average both channels for mono
                monoData[i] = (leftData[i] + rightData[i]) / 2;
              }
            } else {
              // For more than 2 channels, mix all channels
              for (let i = 0; i < originalBuffer.length; i++) {
                let sum = 0;
                for (let channel = 0; channel < numberOfChannels; channel++) {
                  sum += originalBuffer.getChannelData(channel)[i];
                }
                monoData[i] = sum / numberOfChannels;
              }
            }
            
            // Encode to WAV format
            const wavBuffer = this.encodeWAV(monoBuffer);
            
            audioContext.close();
            resolve(wavBuffer);
          } catch (error) {
            audioContext.close();
            reject(new Error(`Failed to convert to mono: ${error.message}`));
          }
        }, (error) => {
          audioContext.close();
          reject(new Error(`Failed to decode audio: ${error.message}`));
        });
      } catch (error) {
        reject(new Error(`AudioContext creation failed: ${error.message}`));
      }
    });
  }
  
  /**
   * Encode AudioBuffer to WAV format
   */
  private static encodeWAV(buffer: AudioBuffer): ArrayBuffer {
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const bitsPerSample = 16;
    const bytesPerSample = bitsPerSample / 8;
    const blockAlign = numberOfChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = buffer.length * numberOfChannels * bytesPerSample;
    const bufferSize = 44 + dataSize;
    
    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);
    
    // Write WAV header
    // RIFF identifier
    this.writeString(view, 0, 'RIFF');
    // RIFF chunk length
    view.setUint32(4, 36 + dataSize, true);
    // RIFF type
    this.writeString(view, 8, 'WAVE');
    // Format chunk identifier
    this.writeString(view, 12, 'fmt ');
    // Format chunk length
    view.setUint32(16, 16, true);
    // Sample format (PCM)
    view.setUint16(20, 1, true);
    // Channel count
    view.setUint16(22, numberOfChannels, true);
    // Sample rate
    view.setUint32(24, sampleRate, true);
    // Byte rate (sample rate * block align)
    view.setUint32(28, byteRate, true);
    // Block align (channel count * bytes per sample)
    view.setUint16(32, blockAlign, true);
    // Bits per sample
    view.setUint16(34, bitsPerSample, true);
    // Data chunk identifier
    this.writeString(view, 36, 'data');
    // Data chunk length
    view.setUint32(40, dataSize, true);
    
    // Write audio data
    const channelData = buffer.getChannelData(0);
    let offset = 44;
    
    for (let i = 0; i < buffer.length; i++) {
      // Convert float to 16-bit PCM
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
    
    return arrayBuffer;
  }
  
  /**
   * Write string to DataView
   */
  private static writeString(view: DataView, offset: number, string: string): void {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
  
  /**
   * Check if audio file is stereo
   */
  static async checkIfStereo(audioBuffer: ArrayBuffer): Promise<boolean> {
    return new Promise((resolve, reject) => {
      try {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        
        audioContext.decodeAudioData(audioBuffer.slice(0), (buffer) => {
          audioContext.close();
          resolve(buffer.numberOfChannels > 1);
        }, (error) => {
          audioContext.close();
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Convert ArrayBuffer to Blob for download
   */
  static arrayBufferToBlob(arrayBuffer: ArrayBuffer, mimeType: string = 'audio/wav'): Blob {
    return new Blob([arrayBuffer], { type: mimeType });
  }
  
  /**
   * Download converted mono file
   */
  static downloadMonoFile(arrayBuffer: ArrayBuffer, filename: string): void {
    const blob = this.arrayBufferToBlob(arrayBuffer);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = this.addMonoSuffix(filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
  
  /**
   * Add "-mono" suffix to filename
   */
  static addMonoSuffix(filename: string): string {
    const lastDotIndex = filename.lastIndexOf('.');
    if (lastDotIndex === -1) {
      return filename + '-mono';
    }
    return filename.substring(0, lastDotIndex) + '-mono' + filename.substring(lastDotIndex);
  }
}
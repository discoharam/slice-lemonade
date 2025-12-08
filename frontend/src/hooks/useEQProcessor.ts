// frontend/src/hooks/useEQProcessor.ts
import { useState, useRef, useCallback } from 'react';

export interface EQSettings {
  enabled: boolean;
  low: {
    gain: number;     // -12 to +12 dB
    frequency: number; // 80-250 Hz
  };
  high: {
    gain: number;     // -12 to +12 dB
    frequency: number; // 4000-16000 Hz
  };
}

export interface EQPreset {
  id: string;
  name: string;
  description: string;
  settings: Partial<EQSettings>;
  icon: string;
}

export const useEQProcessor = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Default EQ settings
  const defaultEQSettings: EQSettings = {
    enabled: false,
    low: {
      gain: 0,
      frequency: 120
    },
    high: {
      gain: 0,
      frequency: 8000
    }
  };

  // Initialize AudioContext
  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return audioContextRef.current;
  }, []);

  // Process audio buffer with EQ
  const processAudioWithEQ = useCallback(async (
    audioBuffer: ArrayBuffer,
    eqSettings: EQSettings
  ): Promise<ArrayBuffer> => {
    if (!eqSettings.enabled) {
      return audioBuffer;
    }

    setIsProcessing(true);
    
    try {
      const audioContext = getAudioContext();
      
      // Decode audio data
      const originalBuffer = await audioContext.decodeAudioData(audioBuffer.slice(0));
      
      // Create offline context for processing
      const offlineContext = new OfflineAudioContext(
        originalBuffer.numberOfChannels,
        originalBuffer.length,
        originalBuffer.sampleRate
      );
      
      // Create source
      const source = offlineContext.createBufferSource();
      source.buffer = originalBuffer;
      
      // Create EQ nodes
      const lowShelf = offlineContext.createBiquadFilter();
      lowShelf.type = 'lowshelf';
      lowShelf.frequency.value = eqSettings.low.frequency;
      lowShelf.gain.value = eqSettings.low.gain;
      
      const highShelf = offlineContext.createBiquadFilter();
      highShelf.type = 'highshelf';
      highShelf.frequency.value = eqSettings.high.frequency;
      highShelf.gain.value = eqSettings.high.gain;
      
      // Connect audio chain
      source.connect(lowShelf);
      lowShelf.connect(highShelf);
      highShelf.connect(offlineContext.destination);
      
      // Start processing
      source.start(0);
      const processedBuffer = await offlineContext.startRendering();
      
      // Convert back to ArrayBuffer (WAV format)
      const wavBuffer = encodeAudioBufferToWav(processedBuffer);
      
      setIsProcessing(false);
      return wavBuffer;
      
    } catch (error) {
      console.error('EQ processing error:', error);
      setIsProcessing(false);
      throw new Error(`EQ processing failed: ${error}`);
    }
  }, [getAudioContext]);

  // Apply EQ in real-time for preview
  const createEQPreview = useCallback((
    audioUrl: string,
    eqSettings: EQSettings,
    onUpdate?: (buffer: AudioBuffer) => void
  ) => {
    if (!eqSettings.enabled) return null;
    
    const audioContext = getAudioContext();
    const source = audioContext.createBufferSource();
    const lowShelf = audioContext.createBiquadFilter();
    const highShelf = audioContext.createBiquadFilter();
    
    // Setup EQ
    lowShelf.type = 'lowshelf';
    lowShelf.frequency.value = eqSettings.low.frequency;
    lowShelf.gain.value = eqSettings.low.gain;
    
    highShelf.type = 'highshelf';
    highShelf.frequency.value = eqSettings.high.frequency;
    highShelf.gain.value = eqSettings.high.gain;
    
    // Connect chain
    source.connect(lowShelf);
    lowShelf.connect(highShelf);
    highShelf.connect(audioContext.destination);
    
    return {
      source,
      lowShelf,
      highShelf,
      updateSettings: (newSettings: EQSettings) => {
        lowShelf.frequency.value = newSettings.low.frequency;
        lowShelf.gain.value = newSettings.low.gain;
        highShelf.frequency.value = newSettings.high.frequency;
        highShelf.gain.value = newSettings.high.gain;
      }
    };
  }, [getAudioContext]);

  // Encode AudioBuffer to WAV format
  const encodeAudioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const numChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const bitsPerSample = 16;
    const bytesPerSample = bitsPerSample / 8;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = buffer.length * numChannels * bytesPerSample;
    const bufferSize = 44 + dataSize;
    
    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);
    
    // Write WAV header
    // RIFF identifier
    writeString(view, 0, 'RIFF');
    // RIFF chunk length
    view.setUint32(4, 36 + dataSize, true);
    // RIFF type
    writeString(view, 8, 'WAVE');
    // Format chunk identifier
    writeString(view, 12, 'fmt ');
    // Format chunk length
    view.setUint32(16, 16, true);
    // Sample format (PCM)
    view.setUint16(20, 1, true);
    // Channel count
    view.setUint16(22, numChannels, true);
    // Sample rate
    view.setUint32(24, sampleRate, true);
    // Byte rate
    view.setUint32(28, byteRate, true);
    // Block align
    view.setUint16(32, blockAlign, true);
    // Bits per sample
    view.setUint16(34, bitsPerSample, true);
    // Data chunk identifier
    writeString(view, 36, 'data');
    // Data chunk length
    view.setUint32(40, dataSize, true);
    
    // Write audio data
    let offset = 44;
    for (let i = 0; i < buffer.length; i++) {
      for (let channel = 0; channel < numChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
      }
    }
    
    return arrayBuffer;
  };

  // Helper function to write string to DataView
  const writeString = (view: DataView, offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  // Download EQ-processed audio
  const downloadWithEQ = async (
    audioBuffer: ArrayBuffer,
    eqSettings: EQSettings,
    filename: string,
    mimeType: string = 'audio/wav'
  ) => {
    try {
      const processedBuffer = await processAudioWithEQ(audioBuffer, eqSettings);
      const blob = new Blob([processedBuffer], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = addEQSuffix(filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download with EQ failed:', error);
      throw error;
    }
  };

  // Add "-eq" suffix to filename
  const addEQSuffix = (filename: string): string => {
    const lastDotIndex = filename.lastIndexOf('.');
    if (lastDotIndex === -1) {
      return filename + '-eq';
    }
    return filename.substring(0, lastDotIndex) + '-eq' + filename.substring(lastDotIndex);
  };

  // Cleanup
  const cleanup = useCallback(() => {
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  }, []);

  return {
    defaultEQSettings,
    isProcessing,
    processAudioWithEQ,
    createEQPreview,
    downloadWithEQ,
    cleanup
  };
};
// frontend/src/types/eq.ts
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
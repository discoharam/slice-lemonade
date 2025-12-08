declare module 'wavesurfer.js' {
  interface WaveSurferOptions {
    container: string | HTMLElement;
    waveColor?: string;
    progressColor?: string;
    cursorColor?: string;
    cursorWidth?: number;
    barWidth?: number;
    barRadius?: number;
    barGap?: number;
    height?: number;
    width?: number;
    responsive?: boolean;
    normalize?: boolean;
    backend?: 'WebAudio' | 'MediaElement';
    mediaControls?: boolean;
    autoplay?: boolean;
    interact?: boolean;
    hideScrollbar?: boolean;
    audioRate?: number;
    autoCenter?: boolean;
    splitChannels?: boolean;
    plugins?: any[];
    xhr?: {
      requestHeaders?: { key: string; value: string }[];
      withCredentials?: boolean;
    };
  }

  interface WaveSurfer {
    load(url: string | File | Blob): void;
    play(start?: number, end?: number): void;
    pause(): void;
    stop(): void;
    destroy(): void;
    empty(): void;
    setVolume(volume: number): void;
    getVolume(): number;
    toggleMute(): void;
    setMute(mute: boolean): void;
    getCurrentTime(): number;
    getDuration(): number;
    seekTo(progress: number): void;
    skip(offset: number): void;
    skipBackward(seconds?: number): void;
    skipForward(seconds?: number): void;
    setPlaybackRate(rate: number): void;
    getPlaybackRate(): number;
    exportImage(format?: string, quality?: number, type?: string): string;
    exportPCM(length?: number, accuracy?: number, noWindow?: boolean): number[];
    on(event: string, callback: (...args: any[]) => void): void;
    once(event: string, callback: (...args: any[]) => void): void;
    un(event: string, callback: (...args: any[]) => void): void;
    unAll(): void;
  }

  const WaveSurfer: {
    create(options: WaveSurferOptions): WaveSurfer;
  };

  export default WaveSurfer;
}
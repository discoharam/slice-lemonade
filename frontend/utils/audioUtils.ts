// frontend/src/utils/audioUtils.ts
import { StemData } from '../types';

const BACKEND_URL = "http://localhost:5000";

export const getAudioUrl = (jobId: string, trackName: string, format: string): string => {
  return `${BACKEND_URL}/audio/${encodeURIComponent(jobId)}/${encodeURIComponent(trackName)}.${format}`;
};

export const getStemIconType = (track: string): 'vocals' | 'drums' | 'bass' | 'other' => {
  const normalizedTrack = track.toLowerCase();
  
  if (normalizedTrack.includes('vocal')) return 'vocals';
  if (normalizedTrack.includes('drum')) return 'drums';
  if (normalizedTrack.includes('bass')) return 'bass';
  return 'other';
};

export const getFormatInfo = (format: string) => {
  switch(format) {
    case 'mp3': return { 
      color: 'bg-emerald-500/10 border-emerald-500/20',
      textColor: 'text-emerald-700',
      desc: '320kbps',
      iconColor: 'text-emerald-500'
    };
    case 'wav': return { 
      color: 'bg-blue-500/10 border-blue-500/20',
      textColor: 'text-blue-700',
      desc: '24-bit',
      iconColor: 'text-blue-500'
    };
    case 'flac': return { 
      color: 'bg-purple-500/10 border-purple-500/20',
      textColor: 'text-purple-700',
      desc: 'Lossless',
      iconColor: 'text-purple-500'
    };
    default: return { 
      color: 'bg-gray-500/10 border-gray-500/20',
      textColor: 'text-gray-700',
      desc: format.toUpperCase(),
      iconColor: 'text-gray-500'
    };
  }
};

export const getAvailableFormats = (stemData: StemData): string[] => {
  return Object.keys(stemData.formats || {});
};

export const normalizeStemName = (stemName: string): string => {
  const normalized = stemName.toLowerCase();
  
  const stemMap: Record<string, string> = {
    'vocal': 'vocals',
    'drum': 'drums',
    'bass': 'bass',
    'other': 'other',
  };
  
  if (stemMap[normalized]) {
    return stemMap[normalized];
  }
  
  for (const [key, value] of Object.entries(stemMap)) {
    if (normalized.includes(key)) {
      return value;
    }
  }
  
  return normalized;
};

export const formatTrackName = (trackName: string): string => {
  const normalized = normalizeStemName(trackName);
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
};
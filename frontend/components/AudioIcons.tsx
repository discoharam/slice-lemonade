// frontend/src/components/AudioIcons.tsx
import React from 'react';

interface AudioIconProps {
  type: 'vocals' | 'drums' | 'bass' | 'other' | 'eq' | 'mono' | 'stereo' | 'waveform' | 'download' | 'play' | 'pause' | 'volume' | 'settings';
  className?: string;
}

const AudioIcons: React.FC<AudioIconProps> = ({ type, className = 'w-5 h-5' }) => {
  switch (type) {
    case 'vocals':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 15c-1.66 0-3-1.34-3-3V5c0-1.66 1.34-3 3-3s3 1.34 3 3v7c0 1.66-1.34 3-3 3z"/>
          <path d="M17 12c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-2.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
      );
    
    case 'drums':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
          <line x1="12" y1="2" x2="12" y2="22" strokeWidth="2" stroke="currentColor"/>
          <line x1="2" y1="12" x2="22" y2="12" strokeWidth="2" stroke="currentColor"/>
        </svg>
      );
    
    case 'bass':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <rect x="3" y="6" width="18" height="12" rx="2"/>
          <line x1="7" y1="6" x2="7" y2="18" strokeWidth="2" stroke="currentColor"/>
          <line x1="17" y1="6" x2="17" y2="18" strokeWidth="2" stroke="currentColor"/>
          <circle cx="12" cy="12" r="2"/>
        </svg>
      );
    
    case 'other':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
          <circle cx="8.5" cy="10.5" r="1.5"/>
          <circle cx="15.5" cy="10.5" r="1.5"/>
          <path d="M12 16c-1.48 0-2.75-.81-3.45-2H6.88c.8 2.05 2.79 3.5 5.12 3.5s4.32-1.45 5.12-3.5h-1.67c-.7 1.19-1.97 2-3.45 2z"/>
        </svg>
      );
    
    case 'eq':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="2" y="4" width="20" height="16" rx="2"/>
          <path d="M7 10v4"/>
          <path d="M12 8v8"/>
          <path d="M17 6v12"/>
        </svg>
      );
    
    case 'mono':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v12"/>
          <path d="M8 9h8"/>
          <path d="M8 15h8"/>
        </svg>
      );
    
    case 'stereo':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <circle cx="8" cy="12" r="3"/>
          <circle cx="16" cy="12" r="3"/>
          <path d="M8 15v-6"/>
          <path d="M16 15v-6"/>
        </svg>
      );
    
    case 'waveform':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 12h2l2-6 2 12 2-6 2 6 2-12 2 6h2"/>
        </svg>
      );
    
    case 'download':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      );
    
    case 'play':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5,3 19,12 5,21"/>
        </svg>
      );
    
    case 'pause':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="4" width="4" height="16"/>
          <rect x="14" y="4" width="4" height="16"/>
        </svg>
      );
    
    case 'volume':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
        </svg>
      );
    
    case 'settings':
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      );
    
    default:
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10"/>
        </svg>
      );
  }
};

export default AudioIcons;
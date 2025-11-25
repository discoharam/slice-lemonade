export interface SeparationJob {
  job_id: string;
  status: 'processing' | 'completed' | 'error';
  results?: {
    [key: string]: string;
  };
  error?: string;
  timestamp?: string;
  message?: string;
}

export interface AudioFile {
  name: string;
  size: number;
  type: string;
  lastModified: number;
}

export interface TrackInfo {
  name: string;
  url: string;
  type: 'vocals' | 'drums' | 'bass' | 'other' | string;
}
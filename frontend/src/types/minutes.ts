// frontend/src/types/minutes.ts - CONFIRM THIS EXISTS
export interface MinutesPlan {
  id: string;
  name: string;
  minutes: number;
  price: number;
  description: string;
  features: string[];
  popular?: boolean;
}

export interface UserMinutes {
  total: number;
  used: number;
  remaining: number;
  lastUpdated: string;
}

export interface ProcessingEstimate {
  fileSizeMB: number;
  estimatedMinutes: number;
  complexity: 'low' | 'medium' | 'high';
}
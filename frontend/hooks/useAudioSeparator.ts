import { useState } from 'react';
import { SeparationJob } from '../types';
import { separateAudio, downloadTrack as getDownloadUrl } from '../utils/api';

export const useAudioSeparator = () => {
  const [currentJob, setCurrentJob] = useState<SeparationJob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const separateAudioFile = async (file: File) => {
    setIsProcessing(true);
    setProgress(0);
    setCurrentJob(null);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 1000);

      const result = await separateAudio(file);
      
      clearInterval(progressInterval);
      setProgress(100);
      setCurrentJob(result);
      
      return result;
    } catch (error: any) {
      const errorJob: SeparationJob = {
        job_id: 'error',
        status: 'error',
        error: error.response?.data?.error || error.message || 'Separation failed'
      };
      setCurrentJob(errorJob);
      throw error;
    } finally {
      setIsProcessing(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  const downloadTrack = (jobId: string, trackName: string) => {
    const url = getDownloadUrl(jobId, trackName);
    window.open(url, '_blank');
  };

  const reset = () => {
    setCurrentJob(null);
    setIsProcessing(false);
    setProgress(0);
  };

  return {
    separateAudio: separateAudioFile,
    downloadTrack,
    currentJob,
    isProcessing,
    progress,
    reset
  };
};
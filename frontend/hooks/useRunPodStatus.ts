import { useState, useEffect } from 'react';
import { checkJobStatus } from '../utils/api';

export const useRunPodStatus = (jobId: string | null) => {
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!jobId) return;

    const pollStatus = async () => {
      try {
        const jobStatus = await checkJobStatus(jobId);
        setStatus(jobStatus.status === 'completed' ? 'completed' : 'processing');
        setMessage(jobStatus.message || 'Processing...');
      } catch (error) {
        setStatus('error');
        setMessage('Failed to check job status');
      }
    };

    // Poll every 5 seconds if still processing
    const interval = setInterval(pollStatus, 5000);
    pollStatus(); // Initial check

    return () => clearInterval(interval);
  }, [jobId]);

  return { status, message };
};
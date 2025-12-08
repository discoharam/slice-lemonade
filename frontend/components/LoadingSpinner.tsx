// frontend/src/components/LoadingSpinner.tsx
import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Processing...' }) => {
  return (
    <div className="text-center py-6">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-yellow-500 mx-auto mb-3"></div>
      <p className="text-gray-700">{message}</p>
      <p className="text-xs text-gray-500 mt-1">
        Processing at 320kbps professional quality
      </p>
      <div className="mt-2 bg-gray-100 rounded-full h-1 w-40 mx-auto overflow-hidden">
        <div 
          className="bg-gradient-to-r from-yellow-500 to-orange-500 h-full animate-pulse" 
          style={{ width: '50%' }}
        />
      </div>
    </div>
  );
};

export default React.memo(LoadingSpinner);
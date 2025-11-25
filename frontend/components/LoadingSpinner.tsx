import React from 'react';

interface LoadingSpinnerProps {
  progress?: number;
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  progress = 0, 
  message = "Processing your audio..." 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="relative w-20 h-20 mb-4">
        <div className="absolute inset-0 border-4 border-yellow-200 rounded-full"></div>
        <div 
          className="absolute inset-0 border-4 border-yellow-500 rounded-full animate-spin"
          style={{ 
            borderTopColor: 'transparent',
            borderRightColor: 'transparent',
            borderBottomColor: 'transparent'
          }}
        ></div>
        {progress > 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-sm font-semibold text-yellow-600">{progress}%</span>
          </div>
        )}
      </div>
      <p className="text-gray-600 text-center mb-2">{message}</p>
      <div className="w-64 bg-gray-200 rounded-full h-2">
        <div 
          className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-sm text-gray-500 mt-4 text-center">
        This may take a few minutes depending on the audio length...
      </p>
    </div>
  );
};
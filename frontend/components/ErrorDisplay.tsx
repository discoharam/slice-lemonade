// frontend/src/components/ErrorDisplay.tsx
import React from 'react';

interface ErrorDisplayProps {
  error: string;
  onClear: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = React.memo(({ error, onClear }) => {
  if (!error) return null;

  return (
    <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-md">
      <div className="flex items-start">
        <div className="text-red-500 mr-2 text-sm">!</div>
        <div className="flex-1">
          <p className="text-red-600 text-sm font-medium">Error: {error}</p>
          <button
            onClick={onClear}
            className="mt-1 text-xs text-red-500 hover:text-red-700"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
});

ErrorDisplay.displayName = 'ErrorDisplay';

export default ErrorDisplay;
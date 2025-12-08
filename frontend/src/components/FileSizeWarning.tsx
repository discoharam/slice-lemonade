import React from 'react';

interface FileSizeWarningProps {
  file: File;
  selectedFormat: string;
  selectedQuality: string;
}

const FileSizeWarning: React.FC<FileSizeWarningProps> = ({ 
  file, 
  selectedFormat, 
  selectedQuality 
}) => {
  const fileSizeMB = file.size / 1024 / 1024;
  
  const getWarningMessage = () => {
    if (fileSizeMB > 100) {
      return {
        type: 'error' as const,
        message: 'File exceeds 100MB limit. Please use a smaller file.'
      };
    }
    
    if (fileSizeMB > 50 && selectedFormat === 'wav') {
      return {
        type: 'warning' as const,
        message: 'Large WAV files may process slower. MP3 is recommended for files >50MB.'
      };
    }
    
    if (fileSizeMB > 20) {
      return {
        type: 'info' as const,
        message: 'Processing may take 3-5 minutes for larger files.'
      };
    }
    
    return null;
  };
  
  const warning = getWarningMessage();
  
  if (!warning) return null;
  
  const bgColors = {
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200'
  };
  
  const textColors = {
    error: 'text-red-700',
    warning: 'text-yellow-700',
    info: 'text-blue-700'
  };
  
  return (
    <div className={`p-4 rounded-lg border ${bgColors[warning.type]}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {warning.type === 'error' && '❌'}
          {warning.type === 'warning' && '⚠️'}
          {warning.type === 'info' && 'ℹ️'}
        </div>
        <div className="ml-3">
          <p className={`text-sm font-medium ${textColors[warning.type]}`}>
            {warning.message}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            File size: {fileSizeMB.toFixed(2)} MB • Format: {selectedFormat.toUpperCase()} • Quality: {selectedQuality}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileSizeWarning;
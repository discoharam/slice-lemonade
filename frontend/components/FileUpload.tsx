import React, { useCallback, useState } from 'react';
import { Upload, Music, FileAudio } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = (file: File) => {
    const allowedTypes = [
      'audio/mpeg', 
      'audio/wav', 
      'audio/flac', 
      'audio/mp4',
      'audio/aac',
      'audio/ogg'
    ];

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|flac|m4a|aac|ogg)$/i)) {
      alert('Please upload a valid audio file (MP3, WAV, FLAC, M4A, AAC, OGG)');
      return;
    }

    if (file.size > 100 * 1024 * 1024) {
      alert('File size must be less than 100MB');
      return;
    }

    setSelectedFile(file);
    onFileSelect(file);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        <label
          htmlFor="file-upload"
          className={`relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
            dragActive 
              ? 'border-yellow-400 bg-yellow-50 scale-[1.02]' 
              : 'border-gray-300 hover:border-gray-400 bg-gray-50 hover:bg-gray-100'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept="audio/*,.mp3,.wav,.flac,.m4a,.aac,.ogg"
            onChange={handleChange}
            disabled={isProcessing}
          />
          
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Music className="w-16 h-16 text-gray-400 mb-4" />
            <p className="text-xl font-semibold text-gray-700 mb-2">
              Drop your audio file here
            </p>
            <p className="text-sm text-gray-500 mb-1">
              or click to browse
            </p>
            <p className="text-xs text-gray-400">
              Supports MP3, WAV, FLAC, M4A, AAC, OGG • Max 100MB
            </p>
          </div>
        </label>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <FileAudio className="w-12 h-12 text-yellow-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-lg font-semibold text-gray-900 truncate">
                {selectedFile.name}
              </p>
              <p className="text-sm text-gray-500">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-500 transition-colors"
              disabled={isProcessing}
            >
              <Upload className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
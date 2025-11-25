import React from 'react';
import { FileUpload } from './components/FileUpload';
import { ResultDisplay } from './components/ResultDisplay';
import { LoadingSpinner } from './components/LoadingSpinner';
import { useAudioSeparator } from './hooks/useAudioSeparator';

function App() {
  const { separateAudio, downloadTrack, currentJob, isProcessing, progress, reset } = useAudioSeparator();

  const handleFileSelect = async (file: File) => {
    try {
      await separateAudio(file);
    } catch (error) {
      console.error('Separation error:', error);
    }
  };

  const handleNewFile = () => {
    reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center space-x-4 mb-4">
            <div className="text-5xl">🍋</div>
            <h1 className="text-5xl font-bold text-gray-800">
              Slice Lemonade
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Separate vocals and instruments from any audio file using AI-powered Demucs technology
          </p>
        </header>

        {/* Main Content */}
        <main>
          {!currentJob && !isProcessing && (
            <FileUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />
          )}

          {isProcessing && (
            <div className="w-full max-w-2xl mx-auto">
              <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
                <LoadingSpinner 
                  progress={progress}
                  message="Separating audio stems with AI..."
                />
              </div>
            </div>
          )}

          {currentJob && currentJob.status === 'completed' && (
            <>
              <ResultDisplay job={currentJob} onDownload={downloadTrack} />
              <div className="text-center mt-8">
                <button
                  onClick={handleNewFile}
                  className="btn-primary"
                >
                  Process Another File
                </button>
              </div>
            </>
          )}

          {currentJob && currentJob.status === 'error' && (
            <div className="text-center mt-8">
              <button
                onClick={handleNewFile}
                className="btn-primary"
              >
                Try Again
              </button>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 text-center">
          <div className="border-t border-gray-200 pt-8">
            <p className="text-gray-500">
              Powered by <span className="font-semibold">Demucs</span> and <span className="font-semibold">RunPod</span> • Made with 🍋
            </p>
            <p className="text-sm text-gray-400 mt-2">
              GPU-powered audio separation on demand
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
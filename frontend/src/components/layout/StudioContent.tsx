import React from 'react';
import WorkflowSelector from './WorkflowSelector';
import FileUploadArea from '../FileUploadArea';
import MinutesInfo from '../MinutesInfo';
import ErrorDisplay from '../ErrorDisplay';
import { Zap, Music } from 'lucide-react';

interface StudioContentProps {
  selectedWorkflow: string;
  onSelectWorkflow: (workflow: string) => void;
  processingEstimate?: any;
  minutes: any;
  file: File | null;
  isDragging: boolean;
  onFileChange: (file: File) => void;
  onDragOver: (isDragging: boolean) => void;
  loading: boolean;
  error: string;
  onSeparateClick: () => void;
  onReset: () => void;
  showTrimmer: boolean;
  onShowTrimmer: () => void;
  onUpgradeClick: () => void;
}

const StudioContent: React.FC<StudioContentProps> = ({
  selectedWorkflow,
  onSelectWorkflow,
  processingEstimate,
  minutes,
  file,
  isDragging,
  onFileChange,
  onDragOver,
  loading,
  error,
  onSeparateClick,
  onReset,
  showTrimmer,
  onShowTrimmer,
  onUpgradeClick
}) => {
  const handleUtilityAction = () => {
    if (!file) return;
    
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    
    let filename = file.name;
    if (selectedWorkflow === 'trim') filename = 'trimmed_' + filename;
    if (selectedWorkflow === 'mono') filename = 'mono_' + filename;
    if (selectedWorkflow === 'convert') filename = 'converted_' + filename;
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Workflow Selector & Info */}
        <div className="lg:col-span-1 space-y-6">
          <WorkflowSelector
            selectedWorkflow={selectedWorkflow}
            onSelectWorkflow={onSelectWorkflow}
            processingEstimate={processingEstimate}
          />
          
          {selectedWorkflow === 'separate' && processingEstimate && (
            <div className="bg-onsync-elevated border border-onsync rounded-2xl p-5">
              <MinutesInfo
                estimate={processingEstimate}
                remainingMinutes={minutes.remaining}
                onUpgradeClick={onUpgradeClick}
              />
            </div>
          )}
        </div>

        {/* Right Column - Main Content */}
        <div className="lg:col-span-2">
          <div className="bg-onsync-container border border-onsync rounded-2xl p-5 h-full">
            {!file ? (
              <div className="text-center py-12">
                <div className="relative mb-6">
                  <div className="text-5xl mb-4 text-onsync-primary">🎵</div>
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center text-xs text-white font-bold">
                    AI
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-onsync-primary mb-2">
                  Start separating tracks
                </h3>
                <p className="text-onsync-secondary mb-8 max-w-md mx-auto">
                  Upload audio to begin {selectedWorkflow === 'separate' ? 'AI-powered separation' : 'audio processing'}
                </p>
                <div className="max-w-md mx-auto">
                  <FileUploadArea
                    file={file}
                    isDragging={isDragging}
                    onFileChange={onFileChange}
                    onDragOver={onDragOver}
                    showTrimmer={showTrimmer}
                    onShowTrimmer={onShowTrimmer}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* File Header */}
                <div className="flex items-center justify-between p-4 bg-onsync-elevated rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg">
                      <Music className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-onsync-primary truncate max-w-xs">
                        {file.name}
                      </h3>
                      <p className="text-sm text-onsync-secondary">
                        {(file.size / 1024 / 1024).toFixed(2)} MB • Ready for processing
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={onReset}
                    className="text-sm px-3 py-1.5 text-onsync-secondary hover:text-onsync-primary hover:bg-onsync-container rounded-lg transition-colors"
                  >
                    Change file
                  </button>
                </div>

                {/* Action Button */}
                {selectedWorkflow === 'separate' ? (
                  <button
                    onClick={onSeparateClick}
                    disabled={loading}
                    className="w-full py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-xl transition-all duration-300 hover:scale-[1.02] hover:shadow-lg disabled:opacity-50 text-lg"
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        Processing with AI...
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        <Zap className="w-5 h-5 mr-2" />
                        Separate Tracks ({processingEstimate ? `${processingEstimate.estimatedMinutes.toFixed(1)} min` : 'Processing'})
                      </div>
                    )}
                  </button>
                ) : (
                  <div className="bg-onsync-elevated border border-onsync rounded-xl p-5">
                    <div className="text-center mb-4">
                      <div className="text-2xl mb-2 text-onsync-primary">
                        {selectedWorkflow === 'trim' && '✂️'}
                        {selectedWorkflow === 'mono' && '🔊'}
                        {selectedWorkflow === 'convert' && '📥'}
                      </div>
                      <h4 className="font-semibold text-onsync-primary">
                        {selectedWorkflow === 'trim' && 'Trim Audio'}
                        {selectedWorkflow === 'mono' && 'Convert to Mono'}
                        {selectedWorkflow === 'convert' && 'Quick Convert'}
                      </h4>
                      <p className="text-sm text-onsync-secondary">
                        No minutes required • Process locally
                      </p>
                    </div>
                    <button
                      onClick={handleUtilityAction}
                      className="w-full py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
                    >
                      <div className="flex items-center justify-center">
                        {selectedWorkflow === 'trim' && '✂️ Trim & Download'}
                        {selectedWorkflow === 'mono' && '🔊 Convert & Download'}
                        {selectedWorkflow === 'convert' && '📥 Download'}
                      </div>
                    </button>
                  </div>
                )}

                {error && (
                  <ErrorDisplay error={error} onClear={onReset} />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudioContent;
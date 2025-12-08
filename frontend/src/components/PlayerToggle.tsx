// frontend/src/components/PlayerToggle.tsx - CLEAN VERSION
import React from 'react';
import AudioIcons from './AudioIcons';

interface PlayerToggleProps {
  useSimplePlayer: boolean;
  onToggle: () => void;
}

const PlayerToggle: React.FC<PlayerToggleProps> = ({ useSimplePlayer, onToggle }) => {
  return (
    <div className="flex items-center space-x-1">
      <button
        onClick={onToggle}
        className={`p-1.5 rounded-md transition-colors ${
          !useSimplePlayer 
            ? 'bg-blue-100 text-blue-600' 
            : 'bg-gray-100 text-gray-400 hover:text-gray-600'
        }`}
        title="Waveform Player"
      >
        <AudioIcons type="waveform" className="w-4 h-4" />
      </button>
      <button
        onClick={onToggle}
        className={`p-1.5 rounded-md transition-colors ${
          useSimplePlayer 
            ? 'bg-blue-100 text-blue-600' 
            : 'bg-gray-100 text-gray-400 hover:text-gray-600'
        }`}
        title="Simple Player"
      >
        <div className="w-4 h-4 flex items-center justify-center">
          <div className="w-3 h-3 bg-current rounded-sm"></div>
        </div>
      </button>
    </div>
  );
};

export default React.memo(PlayerToggle);
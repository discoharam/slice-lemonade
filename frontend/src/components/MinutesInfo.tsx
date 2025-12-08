// frontend/src/components/MinutesInfo.tsx - FIXED
import React from 'react';
import { Clock, Zap, AlertTriangle } from 'lucide-react';
import { ProcessingEstimate } from '../types/minutes';

interface MinutesInfoProps {
  estimate: ProcessingEstimate;
  remainingMinutes: number;
  onUpgradeClick?: () => void;
}

const MinutesInfo: React.FC<MinutesInfoProps> = ({
  estimate,
  remainingMinutes,
  onUpgradeClick
}) => {
  const hasEnoughMinutes = remainingMinutes >= estimate.estimatedMinutes;
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
          <Clock className="w-4 h-4" />
          <span>Estimated: {estimate.estimatedMinutes.toFixed(1)} minutes</span>
        </div>
        <div className="flex items-center space-x-2">
          <Zap className="w-4 h-4 text-yellow-500" />
          <span className="font-medium text-gray-800 dark:text-gray-200">
            {remainingMinutes.toFixed(1)} remaining
          </span>
        </div>
      </div>

      {!hasEnoughMinutes && (
        <div className="flex items-center justify-between p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
          <div className="flex items-center space-x-2 text-red-700 dark:text-red-300">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm">
              Need {estimate.estimatedMinutes.toFixed(1)} minutes
            </span>
          </div>
          <button
            onClick={onUpgradeClick}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded transition-colors"
          >
            Upgrade
          </button>
        </div>
      )}

      <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
        <span>Complexity: {estimate.complexity}</span>
        <span>{estimate.fileSizeMB.toFixed(1)} MB</span>
      </div>
    </div>
  );
};

export default MinutesInfo;
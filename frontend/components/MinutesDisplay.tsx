// frontend/src/components/MinutesDisplay.tsx - MINIMAL VERSION
import React from 'react';
import { Battery, BatteryWarning, Zap, AlertTriangle } from 'lucide-react';
import { UserMinutes } from '../types/minutes';

interface MinutesDisplayProps {
  minutes: UserMinutes;
  showWarning?: boolean;
  compact?: boolean;
}

const MinutesDisplay: React.FC<MinutesDisplayProps> = ({
  minutes,
  showWarning = false,
  compact = false
}) => {
  const percentage = (minutes.remaining / minutes.total) * 100;
  
  const getColorClass = () => {
    if (percentage > 50) return 'text-green-600 dark:text-green-400';
    if (percentage > 20) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getBarColor = () => {
    if (percentage > 50) return 'bg-green-500';
    if (percentage > 20) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getIcon = () => {
    if (percentage > 50) return <Battery className="w-4 h-4" />;
    if (percentage > 20) return <BatteryWarning className="w-4 h-4" />;
    return <AlertTriangle className="w-4 h-4" />;
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800/50 rounded-lg px-3 py-2">
        <div className={`${getColorClass()}`}>
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {minutes.remaining.toFixed(1)}
            </span>
          </div>
          <div className="w-full bg-gray-300 dark:bg-gray-700 rounded-full h-1.5 mt-1 overflow-hidden">
            <div 
              className={`h-full rounded-full ${getBarColor()} transition-all duration-300`}
              style={{ width: `${Math.max(5, percentage)}%` }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 border border-gray-300 dark:border-gray-700 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Zap className="w-4 h-4 text-yellow-500" />
          <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
            Processing Minutes
          </h3>
        </div>
        <div className={`text-lg font-bold ${getColorClass()}`}>
          {minutes.remaining.toFixed(1)}
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>Available</span>
          <span>{minutes.used.toFixed(1)} used • {minutes.total.toFixed(1)} total</span>
        </div>
        
        <div className="w-full bg-gray-300 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
          <div 
            className={`h-full rounded-full ${getBarColor()} transition-all duration-500`}
            style={{ width: `${Math.max(3, percentage)}%` }}
          />
        </div>
        
        {showWarning && minutes.remaining < 2 && (
          <div className="flex items-center space-x-1.5 text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 p-1.5 rounded">
            <AlertTriangle className="w-3 h-3" />
            <span>Low minutes. Consider upgrading to continue processing.</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MinutesDisplay;
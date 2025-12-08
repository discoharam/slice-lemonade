import React, { memo } from 'react';
import { Split, Scissors, VolumeX, Download } from 'lucide-react';

interface WorkflowOption {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
  minutes?: number;
  free?: boolean;
}

interface WorkflowSelectorProps {
  selectedWorkflow: string;
  onSelectWorkflow: (workflowId: string) => void;
  processingEstimate?: { estimatedMinutes: number };
}

const WorkflowSelector: React.FC<WorkflowSelectorProps> = memo(({
  selectedWorkflow,
  onSelectWorkflow,
  processingEstimate
}) => {
  const workflows: WorkflowOption[] = [
    {
      id: 'separate',
      icon: <Split className="w-5 h-5" />,
      title: "AI Separation",
      description: "Split audio into stems",
      color: "from-blue-500 to-blue-600",
      minutes: processingEstimate?.estimatedMinutes
    },
    {
      id: 'trim',
      icon: <Scissors className="w-5 h-5" />,
      title: "Trim & Export",
      description: "Cut and download sections",
      color: "from-green-500 to-green-600",
      free: true
    },
    {
      id: 'mono',
      icon: <VolumeX className="w-5 h-5" />,
      title: "Mono Convert",
      description: "Convert stereo to mono",
      color: "from-purple-500 to-purple-600",
      free: true
    },
    {
      id: 'convert',
      icon: <Download className="w-5 h-5" />,
      title: "Quick Download",
      description: "Convert format & download",
      color: "from-yellow-500 to-orange-500",
      free: true
    }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-5">
      <h2 className="font-semibold text-gray-800 dark:text-white mb-4">Select Process</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {workflows.map((workflow) => (
          <button
            key={workflow.id}
            onClick={() => onSelectWorkflow(workflow.id)}
            className={`p-4 rounded-xl border transition-colors duration-150 ${
              selectedWorkflow === workflow.id 
                ? `border-transparent bg-gradient-to-r ${workflow.color} text-white` 
                : 'border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  selectedWorkflow === workflow.id ? 'bg-white/20' : 'bg-gray-100 dark:bg-gray-700'
                }`}>
                  {workflow.icon}
                </div>
                <div className="text-left">
                  <h4 className="font-semibold">{workflow.title}</h4>
                  <p className={`text-sm ${selectedWorkflow === workflow.id ? 'opacity-90' : 'text-gray-600 dark:text-gray-400'}`}>
                    {workflow.description}
                  </p>
                </div>
              </div>
              {workflow.minutes !== undefined && (
                <div className={`text-sm font-medium ${selectedWorkflow === workflow.id ? 'text-white/90' : 'text-gray-600 dark:text-gray-400'}`}>
                  {workflow.minutes.toFixed(1)} min
                </div>
              )}
              {workflow.free && (
                <div className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                  FREE
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
});

WorkflowSelector.displayName = 'WorkflowSelector';

export default WorkflowSelector;
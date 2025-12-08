// frontend/src/components/EQVisualizer.tsx
import React, { useEffect, useRef } from 'react';
import { EQSettings } from '../hooks/useEQProcessor';

interface EQVisualizerProps {
  eqSettings: EQSettings;
  width?: number;
  height?: number;
}

const EQVisualizer: React.FC<EQVisualizerProps> = ({
  eqSettings,
  width = 200,
  height = 80
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current || !eqSettings.enabled) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.lineWidth = 1;
    
    // Horizontal lines (dB)
    for (let i = 0; i <= 4; i++) {
      const y = (height / 4) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    // Vertical lines (frequency)
    for (let i = 0; i <= 4; i++) {
      const x = (width / 4) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Draw EQ curve
    const centerY = height / 2;
    
    // Low shelf curve
    if (eqSettings.low.gain !== 0) {
      const lowFreqX = (Math.log10(eqSettings.low.frequency) - Math.log10(80)) / 
                      (Math.log10(16000) - Math.log10(80)) * width;
      
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, centerY - (eqSettings.low.gain / 12) * (height / 2));
      ctx.lineTo(lowFreqX, centerY - (eqSettings.low.gain / 12) * (height / 2));
      ctx.lineTo(width / 2, centerY);
      ctx.stroke();
    }
    
    // High shelf curve
    if (eqSettings.high.gain !== 0) {
      const highFreqX = (Math.log10(eqSettings.high.frequency) - Math.log10(80)) / 
                       (Math.log10(16000) - Math.log10(80)) * width;
      
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(width / 2, centerY);
      ctx.lineTo(highFreqX, centerY - (eqSettings.high.gain / 12) * (height / 2));
      ctx.lineTo(width, centerY - (eqSettings.high.gain / 12) * (height / 2));
      ctx.stroke();
    }
    
    // Draw center line
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
    
    // Add frequency labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    
    const frequencies = [80, 250, 1000, 4000, 16000];
    frequencies.forEach(freq => {
      const x = (Math.log10(freq) - Math.log10(80)) / 
               (Math.log10(16000) - Math.log10(80)) * width;
      const label = freq >= 1000 ? `${freq/1000}k` : freq.toString();
      ctx.fillText(label, x, height - 5);
    });
    
    // Add gain labels
    ctx.textAlign = 'left';
    ctx.fillText('+12dB', 5, 10);
    ctx.fillText('0dB', 5, centerY + 3);
    ctx.fillText('-12dB', 5, height - 5);
    
  }, [eqSettings, width, height]);
  
  if (!eqSettings.enabled) {
    return (
      <div className="text-center text-gray-400 text-xs py-4">
        EQ is disabled
      </div>
    );
  }
  
  return (
    <div className="bg-white border border-gray-300 rounded p-2">
      <div className="text-xs text-gray-600 mb-1 text-center">EQ Curve</div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full"
      />
    </div>
  );
};

export default EQVisualizer;
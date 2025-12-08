import React,{useState,useCallback}from'react';import ToolLayout from'../layout/ToolLayout';
const SpectrogramContent:React.FC<{file:File|null;isDragging:boolean;onFileChange:(file:File)=>void;onDragOver:(isDragging:boolean)=>void;onReset:()=>void;}>=({file,isDragging,onFileChange,onDragOver,onReset})=>{const[isAnalyzing,setIsAnalyzing]=useState(false);const handleAnalyze=useCallback(()=>{if(!file)return;setIsAnalyzing(true);setTimeout(()=>{setIsAnalyzing(false);},1500);},[file]);return(<ToolLayout title="Spectrogram Analyzer"description="Visual audio frequency analysis"icon="bar-chart"file={file}isDragging={isDragging}onFileChange={onFileChange}onDragOver={onDragOver}onReset={onReset}onAction={handleAnalyze}actionLabel="Generate Spectrogram"isProcessing={isAnalyzing}showOptions={false}>{isAnalyzing&&(<div className="mt-4"><div className="bg-[#1a1a1a] rounded-lg p-4 border border-onsync"><div className="aspect-video bg-[#000000] rounded flex flex-col items-center justify-center"><Icon name="bar-chart"className="text-[#444] mb-3"size={32}/><p className="text-[#b3b3b3] text-sm">Generating spectrogram...</p><p className="text-[#666] text-xs mt-1">Frequency range: 20Hz - 20kHz</p></div><div className="flex items-center justify-between mt-3 text-sm"><div className="text-[#808080]">Analyzing audio frequencies</div><button className="text-[#b3b3b3] hover:text-onsync-primary"><Icon name="download"size={16}/></button></div></div></div>)}</ToolLayout>);};import{Icon}from'../icons/IconSystem';export default SpectrogramContent;







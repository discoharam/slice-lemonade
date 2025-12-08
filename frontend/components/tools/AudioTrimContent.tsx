import React,{useState,useCallback}from'react';import ToolLayout from'../layout/ToolLayout';
const AudioTrimContent:React.FC<{file:File|null;isDragging:boolean;onFileChange:(file:File)=>void;onDragOver:(isDragging:boolean)=>void;onReset:()=>void;onOpenTrimmer?:()=>void;}>=({file,isDragging,onFileChange,onDragOver,onReset,onOpenTrimmer})=>{
const[isProcessing,setIsProcessing]=useState(false);
const handleOpenTrimmer=useCallback(()=>{
if(!file){alert('Please select a file first');return;}
if(onOpenTrimmer){onOpenTrimmer();}
},[file,onOpenTrimmer]);
const handleAction=useCallback(()=>{
if(!file)return;
setIsProcessing(true);
setTimeout(()=>{
const url=URL.createObjectURL(file);
const link=document.createElement('a');
const nameWithoutExt=file.name.replace(/\.[^/.]+$/,"");
link.href=url;
link.download=`${nameWithoutExt}.mp3`;
document.body.appendChild(link);
link.click();
document.body.removeChild(link);
URL.revokeObjectURL(url);
setIsProcessing(false);
},500);
},[file]);
return(<ToolLayout title="Audio Trimmer"description="Precise audio cutting and editing"icon="scissors"file={file}isDragging={isDragging}onFileChange={onFileChange}onDragOver={onDragOver}onReset={onReset}onAction={handleAction}actionLabel="Trim Audio"isProcessing={isProcessing}showOptions={false}>{file&&(<button onClick={handleOpenTrimmer}className="w-full mt-3 py-2.5 text-onsync-secondary dark:text-[#b3b3b3] hover:text-onsync-primary dark:hover:text-white hover:bg-onsync-container/50 dark:hover:bg-white/5 rounded-lg transition-onSync flex items-center justify-center border border-onsync dark:border-[#383838]">
<svg className="w-4 h-4 mr-2"viewBox="0 0 24 24"fill="none"stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16"y1="13"x2="8"y2="13"/><line x1="16"y1="17"x2="8"y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
Open Advanced Trimmer</button>)}</ToolLayout>);};export default AudioTrimContent;
// frontend/src/types/index.ts - REPLACE ENTIRE FILE
export interface StemData{formats:Record<string,string>;primary:string;isMono?:boolean;canConvertToMono?:boolean;}
export interface Job{job_id:string;status:'processing'|'completed'|'error';stems?:Record<string,StemData>;audio_urls?:Record<string,{formats:string[];urls:Record<string,string>}>;error?:string;timestamp?:string;primary_format?:string;quality?:string;warning?:string;stems_count?:number;note?:string;}
export interface TrimState{startTime:number;endTime:number;isTrimming:boolean;}
export interface UploadState{file:File|null;job:Job|null;loading:boolean;error:string;warning:string;selectedFormats:Record<string,string>;useSimplePlayer:boolean;isDragging:boolean;trim:TrimState;monoConversions:Record<string,boolean>;eqSettings:Record<string,EQSettings>;}
export interface EQSettings{enabled:boolean;low:{gain:number;frequency:number;};high:{gain:number;frequency:number;};}
export interface FrequencyProfile{frequencies:Float32Array;noiseFloor:number;peaks:{frequency:number;magnitude:number}[];sampleRate:number;}
export interface NoiseReductionSettings{reductionAmount:number;attackTime:number;releaseTime:number;learnFromSelection:boolean;preserveTransients:boolean;}
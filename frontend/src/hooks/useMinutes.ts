import { useState, useEffect } from 'react';
const DEFAULT_MINUTES = 10;
export const useMinutes = () => {
 const [minutes, setMinutes] = useState(() => {
  const saved = localStorage.getItem('slice-lemonade-minutes');
  if (saved) return JSON.parse(saved);
  return {total: DEFAULT_MINUTES,used: 0,remaining: DEFAULT_MINUTES,lastUpdated: new Date().toISOString()};
 });
 const [isLowOnMinutes, setIsLowOnMinutes] = useState(false);
 useEffect(() => {
  localStorage.setItem('slice-lemonade-minutes', JSON.stringify(minutes));
  setIsLowOnMinutes(minutes.remaining < 2);
 }, [minutes]);
 const estimateProcessingMinutes = (fileSizeMB: number): any => {
  const estimated = Math.max(0.5, Math.ceil(fileSizeMB / 5));
  let complexity: 'low' | 'medium' | 'high' = 'low';
  if (fileSizeMB > 20) complexity = 'medium';
  if (fileSizeMB > 50) complexity = 'high';
  return {fileSizeMB,estimatedMinutes: estimated,complexity};
 };
 const useMinutesForProcessing = (estimatedMinutes: number): boolean => {
  if (minutes.remaining < estimatedMinutes) return false;
  setMinutes(prev => ({...prev,used: prev.used + estimatedMinutes,remaining: prev.remaining - estimatedMinutes,lastUpdated: new Date().toISOString()}));
  return true;
 };
 const addMinutes = (additionalMinutes: number) => {
  setMinutes(prev => ({...prev,total: prev.total + additionalMinutes,remaining: prev.remaining + additionalMinutes,lastUpdated: new Date().toISOString()}));
 };
 const resetMinutes = () => {
  setMinutes({total: DEFAULT_MINUTES,used: 0,remaining: DEFAULT_MINUTES,lastUpdated: new Date().toISOString()});
 };
 return {minutes,isLowOnMinutes,estimateProcessingMinutes,useMinutesForProcessing,addMinutes,resetMinutes};
};
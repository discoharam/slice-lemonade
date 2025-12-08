import { useCallback, useEffect } from 'react';
import { useFileUpload } from './useFileUpload';
import { useMinutes } from './useMinutes';
import { useUIState } from './useUIState';
export const useAppLogic = () => {
 const fileUpload = useFileUpload();
 const minutes = useMinutes();
 const uiState = useUIState();
 const handleSeparateClick = useCallback(async () => {
  const { file } = fileUpload.state;
  const { processingEstimate } = uiState;
  const { minutes: userMinutes, useMinutesForProcessing } = minutes;
  if (!file) return;
  if (processingEstimate && userMinutes.remaining < processingEstimate.estimatedMinutes) {uiState.openUpgradeModal();return;}
  if (processingEstimate) {
   const success = useMinutesForProcessing(processingEstimate.estimatedMinutes);
   if (!success) {uiState.openUpgradeModal();return;}
  }
  await fileUpload.handleUpload();
 }, [fileUpload, uiState, minutes]);
 useEffect(() => {
  const { file } = fileUpload.state;
  const { estimateProcessingMinutes } = minutes;
  const { updateProcessingEstimate } = uiState;
  if (file) {
   const fileSizeMB = file.size / 1024 / 1024;
   const estimate = estimateProcessingMinutes(fileSizeMB);
   updateProcessingEstimate(estimate);
  } else {
   updateProcessingEstimate(null);
  }
 }, [fileUpload.state.file, minutes.estimateProcessingMinutes, uiState.updateProcessingEstimate]);
 const handleSelectPlan = useCallback((plan: any) => {
  if (plan.price > 0) {minutes.addMinutes(plan.minutes);uiState.updateUserPlan(plan.name);}
  uiState.closeUpgradeModal();
 }, [minutes, uiState]);
 const handleSignOut = useCallback(() => {
  minutes.resetMinutes();uiState.updateUserPlan('Free');uiState.closeProfileDropdown();
 }, [minutes, uiState]);
 return {fileUpload,minutes,uiState,handleSeparateClick,handleSelectPlan,handleSignOut,};
};
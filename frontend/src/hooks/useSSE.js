import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useStudioStore } from '../stores/studioStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export function useSSE(jobId, onComplete) {
  const queryClient = useQueryClient();
  const { setCurrentJob, updateJobProgress, addNotification } = useStudioStore();

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(`${API_BASE_URL}/jobs/${jobId}/events`);
    setCurrentJob({ id: jobId, progress: 0, stage: 'Connecting...', status: 'running' });

    eventSource.addEventListener('job_started', (e) => {
      try {
        const data = JSON.parse(e.data);
        updateJobProgress(data.progress || 10, data.stage || 'Starting...');
      } catch {}
    });

    eventSource.addEventListener('stage_started', (e) => {
      try {
        const data = JSON.parse(e.data);
        updateJobProgress(data.progress, data.stage);
        addNotification(`Stage: ${data.stage}`, 'info');
      } catch {}
    });

    eventSource.addEventListener('progress_updated', (e) => {
      try {
        const data = JSON.parse(e.data);
        updateJobProgress(data.progress, data.stage);
      } catch {}
    });

    eventSource.addEventListener('asset_generated', (e) => {
      try {
        const data = JSON.parse(e.data);
        addNotification(`Asset generated for panel ${data.panel_number || ''}`, 'success');
      } catch {}
    });

    eventSource.addEventListener('approval_required', (e) => {
      try {
        const data = JSON.parse(e.data);
        addNotification('Outline generated! Please review and approve.', 'warning');
      } catch {}
    });

    eventSource.addEventListener('job_completed', (e) => {
      try {
        const data = JSON.parse(e.data);
        updateJobProgress(100, 'Completed');
        addNotification('Generation completed successfully!', 'success');
        queryClient.invalidateQueries();
        if (onComplete) onComplete(data);
      } catch {}
      eventSource.close();
    });

    eventSource.addEventListener('job_failed', (e) => {
      try {
        const data = JSON.parse(e.data);
        addNotification(`Generation failed: ${data.error || 'Unknown error'}`, 'error');
      } catch {}
      eventSource.close();
    });

    eventSource.onerror = () => {
      // Browser EventSource automatically retries connection
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, queryClient]);
}

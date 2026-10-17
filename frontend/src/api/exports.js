import { apiRequest } from './client';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const exportsApi = {
  exportChapter: (chapterId, data = {}) => 
    apiRequest(`/chapters/${chapterId}/exports`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getExport: (exportId) => 
    apiRequest(`/exports/${exportId}`),

  getDownloadUrl: (exportId) => `${API_BASE_URL}/exports/${exportId}/download`,
};

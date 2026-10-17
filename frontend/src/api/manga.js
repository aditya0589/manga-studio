import { apiRequest } from './client';

export const mangaApi = {
  getPages: (chapterId) => 
    apiRequest(`/chapters/${chapterId}/pages`),

  getProjectPages: (projectId) =>
    apiRequest(`/projects/${projectId}/pages`),

  createPage: (chapterId) => 
    apiRequest(`/chapters/${chapterId}/pages`, { method: 'POST' }),

  updatePanel: (panelId, data) => 
    apiRequest(`/panels/${panelId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  generatePanel: (panelId, data = {}) => 
    apiRequest(`/panels/${panelId}/generate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  regeneratePanel: (panelId, data = {}) => 
    apiRequest(`/panels/${panelId}/regenerate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  approvePanel: (panelId) => 
    apiRequest(`/panels/${panelId}/approve`, { method: 'POST' }),
};

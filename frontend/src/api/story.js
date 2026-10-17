import { apiRequest } from './client';

export const storyApi = {
  analyze: (projectId, data = {}) => 
    apiRequest(`/projects/${projectId}/analyze`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  generateStoryBible: (projectId, data = {}) => 
    apiRequest(`/projects/${projectId}/story-bible/generate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  generateChapter: (projectId, data) => 
    apiRequest(`/projects/${projectId}/chapters/generate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getChapter: (chapterId) => 
    apiRequest(`/chapters/${chapterId}`),

  updateChapter: (chapterId, data) => 
    apiRequest(`/chapters/${chapterId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  approveChapter: (chapterId, data = {}) => 
    apiRequest(`/chapters/${chapterId}/approve`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  reviseChapter: (chapterId, data) => 
    apiRequest(`/chapters/${chapterId}/revise`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

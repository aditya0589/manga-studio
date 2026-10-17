import { apiRequest } from './client';

export const charactersApi = {
  list: (projectId) => 
    apiRequest(`/projects/${projectId}/characters`),

  create: (projectId, data) => 
    apiRequest(`/projects/${projectId}/characters`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (characterId, data) => 
    apiRequest(`/characters/${characterId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  uploadReference: (characterId, file, referenceType = 'canonical_face') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('reference_type', referenceType);
    return apiRequest(`/characters/${characterId}/references`, {
      method: 'POST',
      body: formData,
    });
  },

  approveDesign: (characterId, data) => 
    apiRequest(`/characters/${characterId}/approve-design`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

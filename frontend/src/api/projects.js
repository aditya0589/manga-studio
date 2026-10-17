import { apiRequest } from './client';

export const projectsApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/projects${query ? `?${query}` : ''}`);
  },

  get: (id) => apiRequest(`/projects/${id}`),

  create: (data) => 
    apiRequest('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id, data) => 
    apiRequest(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id) => 
    apiRequest(`/projects/${id}`, { method: 'DELETE' }),
};

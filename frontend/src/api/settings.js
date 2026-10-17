import { apiRequest } from './client';

export const settingsApi = {
  getProviders: () => apiRequest('/settings/providers'),
  getModels: () => apiRequest('/settings/models'),
  getUsage: () => apiRequest('/settings/usage'),
};

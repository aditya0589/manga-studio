import { apiRequest } from './client';

export const authApi = {
  register: (email, password) => 
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  login: (email, password) => 
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  logout: () => 
    apiRequest('/auth/logout', { method: 'POST' }),

  getMe: () => 
    apiRequest('/auth/me'),
};

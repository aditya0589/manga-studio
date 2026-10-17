import { create } from 'zustand';
import { authApi } from '../api/auth';

export const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('manga_studio_user') || 'null'),
  token: localStorage.getItem('manga_studio_token') || null,
  isAuthenticated: !!localStorage.getItem('manga_studio_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authApi.login(email, password);
      localStorage.setItem('manga_studio_token', data.access_token);
      localStorage.setItem('manga_studio_user', JSON.stringify(data.user));
      set({
        token: data.access_token,
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });
      return data;
    } catch (err) {
      set({ error: err.message, isLoading: false });
      throw err;
    }
  },

  register: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authApi.register(email, password);
      localStorage.setItem('manga_studio_token', data.access_token);
      localStorage.setItem('manga_studio_user', JSON.stringify(data.user));
      set({
        token: data.access_token,
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });
      return data;
    } catch (err) {
      set({ error: err.message, isLoading: false });
      throw err;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore network errors during logout
    }
    localStorage.removeItem('manga_studio_token');
    localStorage.removeItem('manga_studio_user');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('manga_studio_token');
    if (!token) return;
    try {
      const user = await authApi.getMe();
      localStorage.setItem('manga_studio_user', JSON.stringify(user));
      set({ user, isAuthenticated: true });
    } catch {
      get().logout();
    }
  },
}));

// Listen to global logout event from client.js
if (typeof window !== 'undefined') {
  window.addEventListener('auth_logout', () => {
    useAuthStore.getState().logout();
  });
}

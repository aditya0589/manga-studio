/**
 * AI Manga Studio - API Client
 * Centralized fetch wrapper handling auth headers, base URL, and JSON errors.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('manga_studio_token');
  
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Set JSON Content-Type if body is not FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const response = await fetch(`${API_BASE_URL}${cleanEndpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred';
    if (contentType.includes('application/json')) {
      const errData = await response.json();
      errorDetail = errData.detail || errorDetail;
    } else {
      errorDetail = await response.text();
    }
    
    // Automatically logout if 401 Unauthorized
    if (response.status === 401) {
      localStorage.removeItem('manga_studio_token');
      localStorage.removeItem('manga_studio_user');
      window.dispatchEvent(new Event('auth_logout'));
    }

    throw new Error(errorDetail);
  }

  if (contentType.includes('application/json')) {
    return await response.json();
  }
  return await response.blob();
}

export default apiRequest;

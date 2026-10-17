import { apiRequest } from './client';

export const uploadsApi = {
  uploadDocument: (projectId, file, documentType = 'manuscript') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    return apiRequest(`/projects/${projectId}/uploads`, {
      method: 'POST',
      body: formData,
    });
  },

  listDocuments: (projectId) => 
    apiRequest(`/projects/${projectId}/documents`),

  getDocument: (documentId) => 
    apiRequest(`/documents/${documentId}`),

  deleteDocument: (documentId) => 
    apiRequest(`/documents/${documentId}`, { method: 'DELETE' }),
};

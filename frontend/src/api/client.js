import axios from 'axios';
import toast from 'react-hot-toast';

const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = document.cookie.split('; ').find(row => row.startsWith('csrf_token='))?.split('=')[1];
  if (token) {
    config.headers['X-CSRF-Token'] = token;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Handled by AuthContext and ProtectedRoute without forcing full page reload
      } else if (error.response.status === 403) {
        toast.error('Access denied.');
      } else if (error.response.status >= 500) {
        toast.error('Server error. Please try again later.');
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  me: () => apiClient.get('/auth/me'),
  login: (data) => apiClient.post('/auth/login', data),
  register: (data) => apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout'),
};

export const scoreApi = {
  getScores: () => apiClient.get('/score'),
};

export const uploadApi = {
  uploadResume: (data) => apiClient.post('/upload', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
};

export const analyzeApi = {
  analyze: (file, jdText, role = '') => {
    const form = new FormData();
    form.append('resume', file);
    form.append('jd_text', jdText);
    form.append('role', role);
    return apiClient.post('/analyze', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const roadmapApi = {
  getRoadmap: (id) => apiClient.get(`/roadmap/${id}`),
  generateRoadmap: (data) => apiClient.post('/roadmap', data),
  getProviderStatus: () => apiClient.get('/roadmap/provider-status'),
};

export const compareApi = {
  compareCandidates: (ids) => apiClient.post('/compare', { ids }),
};

export const exportApi = {
  exportReport: (id) => apiClient.get(`/export/${id}`, { responseType: 'blob' }),
};

export const fairnessApi = {
  checkFairness: (data) => apiClient.post('/fairness', data),
};

export default apiClient;

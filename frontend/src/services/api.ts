// API Service for STBank LeadGen Frontend
import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  Lead,
  LeadListItem,
  LeadFormData,
  LeadStats,
  LeadStatusUpdate,
  LeadAssign,
  Token,
  LoginCredentials,
  DuplicateCheck,
  User,
  LeadStatus,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`;
            return api.request(error.config);
          }
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ============ Auth API ============

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<Token> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<Token>('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<Token> => {
    const response = await api.post<Token>('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// ============ Lead API ============

export const leadApi = {
  // Public endpoints
  createLead: async (data: LeadFormData): Promise<Lead> => {
    const response = await api.post<Lead>('/leads', data);
    return response.data;
  },

  checkDuplicate: async (phone: string): Promise<DuplicateCheck> => {
    const response = await api.get<DuplicateCheck>('/leads/duplicate-check', {
      params: { phone },
    });
    return response.data;
  },

  // Protected endpoints
  getLeads: async (
    status?: LeadStatus,
    limit = 100,
    offset = 0
  ): Promise<LeadListItem[]> => {
    const response = await api.get<LeadListItem[]>('/leads', {
      params: { status, limit, offset },
    });
    return response.data;
  },

  getLeadStats: async (): Promise<LeadStats> => {
    const response = await api.get<LeadStats>('/leads/stats');
    return response.data;
  },

  getLead: async (id: number): Promise<Lead> => {
    const response = await api.get<Lead>(`/leads/${id}`);
    return response.data;
  },

  updateLeadStatus: async (
    id: number,
    data: LeadStatusUpdate
  ): Promise<Lead> => {
    const response = await api.patch<Lead>(`/leads/${id}/status`, data);
    return response.data;
  },

  assignLead: async (id: number, data: LeadAssign): Promise<Lead> => {
    const response = await api.patch<Lead>(`/leads/${id}/assign`, data);
    return response.data;
  },

  exportLeads: async (status?: LeadStatus): Promise<Blob> => {
    const response = await api.get('/leads/export/csv', {
      params: { status },
      responseType: 'blob',
    });
    return response.data;
  },
};

// ============ Utility Functions ============

export const saveTokens = (token: Token): void => {
  localStorage.setItem('access_token', token.access_token);
  localStorage.setItem('refresh_token', token.refresh_token);
};

export const clearTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export default api;
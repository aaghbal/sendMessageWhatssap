import axios, { AxiosInstance, AxiosError } from 'axios';
import { AuthResponse, LoginCredentials, RegisterData } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);

              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post('/auth/login/', credentials);
    return response.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.api.post('/auth/register/', data);
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await this.api.post('/auth/logout/', { refresh_token: refreshToken });
      } catch (error) {
        // Ignore logout errors
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  async verifyEmail(key: string): Promise<void> {
    const response = await this.api.post('/auth/verify-email/', { key });
    return response.data;
  }

  async resendVerification(email: string): Promise<void> {
    const response = await this.api.post('/auth/resend-verification/', { email });
    return response.data;
  }

  async resetPassword(email: string): Promise<void> {
    const response = await this.api.post('/auth/password/reset/', { email });
    return response.data;
  }

  async confirmPasswordReset(uid: string, token: string, new_password: string): Promise<void> {
    const response = await this.api.post('/auth/password/reset/confirm/', {
      uid,
      token,
      new_password,
    });
    return response.data;
  }

  // Dashboard
  async getDashboardStats() {
    const response = await this.api.get('/dashboard/stats/');
    return response.data;
  }

  // Contacts
  async getContacts(page = 1, search = '') {
    const response = await this.api.get('/contacts/', {
      params: { page, search },
    });
    return response.data;
  }

  async createContact(data: any) {
    const response = await this.api.post('/contacts/', data);
    return response.data;
  }

  async updateContact(id: number, data: any) {
    const response = await this.api.put(`/contacts/${id}/`, data);
    return response.data;
  }

  async deleteContact(id: number) {
    await this.api.delete(`/contacts/${id}/`);
  }

  async importContacts(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post('/contacts/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async exportContacts() {
    const response = await this.api.get('/contacts/export/', {
      responseType: 'blob',
    });
    return response.data;
  }

  // Contact Groups
  async getContactGroups() {
    const response = await this.api.get('/contact-groups/');
    return response.data;
  }

  async createContactGroup(data: any) {
    const response = await this.api.post('/contact-groups/', data);
    return response.data;
  }

  async updateContactGroup(id: number, data: any) {
    const response = await this.api.put(`/contact-groups/${id}/`, data);
    return response.data;
  }

  async deleteContactGroup(id: number) {
    await this.api.delete(`/contact-groups/${id}/`);
  }



  // Campaigns
  async getCampaigns(page = 1, status = '') {
    const response = await this.api.get('/campaigns/', {
      params: { page, status },
    });
    return response.data;
  }

  async createCampaign(data: any) {
    const response = await this.api.post('/campaigns/', data);
    return response.data;
  }

  async updateCampaign(id: number, data: any) {
    const response = await this.api.put(`/campaigns/${id}/`, data);
    return response.data;
  }

  async deleteCampaign(id: number) {
    await this.api.delete(`/campaigns/${id}/`);
  }

  async startCampaign(id: number) {
    const response = await this.api.post(`/campaigns/${id}/start/`);
    return response.data;
  }

  async stopCampaign(id: number) {
    const response = await this.api.post(`/campaigns/${id}/stop/`);
    return response.data;
  }

  async getCampaignAnalytics(id: number) {
    const response = await this.api.get(`/campaigns/${id}/analytics/`);
    return response.data;
  }

  // Messages
  async getMessages(page = 1, status = '') {
    const response = await this.api.get('/messages/', {
      params: { page, status },
    });
    return response.data;
  }

  async sendMessage(data: any) {
    const response = await this.api.post('/messages/sent/send_message/', data);
    return response.data;
  }

  async sendBulkMessages(data: any) {
    const response = await this.api.post('/messages/sent/send_bulk_messages/', data);
    return response.data;
  }

  // Analytics
  async getAnalytics(dateRange = '7days') {
    const response = await this.api.get('/analytics/', {
      params: { date_range: dateRange },
    });
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;

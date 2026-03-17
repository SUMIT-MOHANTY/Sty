import axios from 'axios';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/auth';

const API_URL = '/api/auth';

export const authService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', data.email);
    formData.append('password', data.password);

    const response = await axios.post(`${API_URL}/login`, formData);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await axios.post(`${API_URL}/register`, data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await axios.get(`${API_URL}/me`);
    return response.data;
  },

  setToken(token: string): void {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  logout(): void {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
};

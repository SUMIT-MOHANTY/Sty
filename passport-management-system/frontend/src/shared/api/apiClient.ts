import axios from 'axios';

// Base API configuration
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // You could implement token refresh logic here
        // const refreshToken = localStorage.getItem('refreshToken');
        // const res = await axios.post(`${baseURL}/auth/refresh`, { refreshToken });
        // localStorage.setItem('accessToken', res.data.accessToken);
        // originalRequest.headers['Authorization'] = `Bearer ${res.data.accessToken}`;
        // return apiClient(originalRequest);

        // For now, just redirect to login
        window.location.href = '/login';
        return Promise.reject(error);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('accessToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

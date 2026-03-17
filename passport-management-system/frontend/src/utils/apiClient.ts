import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Create the API client
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS & cookies
});

// Request interceptor for adding auth token and other headers
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // Add fingerprint to requests to help prevent CSRF
    const fingerprint = generateFingerprint();
    if (config.headers) {
      config.headers['X-Client-ID'] = fingerprint;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response;
  },
  (error: AxiosError) => {
    // Handle session expiry
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login?session=expired';
    }

    // Handle rate limiting
    if (error.response?.status === 429) {
      console.warn('Rate limit exceeded. Please try again later.');
    }

    // Handle server errors
    if (error.response?.status && error.response?.status >= 500) {
      console.error('Server error occurred. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Generate a simple browser fingerprint for request tracking
function generateFingerprint(): string {
  const screenInfo = `${window.screen.height}x${window.screen.width}x${window.screen.colorDepth}`;
  const timezone = new Date().getTimezoneOffset();
  const fingerprint = btoa(`${screenInfo}-${timezone}-${navigator.language}`);
  return fingerprint.slice(0, 32);
}

export { apiClient };

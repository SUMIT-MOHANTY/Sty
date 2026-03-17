import { apiClient } from './apiClient';

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    user_id: string;
    email: string;
    role: string;
    first_name: string;
    last_name: string;
  };
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', {
      email,
      password,
    });

    // Set the authorization header for future requests
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;

    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Login failed');
    }
    throw new Error('Unable to connect to the server');
  }
};

export const logout = (): void => {
  // Remove auth header
  delete apiClient.defaults.headers.common['Authorization'];
};

export const verifyEmail = async (token: string): Promise<{ message: string }> => {
  try {
    const response = await apiClient.post<{ message: string }>('/api/auth/verify-email', {
      token,
    });
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Email verification failed');
    }
    throw new Error('Unable to connect to the server');
  }
};

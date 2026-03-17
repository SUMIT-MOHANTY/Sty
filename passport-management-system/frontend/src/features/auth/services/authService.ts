import { apiClient } from '../../../shared/api/apiClient';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
  };
}

export const authService = {
  /**
   * Login user with email and password
   * @param credentials User login credentials
   * @returns Auth response with token and user data
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  /**
   * Register new user
   * @param userData User registration data
   * @returns Auth response with token and user data
   */
  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register', userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  /**
   * Verify user email with token
   * @param token Email verification token
   * @returns Success status
   */
  async verifyEmail(token: string): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.get<{ success: boolean }>(`/auth/verify-email/${token}`);
      return response.data;
    } catch (error) {
      console.error('Email verification error:', error);
      throw error;
    }
  },

  /**
   * Request password reset
   * @param email User email
   * @returns Success status
   */
  async requestPasswordReset(email: string): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.post<{ success: boolean }>('/auth/request-password-reset', { email });
      return response.data;
    } catch (error) {
      console.error('Password reset request error:', error);
      throw error;
    }
  },

  /**
   * Reset password with token
   * @param token Password reset token
   * @param newPassword New password
   * @returns Success status
   */
  async resetPassword(token: string, newPassword: string): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.post<{ success: boolean }>('/auth/reset-password', {
        token,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  },

  /**
   * Logout user - clear tokens
   */
  async logout(): Promise<void> {
    // This would typically involve clearing tokens from storage,
    // which would be handled by the auth context
    try {
      await apiClient.post('/auth/logout');
      // Token clearing will be handled by the auth context
    } catch (error) {
      console.error('Logout error:', error);
      // Even if the server request fails, we should still clear local tokens
      throw error;
    }
  },

  /**
   * Get current user profile
   * @returns User profile data
   */
  async getCurrentUser(): Promise<AuthResponse['user']> {
    try {
      const response = await apiClient.get<AuthResponse['user']>('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }
};

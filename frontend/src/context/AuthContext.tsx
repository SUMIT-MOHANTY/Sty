import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Define types for authentication
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'applicant' | 'admin';
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  error: string | null;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  register: async () => {},
  error: null
});

// Custom hook for using the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component that wraps the app and provides auth context
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('token');

        if (!token) {
          setIsLoading(false);
          return;
        }

        // Validate token with backend
        const response = await axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.status === 200) {
          setUser(response.data);
        }
      } catch (err) {
        // Token invalid or expired
        localStorage.removeItem('token');
        setError('Authentication session expired');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/auth/login', { email, password });

      if (response.status === 200) {
        const { token, user } = response.data;
        localStorage.setItem('token', token);
        setUser(user);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw new Error(err.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  // Register function
  const register = async (userData: RegisterData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/auth/register', userData);

      if (response.status === 201) {
        const { token, user } = response.data;
        localStorage.setItem('token', token);
        setUser(user);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw new Error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Provide the auth context to consuming components
  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      logout,
      register,
      error
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;

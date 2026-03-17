import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from './services/authService';

export interface User {
  user_id: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already logged in on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const userData = JSON.parse(localStorage.getItem('user') || '{}');
          setUser(userData);
        }
      } catch (err) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login(email, password);
      const { access_token, user } = response;

      // Store token and user data
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      setUser(user);
      return user;
    } catch (err: any) {
      setError(err.message || 'Failed to log in');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth as useAuthContext } from '../context/AuthContext';

interface UseAuthOptions {
  requireAuth?: boolean;
  requireAdmin?: boolean;
  redirectTo?: string;
}

export const useAuth = (options: UseAuthOptions = {}) => {
  const {
    requireAuth = false,
    requireAdmin = false,
    redirectTo = '/login'
  } = options;

  const auth = useAuthContext();
  const navigate = useNavigate();

  useEffect(() => {
    if (requireAuth && !auth.isAuthenticated) {
      navigate(redirectTo, { replace: true });
    }

    if (requireAdmin && !auth.isAdmin) {
      navigate('/dashboard', { replace: true });
    }
  }, [auth.isAuthenticated, auth.isAdmin, navigate, redirectTo, requireAuth, requireAdmin]);

  return auth;
};

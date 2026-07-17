/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { usersApi } from '@/api/users';
import { socketManager } from '@/services/socket';
import type { LoginResponse } from '../types/auth';
import type { User } from '../types/user';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (data: LoginResponse) => void;
  updateUser: (user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isAuthChecking: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token'),
  );
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(() =>
    Boolean(localStorage.getItem('access_token')),
  );

  const clearAuth = useCallback(() => {
    setUser(null);
    setToken(null);
    setIsAuthChecking(false);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    socketManager.disconnect();
  }, []);

  const login = useCallback((data: LoginResponse) => {
    setUser(data.user);
    setToken(data.access_token);
    setIsAuthChecking(true);
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('access_token', data.access_token);
  }, []);

  const updateUser = useCallback((nextUser: User) => {
    setUser(nextUser);
    localStorage.setItem('user', JSON.stringify(nextUser));
  }, []);

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  useEffect(() => {
    let cancelled = false;

    async function validateToken() {
      if (!token) {
        setIsAuthChecking(false);
        socketManager.disconnect();
        return;
      }

      setIsAuthChecking(true);
      try {
        const currentUser = await usersApi.getMe();
        if (cancelled) return;
        setUser(currentUser);
        localStorage.setItem('user', JSON.stringify(currentUser));
        socketManager.connect(token);
      } catch {
        if (!cancelled) {
          clearAuth();
        }
      } finally {
        if (!cancelled) {
          setIsAuthChecking(false);
        }
      }
    }

    validateToken();

    return () => {
      cancelled = true;
    };
  }, [token, clearAuth]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAuth();
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [clearAuth]);

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      updateUser,
      logout,
      isAuthenticated: Boolean(token && user),
      isAuthChecking,
    }),
    [user, token, login, updateUser, logout, isAuthChecking],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

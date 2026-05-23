/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, LoginResponse } from '../types/chat';
import { socketManager } from '../socket/socketManager';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (data: LoginResponse) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );

  useEffect(() => {
    if (token) {
      // 连接Socket，socketManager会处理token变化和重复连接
      socketManager.connect(token);
    } else {
      // 没有token时断开连接
      socketManager.disconnect();
    }

    // 组件卸载时清理
    return () => {
      // 注意：不要在这里断开连接，因为其他组件可能还需要连接
      // 只在token变化时由上面的逻辑处理
    };
  }, [token]);

  const login = (data: LoginResponse) => {
    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('access_token', data.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    socketManager.disconnect();
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth必须在AuthProvider内使用');
  return context;
};
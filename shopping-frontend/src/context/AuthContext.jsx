import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

function decodeToken(token) {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(window.atob(normalized));
  } catch {
    return null;
  }
}

function buildUserFromToken(token) {
  const payload = decodeToken(token);
  if (!payload?.sub) return null;
  return { email: payload.sub, role: payload.role || 'USER' };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      api.defaults.headers.common.Authorization = `Bearer ${storedToken}`;
      setUser(buildUserFromToken(storedToken));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const accessToken = response.data.access_token;
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    setUser(buildUserFromToken(accessToken) || { email, role: 'USER' });
    return response.data;
  };

  const register = async (email, password) => {
    return api.post('/auth/register', { email, password });
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common.Authorization;
    setToken(null);
    setUser(null);
  };

  const value = useMemo(() => ({ user, token, loading, login, register, logout, setUser }), [user, token, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
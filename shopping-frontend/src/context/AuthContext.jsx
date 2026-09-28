import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

function decodeToken(token) {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
    return JSON.parse(window.atob(padded));
  } catch {
    return null;
  }
}

function buildUserFromToken(token) {
  const payload = decodeToken(token);
  if (!payload?.sub || (payload.exp && payload.exp * 1000 <= Date.now())) return null;
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
      const storedUser = buildUserFromToken(storedToken);
      if (storedUser) {
        setUser(storedUser);
      } else {
        localStorage.removeItem('token');
        delete api.defaults.headers.common.Authorization;
        setToken(null);
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => {
      localStorage.removeItem('token');
      delete api.defaults.headers.common.Authorization;
      setToken(null);
      setUser(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const accessToken = response.data.access_token;
    const authenticatedUser = buildUserFromToken(accessToken);
    if (!authenticatedUser) {
      throw new Error('Login response did not contain a valid access token.');
    }
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    setUser(authenticatedUser);
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
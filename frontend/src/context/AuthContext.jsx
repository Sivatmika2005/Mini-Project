import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem('session_token');
      if (token) {
        try {
          const res = await api.getMe();
          setUser(res.user);
        } catch (e) {
          localStorage.removeItem('session_token');
          setUser(null);
        }
      }
      setLoading(false);
    }
    checkAuth();
  }, []);

  const login = async (username_or_email, password) => {
    const res = await api.login(username_or_email, password);
    localStorage.setItem('session_token', res.token);
    setUser(res.user);
    return res;
  };

  const register = async (username, email, password) => {
    const res = await api.register(username, email, password);
    if (res.token) {
      localStorage.setItem('session_token', res.token);
      setUser(res.user);
    }
    return res;
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (e) {}
    localStorage.removeItem('session_token');
    setUser(null);
  };

  const updateUser = (updatedFields) => {
    setUser((prev) => (prev ? { ...prev, ...updatedFields } : null));
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

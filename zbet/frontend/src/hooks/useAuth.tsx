'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User, LoginCredentials, UserCreate } from '@/types';
import { authApi, tokenManager, zcashApi } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => void;
  refreshBalance: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  const isAuthenticated = !!user;

  useEffect(() => {
    setMounted(true);
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Only check auth status on client side to avoid hydration issues
      if (typeof window === 'undefined') {
        setLoading(false);
        return;
      }
      
      const token = tokenManager.getToken();
      if (token) {
        const isValid = await authApi.checkTokenStatus();
        if (isValid) {
          const userData = await authApi.getMe();
          setUser(userData);
        } else {
          tokenManager.removeToken();
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      tokenManager.removeToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      const authData = await authApi.login(credentials);
      tokenManager.setToken(authData.access_token);
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (userData: UserCreate) => {
    try {
      const newUser = await authApi.register(userData);
      // Auto-login after registration
      await login({ username: userData.username, password: userData.password });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    tokenManager.removeToken();
    setUser(null);
  };

  const refreshBalance = async () => {
    try {
      if (!user) {
        throw new Error('No user logged in');
      }
      
      const balanceData = await zcashApi.refreshBalance();
      
      // Update user with new balance information
      setUser(prevUser => {
        if (!prevUser) return null;
        return {
          ...prevUser,
          balance: balanceData.balance.toString(),
          transparent_balance: balanceData.transparent_balance,
          shielded_balance: balanceData.shielded_balance
        };
      });
    } catch (error) {
      console.error('Failed to refresh balance:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading: loading || !mounted,
        login,
        register,
        logout,
        refreshBalance,
        isAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

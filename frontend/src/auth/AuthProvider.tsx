/** Зберігає стан авторизації і тримає токен у localStorage. */

import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';

import { setUnauthorizedHandler } from '@/api/client';
import { authApi } from '@/api/endpoints';
import { AuthContext, type AuthContextValue } from '@/auth/AuthContext';
import { clearToken, getToken, setToken } from '@/lib/storage';
import type { LoginPayload, RegisterPayload, User } from '@/types/api';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  const resetSession = useCallback(() => {
    clearToken();
    setUser(null);
    queryClient.clear();
  }, [queryClient]);

  /** Токен у localStorage міг протермінуватися, тому перевіряємо його на сервері. */
  const refresh = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const current = await authApi.me();
      setUser(current);
    } catch {
      resetSession();
    } finally {
      setIsLoading(false);
    }
  }, [resetSession]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
      queryClient.clear();
    });
  }, [queryClient]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const response = await authApi.login(payload);
      setToken(response.access_token);
      setUser(response.user);
      await queryClient.invalidateQueries();
      return response.user;
    },
    [queryClient],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      const response = await authApi.register(payload);
      setToken(response.access_token);
      setUser(response.user);
      await queryClient.invalidateQueries();
      return response.user;
    },
    [queryClient],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Навіть якщо сервер недоступний, локальний вихід має спрацювати.
    }
    resetSession();
  }, [resetSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
      refresh,
    }),
    [user, isLoading, login, register, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

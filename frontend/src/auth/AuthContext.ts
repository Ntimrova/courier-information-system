/** Контекст авторизації (окремий файл, щоб не ламати Fast Refresh). */

import { createContext } from 'react';

import type { LoginPayload, RegisterPayload, User } from '@/types/api';

export interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

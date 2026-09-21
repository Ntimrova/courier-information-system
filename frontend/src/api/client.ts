/** Єдиний axios-клієнт: підставляє токен і обробляє 401. */

import axios from 'axios';

import { clearToken, getToken } from '@/lib/storage';

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 20_000,
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Викликається, коли токен більше не діє. Підставляється в AuthProvider. */
let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const url: string = error?.config?.url ?? '';
    // Невдалий вхід теж повертає 401, але це не протермінована сесія,
    // тож на сторінці входу нікого нікуди не перекидаємо.
    const isLoginAttempt = url.includes('/auth/login');

    if (
      (status === 401 || error?.response?.data?.error?.code === 'USER_INACTIVE') &&
      !isLoginAttempt
    ) {
      clearToken();
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

export const API_V1 = '/api/v1';

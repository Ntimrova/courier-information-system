/**
 * Робота з JWT у localStorage.
 *
 * Згідно з вимогами тут зберігається лише токен. Дані користувача,
 * замовлення й довідники завжди беруться з backend через TanStack Query.
 */

const TOKEN_KEY = 'cis.access_token';

export function getToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Режим приватного перегляду може забороняти запис - працюємо далі.
  }
}

export function clearToken(): void {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Нічого не робимо: токен усе одно зникне разом із вкладкою.
  }
}

/** Перетворення помилок API на зрозумілий користувачу текст. */

import { AxiosError } from 'axios';

import { t } from '@/i18n/uk';
import type { ApiErrorBody } from '@/types/api';

export interface ReadableError {
  message: string;
  code: string;
  fieldErrors: Record<string, string>;
  status?: number;
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  return (
    typeof value === 'object' &&
    value !== null &&
    'error' in value &&
    typeof (value as ApiErrorBody).error === 'object'
  );
}

/**
 * Розкладає будь-яку помилку на текст для користувача і помилки по полях.
 *
 * Backend завжди повертає один формат, тож тут потрібен лише один розбір,
 * а не окремий на кожну сторінку.
 */
export function toReadableError(error: unknown): ReadableError {
  if (error instanceof AxiosError) {
    if (!error.response) {
      return { message: t.networkError, code: 'NETWORK_ERROR', fieldErrors: {} };
    }

    const body = error.response.data;
    if (isApiErrorBody(body)) {
      const fieldErrors: Record<string, string> = {};
      const details = body.error.details;
      if (Array.isArray(details)) {
        for (const item of details) {
          if (item.field) {
            fieldErrors[item.field] = item.message ?? '';
          }
        }
      }
      return {
        message: body.error.message || t.unknownError,
        code: body.error.code,
        fieldErrors,
        status: error.response.status,
      };
    }

    return {
      message: error.message || t.unknownError,
      code: 'HTTP_ERROR',
      fieldErrors: {},
      status: error.response.status,
    };
  }

  if (error instanceof Error) {
    return { message: error.message || t.unknownError, code: 'ERROR', fieldErrors: {} };
  }

  return { message: t.unknownError, code: 'UNKNOWN', fieldErrors: {} };
}

export function errorMessage(error: unknown): string {
  return toReadableError(error).message;
}

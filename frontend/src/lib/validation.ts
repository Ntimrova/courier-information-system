/**
 * Спільні правила валідації форм.
 *
 * Ті самі обмеження діють і на backend: frontend лише швидше показує
 * помилку, а останнє слово завжди за сервером.
 */

import { z } from 'zod';

/** Прибирає пробіли, дужки й дефіси: "+38 (067) 123-45-67" -> "+380671234567". */
export function normalizePhone(value: string): string {
  const cleaned = value.replace(/[\s()\-.]/g, '').trim();
  return cleaned.startsWith('00') ? `+${cleaned.slice(2)}` : cleaned;
}

export const phoneField = z
  .string()
  .min(1, 'Введіть телефон')
  .transform(normalizePhone)
  .refine((value) => /^\+?\d{10,15}$/.test(value), {
    message: 'Телефон має містити від 10 до 15 цифр, наприклад +380671234567',
  });

export const nameField = z
  .string()
  .trim()
  .min(2, 'Щонайменше 2 символи')
  .max(80, 'Не більше 80 символів');

export const personNameField = z
  .string()
  .trim()
  .min(2, 'Щонайменше 2 символи')
  .max(160, 'Не більше 160 символів');

export const addressField = z
  .string()
  .trim()
  .min(5, 'Вкажіть адресу повністю, щонайменше 5 символів')
  .max(300, 'Не більше 300 символів');

export const descriptionField = z
  .string()
  .trim()
  .min(3, 'Опишіть відправлення, щонайменше 3 символи')
  .max(500, 'Не більше 500 символів');

export const commentField = z
  .string()
  .trim()
  .max(1000, 'Не більше 1000 символів')
  .optional()
  .or(z.literal(''));

export const weightField = z
  .string()
  .min(1, 'Вкажіть вагу')
  .refine((value) => !Number.isNaN(Number(value.replace(',', '.'))), {
    message: 'Вага має бути числом',
  })
  .refine((value) => Number(value.replace(',', '.')) > 0, {
    message: 'Вага має бути більшою за нуль',
  })
  .refine((value) => Number(value.replace(',', '.')) <= 1000, {
    message: 'Вага не може перевищувати 1000 кг',
  });

/** Дата доставки не може бути в минулому. */
export const futureDateField = z
  .string()
  .min(1, 'Вкажіть бажану дату доставки')
  .refine(
    (value) => {
      const chosen = new Date(`${value}T00:00:00`);
      if (Number.isNaN(chosen.getTime())) return false;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return chosen >= today;
    },
    { message: 'Дата доставки не може бути в минулому' },
  );

export const passwordField = z
  .string()
  .min(8, 'Пароль має містити щонайменше 8 символів')
  .max(128, 'Пароль занадто довгий');

/** Необов'язковий пароль: порожній рядок означає "не змінювати". */
export const optionalPasswordField = z
  .string()
  .max(128, 'Пароль занадто довгий')
  .refine((value) => value === '' || value.length >= 8, {
    message: 'Пароль має містити щонайменше 8 символів',
  });

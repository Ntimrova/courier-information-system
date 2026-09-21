/** Схеми валідації форми користувача. */

import { z } from 'zod';

import { nameField, optionalPasswordField, passwordField, phoneField } from '@/lib/validation';
import { USER_ROLES } from '@/types/api';

const baseFields = {
  first_name: nameField,
  last_name: nameField,
  email: z.string().min(1, 'Введіть email').email('Некоректний email').max(255),
  phone: phoneField,
  role: z.enum(USER_ROLES),
};

/** Під час створення пароль обов'язковий. */
export const createUserSchema = z.object({ ...baseFields, password: passwordField });

/** Під час редагування порожній пароль означає "не змінювати". */
export const editUserSchema = z.object({ ...baseFields, password: optionalPasswordField });

export type UserFormValues = z.infer<typeof createUserSchema>;

export const USER_FORM_FIELDS = [
  'first_name',
  'last_name',
  'email',
  'phone',
  'role',
  'password',
] as const;

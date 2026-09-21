/** Схема валідації форми замовлення. Ті самі правила діють на backend. */

import { z } from 'zod';

import {
  addressField,
  commentField,
  descriptionField,
  futureDateField,
  personNameField,
  phoneField,
  weightField,
} from '@/lib/validation';
import { DELIVERY_TYPES, PACKAGE_SIZES } from '@/types/api';

export const orderFormSchema = z
  .object({
    customer_id: z.string().optional(),
    sender_name: personNameField,
    sender_phone: phoneField,
    pickup_address: addressField,
    recipient_name: personNameField,
    recipient_phone: phoneField,
    delivery_address: addressField,
    package_description: descriptionField,
    package_weight: weightField,
    package_size: z.enum(PACKAGE_SIZES),
    delivery_type: z.enum(DELIVERY_TYPES),
    desired_delivery_date: futureDateField,
    comment: commentField,
  })
  .refine(
    (values) =>
      values.pickup_address.trim().toLowerCase() !== values.delivery_address.trim().toLowerCase(),
    {
      path: ['delivery_address'],
      message: 'Адреса отримання та адреса доставки не повинні збігатися',
    },
  );

export type OrderFormValues = z.infer<typeof orderFormSchema>;

/** Значення, з яких починається порожня форма. */
export const emptyOrderForm: OrderFormValues = {
  customer_id: '',
  sender_name: '',
  sender_phone: '',
  pickup_address: '',
  recipient_name: '',
  recipient_phone: '',
  delivery_address: '',
  package_description: '',
  package_weight: '',
  package_size: 'SMALL',
  delivery_type: 'STANDARD',
  desired_delivery_date: '',
  comment: '',
};

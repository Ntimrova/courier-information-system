/** Кольорова позначка статусу замовлення. */

import { Chip, type ChipProps } from '@mui/material';

import { STATUS_LABELS } from '@/i18n/uk';
import type { AnyOrderStatus } from '@/types/api';

const STATUS_COLORS: Record<AnyOrderStatus, ChipProps['color']> = {
  CREATED: 'info',
  CONFIRMED: 'primary',
  WAITING_FOR_COURIER: 'warning',
  CANCELLED: 'error',
  COURIER_ASSIGNED: 'secondary',
  PICKED_UP: 'secondary',
  IN_TRANSIT: 'secondary',
  DELIVERED: 'success',
  DELIVERY_FAILED: 'error',
};

export function StatusChip({
  status,
  size = 'small',
}: {
  status: AnyOrderStatus;
  size?: 'small' | 'medium';
}) {
  return (
    <Chip
      label={STATUS_LABELS[status] ?? status}
      color={STATUS_COLORS[status] ?? 'default'}
      size={size}
      variant="filled"
    />
  );
}

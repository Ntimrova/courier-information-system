/** Спільна форма створення й редагування замовлення. */

import { zodResolver } from '@hookform/resolvers/zod';
import {
  Alert,
  Box,
  Button,
  Divider,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';

import { usersApi } from '@/api/endpoints';
import { mustChooseCustomer } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import {
  emptyOrderForm,
  orderFormSchema,
  type OrderFormValues,
} from '@/features/orders/orderSchema';
import { DELIVERY_TYPE_LABELS, PACKAGE_SIZE_LABELS, t } from '@/i18n/uk';
import { toReadableError } from '@/lib/errors';
import { DELIVERY_TYPES, PACKAGE_SIZES } from '@/types/api';

export interface OrderFormProps {
  defaultValues?: Partial<OrderFormValues>;
  submitLabel: string;
  /** У режимі редагування клієнта змінювати не можна. */
  mode: 'create' | 'edit';
  submitting: boolean;
  submitError?: unknown;
  onSubmit: (values: OrderFormValues) => void;
  onCancel: () => void;
}

export function OrderForm({
  defaultValues,
  submitLabel,
  mode,
  submitting,
  submitError,
  onSubmit,
  onCancel,
}: OrderFormProps) {
  const { user } = useAuth();
  const needsCustomer = mode === 'create' && user !== null && mustChooseCustomer(user.role);

  const customersQuery = useQuery({
    queryKey: ['users', 'customer-options'],
    queryFn: usersApi.customerOptions,
    enabled: needsCustomer,
  });

  const {
    control,
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<OrderFormValues>({
    resolver: zodResolver(orderFormSchema),
    defaultValues: { ...emptyOrderForm, ...defaultValues },
  });

  // Помилки валідації з backend показуємо біля відповідних полів.
  useEffect(() => {
    if (!submitError) return;
    const readable = toReadableError(submitError);
    for (const [field, message] of Object.entries(readable.fieldErrors)) {
      if (field in emptyOrderForm) {
        setError(field as keyof OrderFormValues, { type: 'server', message });
      }
    }
  }, [submitError, setError]);

  const serverMessage = submitError ? toReadableError(submitError).message : null;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Stack spacing={3}>
        {serverMessage ? <Alert severity="error">{serverMessage}</Alert> : null}

        {needsCustomer ? (
          <Paper variant="outlined" sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" gutterBottom>
              {t.fieldCustomer}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Controller
              name="customer_id"
              control={control}
              rules={{ required: true }}
              render={({ field }) => (
                <TextField
                  select
                  label={t.fieldCustomer}
                  value={field.value ?? ''}
                  onChange={field.onChange}
                  error={Boolean(errors.customer_id)}
                  helperText={
                    errors.customer_id?.message ??
                    'Оберіть клієнта, від імені якого оформлюється замовлення'
                  }
                  disabled={customersQuery.isPending}
                >
                  {(customersQuery.data ?? []).map((customer) => (
                    <MenuItem key={customer.id} value={String(customer.id)}>
                      {customer.full_name} ({customer.email})
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Paper>
        ) : null}

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionSender}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label={t.fieldSenderName}
                error={Boolean(errors.sender_name)}
                helperText={errors.sender_name?.message}
                {...register('sender_name')}
              />
              <TextField
                label={t.fieldSenderPhone}
                placeholder="+380671234567"
                error={Boolean(errors.sender_phone)}
                helperText={errors.sender_phone?.message}
                {...register('sender_phone')}
              />
            </Stack>
            <TextField
              label={t.fieldPickupAddress}
              error={Boolean(errors.pickup_address)}
              helperText={errors.pickup_address?.message}
              {...register('pickup_address')}
            />
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionRecipient}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label={t.fieldRecipientName}
                error={Boolean(errors.recipient_name)}
                helperText={errors.recipient_name?.message}
                {...register('recipient_name')}
              />
              <TextField
                label={t.fieldRecipientPhone}
                placeholder="+380501112233"
                error={Boolean(errors.recipient_phone)}
                helperText={errors.recipient_phone?.message}
                {...register('recipient_phone')}
              />
            </Stack>
            <TextField
              label={t.fieldDeliveryAddress}
              error={Boolean(errors.delivery_address)}
              helperText={errors.delivery_address?.message}
              {...register('delivery_address')}
            />
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionPackage}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack spacing={2}>
            <TextField
              label={t.fieldPackageDescription}
              multiline
              minRows={2}
              error={Boolean(errors.package_description)}
              helperText={errors.package_description?.message}
              {...register('package_description')}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label={t.fieldPackageWeight}
                placeholder="1.5"
                inputMode="decimal"
                error={Boolean(errors.package_weight)}
                helperText={errors.package_weight?.message}
                {...register('package_weight')}
              />
              <Controller
                name="package_size"
                control={control}
                render={({ field }) => (
                  <TextField
                    select
                    label={t.fieldPackageSize}
                    value={field.value}
                    onChange={field.onChange}
                    error={Boolean(errors.package_size)}
                    helperText={errors.package_size?.message}
                  >
                    {PACKAGE_SIZES.map((size) => (
                      <MenuItem key={size} value={size}>
                        {PACKAGE_SIZE_LABELS[size]}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Controller
                name="delivery_type"
                control={control}
                render={({ field }) => (
                  <TextField
                    select
                    label={t.fieldDeliveryType}
                    value={field.value}
                    onChange={field.onChange}
                    error={Boolean(errors.delivery_type)}
                    helperText={errors.delivery_type?.message}
                  >
                    {DELIVERY_TYPES.map((type) => (
                      <MenuItem key={type} value={type}>
                        {DELIVERY_TYPE_LABELS[type]}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
              <TextField
                type="date"
                label={t.fieldDesiredDate}
                slotProps={{ inputLabel: { shrink: true } }}
                error={Boolean(errors.desired_delivery_date)}
                helperText={errors.desired_delivery_date?.message}
                {...register('desired_delivery_date')}
              />
            </Stack>
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionExtra}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TextField
            label={t.fieldComment}
            multiline
            minRows={3}
            error={Boolean(errors.comment)}
            helperText={errors.comment?.message}
            {...register('comment')}
          />
        </Paper>

        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button onClick={onCancel} disabled={submitting}>
            {t.actionCancel}
          </Button>
          <Button type="submit" variant="contained" disabled={submitting}>
            {submitting ? t.saving : submitLabel}
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
}

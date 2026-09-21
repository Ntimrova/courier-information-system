/** Форма створення й редагування користувача (для адміністратора). */

import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, MenuItem, Paper, Stack, TextField } from '@mui/material';
import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';

import {
  createUserSchema,
  editUserSchema,
  USER_FORM_FIELDS,
  type UserFormValues,
} from '@/features/users/userSchema';
import { ROLE_LABELS, t } from '@/i18n/uk';
import { toReadableError } from '@/lib/errors';
import { USER_ROLES } from '@/types/api';

export interface UserFormProps {
  mode: 'create' | 'edit';
  defaultValues?: Partial<UserFormValues>;
  submitting: boolean;
  submitError?: unknown;
  onSubmit: (values: UserFormValues) => void;
  onCancel: () => void;
}

export function UserForm({
  mode,
  defaultValues,
  submitting,
  submitError,
  onSubmit,
  onCancel,
}: UserFormProps) {
  const {
    control,
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<UserFormValues>({
    resolver: zodResolver(mode === 'create' ? createUserSchema : editUserSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      role: 'CUSTOMER',
      password: '',
      ...defaultValues,
    },
  });

  useEffect(() => {
    if (!submitError) return;
    const readable = toReadableError(submitError);
    for (const [field, message] of Object.entries(readable.fieldErrors)) {
      if ((USER_FORM_FIELDS as readonly string[]).includes(field)) {
        setError(field as keyof UserFormValues, { type: 'server', message });
      }
    }
  }, [submitError, setError]);

  const serverMessage = submitError ? toReadableError(submitError).message : null;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Stack spacing={3}>
        {serverMessage ? <Alert severity="error">{serverMessage}</Alert> : null}

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label={t.fieldFirstName}
                error={Boolean(errors.first_name)}
                helperText={errors.first_name?.message}
                {...register('first_name')}
              />
              <TextField
                label={t.fieldLastName}
                error={Boolean(errors.last_name)}
                helperText={errors.last_name?.message}
                {...register('last_name')}
              />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label={t.fieldEmail}
                type="email"
                error={Boolean(errors.email)}
                helperText={errors.email?.message}
                {...register('email')}
              />
              <TextField
                label={t.fieldPhone}
                placeholder="+380671234567"
                error={Boolean(errors.phone)}
                helperText={errors.phone?.message}
                {...register('phone')}
              />
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Controller
                name="role"
                control={control}
                render={({ field }) => (
                  <TextField
                    select
                    label={t.fieldRole}
                    value={field.value}
                    onChange={field.onChange}
                    error={Boolean(errors.role)}
                    helperText={errors.role?.message}
                  >
                    {USER_ROLES.map((value) => (
                      <MenuItem key={value} value={value}>
                        {ROLE_LABELS[value]}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
              <TextField
                label={mode === 'create' ? t.fieldPassword : t.fieldNewPassword}
                type="password"
                autoComplete="new-password"
                error={Boolean(errors.password)}
                helperText={
                  errors.password?.message ?? (mode === 'edit' ? t.leavePasswordEmpty : undefined)
                }
                {...register('password')}
              />
            </Stack>
          </Stack>
        </Paper>

        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button onClick={onCancel} disabled={submitting}>
            {t.actionCancel}
          </Button>
          <Button type="submit" variant="contained" disabled={submitting}>
            {submitting ? t.saving : mode === 'create' ? t.actionCreate : t.actionSave}
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
}

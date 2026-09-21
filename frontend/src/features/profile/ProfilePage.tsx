import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, Chip, Paper, Stack, TextField, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { usersApi } from '@/api/endpoints';
import { useAuth } from '@/auth/useAuth';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { ROLE_LABELS, t } from '@/i18n/uk';
import { toReadableError } from '@/lib/errors';
import { formatDateTime } from '@/lib/format';
import { nameField, optionalPasswordField, phoneField } from '@/lib/validation';
import type { ProfileUpdatePayload } from '@/types/api';

const profileSchema = z.object({
  first_name: nameField,
  last_name: nameField,
  phone: phoneField,
  password: optionalPasswordField,
});

type ProfileForm = z.infer<typeof profileSchema>;

export function ProfilePage() {
  const { user, refresh } = useAuth();
  const notify = useNotify();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name ?? '',
      last_name: user?.last_name ?? '',
      phone: user?.phone ?? '',
      password: '',
    },
  });

  const mutation = useMutation({
    mutationFn: (payload: ProfileUpdatePayload) => usersApi.updateProfile(payload),
    onSuccess: async (updated) => {
      notify(t.profileUpdated);
      await refresh();
      reset({
        first_name: updated.first_name,
        last_name: updated.last_name,
        phone: updated.phone,
        password: '',
      });
    },
  });

  if (!user) return null;

  const serverMessage = mutation.error ? toReadableError(mutation.error).message : null;

  const onSubmit = (values: ProfileForm) => {
    const payload: ProfileUpdatePayload = {
      first_name: values.first_name,
      last_name: values.last_name,
      phone: values.phone,
    };
    if (values.password) payload.password = values.password;
    mutation.mutate(payload);
  };

  return (
    <Box sx={{ maxWidth: 760 }}>
      <PageHeader title={t.profileTitle} subtitle={t.profileSubtitle} />

      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap alignItems="center">
            <Box>
              <Typography variant="caption" color="text.secondary">
                {t.fieldEmail}
              </Typography>
              <Typography>{user.email}</Typography>
              <Typography variant="caption" color="text.secondary">
                {t.profileEmailHint}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                {t.fieldRole}
              </Typography>
              <Chip label={ROLE_LABELS[user.role]} color="primary" size="small" />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                {t.colCreatedAt}
              </Typography>
              <Typography>{formatDateTime(user.created_at)}</Typography>
            </Box>
          </Stack>
        </Paper>

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
                <TextField
                  label={t.fieldPhone}
                  placeholder="+380671234567"
                  error={Boolean(errors.phone)}
                  helperText={errors.phone?.message}
                  {...register('phone')}
                />
                <TextField
                  label={t.fieldNewPassword}
                  type="password"
                  autoComplete="new-password"
                  error={Boolean(errors.password)}
                  helperText={errors.password?.message ?? t.leavePasswordEmpty}
                  {...register('password')}
                />
              </Stack>
            </Paper>

            <Stack direction="row" justifyContent="flex-end">
              <Button type="submit" variant="contained" disabled={mutation.isPending}>
                {mutation.isPending ? t.saving : t.actionSave}
              </Button>
            </Stack>
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
}

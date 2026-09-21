import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, Link, Stack, TextField, Typography } from '@mui/material';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { useAuth } from '@/auth/useAuth';
import { AuthShell } from '@/features/auth/AuthShell';
import { t } from '@/i18n/uk';
import { errorMessage } from '@/lib/errors';
import { nameField, phoneField } from '@/lib/validation';

const registerSchema = z
  .object({
    first_name: nameField,
    last_name: nameField,
    email: z.string().min(1, 'Введіть email').email('Некоректний email').max(255),
    phone: phoneField,
    password: z
      .string()
      .min(8, 'Пароль має містити щонайменше 8 символів')
      .max(128, 'Пароль занадто довгий'),
    password_repeat: z.string().min(1, 'Повторіть пароль'),
  })
  .refine((values) => values.password === values.password_repeat, {
    path: ['password_repeat'],
    message: 'Паролі не збігаються',
  });

type RegisterForm = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      password: '',
      password_repeat: '',
    },
  });

  const onSubmit = async (values: RegisterForm) => {
    setFormError(null);
    try {
      await registerUser({
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        phone: values.phone,
        password: values.password,
      });
      navigate('/dashboard', { replace: true });
    } catch (error) {
      setFormError(errorMessage(error));
    }
  };

  return (
    <AuthShell title={t.registerTitle} subtitle={t.registerSubtitle}>
      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          {formError ? <Alert severity="error">{formError}</Alert> : null}

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              label={t.fieldFirstName}
              autoFocus
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
            label={t.fieldEmail}
            type="email"
            autoComplete="email"
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
          <TextField
            label={t.fieldPassword}
            type="password"
            autoComplete="new-password"
            error={Boolean(errors.password)}
            helperText={errors.password?.message}
            {...register('password')}
          />
          <TextField
            label={t.fieldPasswordRepeat}
            type="password"
            autoComplete="new-password"
            error={Boolean(errors.password_repeat)}
            helperText={errors.password_repeat?.message}
            {...register('password_repeat')}
          />

          <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
            {isSubmitting ? t.loading : t.submitRegister}
          </Button>

          <Typography variant="body2" align="center" color="text.secondary">
            {t.haveAccount}{' '}
            <Link component={RouterLink} to="/login">
              {t.goToLogin}
            </Link>
          </Typography>
        </Stack>
      </Box>
    </AuthShell>
  );
}

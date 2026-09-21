import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, Link, Stack, TextField, Typography } from '@mui/material';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { useAuth } from '@/auth/useAuth';
import { AuthShell } from '@/features/auth/AuthShell';
import { t } from '@/i18n/uk';
import { errorMessage } from '@/lib/errors';

const loginSchema = z.object({
  email: z.string().min(1, 'Введіть email').email('Некоректний email'),
  password: z.string().min(1, 'Введіть пароль'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async (values: LoginForm) => {
    setFormError(null);
    try {
      await login(values);
      const from = (location.state as { from?: string } | null)?.from ?? '/dashboard';
      navigate(from, { replace: true });
    } catch (error) {
      setFormError(errorMessage(error));
    }
  };

  return (
    <AuthShell title={t.loginTitle} subtitle={t.loginSubtitle}>
      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          {formError ? <Alert severity="error">{formError}</Alert> : null}

          <TextField
            label={t.fieldEmail}
            type="email"
            autoComplete="email"
            autoFocus
            error={Boolean(errors.email)}
            helperText={errors.email?.message}
            {...register('email')}
          />
          <TextField
            label={t.fieldPassword}
            type="password"
            autoComplete="current-password"
            error={Boolean(errors.password)}
            helperText={errors.password?.message}
            {...register('password')}
          />

          <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
            {isSubmitting ? t.loading : t.submitLogin}
          </Button>

          <Typography variant="body2" align="center" color="text.secondary">
            {t.noAccount}{' '}
            <Link component={RouterLink} to="/register">
              {t.goToRegister}
            </Link>
          </Typography>
        </Stack>
      </Box>
    </AuthShell>
  );
}

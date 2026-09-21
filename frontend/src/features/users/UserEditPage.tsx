import { Box } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';

import { usersApi } from '@/api/endpoints';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { ErrorState, LoadingState } from '@/components/common/StateViews';
import { UserForm } from '@/features/users/UserForm';
import type { UserFormValues } from '@/features/users/userSchema';
import { t } from '@/i18n/uk';
import type { UserUpdatePayload } from '@/types/api';

export function UserEditPage() {
  const { id } = useParams<{ id: string }>();
  const userId = Number(id);
  const navigate = useNavigate();
  const notify = useNotify();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['users', userId],
    queryFn: () => usersApi.get(userId),
    enabled: Number.isFinite(userId),
  });

  const mutation = useMutation({
    mutationFn: (payload: UserUpdatePayload) => usersApi.update(userId, payload),
    onSuccess: async () => {
      notify(t.userUpdated);
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      navigate('/users', { replace: true });
    },
  });

  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  const target = query.data;

  const handleSubmit = (values: UserFormValues) => {
    const payload: UserUpdatePayload = {
      first_name: values.first_name,
      last_name: values.last_name,
      email: values.email,
      phone: values.phone,
      role: values.role,
    };
    // Порожнє поле пароля означає "залишити як було".
    if (values.password) payload.password = values.password;
    mutation.mutate(payload);
  };

  return (
    <Box sx={{ maxWidth: 760 }}>
      <PageHeader title={t.userEditTitle} subtitle={target.email} />
      <UserForm
        mode="edit"
        defaultValues={{
          first_name: target.first_name,
          last_name: target.last_name,
          email: target.email,
          phone: target.phone,
          role: target.role,
          password: '',
        }}
        submitting={mutation.isPending}
        submitError={mutation.error}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/users')}
      />
    </Box>
  );
}

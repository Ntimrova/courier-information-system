import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { usersApi } from '@/api/endpoints';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { UserForm } from '@/features/users/UserForm';
import type { UserFormValues } from '@/features/users/userSchema';
import { t } from '@/i18n/uk';
import type { UserCreatePayload } from '@/types/api';

export function UserCreatePage() {
  const navigate = useNavigate();
  const notify = useNotify();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: UserCreatePayload) => usersApi.create(payload),
    onSuccess: async () => {
      notify(t.userCreated);
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      navigate('/users', { replace: true });
    },
  });

  return (
    <Box sx={{ maxWidth: 760 }}>
      <PageHeader title={t.userCreateTitle} />
      <UserForm
        mode="create"
        submitting={mutation.isPending}
        submitError={mutation.error}
        onSubmit={(values: UserFormValues) =>
          mutation.mutate({
            first_name: values.first_name,
            last_name: values.last_name,
            email: values.email,
            phone: values.phone,
            password: values.password,
            role: values.role,
            is_active: true,
          })
        }
        onCancel={() => navigate('/users')}
      />
    </Box>
  );
}

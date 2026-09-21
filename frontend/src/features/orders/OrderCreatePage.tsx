import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { ordersApi } from '@/api/endpoints';
import { mustChooseCustomer } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { PageHeader } from '@/components/common/PageHeader';
import { useNotify } from '@/components/common/NotifyContext';
import { OrderForm } from '@/features/orders/OrderForm';
import type { OrderFormValues } from '@/features/orders/orderSchema';
import { t } from '@/i18n/uk';
import type { OrderPayload } from '@/types/api';

export function OrderCreatePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const notify = useNotify();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: OrderPayload) => ordersApi.create(payload),
    onSuccess: async (order) => {
      notify(t.orderCreated);
      await queryClient.invalidateQueries({ queryKey: ['orders'] });
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      navigate(`/orders/${order.id}`, { replace: true });
    },
  });

  const handleSubmit = (values: OrderFormValues) => {
    const needsCustomer = user ? mustChooseCustomer(user.role) : false;
    const payload: OrderPayload = {
      sender_name: values.sender_name,
      sender_phone: values.sender_phone,
      pickup_address: values.pickup_address,
      recipient_name: values.recipient_name,
      recipient_phone: values.recipient_phone,
      delivery_address: values.delivery_address,
      package_description: values.package_description,
      package_weight: values.package_weight.replace(',', '.'),
      package_size: values.package_size,
      delivery_type: values.delivery_type,
      desired_delivery_date: values.desired_delivery_date,
      comment: values.comment ? values.comment : null,
      customer_id: needsCustomer && values.customer_id ? Number(values.customer_id) : null,
    };
    mutation.mutate(payload);
  };

  const defaults =
    user && user.role === 'CUSTOMER'
      ? { sender_name: user.full_name, sender_phone: user.phone }
      : undefined;

  return (
    <Box sx={{ maxWidth: 900 }}>
      <PageHeader title={t.orderCreateTitle} />
      <OrderForm
        mode="create"
        defaultValues={defaults}
        submitLabel={t.actionCreate}
        submitting={mutation.isPending}
        submitError={mutation.error}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/orders')}
      />
    </Box>
  );
}

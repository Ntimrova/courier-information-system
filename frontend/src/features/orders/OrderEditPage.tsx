import { Box } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';

import { ordersApi } from '@/api/endpoints';
import { canEditOrder } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { ErrorState, LoadingState } from '@/components/common/StateViews';
import { OrderForm } from '@/features/orders/OrderForm';
import type { OrderFormValues } from '@/features/orders/orderSchema';
import { ForbiddenPage } from '@/pages/ForbiddenPage';
import { t } from '@/i18n/uk';
import type { OrderPayload } from '@/types/api';

export function OrderEditPage() {
  const { id } = useParams<{ id: string }>();
  const orderId = Number(id);
  const { user } = useAuth();
  const navigate = useNavigate();
  const notify = useNotify();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['orders', orderId],
    queryFn: () => ordersApi.get(orderId),
    enabled: Number.isFinite(orderId),
  });

  const mutation = useMutation({
    mutationFn: (payload: Partial<OrderPayload>) => ordersApi.update(orderId, payload),
    onSuccess: async () => {
      notify(t.orderUpdated);
      await queryClient.invalidateQueries({ queryKey: ['orders'] });
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      navigate(`/orders/${orderId}`, { replace: true });
    },
  });

  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  const order = query.data;
  const isOwnOrder = user?.id === order.customer_id;
  if (!user || !canEditOrder(user.role, order.status, isOwnOrder)) {
    return <ForbiddenPage />;
  }

  const handleSubmit = (values: OrderFormValues) => {
    mutation.mutate({
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
    });
  };

  return (
    <Box sx={{ maxWidth: 900 }}>
      <PageHeader title={t.orderEditTitle} subtitle={order.tracking_number} />
      <OrderForm
        mode="edit"
        defaultValues={{
          sender_name: order.sender_name,
          sender_phone: order.sender_phone,
          pickup_address: order.pickup_address,
          recipient_name: order.recipient_name,
          recipient_phone: order.recipient_phone,
          delivery_address: order.delivery_address,
          package_description: order.package_description,
          package_weight: order.package_weight,
          package_size: order.package_size,
          delivery_type: order.delivery_type,
          desired_delivery_date: order.desired_delivery_date,
          comment: order.comment ?? '',
        }}
        submitLabel={t.actionSave}
        submitting={mutation.isPending}
        submitError={mutation.error}
        onSubmit={handleSubmit}
        onCancel={() => navigate(`/orders/${orderId}`)}
      />
    </Box>
  );
}

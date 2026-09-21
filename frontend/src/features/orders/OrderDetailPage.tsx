import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import {
  Box,
  Button,
  Divider,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';

import { ordersApi } from '@/api/endpoints';
import {
  canCancelOrder,
  canChangeOrderStatus,
  canEditOrder,
  nextStatuses,
} from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { ErrorState, LoadingState } from '@/components/common/StateViews';
import { StatusChip } from '@/components/common/StatusChip';
import { DELIVERY_TYPE_LABELS, PACKAGE_SIZE_LABELS, STATUS_LABELS, t } from '@/i18n/uk';
import { errorMessage } from '@/lib/errors';
import { formatDate, formatDateTime, formatWeight } from '@/lib/format';
import type { OrderStatus } from '@/types/api';

function Field({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ flex: '1 1 260px', minWidth: 220 }}>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
        {value}
      </Typography>
    </Box>
  );
}

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const orderId = Number(id);
  const { user } = useAuth();
  const navigate = useNavigate();
  const notify = useNotify();
  const queryClient = useQueryClient();

  const [cancelOpen, setCancelOpen] = useState(false);
  const [statusValue, setStatusValue] = useState<OrderStatus | ''>('');
  const [statusComment, setStatusComment] = useState('');

  const orderQuery = useQuery({
    queryKey: ['orders', orderId],
    queryFn: () => ordersApi.get(orderId),
    enabled: Number.isFinite(orderId),
  });

  const historyQuery = useQuery({
    queryKey: ['orders', orderId, 'history'],
    queryFn: () => ordersApi.history(orderId),
    enabled: Number.isFinite(orderId) && orderQuery.isSuccess,
  });

  const refreshAll = async () => {
    await queryClient.invalidateQueries({ queryKey: ['orders'] });
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };

  const statusMutation = useMutation({
    mutationFn: ({ status, comment }: { status: OrderStatus; comment?: string }) =>
      ordersApi.changeStatus(orderId, status, comment),
    onSuccess: async () => {
      notify(t.orderStatusChanged);
      setStatusValue('');
      setStatusComment('');
      await refreshAll();
    },
    onError: (error) => notify(errorMessage(error), 'error'),
  });

  const cancelMutation = useMutation({
    mutationFn: (comment?: string) => ordersApi.cancel(orderId, comment),
    onSuccess: async () => {
      notify(t.orderCancelled);
      setCancelOpen(false);
      await refreshAll();
    },
    onError: (error) => {
      notify(errorMessage(error), 'error');
      setCancelOpen(false);
    },
  });

  if (orderQuery.isPending) return <LoadingState />;
  if (orderQuery.isError) {
    return <ErrorState error={orderQuery.error} onRetry={() => orderQuery.refetch()} />;
  }

  const order = orderQuery.data;
  const isOwnOrder = user?.id === order.customer_id;
  const canEdit = user ? canEditOrder(user.role, order.status, isOwnOrder) : false;
  const canCancel = user ? canCancelOrder(user.role, order.status, isOwnOrder) : false;
  const canChangeStatus = user ? canChangeOrderStatus(user.role) : false;
  // Скасування має власну кнопку, тож зі списку статусів його прибираємо.
  const availableStatuses = nextStatuses(order.status).filter((value) => value !== 'CANCELLED');

  return (
    <Box>
      <PageHeader
        title={`${t.orderDetailTitle} ${order.tracking_number}`}
        subtitle={`${t.colCreatedAt}: ${formatDateTime(order.created_at)}`}
        action={
          <Stack direction="row" spacing={1}>
            <Button component={RouterLink} to="/orders" startIcon={<ArrowBackIcon />}>
              {t.actionBack}
            </Button>
            {canEdit ? (
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => navigate(`/orders/${order.id}/edit`)}
              >
                {t.actionEdit}
              </Button>
            ) : null}
            {canCancel ? (
              <Button color="error" variant="outlined" onClick={() => setCancelOpen(true)}>
                {t.actionCancelOrder}
              </Button>
            ) : null}
          </Stack>
        }
      />

      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">{t.colStatus}:</Typography>
            <StatusChip status={order.status} size="medium" />
            {order.cancelled_at ? (
              <Typography variant="body2" color="text.secondary">
                {formatDateTime(order.cancelled_at)}
              </Typography>
            ) : null}
          </Stack>

          {canChangeStatus ? (
            <>
              <Divider sx={{ mb: 2 }} />
              {availableStatuses.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  {t.noStatusAvailable}
                </Typography>
              ) : (
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="flex-start">
                  <TextField
                    select
                    label={t.newStatus}
                    value={statusValue}
                    onChange={(event) => setStatusValue(event.target.value as OrderStatus)}
                    sx={{ minWidth: 220, maxWidth: 260 }}
                  >
                    {availableStatuses.map((value) => (
                      <MenuItem key={value} value={value}>
                        {STATUS_LABELS[value]}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    label={t.statusChangeComment}
                    value={statusComment}
                    onChange={(event) => setStatusComment(event.target.value)}
                    slotProps={{ htmlInput: { maxLength: 500 } }}
                    sx={{ flex: 1 }}
                  />
                  <Button
                    variant="contained"
                    disabled={!statusValue || statusMutation.isPending}
                    onClick={() =>
                      statusValue &&
                      statusMutation.mutate({
                        status: statusValue,
                        comment: statusComment.trim() || undefined,
                      })
                    }
                    sx={{ mt: { sm: 0.25 } }}
                  >
                    {t.actionChangeStatus}
                  </Button>
                </Stack>
              )}
            </>
          ) : null}
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionSender}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack direction="row" flexWrap="wrap" gap={2}>
            <Field
              label={t.fieldCustomer}
              value={order.customer?.full_name ?? `#${order.customer_id}`}
            />
            <Field label={t.fieldSenderName} value={order.sender_name} />
            <Field label={t.fieldSenderPhone} value={order.sender_phone} />
            <Field label={t.fieldPickupAddress} value={order.pickup_address} />
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionRecipient}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack direction="row" flexWrap="wrap" gap={2}>
            <Field label={t.fieldRecipientName} value={order.recipient_name} />
            <Field label={t.fieldRecipientPhone} value={order.recipient_phone} />
            <Field label={t.fieldDeliveryAddress} value={order.delivery_address} />
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t.sectionPackage}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Stack direction="row" flexWrap="wrap" gap={2}>
            <Field label={t.fieldPackageDescription} value={order.package_description} />
            <Field label={t.fieldPackageWeight} value={formatWeight(order.package_weight)} />
            <Field label={t.fieldPackageSize} value={PACKAGE_SIZE_LABELS[order.package_size]} />
            <Field label={t.fieldDeliveryType} value={DELIVERY_TYPE_LABELS[order.delivery_type]} />
            <Field label={t.fieldDesiredDate} value={formatDate(order.desired_delivery_date)} />
            <Field label={t.fieldComment} value={order.comment ?? '-'} />
          </Stack>
        </Paper>

        <Paper variant="outlined">
          <Box sx={{ p: 2.5, pb: 1 }}>
            <Typography variant="subtitle1">{t.historyTitle}</Typography>
          </Box>
          <Divider />
          {historyQuery.isPending ? (
            <LoadingState />
          ) : historyQuery.isError ? (
            <ErrorState error={historyQuery.error} onRetry={() => historyQuery.refetch()} />
          ) : historyQuery.data.length === 0 ? (
            <Box sx={{ p: 3 }}>
              <Typography color="text.secondary">{t.historyEmpty}</Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t.colCreatedAt}</TableCell>
                    <TableCell>{t.colStatus}</TableCell>
                    <TableCell>{t.historyChangedBy}</TableCell>
                    <TableCell>{t.fieldComment}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historyQuery.data.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell sx={{ whiteSpace: 'nowrap' }}>
                        {formatDateTime(entry.created_at)}
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          {entry.previous_status ? (
                            <>
                              <Typography variant="body2" color="text.secondary">
                                {STATUS_LABELS[entry.previous_status]}
                              </Typography>
                              <Typography variant="body2" color="text.disabled">
                                &rarr;
                              </Typography>
                            </>
                          ) : null}
                          <StatusChip status={entry.new_status} />
                        </Stack>
                      </TableCell>
                      <TableCell>{entry.changed_by?.full_name ?? t.historySystem}</TableCell>
                      <TableCell>{entry.comment ?? '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Stack>

      <ConfirmDialog
        open={cancelOpen}
        title={t.confirmCancelTitle}
        description={t.confirmCancelText}
        confirmLabel={t.actionCancelOrder}
        confirmColor="error"
        withComment
        commentLabel={t.cancelReason}
        busy={cancelMutation.isPending}
        onConfirm={(comment) => cancelMutation.mutate(comment)}
        onClose={() => setCancelOpen(false)}
      />
    </Box>
  );
}

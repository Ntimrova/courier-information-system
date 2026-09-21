import AddIcon from '@mui/icons-material/Add';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';

import { dashboardApi } from '@/api/endpoints';
import { canCreateOrders } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/common/StateViews';
import { StatusChip } from '@/components/common/StatusChip';
import { DELIVERY_TYPE_LABELS, t } from '@/i18n/uk';
import { formatDate, truncate } from '@/lib/format';

function StatCard({ label, value, color }: { label: string; value: number; color?: string }) {
  return (
    <Card variant="outlined" sx={{ flex: '1 1 160px', minWidth: 150 }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {label}
        </Typography>
        <Typography variant="h4" sx={{ color: color ?? 'text.primary' }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const query = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardApi.summary,
  });

  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;

  const summary = query.data;
  const counters = summary.counters;
  const isCustomer = summary.scope === 'own';

  return (
    <Box>
      <PageHeader
        title={`${t.dashboardGreeting}, ${user?.first_name ?? ''}!`}
        subtitle={isCustomer ? t.myOrdersTitle : t.dashboardTitle}
        action={
          user && canCreateOrders(user.role) ? (
            <Button
              component={RouterLink}
              to="/orders/new"
              variant="contained"
              startIcon={<AddIcon />}
            >
              {t.navNewOrder}
            </Button>
          ) : undefined
        }
      />

      {summary.scope === 'none' ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          {t.courierComingSoon}
        </Alert>
      ) : null}

      <Stack direction="row" flexWrap="wrap" gap={2} sx={{ mb: 4 }}>
        <StatCard label={t.statTotal} value={counters.total} />
        <StatCard label={t.statCreated} value={counters.created} color="info.main" />
        <StatCard label={t.statConfirmed} value={counters.confirmed} color="primary.main" />
        <StatCard label={t.statWaiting} value={counters.waiting_for_courier} color="warning.main" />
        <StatCard label={t.statCancelled} value={counters.cancelled} color="error.main" />
        {isCustomer ? (
          <StatCard label={t.statActive} value={counters.active} color="success.main" />
        ) : null}
        {summary.total_users !== null ? (
          <StatCard label={t.statUsers} value={summary.total_users} />
        ) : null}
        {summary.active_users !== null ? (
          <StatCard label={t.statActiveUsers} value={summary.active_users} color="success.main" />
        ) : null}
      </Stack>

      <Typography variant="h6" sx={{ mb: 2 }}>
        {t.recentOrders}
      </Typography>

      {summary.recent_orders.length === 0 ? (
        <Paper variant="outlined">
          <EmptyState
            title={t.ordersEmpty}
            action={
              user && canCreateOrders(user.role) ? (
                <Button component={RouterLink} to="/orders/new" variant="contained">
                  {t.navNewOrder}
                </Button>
              ) : undefined
            }
          />
        </Paper>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t.colTrackingNumber}</TableCell>
                {!isCustomer ? <TableCell>{t.colCustomer}</TableCell> : null}
                <TableCell>{t.colDeliveryAddress}</TableCell>
                <TableCell>{t.colDeliveryType}</TableCell>
                <TableCell>{t.colDesiredDate}</TableCell>
                <TableCell>{t.colStatus}</TableCell>
                <TableCell align="right">{t.colActions}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {summary.recent_orders.map((order) => (
                <TableRow key={order.id} hover>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>{order.tracking_number}</TableCell>
                  {!isCustomer ? (
                    <TableCell>{order.customer?.full_name ?? `#${order.customer_id}`}</TableCell>
                  ) : null}
                  <TableCell>{truncate(order.delivery_address, 36)}</TableCell>
                  <TableCell>{DELIVERY_TYPE_LABELS[order.delivery_type]}</TableCell>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>
                    {formatDate(order.desired_delivery_date)}
                  </TableCell>
                  <TableCell>
                    <StatusChip status={order.status} />
                  </TableCell>
                  <TableCell align="right">
                    <Button component={RouterLink} to={`/orders/${order.id}`} size="small">
                      {t.actionView}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

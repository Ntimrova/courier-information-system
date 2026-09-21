import AddIcon from '@mui/icons-material/Add';
import {
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
} from '@mui/material';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { ordersApi } from '@/api/endpoints';
import { canCreateOrders, canSeeAllOrders } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/common/StateViews';
import { StatusChip } from '@/components/common/StatusChip';
import { DELIVERY_TYPE_LABELS, STATUS_LABELS, t } from '@/i18n/uk';
import { formatDate, formatDateTime, truncate } from '@/lib/format';
import { useDebouncedValue } from '@/lib/useDebouncedValue';
import { DELIVERY_TYPES, ORDER_STATUSES, type DeliveryType, type OrderStatus } from '@/types/api';

type SortField = 'tracking_number' | 'desired_delivery_date' | 'status' | 'created_at';

export function OrdersListPage() {
  const { user } = useAuth();
  const showsAllOrders = user ? canSeeAllOrders(user.role) : false;

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [searchInput, setSearchInput] = useState('');
  const [status, setStatus] = useState<OrderStatus | ''>('');
  const [deliveryType, setDeliveryType] = useState<DeliveryType | ''>('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortBy, setSortBy] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const search = useDebouncedValue(searchInput, 400);
  const hasFilters = Boolean(search || status || deliveryType || dateFrom || dateTo);

  // Після зміни фільтра показувати сьому сторінку старого списку немає сенсу.
  useEffect(() => {
    setPage(0);
  }, [search, status, deliveryType, dateFrom, dateTo, pageSize]);

  const query = useQuery({
    queryKey: [
      'orders',
      { page, pageSize, search, status, deliveryType, dateFrom, dateTo, sortBy, sortOrder },
    ],
    queryFn: () =>
      ordersApi.list({
        page: page + 1,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
        search: search || undefined,
        status: status || undefined,
        delivery_type: deliveryType || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
    placeholderData: keepPreviousData,
  });

  const items = useMemo(() => query.data?.items ?? [], [query.data]);
  const total = query.data?.meta.total ?? 0;

  const toggleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const resetFilters = () => {
    setSearchInput('');
    setStatus('');
    setDeliveryType('');
    setDateFrom('');
    setDateTo('');
  };

  return (
    <Box>
      <PageHeader
        title={showsAllOrders ? t.ordersTitle : t.myOrdersTitle}
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

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} flexWrap="wrap" useFlexGap>
          <TextField
            label={t.actionSearch}
            placeholder={t.ordersSearchPlaceholder}
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            sx={{ minWidth: { md: 260 }, flex: '1 1 240px' }}
          />
          <TextField
            select
            label={t.colStatus}
            value={status}
            onChange={(event) => setStatus(event.target.value as OrderStatus | '')}
            sx={{ minWidth: 180, flex: '0 1 200px' }}
          >
            <MenuItem value="">{t.allStatusesOrder}</MenuItem>
            {ORDER_STATUSES.map((value) => (
              <MenuItem key={value} value={value}>
                {STATUS_LABELS[value]}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label={t.filterDeliveryType}
            value={deliveryType}
            onChange={(event) => setDeliveryType(event.target.value as DeliveryType | '')}
            sx={{ minWidth: 170, flex: '0 1 190px' }}
          >
            <MenuItem value="">{t.allDeliveryTypes}</MenuItem>
            {DELIVERY_TYPES.map((value) => (
              <MenuItem key={value} value={value}>
                {DELIVERY_TYPE_LABELS[value]}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            type="date"
            label={t.filterDateFrom}
            value={dateFrom}
            onChange={(event) => setDateFrom(event.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            sx={{ minWidth: 170, flex: '0 1 190px' }}
          />
          <TextField
            type="date"
            label={t.filterDateTo}
            value={dateTo}
            onChange={(event) => setDateTo(event.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            sx={{ minWidth: 170, flex: '0 1 190px' }}
          />
          <Button onClick={resetFilters} disabled={!hasFilters} sx={{ alignSelf: 'center' }}>
            {t.actionReset}
          </Button>
        </Stack>
      </Paper>

      {query.isError ? (
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      ) : query.isPending ? (
        <LoadingState />
      ) : items.length === 0 ? (
        <Paper variant="outlined">
          <EmptyState
            title={hasFilters ? t.ordersEmptyFiltered : t.ordersEmpty}
            action={
              hasFilters ? (
                <Button onClick={resetFilters} variant="outlined">
                  {t.actionReset}
                </Button>
              ) : user && canCreateOrders(user.role) ? (
                <Button component={RouterLink} to="/orders/new" variant="contained">
                  {t.navNewOrder}
                </Button>
              ) : undefined
            }
          />
        </Paper>
      ) : (
        <Paper variant="outlined">
          <TableContainer>
            <Table size="small" sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell sortDirection={sortBy === 'tracking_number' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'tracking_number'}
                      direction={sortBy === 'tracking_number' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('tracking_number')}
                    >
                      {t.colTrackingNumber}
                    </TableSortLabel>
                  </TableCell>
                  {showsAllOrders ? <TableCell>{t.colCustomer}</TableCell> : null}
                  <TableCell>{t.colPickupAddress}</TableCell>
                  <TableCell>{t.colDeliveryAddress}</TableCell>
                  <TableCell>{t.colDeliveryType}</TableCell>
                  <TableCell sortDirection={sortBy === 'desired_delivery_date' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'desired_delivery_date'}
                      direction={sortBy === 'desired_delivery_date' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('desired_delivery_date')}
                    >
                      {t.colDesiredDate}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell sortDirection={sortBy === 'status' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'status'}
                      direction={sortBy === 'status' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('status')}
                    >
                      {t.colStatus}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell sortDirection={sortBy === 'created_at' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'created_at'}
                      direction={sortBy === 'created_at' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('created_at')}
                    >
                      {t.colCreatedAt}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">{t.colActions}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((order) => (
                  <TableRow key={order.id} hover>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>{order.tracking_number}</TableCell>
                    {showsAllOrders ? (
                      <TableCell>{order.customer?.full_name ?? `#${order.customer_id}`}</TableCell>
                    ) : null}
                    <TableCell>{truncate(order.pickup_address, 32)}</TableCell>
                    <TableCell>{truncate(order.delivery_address, 32)}</TableCell>
                    <TableCell>{DELIVERY_TYPE_LABELS[order.delivery_type]}</TableCell>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                      {formatDate(order.desired_delivery_date)}
                    </TableCell>
                    <TableCell>
                      <StatusChip status={order.status} />
                    </TableCell>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                      {formatDateTime(order.created_at)}
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
          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={(_, nextPage) => setPage(nextPage)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(event) => setPageSize(Number(event.target.value))}
            rowsPerPageOptions={[10, 20, 50, 100]}
            labelRowsPerPage={t.rowsPerPage}
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} ${t.paginationOf} ${count}`}
          />
        </Paper>
      )}
    </Box>
  );
}

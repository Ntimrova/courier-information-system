import AddIcon from '@mui/icons-material/Add';
import {
  Box,
  Button,
  Chip,
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
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { usersApi } from '@/api/endpoints';
import { canManageUsers } from '@/auth/permissions';
import { useAuth } from '@/auth/useAuth';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { useNotify } from '@/components/common/NotifyContext';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState, ErrorState, LoadingState } from '@/components/common/StateViews';
import { ROLE_LABELS, t } from '@/i18n/uk';
import { errorMessage } from '@/lib/errors';
import { formatDateTime } from '@/lib/format';
import { useDebouncedValue } from '@/lib/useDebouncedValue';
import { USER_ROLES, type User, type UserRole } from '@/types/api';

type SortField = 'last_name' | 'email' | 'role' | 'created_at';

export function UsersListPage() {
  const { user } = useAuth();
  const notify = useNotify();
  const queryClient = useQueryClient();
  const canManage = user ? canManageUsers(user.role) : false;

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [searchInput, setSearchInput] = useState('');
  const [role, setRole] = useState<UserRole | ''>('');
  const [activeFilter, setActiveFilter] = useState<'' | 'true' | 'false'>('');
  const [sortBy, setSortBy] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [pendingUser, setPendingUser] = useState<User | null>(null);

  const search = useDebouncedValue(searchInput, 400);
  const hasFilters = Boolean(search || role || activeFilter);

  useEffect(() => {
    setPage(0);
  }, [search, role, activeFilter, pageSize]);

  const query = useQuery({
    queryKey: ['users', { page, pageSize, search, role, activeFilter, sortBy, sortOrder }],
    queryFn: () =>
      usersApi.list({
        page: page + 1,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
        search: search || undefined,
        role: role || undefined,
        is_active: activeFilter === '' ? undefined : activeFilter === 'true',
      }),
    placeholderData: keepPreviousData,
  });

  const statusMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      usersApi.setStatus(userId, isActive),
    onSuccess: async () => {
      notify(t.userStatusChanged);
      setPendingUser(null);
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error) => {
      notify(errorMessage(error), 'error');
      setPendingUser(null);
    },
  });

  const toggleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const resetFilters = () => {
    setSearchInput('');
    setRole('');
    setActiveFilter('');
  };

  const items = query.data?.items ?? [];
  const total = query.data?.meta.total ?? 0;

  return (
    <Box>
      <PageHeader
        title={t.usersTitle}
        subtitle={t.usersSubtitle}
        action={
          canManage ? (
            <Button
              component={RouterLink}
              to="/users/new"
              variant="contained"
              startIcon={<AddIcon />}
            >
              {t.userCreateTitle}
            </Button>
          ) : undefined
        }
      />

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} flexWrap="wrap" useFlexGap>
          <TextField
            label={t.actionSearch}
            placeholder={t.usersSearchPlaceholder}
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            sx={{ minWidth: { md: 260 }, flex: '1 1 240px' }}
          />
          <TextField
            select
            label={t.filterRole}
            value={role}
            onChange={(event) => setRole(event.target.value as UserRole | '')}
            sx={{ minWidth: 180, flex: '0 1 200px' }}
          >
            <MenuItem value="">{t.allRoles}</MenuItem>
            {USER_ROLES.map((value) => (
              <MenuItem key={value} value={value}>
                {ROLE_LABELS[value]}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label={t.filterStatus}
            value={activeFilter}
            onChange={(event) => setActiveFilter(event.target.value as '' | 'true' | 'false')}
            sx={{ minWidth: 180, flex: '0 1 200px' }}
          >
            <MenuItem value="">{t.allStatuses}</MenuItem>
            <MenuItem value="true">{t.statusActive}</MenuItem>
            <MenuItem value="false">{t.statusBlocked}</MenuItem>
          </TextField>
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
            title={t.emptyTitle}
            action={
              hasFilters ? (
                <Button onClick={resetFilters} variant="outlined">
                  {t.actionReset}
                </Button>
              ) : undefined
            }
          />
        </Paper>
      ) : (
        <Paper variant="outlined">
          <TableContainer>
            <Table size="small" sx={{ minWidth: 800 }}>
              <TableHead>
                <TableRow>
                  <TableCell sortDirection={sortBy === 'last_name' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'last_name'}
                      direction={sortBy === 'last_name' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('last_name')}
                    >
                      {t.colName}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell sortDirection={sortBy === 'email' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'email'}
                      direction={sortBy === 'email' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('email')}
                    >
                      {t.colEmail}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>{t.colPhone}</TableCell>
                  <TableCell sortDirection={sortBy === 'role' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'role'}
                      direction={sortBy === 'role' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('role')}
                    >
                      {t.colRole}
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>{t.colStatus}</TableCell>
                  <TableCell sortDirection={sortBy === 'created_at' ? sortOrder : false}>
                    <TableSortLabel
                      active={sortBy === 'created_at'}
                      direction={sortBy === 'created_at' ? sortOrder : 'asc'}
                      onClick={() => toggleSort('created_at')}
                    >
                      {t.colCreatedAt}
                    </TableSortLabel>
                  </TableCell>
                  {canManage ? <TableCell align="right">{t.colActions}</TableCell> : null}
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{item.full_name}</TableCell>
                    <TableCell>{item.email}</TableCell>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>{item.phone}</TableCell>
                    <TableCell>{ROLE_LABELS[item.role]}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={item.is_active ? t.statusActive : t.statusBlocked}
                        color={item.is_active ? 'success' : 'default'}
                        variant={item.is_active ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell sx={{ whiteSpace: 'nowrap' }}>
                      {formatDateTime(item.created_at)}
                    </TableCell>
                    {canManage ? (
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                          <Button component={RouterLink} to={`/users/${item.id}/edit`} size="small">
                            {t.actionEdit}
                          </Button>
                          <Button
                            size="small"
                            color={item.is_active ? 'error' : 'success'}
                            disabled={item.id === user?.id}
                            onClick={() => setPendingUser(item)}
                          >
                            {item.is_active ? t.actionBlock : t.actionActivate}
                          </Button>
                        </Stack>
                      </TableCell>
                    ) : null}
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

      <ConfirmDialog
        open={pendingUser !== null}
        title={pendingUser?.is_active ? t.confirmBlockTitle : t.confirmActivateTitle}
        description={pendingUser?.is_active ? t.confirmBlockText : t.confirmActivateText}
        confirmLabel={pendingUser?.is_active ? t.actionBlock : t.actionActivate}
        confirmColor={pendingUser?.is_active ? 'error' : 'success'}
        busy={statusMutation.isPending}
        onConfirm={() =>
          pendingUser &&
          statusMutation.mutate({ userId: pendingUser.id, isActive: !pendingUser.is_active })
        }
        onClose={() => setPendingUser(null)}
      />
    </Box>
  );
}

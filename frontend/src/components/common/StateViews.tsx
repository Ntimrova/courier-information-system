/** Стани завантаження, порожнього списку й помилки - в одному місці. */

import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import InboxIcon from '@mui/icons-material/Inbox';
import { Alert, AlertTitle, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

import { t } from '@/i18n/uk';
import { errorMessage } from '@/lib/errors';

export function LoadingState({ label = t.loading }: { label?: string }) {
  return (
    <Stack alignItems="center" justifyContent="center" spacing={2} sx={{ py: 6 }}>
      <CircularProgress />
      <Typography color="text.secondary">{label}</Typography>
    </Stack>
  );
}

export function EmptyState({
  title = t.emptyTitle,
  description,
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <Stack alignItems="center" spacing={1.5} sx={{ py: 6, px: 2, textAlign: 'center' }}>
      <InboxIcon sx={{ fontSize: 48, color: 'text.disabled' }} />
      <Typography variant="h6">{title}</Typography>
      {description ? (
        <Typography color="text.secondary" sx={{ maxWidth: 460 }}>
          {description}
        </Typography>
      ) : null}
      {action ? <Box sx={{ pt: 1 }}>{action}</Box> : null}
    </Stack>
  );
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <Box sx={{ py: 4, px: 2 }}>
      <Alert
        severity="error"
        icon={<ErrorOutlineIcon />}
        action={
          onRetry ? (
            <Button color="inherit" size="small" onClick={onRetry}>
              {t.actionRetry}
            </Button>
          ) : undefined
        }
      >
        <AlertTitle>{t.errorTitle}</AlertTitle>
        {errorMessage(error)}
      </Alert>
    </Box>
  );
}

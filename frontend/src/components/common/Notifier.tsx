/** Простий показ повідомлень про успіх і помилки (snackbar). */

import { Alert, Snackbar } from '@mui/material';
import { useCallback, useMemo, useState, type ReactNode } from 'react';

import { NotifyContext, type NotifySeverity } from '@/components/common/NotifyContext';

interface NotifyState {
  open: boolean;
  message: string;
  severity: NotifySeverity;
}

export function Notifier({ children }: { children: ReactNode }) {
  const [state, setState] = useState<NotifyState>({
    open: false,
    message: '',
    severity: 'success',
  });

  const notify = useCallback((message: string, severity: NotifySeverity = 'success') => {
    setState({ open: true, message, severity });
  }, []);

  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <NotifyContext.Provider value={value}>
      {children}
      <Snackbar
        open={state.open}
        autoHideDuration={5000}
        onClose={() => setState((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity={state.severity}
          variant="filled"
          onClose={() => setState((prev) => ({ ...prev, open: false }))}
          sx={{ width: '100%' }}
        >
          {state.message}
        </Alert>
      </Snackbar>
    </NotifyContext.Provider>
  );
}

import { createContext, useContext } from 'react';

export type NotifySeverity = 'success' | 'error' | 'info' | 'warning';

export interface NotifyContextValue {
  notify: (message: string, severity?: NotifySeverity) => void;
}

export const NotifyContext = createContext<NotifyContextValue | null>(null);

export function useNotify(): NotifyContextValue['notify'] {
  const context = useContext(NotifyContext);
  if (context === null) {
    throw new Error('useNotify можна викликати лише всередині <Notifier>');
  }
  return context.notify;
}

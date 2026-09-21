import { useContext } from 'react';

import { AuthContext, type AuthContextValue } from '@/auth/AuthContext';

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth можна викликати лише всередині <AuthProvider>');
  }
  return context;
}

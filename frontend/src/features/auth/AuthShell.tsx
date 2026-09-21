/** Спільна картка для сторінок входу й реєстрації. */

import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import { Box, Paper, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        px: 2,
        py: 4,
      }}
    >
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, sm: 4 },
          width: '100%',
          maxWidth: 480,
          border: 1,
          borderColor: 'divider',
        }}
      >
        <Stack spacing={1} alignItems="center" sx={{ mb: 3 }}>
          <LocalShippingIcon color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="h5" component="h1">
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            {subtitle}
          </Typography>
        </Stack>
        {children}
      </Paper>
    </Box>
  );
}

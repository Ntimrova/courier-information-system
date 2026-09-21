import SearchOffIcon from '@mui/icons-material/SearchOff';
import { Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { t } from '@/i18n/uk';

export function NotFoundPage() {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: { xs: 6, md: 10 }, px: 2 }}>
      <Stack spacing={2} alignItems="center" textAlign="center" sx={{ maxWidth: 460 }}>
        <SearchOffIcon sx={{ fontSize: 64, color: 'text.disabled' }} />
        <Typography variant="h4" component="h1">
          404
        </Typography>
        <Typography variant="h6">{t.notFoundTitle}</Typography>
        <Typography color="text.secondary">{t.notFoundText}</Typography>
        <Button component={RouterLink} to="/dashboard" variant="contained">
          {t.goHome}
        </Button>
      </Stack>
    </Box>
  );
}

import BlockIcon from '@mui/icons-material/Block';
import { Box, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { t } from '@/i18n/uk';

export function ForbiddenPage() {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: { xs: 6, md: 10 }, px: 2 }}>
      <Stack spacing={2} alignItems="center" textAlign="center" sx={{ maxWidth: 460 }}>
        <BlockIcon sx={{ fontSize: 64, color: 'error.main' }} />
        <Typography variant="h4" component="h1">
          403
        </Typography>
        <Typography variant="h6">{t.forbiddenTitle}</Typography>
        <Typography color="text.secondary">{t.forbiddenText}</Typography>
        <Button component={RouterLink} to="/dashboard" variant="contained">
          {t.goHome}
        </Button>
      </Stack>
    </Box>
  );
}

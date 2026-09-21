import { createTheme } from '@mui/material/styles';
import { ukUA } from '@mui/material/locale';

export const theme = createTheme(
  {
    palette: {
      mode: 'light',
      primary: { main: '#1B5E9B' },
      secondary: { main: '#E07A2F' },
      background: { default: '#F4F6F9', paper: '#FFFFFF' },
      success: { main: '#2E7D32' },
      warning: { main: '#ED6C02' },
      error: { main: '#C62828' },
      info: { main: '#0277BD' },
    },
    typography: {
      fontFamily:
        '"Inter", "Segoe UI", "Roboto", "Helvetica Neue", system-ui, -apple-system, sans-serif',
      h4: { fontWeight: 600 },
      h5: { fontWeight: 600 },
      h6: { fontWeight: 600 },
      button: { textTransform: 'none', fontWeight: 500 },
    },
    shape: { borderRadius: 10 },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: 'none' },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          head: { fontWeight: 600, whiteSpace: 'nowrap' },
        },
      },
      MuiTextField: {
        defaultProps: { size: 'small', fullWidth: true },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
      },
    },
  },
  ukUA,
);

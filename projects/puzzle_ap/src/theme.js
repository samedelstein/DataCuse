import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2f3c7e',
      light: '#5867a8',
      dark: '#202b5c',
      contrastText: '#fff',
    },
    secondary: {
      main: '#f2c14e',
      light: '#f6d27e',
      dark: '#d9a63f',
      contrastText: '#1f2937',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#e07a1f',
    },
    success: {
      main: '#2f855a',
    },
    background: {
      default: '#f7f5f2',
      paper: '#ffffff',
    },
    text: {
      primary: '#1f2937',
      secondary: '#5f6b7a',
    },
  },
  typography: {
    fontFamily: [
      '"Poppins"',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    subtitle1: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #2f3c7e 0%, #4252a1 100%)',
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: 72,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 12,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(47, 60, 126, 0.08)',
          boxShadow: '0 8px 24px rgba(31, 41, 55, 0.08)',
          '&:hover': {
            boxShadow: '0 12px 28px rgba(31, 41, 55, 0.12)',
          },
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        fullWidth: true,
      },
    },
    MuiFab: {
      styleOverrides: {
        root: {
          boxShadow: '0 12px 24px rgba(47, 60, 126, 0.25)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
  },
});

export default theme;

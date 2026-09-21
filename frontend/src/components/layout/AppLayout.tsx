/** Спільний каркас: бокове меню, верхня панель, контент. */

import AddIcon from '@mui/icons-material/Add';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import {
  AppBar,
  Avatar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState, type ReactElement } from 'react';
import { Link as RouterLink, Outlet, useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '@/auth/useAuth';
import { canCreateOrders, canViewUsers } from '@/auth/permissions';
import { ROLE_LABELS, t } from '@/i18n/uk';

const DRAWER_WIDTH = 248;

interface NavItem {
  to: string;
  label: string;
  icon: ReactElement;
  visible: boolean;
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!user) return null;

  const navItems: NavItem[] = [
    { to: '/dashboard', label: t.navDashboard, icon: <DashboardIcon />, visible: true },
    {
      to: '/orders',
      label: t.navOrders,
      icon: <LocalShippingIcon />,
      visible: user.role !== 'COURIER',
    },
    {
      to: '/orders/new',
      label: t.navNewOrder,
      icon: <AddIcon />,
      visible: canCreateOrders(user.role),
    },
    {
      to: '/users',
      label: t.navUsers,
      icon: <PeopleIcon />,
      visible: canViewUsers(user.role),
    },
    { to: '/profile', label: t.navProfile, icon: <PersonIcon />, visible: true },
  ];

  const isSelected = (to: string) => {
    if (to === '/orders') {
      return location.pathname === '/orders' || /^\/orders\/\d+/.test(location.pathname);
    }
    return location.pathname === to || location.pathname.startsWith(`${to}/`);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar sx={{ px: 2.5 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <LocalShippingIcon color="primary" />
          <Box>
            <Typography variant="subtitle1" fontWeight={700} lineHeight={1.2}>
              {t.appName}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {t.appSubtitle}
            </Typography>
          </Box>
        </Stack>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, py: 1.5, flexGrow: 1 }}>
        {navItems
          .filter((item) => item.visible)
          .map((item) => (
            <ListItemButton
              key={item.to}
              component={RouterLink}
              to={item.to}
              selected={isSelected(item.to)}
              onClick={() => setMobileOpen(false)}
              sx={{ borderRadius: 2, mb: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
      </List>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
            {user.first_name.charAt(0)}
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="body2" fontWeight={600} noWrap>
              {user.full_name}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {ROLE_LABELS[user.role]}
            </Typography>
          </Box>
        </Stack>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ gap: 1 }}>
          <IconButton
            edge="start"
            onClick={() => setMobileOpen(true)}
            aria-label={t.openMenu}
            sx={{ display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="subtitle1" fontWeight={600} noWrap>
              {user.full_name}
            </Typography>
          </Box>

          <Chip label={ROLE_LABELS[user.role]} size="small" color="primary" variant="outlined" />

          <Tooltip title={t.navLogout}>
            <IconButton onClick={handleLogout} aria-label={t.navLogout}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isDesktop ? 'permanent' : 'temporary'}
          open={isDesktop ? true : mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: isDesktop ? 'none' : 'block', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              borderRight: 1,
              borderColor: 'divider',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          // Без minWidth: 0 flex-елемент розтягується під найширший вміст
          // (наприклад, таблицю) і на телефоні з'являється горизонтальний скрол.
          minWidth: 0,
          maxWidth: '100%',
          width: { xs: '100%', md: `calc(100% - ${DRAWER_WIDTH}px)` },
          px: { xs: 2, sm: 3 },
          py: 3,
          mt: 8,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}

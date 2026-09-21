/** Опис усіх маршрутів застосунку. */

import { Navigate, Route, Routes } from 'react-router-dom';

import { GuestRoute, ProtectedRoute, RoleRoute } from '@/auth/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/features/auth/LoginPage';
import { RegisterPage } from '@/features/auth/RegisterPage';
import { DashboardPage } from '@/features/dashboard/DashboardPage';
import { OrderCreatePage } from '@/features/orders/OrderCreatePage';
import { OrderDetailPage } from '@/features/orders/OrderDetailPage';
import { OrderEditPage } from '@/features/orders/OrderEditPage';
import { OrdersListPage } from '@/features/orders/OrdersListPage';
import { ProfilePage } from '@/features/profile/ProfilePage';
import { UserCreatePage } from '@/features/users/UserCreatePage';
import { UserEditPage } from '@/features/users/UserEditPage';
import { UsersListPage } from '@/features/users/UsersListPage';
import { ForbiddenPage } from '@/pages/ForbiddenPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export function AppRoutes() {
  return (
    <Routes>
      {/* Сторінки для неавторизованих */}
      <Route element={<GuestRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Усе інше вимагає входу */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />

          {/* Замовлення: кур'єру в частині 1 сюди ще зарано */}
          <Route element={<RoleRoute allow={['ADMIN', 'DISPATCHER', 'MANAGER', 'CUSTOMER']} />}>
            <Route path="/orders" element={<OrdersListPage />} />
            <Route path="/orders/:id" element={<OrderDetailPage />} />
            <Route path="/orders/:id/edit" element={<OrderEditPage />} />
          </Route>
          <Route element={<RoleRoute allow={['ADMIN', 'DISPATCHER', 'CUSTOMER']} />}>
            <Route path="/orders/new" element={<OrderCreatePage />} />
          </Route>

          {/* Користувачі: перегляд - ADMIN і MANAGER, зміни - лише ADMIN */}
          <Route element={<RoleRoute allow={['ADMIN', 'MANAGER']} />}>
            <Route path="/users" element={<UsersListPage />} />
          </Route>
          <Route element={<RoleRoute allow={['ADMIN']} />}>
            <Route path="/users/new" element={<UserCreatePage />} />
            <Route path="/users/:id/edit" element={<UserEditPage />} />
          </Route>

          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

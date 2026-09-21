/**
 * Дзеркало прав ролей із backend.
 *
 * Тут воно потрібне лише щоб не показувати кнопки, які все одно не
 * спрацюють. Справжня перевірка завжди відбувається на сервері: сховати
 * кнопку це як прибрати табличку з дверей, а не замкнути їх.
 */

import type { AnyOrderStatus, OrderStatus, UserRole } from '@/types/api';

export const ROLES_SEEING_ALL_ORDERS: UserRole[] = ['ADMIN', 'DISPATCHER', 'MANAGER'];
export const ROLES_MANAGING_USERS: UserRole[] = ['ADMIN'];
export const ROLES_VIEWING_USERS: UserRole[] = ['ADMIN', 'MANAGER'];
export const ROLES_CREATING_ORDERS: UserRole[] = ['ADMIN', 'DISPATCHER', 'CUSTOMER'];
export const ROLES_CHANGING_STATUS: UserRole[] = ['ADMIN', 'DISPATCHER'];

/** Статуси, у яких замовлення ще можна редагувати чи скасувати. */
const EDITABLE_STATUSES: AnyOrderStatus[] = ['CREATED', 'CONFIRMED', 'WAITING_FOR_COURIER'];

/** Дозволені переходи статусів першої частини. */
export const ALLOWED_TRANSITIONS: Record<string, OrderStatus[]> = {
  CREATED: ['CONFIRMED', 'CANCELLED'],
  CONFIRMED: ['WAITING_FOR_COURIER', 'CANCELLED'],
  WAITING_FOR_COURIER: ['CANCELLED'],
  CANCELLED: [],
};

export function canSeeAllOrders(role: UserRole): boolean {
  return ROLES_SEEING_ALL_ORDERS.includes(role);
}

export function canViewUsers(role: UserRole): boolean {
  return ROLES_VIEWING_USERS.includes(role);
}

export function canManageUsers(role: UserRole): boolean {
  return ROLES_MANAGING_USERS.includes(role);
}

export function canCreateOrders(role: UserRole): boolean {
  return ROLES_CREATING_ORDERS.includes(role);
}

export function canChangeOrderStatus(role: UserRole): boolean {
  return ROLES_CHANGING_STATUS.includes(role);
}

/** Диспетчер і адміністратор мусять указати клієнта у формі замовлення. */
export function mustChooseCustomer(role: UserRole): boolean {
  return role === 'ADMIN' || role === 'DISPATCHER';
}

export function canEditOrder(
  role: UserRole,
  orderStatus: AnyOrderStatus,
  isOwnOrder: boolean,
): boolean {
  if (orderStatus === 'CANCELLED') return false;
  if (role === 'ADMIN' || role === 'DISPATCHER') return true;
  if (role === 'CUSTOMER') {
    return isOwnOrder && EDITABLE_STATUSES.includes(orderStatus);
  }
  return false;
}

export function canCancelOrder(
  role: UserRole,
  orderStatus: AnyOrderStatus,
  isOwnOrder: boolean,
): boolean {
  if (!EDITABLE_STATUSES.includes(orderStatus)) return false;
  return canEditOrder(role, orderStatus, isOwnOrder);
}

export function nextStatuses(current: AnyOrderStatus): OrderStatus[] {
  return ALLOWED_TRANSITIONS[current] ?? [];
}

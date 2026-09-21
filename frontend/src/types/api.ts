/** Типи, що дзеркалять схеми backend. */

export const USER_ROLES = ['ADMIN', 'DISPATCHER', 'COURIER', 'CUSTOMER', 'MANAGER'] as const;
export type UserRole = (typeof USER_ROLES)[number];

/** Статуси, доступні в першій частині системи. */
export const ORDER_STATUSES = ['CREATED', 'CONFIRMED', 'WAITING_FOR_COURIER', 'CANCELLED'] as const;
export type OrderStatus = (typeof ORDER_STATUSES)[number];

/** Статуси частин 2 і 3: backend їх знає, але поки не встановлює. */
export const FUTURE_ORDER_STATUSES = [
  'COURIER_ASSIGNED',
  'PICKED_UP',
  'IN_TRANSIT',
  'DELIVERED',
  'DELIVERY_FAILED',
] as const;
export type AnyOrderStatus = OrderStatus | (typeof FUTURE_ORDER_STATUSES)[number];

export const DELIVERY_TYPES = ['STANDARD', 'EXPRESS'] as const;
export type DeliveryType = (typeof DELIVERY_TYPES)[number];

export const PACKAGE_SIZES = ['SMALL', 'MEDIUM', 'LARGE'] as const;
export type PackageSize = (typeof PACKAGE_SIZES)[number];

export interface User {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserShort {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  role: UserRole;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Order {
  id: number;
  tracking_number: string;
  customer_id: number;
  customer: UserShort | null;
  sender_name: string;
  sender_phone: string;
  pickup_address: string;
  recipient_name: string;
  recipient_phone: string;
  delivery_address: string;
  package_description: string;
  package_weight: string;
  package_size: PackageSize;
  delivery_type: DeliveryType;
  desired_delivery_date: string;
  comment: string | null;
  status: AnyOrderStatus;
  created_at: string;
  updated_at: string;
  cancelled_at: string | null;
}

export interface OrderListItem {
  id: number;
  tracking_number: string;
  customer_id: number;
  customer: UserShort | null;
  pickup_address: string;
  delivery_address: string;
  delivery_type: DeliveryType;
  desired_delivery_date: string;
  status: AnyOrderStatus;
  created_at: string;
}

export interface OrderStatusHistoryEntry {
  id: number;
  order_id: number;
  previous_status: AnyOrderStatus | null;
  new_status: AnyOrderStatus;
  changed_by_user_id: number | null;
  changed_by: UserShort | null;
  comment: string | null;
  created_at: string;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PageMeta;
}

export interface OrderCounters {
  total: number;
  created: number;
  confirmed: number;
  waiting_for_courier: number;
  cancelled: number;
  active: number;
}

export interface DashboardSummary {
  role: UserRole;
  scope: 'all' | 'own' | 'none';
  counters: OrderCounters;
  recent_orders: OrderListItem[];
  total_users: number | null;
  active_users: number | null;
}

export interface ApiErrorDetailItem {
  field?: string;
  message?: string;
  type?: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetailItem[] | string | null;
  };
}

// --- Запити ---

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
}

export interface UserCreatePayload extends RegisterPayload {
  role: UserRole;
  is_active: boolean;
}

export interface UserUpdatePayload {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  role?: UserRole;
  password?: string;
}

export interface ProfileUpdatePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
  password?: string;
}

export interface OrderPayload {
  sender_name: string;
  sender_phone: string;
  pickup_address: string;
  recipient_name: string;
  recipient_phone: string;
  delivery_address: string;
  package_description: string;
  package_weight: string;
  package_size: PackageSize;
  delivery_type: DeliveryType;
  desired_delivery_date: string;
  comment?: string | null;
  customer_id?: number | null;
}

export interface UserListQuery {
  page: number;
  page_size: number;
  sort_by: string;
  sort_order: 'asc' | 'desc';
  search?: string;
  role?: UserRole | '';
  is_active?: boolean | null;
}

export interface OrderListQuery {
  page: number;
  page_size: number;
  sort_by: string;
  sort_order: 'asc' | 'desc';
  search?: string;
  status?: OrderStatus | '';
  delivery_type?: DeliveryType | '';
  date_from?: string;
  date_to?: string;
}

/** Виклики REST API. Компоненти не знають про axios і про адреси. */

import { API_V1, apiClient } from '@/api/client';
import type {
  DashboardSummary,
  LoginPayload,
  Order,
  OrderListItem,
  OrderListQuery,
  OrderPayload,
  OrderStatus,
  OrderStatusHistoryEntry,
  PaginatedResponse,
  ProfileUpdatePayload,
  RegisterPayload,
  TokenResponse,
  User,
  UserCreatePayload,
  UserListQuery,
  UserShort,
  UserUpdatePayload,
} from '@/types/api';

/** Прибирає порожні значення, щоб у URL не було `?search=&role=`. */
function cleanParams(params: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    result[key] = value;
  }
  return result;
}

// --- Авторизація ---

export const authApi = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>(`${API_V1}/auth/login`, payload);
    return data;
  },
  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>(`${API_V1}/auth/register`, payload);
    return data;
  },
  async me(): Promise<User> {
    const { data } = await apiClient.get<User>(`${API_V1}/auth/me`);
    return data;
  },
  async logout(): Promise<void> {
    await apiClient.post(`${API_V1}/auth/logout`);
  },
};

// --- Користувачі ---

export const usersApi = {
  async list(query: UserListQuery): Promise<PaginatedResponse<User>> {
    const { data } = await apiClient.get<PaginatedResponse<User>>(`${API_V1}/users`, {
      params: cleanParams({ ...query }),
    });
    return data;
  },
  async get(userId: number): Promise<User> {
    const { data } = await apiClient.get<User>(`${API_V1}/users/${userId}`);
    return data;
  },
  async create(payload: UserCreatePayload): Promise<User> {
    const { data } = await apiClient.post<User>(`${API_V1}/users`, payload);
    return data;
  },
  async update(userId: number, payload: UserUpdatePayload): Promise<User> {
    const { data } = await apiClient.patch<User>(`${API_V1}/users/${userId}`, payload);
    return data;
  },
  async setStatus(userId: number, isActive: boolean): Promise<User> {
    const { data } = await apiClient.patch<User>(`${API_V1}/users/${userId}/status`, {
      is_active: isActive,
    });
    return data;
  },
  async updateProfile(payload: ProfileUpdatePayload): Promise<User> {
    const { data } = await apiClient.patch<User>(`${API_V1}/users/me`, payload);
    return data;
  },
  async customerOptions(): Promise<UserShort[]> {
    const { data } = await apiClient.get<UserShort[]>(`${API_V1}/users/customers`);
    return data;
  },
};

// --- Замовлення ---

export const ordersApi = {
  async list(query: OrderListQuery): Promise<PaginatedResponse<OrderListItem>> {
    const { data } = await apiClient.get<PaginatedResponse<OrderListItem>>(`${API_V1}/orders`, {
      params: cleanParams({ ...query }),
    });
    return data;
  },
  async get(orderId: number): Promise<Order> {
    const { data } = await apiClient.get<Order>(`${API_V1}/orders/${orderId}`);
    return data;
  },
  async create(payload: OrderPayload): Promise<Order> {
    const { data } = await apiClient.post<Order>(`${API_V1}/orders`, payload);
    return data;
  },
  async update(orderId: number, payload: Partial<OrderPayload>): Promise<Order> {
    const { data } = await apiClient.patch<Order>(`${API_V1}/orders/${orderId}`, payload);
    return data;
  },
  async changeStatus(orderId: number, status: OrderStatus, comment?: string): Promise<Order> {
    const { data } = await apiClient.post<Order>(`${API_V1}/orders/${orderId}/status`, {
      status,
      comment: comment || null,
    });
    return data;
  },
  async cancel(orderId: number, comment?: string): Promise<Order> {
    const { data } = await apiClient.post<Order>(`${API_V1}/orders/${orderId}/cancel`, {
      comment: comment || null,
    });
    return data;
  },
  async history(orderId: number): Promise<OrderStatusHistoryEntry[]> {
    const { data } = await apiClient.get<OrderStatusHistoryEntry[]>(
      `${API_V1}/orders/${orderId}/history`,
    );
    return data;
  },
};

// --- Dashboard ---

export const dashboardApi = {
  async summary(): Promise<DashboardSummary> {
    const { data } = await apiClient.get<DashboardSummary>(`${API_V1}/dashboard/summary`);
    return data;
  },
};

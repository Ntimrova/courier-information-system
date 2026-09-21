/** Усі підписи інтерфейсу в одному місці - українською. */

import type { AnyOrderStatus, DeliveryType, PackageSize, UserRole } from '@/types/api';

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: 'Адміністратор',
  DISPATCHER: 'Диспетчер',
  COURIER: "Кур'єр",
  CUSTOMER: 'Клієнт',
};

export const STATUS_LABELS: Record<AnyOrderStatus, string> = {
  CREATED: 'Створено',
  CONFIRMED: 'Підтверджено',
  WAITING_FOR_COURIER: "Очікує кур'єра",
  CANCELLED: 'Скасовано',
  COURIER_ASSIGNED: "Призначено кур'єра",
  PICKED_UP: 'Забрано',
  IN_TRANSIT: 'У дорозі',
  DELIVERED: 'Доставлено',
  DELIVERY_FAILED: 'Доставка не вдалася',
};

export const DELIVERY_TYPE_LABELS: Record<DeliveryType, string> = {
  STANDARD: 'Звичайна',
  EXPRESS: 'Експрес',
};

export const PACKAGE_SIZE_LABELS: Record<PackageSize, string> = {
  SMALL: 'Малий',
  MEDIUM: 'Середній',
  LARGE: 'Великий',
};

export const t = {
  appName: "Кур'єрська служба",
  appSubtitle: 'Інформаційна система',

  // Навігація
  navDashboard: 'Головна',
  navOrders: 'Замовлення',
  navUsers: 'Користувачі',
  navProfile: 'Профіль',
  navLogout: 'Вийти',
  navNewOrder: 'Нове замовлення',
  openMenu: 'Відкрити меню',

  // Загальні дії
  actionSave: 'Зберегти',
  actionCreate: 'Створити',
  actionCancel: 'Скасувати',
  actionClose: 'Закрити',
  actionBack: 'Назад',
  actionEdit: 'Редагувати',
  actionView: 'Переглянути',
  actionRetry: 'Спробувати ще раз',
  actionSearch: 'Пошук',
  actionReset: 'Скинути фільтри',
  actionConfirm: 'Підтвердити',
  actionBlock: 'Заблокувати',
  actionActivate: 'Активувати',
  actionCancelOrder: 'Скасувати замовлення',
  actionChangeStatus: 'Змінити статус',

  // Стани
  loading: 'Завантаження...',
  saving: 'Збереження...',
  emptyTitle: 'Нічого не знайдено',
  errorTitle: 'Не вдалося завантажити дані',
  unknownError: 'Сталася невідома помилка. Спробуйте ще раз',
  networkError: "Немає зв'язку із сервером. Перевірте підключення",

  // Авторизація
  loginTitle: 'Вхід у систему',
  loginSubtitle: 'Введіть email і пароль',
  registerTitle: 'Реєстрація клієнта',
  registerSubtitle: 'Створіть обліковий запис, щоб оформлювати замовлення',
  fieldEmail: 'Email',
  fieldPassword: 'Пароль',
  fieldPasswordRepeat: 'Повторіть пароль',
  fieldNewPassword: 'Новий пароль',
  fieldFirstName: "Ім'я",
  fieldLastName: 'Прізвище',
  fieldPhone: 'Телефон',
  fieldRole: 'Роль',
  fieldStatus: 'Статус',
  submitLogin: 'Увійти',
  submitRegister: 'Зареєструватися',
  haveAccount: 'Уже маєте обліковий запис?',
  noAccount: 'Ще не зареєстровані?',
  goToLogin: 'Увійти',
  goToRegister: 'Зареєструватися',
  leavePasswordEmpty: 'Залиште порожнім, щоб не змінювати пароль',

  // Dashboard
  dashboardTitle: 'Головна',
  dashboardGreeting: 'Вітаємо',
  statTotal: 'Усього замовлень',
  statCreated: 'Нові',
  statConfirmed: 'Підтверджені',
  statWaiting: "Очікують кур'єра",
  statCancelled: 'Скасовані',
  statActive: 'Активні',
  statUsers: 'Користувачів',
  statActiveUsers: 'Активних користувачів',
  recentOrders: 'Останні замовлення',
  courierComingSoon:
    "Функціонал кур'єра з'явиться в другій частині системи. Зараз доступний лише вхід і профіль.",

  // Користувачі
  usersTitle: 'Користувачі',
  usersSubtitle: 'Керування обліковими записами',
  userCreateTitle: 'Новий користувач',
  userEditTitle: 'Редагування користувача',
  usersSearchPlaceholder: "Ім'я, email або телефон",
  filterRole: 'Роль',
  filterStatus: 'Статус',
  statusActive: 'Активний',
  statusBlocked: 'Заблокований',
  allRoles: 'Усі ролі',
  allStatuses: 'Усі статуси',
  confirmBlockTitle: 'Заблокувати користувача?',
  confirmBlockText:
    'Користувач більше не зможе увійти в систему, доки ви не активуєте його обліковий запис.',
  confirmActivateTitle: 'Активувати користувача?',
  confirmActivateText: 'Користувач знову зможе входити в систему.',
  userCreated: 'Користувача створено',
  userUpdated: 'Дані користувача збережено',
  userStatusChanged: 'Статус облікового запису змінено',

  // Замовлення
  ordersTitle: 'Замовлення',
  myOrdersTitle: 'Мої замовлення',
  orderCreateTitle: 'Нове замовлення',
  orderEditTitle: 'Редагування замовлення',
  orderDetailTitle: 'Замовлення',
  ordersSearchPlaceholder: "Номер, телефон або ім'я",
  filterDeliveryType: 'Тип доставки',
  filterDateFrom: 'Дата доставки від',
  filterDateTo: 'Дата доставки до',
  allStatusesOrder: 'Усі статуси',
  allDeliveryTypes: 'Усі типи',
  ordersEmpty: 'Замовлень поки немає',
  ordersEmptyFiltered: 'За обраними фільтрами замовлень не знайдено',

  colTrackingNumber: 'Номер',
  colCustomer: 'Клієнт',
  colPickupAddress: 'Адреса отримання',
  colDeliveryAddress: 'Адреса доставки',
  colDeliveryType: 'Тип доставки',
  colDesiredDate: 'Бажана дата',
  colStatus: 'Статус',
  colCreatedAt: 'Створено',
  colActions: 'Дії',
  colName: "Ім'я",
  colEmail: 'Email',
  colPhone: 'Телефон',
  colRole: 'Роль',

  sectionSender: 'Відправник і місце отримання',
  sectionRecipient: 'Одержувач і місце доставки',
  sectionPackage: 'Відправлення',
  sectionExtra: 'Додатково',

  fieldSenderName: "Ім'я відправника",
  fieldSenderPhone: 'Телефон відправника',
  fieldPickupAddress: 'Адреса отримання',
  fieldRecipientName: "Ім'я одержувача",
  fieldRecipientPhone: 'Телефон одержувача',
  fieldDeliveryAddress: 'Адреса доставки',
  fieldPackageDescription: 'Опис відправлення',
  fieldPackageWeight: 'Вага, кг',
  fieldPackageSize: 'Розмір',
  fieldDeliveryType: 'Тип доставки',
  fieldDesiredDate: 'Бажана дата доставки',
  fieldComment: 'Коментар',
  fieldCustomer: 'Клієнт',

  orderCreated: 'Замовлення створено',
  orderUpdated: 'Замовлення збережено',
  orderCancelled: 'Замовлення скасовано',
  orderStatusChanged: 'Статус замовлення змінено',
  confirmCancelTitle: 'Скасувати замовлення?',
  confirmCancelText: 'Скасоване замовлення не можна буде відновити або відредагувати.',
  cancelReason: 'Причина скасування',
  statusChangeTitle: 'Зміна статусу',
  statusChangeComment: 'Коментар до зміни',
  newStatus: 'Новий статус',
  noStatusAvailable: 'Для цього замовлення немає доступних переходів статусу',
  historyTitle: 'Історія статусів',
  historyEmpty: 'Записів історії немає',
  historyChangedBy: 'Змінив',
  historySystem: 'Система',

  // Профіль
  profileTitle: 'Мій профіль',
  profileSubtitle: 'Особисті дані й пароль',
  profileUpdated: 'Профіль оновлено',
  profileEmailHint: 'Email змінює лише адміністратор',

  // Сторінки помилок
  forbiddenTitle: 'Доступ заборонено',
  forbiddenText: 'У вашої ролі немає прав на цю сторінку.',
  notFoundTitle: 'Сторінку не знайдено',
  notFoundText: 'Можливо, адресу введено з помилкою або сторінку видалено.',
  goHome: 'На головну',

  // Пагінація
  rowsPerPage: 'Рядків на сторінці',
  paginationOf: 'з',
} as const;

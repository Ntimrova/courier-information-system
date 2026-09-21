# Інформаційна система локальної кур'єрської компанії

Вебсистема для автоматизації роботи локальної кур'єрської компанії: облік користувачів, оформлення замовлень, контроль статусів і базова аналітика.

**Це частина 1 із трьох.** Вона вже самодостатня: можна зареєструватися, увійти під різними ролями, створити замовлення, провести його через статуси і подивитися історію змін. Кур'єри, маршрути й карти з'являться в наступних частинах.

---

## Зміст

- [Опис системи](#опис-системи)
- [Стек технологій](#стек-технологій)
- [Структура проєкту](#структура-проєкту)
- [Вимоги для запуску](#вимоги-для-запуску)
- [Запуск через Docker](#запуск-через-docker)
- [Запуск без Docker](#запуск-без-docker)
- [Налаштування .env](#налаштування-env)
- [Міграції бази даних](#міграції-бази-даних)
- [Тестові дані](#тестові-дані)
- [Тестові облікові записи](#тестові-облікові-записи)
- [Запуск тестів](#запуск-тестів)
- [Адреси сервісів](#адреси-сервісів)
- [REST API](#rest-api)
- [Ролі та права доступу](#ролі-та-права-доступу)
- [Статуси замовлення](#статуси-замовлення)
- [Відомі обмеження частини 1](#відомі-обмеження-частини-1)
- [План частин 2 і 3](#план-частин-2-і-3)

---

## Опис системи

Уявіть звичайне поштове відділення. Клієнт приносить посилку й заповнює бланк, оператор приймає її та ставить відмітку в журналі, а керівник відділення бачить, скільки посилок прийнято за день. Ця система робить те саме, але в браузері.

**Що вміє частина 1:**

- реєстрація клієнта й вхід за email і паролем із JWT-токеном;
- чотири ролі з різними правами, які перевіряються на сервері;
- управління користувачами: створення, редагування, блокування й активація;
- повний цикл замовлення: створення, перегляд, редагування, скасування;
- автоматичний номер відстеження у зрозумілому форматі `LDC-2026-000001`;
- контроль переходів статусів - неправильний перехід система не пропустить;
- журнал історії: кожна зміна статусу записується окремим рядком із автором і часом;
- пошук, фільтрація, сортування й пагінація - усе рахується на сервері, а не в браузері;
- dashboard із реальними показниками з PostgreSQL;
- інтерфейс повністю українською, адаптивний під телефон.

---

## Стек технологій

| Шар | Технології |
| --- | --- |
| **Frontend** | React 19, TypeScript, Vite 7, Material UI 7, React Router 7, TanStack Query 5, Axios, React Hook Form, Zod, ESLint, Prettier |
| **Backend** | Python 3.12, FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, PostgreSQL 16, JWT (PyJWT), bcrypt, Pytest, Swagger/OpenAPI |
| **Інфраструктура** | Docker, Docker Compose, `.env`, GitHub. Для продакшну: Vercel (frontend), Render (backend), Supabase PostgreSQL (база) |

**Архітектура:** модульний моноліт із REST API. Кожен шар відповідає за своє:

```
HTTP-запит
   │
   ▼
роутер (app/auth, app/users, app/orders, app/dashboard)   тільки HTTP: коди, схеми
   │
   ▼
сервіс (app/services)                                      бізнес-правила й права
   │
   ▼
репозиторій (app/repositories)                             тільки запити до бази
   │
   ▼
PostgreSQL
```

Бізнес-логіка не дублюється в контролерах: роутер лише приймає запит і віддає відповідь.

---

## Структура проєкту

```
courier-information-system/
├── backend/
│   ├── alembic/
│   │   ├── versions/0001_initial_schema.py   # міграція: users, orders, order_status_history
│   │   └── env.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                       # get_db, get_current_user, require_roles
│   │   │   └── v1/router.py                  # збірка всіх роутерів /api/v1
│   │   ├── auth/router.py                    # реєстрація, вхід, me, logout
│   │   ├── users/router.py                   # управління користувачами
│   │   ├── orders/router.py                  # замовлення та історія
│   │   ├── dashboard/router.py               # зведення
│   │   ├── core/
│   │   │   ├── config.py                     # змінні середовища
│   │   │   ├── enums.py                      # ролі, статуси, типи доставки
│   │   │   ├── errors.py                     # єдиний формат помилок
│   │   │   ├── pagination.py                 # PageParams, SortParams, Page
│   │   │   └── security.py                   # bcrypt і JWT
│   │   ├── database/                         # Base, engine, сесії
│   │   ├── models/                           # User, Order, OrderStatusHistory
│   │   ├── schemas/                          # Pydantic-схеми запитів і відповідей
│   │   ├── repositories/                     # доступ до даних
│   │   ├── services/                         # бізнес-логіка
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── order_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── status_rules.py               # таблиця дозволених переходів
│   │   │   └── tracking.py                   # генерація LDC-2026-000001
│   │   ├── tests/                            # 81 тест
│   │   └── main.py                           # створення застосунку, /health
│   ├── scripts/seed.py                       # тестові дані
│   ├── alembic.ini  pyproject.toml  requirements.txt  requirements-dev.txt
│   ├── Dockerfile  entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── api/                              # axios-клієнт і виклики API
│   │   ├── auth/                             # AuthProvider, ProtectedRoute, permissions
│   │   ├── components/
│   │   │   ├── common/                       # StateViews, ConfirmDialog, StatusChip, Notifier
│   │   │   └── layout/AppLayout.tsx          # бокове меню + верхня панель
│   │   ├── features/
│   │   │   ├── auth/                         # вхід і реєстрація
│   │   │   ├── dashboard/
│   │   │   ├── orders/                       # список, форма, деталі, історія
│   │   │   ├── users/
│   │   │   └── profile/
│   │   ├── i18n/uk.ts                        # усі підписи українською
│   │   ├── lib/                              # формати, помилки, валідація, localStorage
│   │   ├── pages/                            # 403 і 404
│   │   ├── types/api.ts                      # типи, що дзеркалять backend
│   │   ├── routes.tsx  App.tsx  main.tsx  theme.ts
│   ├── Dockerfile  nginx.conf  vite.config.ts  eslint.config.js  .prettierrc.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Вимоги для запуску

**Через Docker** (рекомендовано):

- Docker 24+ і Docker Compose v2.

**Без Docker:**

- Python 3.12+
- Node.js 20+ (перевірено на 22) і npm 10+
- PostgreSQL 16+

---

## Запуск через Docker

```bash
git clone <адреса-репозиторію>
cd courier-information-system

cp .env.example .env
# Відкрийте .env і замініть JWT_SECRET_KEY та POSTGRES_PASSWORD на власні значення.

docker compose up --build
```

Перший запуск триває кілька хвилин: збираються образи й ставляться залежності. Контейнер backend сам дочекається бази, накотить міграції та завантажить тестові дані.

Коли в логах з'явиться `Application startup complete`, відкривайте http://localhost:5173.

**Корисні команди:**

```bash
docker compose up -d --build       # у фоновому режимі
docker compose logs -f backend     # логи backend
docker compose down                # зупинити
docker compose down -v             # зупинити й стерти базу (почати з чистого аркуша)
docker compose exec backend alembic upgrade head       # міграції вручну
docker compose exec backend python -m scripts.seed     # тестові дані вручну
docker compose exec backend pytest                     # тести всередині контейнера
```

Щоб не завантажувати тестові дані під час старту, поставте в `.env`:

```env
SEED_ON_START=false
```

---

## Запуск без Docker

### 1. База даних

```bash
createdb courier_db
createdb courier_test          # окрема база для тестів
createuser courier --pwprompt
psql -c "GRANT ALL PRIVILEGES ON DATABASE courier_db TO courier;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE courier_test TO courier;"
```

### 2. Backend

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt

# Змінні середовища (host = localhost, а не db)
export DATABASE_URL="postgresql+psycopg://courier:ваш-пароль@localhost:5432/courier_db"
export JWT_SECRET_KEY="ваш-довгий-випадковий-ключ"
export CORS_ORIGINS="http://localhost:5173"

alembic upgrade head               # створити таблиці
python -m scripts.seed             # завантажити тестові дані

uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

У другому терміналі:

```bash
cd frontend

npm install

# Адреса backend
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Відкрийте http://localhost:5173.

**Інші команди frontend:**

```bash
npm run build        # production-збірка (tsc + vite build)
npm run preview      # подивитися зібрану версію
npm run lint         # ESLint
npm run format       # Prettier
npm run typecheck    # перевірка типів
```

---

## Налаштування .env

Файл `.env` створюється з `.env.example` і в git не потрапляє. Повний перелік змінних - у `.env.example`; нижче найважливіші.

| Змінна | Призначення | Приклад |
| --- | --- | --- |
| `DATABASE_URL` | Підключення до PostgreSQL. У Docker хост - `db`, локально - `localhost` | `postgresql+psycopg://courier:pass@db:5432/courier_db` |
| `JWT_SECRET_KEY` | Ключ підпису токенів. **Обов'язково змініть** | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Скільки живе токен | `480` |
| `CORS_ORIGINS` | Дозволені origin через кому | `http://localhost:5173` |
| `VITE_API_URL` | Адреса backend для браузера | `http://localhost:8000` |
| `SEED_ON_START` | Завантажувати тестові дані під час старту контейнера | `true` |
| `SEED_DEFAULT_PASSWORD` | Пароль тестових облікових записів | `Password123!` |
| `TEST_DATABASE_URL` | База для pytest (очищується між тестами) | `postgresql+psycopg://courier:pass@localhost:5432/courier_test` |

Звичайний DSN `postgresql://...` теж приймається: система сама додасть драйвер `+psycopg`.

> `.env.example` не містить справжніх паролів. Перед першим запуском замініть `JWT_SECRET_KEY` і `POSTGRES_PASSWORD`.

---

## Міграції бази даних

Таблиці створюються **лише** через Alembic. Застосунок не викликає `create_all` під час старту, тож схема ніколи не розходиться з міграціями.

```bash
cd backend

alembic upgrade head               # накотити всі міграції
alembic downgrade -1               # відкотити останню
alembic current                    # яка ревізія зараз
alembic history                    # список міграцій
alembic check                      # чи не розійшлися моделі зі схемою

# нова міграція після зміни моделей
alembic revision --autogenerate -m "опис змін"
```

**Таблиці частини 1:**

| Таблиця | Призначення |
| --- | --- |
| `users` | Облікові записи. Унікальний індекс на `email`, індекси на `phone`, `role`, `is_active` |
| `orders` | Замовлення. Унікальний `tracking_number`, FK на `users`, обмеження `package_weight > 0` і `pickup_address <> delivery_address` |
| `order_status_history` | Журнал змін статусу. FK на `orders` (CASCADE) і `users` (SET NULL) |
| `order_tracking_counters` | Службовий лічильник номерів по роках |

---

## Тестові дані

```bash
cd backend
python -m scripts.seed
```

Скрипт створює 6 користувачів і 5 замовлень у різних статусах. Він ідемпотентний: повторний запуск нічого не дублює.

---

## Тестові облікові записи

Пароль для всіх однаковий: **`Password123!`** (змінюється через `SEED_DEFAULT_PASSWORD`).

| Роль | Email | Що можна перевірити |
| --- | --- | --- |
| Адміністратор | `admin@courier.ua` | Повний доступ: користувачі + замовлення |
| Диспетчер | `dispatcher@courier.ua` | Усі замовлення, зміна статусів, оформлення від імені клієнта |
| Кур'єр | `courier@courier.ua` | Вхід працює, доставка з'явиться в частині 2 |
| Клієнт 1 | `customer1@courier.ua` | Три власні замовлення в різних статусах |
| Клієнт 2 | `customer2@courier.ua` | Два власні замовлення |

> Це демонстраційні дані для локального запуску. У продакшні використовуйте власні облікові записи й паролі.

---

## Запуск тестів

Тести працюють проти справжнього PostgreSQL, а схема ставиться тими самими міграціями, що й у продакшні. Помилка в міграції знайдеться тестом, а не вже на сервері.

```bash
cd backend
source .venv/bin/activate

export TEST_DATABASE_URL="postgresql+psycopg://courier:ваш-пароль@localhost:5432/courier_test"

pytest                              # усі тести
pytest -v                           # з назвами
pytest app/tests/test_orders.py     # один файл
pytest --cov=app --cov-report=term-missing   # з покриттям
```

**Що покрито (81 тест):**

| Файл | Перевіряє |
| --- | --- |
| `test_auth.py` | Реєстрація, вхід, неправильний пароль, блокування, JWT, відсутність пароля у відкритому вигляді |
| `test_users.py` | Права ролей, створення й редагування, блокування, пошук, фільтри, пагінація, сортування |
| `test_orders.py` | Створення, перегляд власних замовлень, заборона на чужі, редагування, уся валідація полів |
| `test_order_status.py` | Дозволені й заборонені переходи, скасування, записи історії |
| `test_dashboard.py` | Лічильники для кожної ролі, останні 5 замовлень |

Перевірка стилю коду:

```bash
cd backend && ruff check app scripts alembic
cd frontend && npm run lint
```

---

## Адреси сервісів

| Сервіс | Адреса |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |
| Health check | http://localhost:8000/health |
| PostgreSQL | `localhost:5432` |

У Swagger спочатку отримайте токен через `POST /api/v1/auth/login`, потім натисніть **Authorize** угорі й вставте сам токен.

---

## REST API

Усі захищені ендпоінти очікують заголовок `Authorization: Bearer <token>`.

### Authentication

| Метод | Шлях | Опис |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Реєстрація клієнта, одразу повертає токен |
| `POST` | `/api/v1/auth/login` | Вхід за email і паролем |
| `GET` | `/api/v1/auth/me` | Дані поточного користувача |
| `POST` | `/api/v1/auth/logout` | Вихід |

### Users

| Метод | Шлях | Доступ |
| --- | --- | --- |
| `GET` | `/api/v1/users` | ADMIN |
| `POST` | `/api/v1/users` | ADMIN |
| `GET` | `/api/v1/users/me` | Усі |
| `PATCH` | `/api/v1/users/me` | Усі (власний профіль) |
| `GET` | `/api/v1/users/customers` | ADMIN, DISPATCHER |
| `GET` | `/api/v1/users/{id}` | ADMIN або сам користувач |
| `PATCH` | `/api/v1/users/{id}` | ADMIN |
| `PATCH` | `/api/v1/users/{id}/status` | ADMIN |

### Orders

| Метод | Шлях | Доступ |
| --- | --- | --- |
| `GET` | `/api/v1/orders` | ADMIN, DISPATCHER - усі; CUSTOMER - власні |
| `POST` | `/api/v1/orders` | ADMIN, DISPATCHER (з `customer_id`), CUSTOMER |
| `GET` | `/api/v1/orders/{id}` | За тим самим правилом, що й список |
| `PATCH` | `/api/v1/orders/{id}` | ADMIN, DISPATCHER; CUSTOMER - власне й нескасоване |
| `POST` | `/api/v1/orders/{id}/status` | ADMIN, DISPATCHER |
| `POST` | `/api/v1/orders/{id}/cancel` | ADMIN, DISPATCHER, CUSTOMER (власне) |
| `GET` | `/api/v1/orders/{id}/history` | За тим самим правилом, що й перегляд |

**Параметри списку замовлень:** `page`, `page_size`, `sort_by`, `sort_order`, `search`, `status`, `delivery_type`, `date_from`, `date_to`, `customer_id`.

**Параметри списку користувачів:** `page`, `page_size`, `sort_by`, `sort_order`, `search`, `role`, `is_active`.

### Dashboard і сервіс

| Метод | Шлях | Опис |
| --- | --- | --- |
| `GET` | `/api/v1/dashboard/summary` | Показники за роллю |
| `GET` | `/health` | Стан сервісу і бази |

### Формат помилок

Будь-яка помилка приходить в одному вигляді, тож frontend завжди знає, де шукати текст:

```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "Перехід «Створено» -> «Очікує кур'єра» заборонено. Доступні статуси: «Скасовано», «Підтверджено».",
    "details": null
  }
}
```

Для помилок валідації в `details` приходить список полів:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Дані не пройшли перевірку",
    "details": [{ "field": "package_weight", "message": "Input should be greater than 0", "type": "greater_than" }]
  }
}
```

**HTTP-коди:** `200` успіх, `201` створено, `401` немає або недійсний токен, `403` недостатньо прав або заблокований запис, `404` не знайдено, `409` порушено бізнес-правило (заборонений перехід, дублікат email), `422` не пройшла валідація.

---

## Ролі та права доступу

Права перевіряються на backend залежністю `require_roles(...)` на кожному ендпоінті. Приховані кнопки на frontend - це зручність, а не захист: прибрати табличку з дверей не те саме, що замкнути їх.

| Дія | ADMIN | DISPATCHER | CUSTOMER | COURIER |
| --- | :---: | :---: | :---: | :---: |
| Переглядати всіх користувачів | ✅ | ❌ | ❌ | ❌ |
| Створювати й редагувати користувачів | ✅ | ❌ | ❌ | ❌ |
| Блокувати й активувати записи | ✅ | ❌ | ❌ | ❌ |
| Переглядати всі замовлення | ✅ | ✅ | ❌ | ❌ |
| Переглядати власні замовлення | ✅ | ✅ | ✅ | ❌ |
| Створювати замовлення | ✅ | ✅ | ✅ | ❌ |
| Створювати від імені клієнта | ✅ | ✅ | ❌ | ❌ |
| Редагувати замовлення | ✅ | ✅ | власне, до передачі кур'єру | ❌ |
| Змінювати статус | ✅ | ✅ | ❌ | ❌ |
| Скасовувати замовлення | ✅ | ✅ | власне | ❌ |
| Бачити dashboard | ✅ | ✅ | ✅ (власні дані) | обмежено |

Додаткові захисні правила: адміністратор не може заблокувати сам себе або зняти з себе роль адміністратора, а заблокований користувач втрачає доступ одразу, навіть із раніше виданим токеном.

---

## Статуси замовлення

Дозволені переходи описані одним словником у `app/services/status_rules.py`. Це як схема ліній метро: потяг їде лише туди, куди веде колія.

```
CREATED ──────► CONFIRMED ──────► WAITING_FOR_COURIER
   │                │                      │
   └────────────────┴──────────────────────┴──────► CANCELLED
```

| Статус | Українською | Використовується |
| --- | --- | --- |
| `CREATED` | Створено | частина 1 |
| `CONFIRMED` | Підтверджено | частина 1 |
| `WAITING_FOR_COURIER` | Очікує кур'єра | частина 1 |
| `CANCELLED` | Скасовано | частина 1 |
| `COURIER_ASSIGNED` | Призначено кур'єра | зарезервовано для частини 2 |
| `PICKED_UP` | Забрано | зарезервовано для частини 2 |
| `IN_TRANSIT` | У дорозі | зарезервовано для частини 2 |
| `DELIVERED` | Доставлено | зарезервовано для частини 2 |
| `DELIVERY_FAILED` | Доставка не вдалася | зарезервовано для частини 2 |

Статуси частини 2 вже є в enum бази даних, але жодна операція частини 1 їх не встановлює - спроба перейти в них повертає `409`.

Кожна зміна статусу автоматично записується в `order_status_history` із попереднім статусом, новим статусом, автором, коментарем і часом. Записи ніколи не редагуються.

---

## Відомі обмеження частини 1

Свідомо не реалізовано (заплановано на частини 2 і 3):

- **Кур'єри й доставка.** Кур'єр може увійти й побачити профіль, але списку доставок у нього ще немає.
- **Карти, GPS, маршрути.** Адреси зберігаються текстом, без координат і геокодування.
- **Оплата й тарифи.** Вартість доставки не рахується.
- **Email-сповіщення.** Система нічого не надсилає.
- **Автоматичне призначення кур'єрів.**

Технічні обмеження поточної реалізації:

- **Refresh token** не реалізований: діє лише access token. Після закінчення строку потрібен повторний вхід.
- **Logout** не веде чорного списку токенів - клієнт просто видаляє токен у себе. Ендпоінт існує як точка розширення.
- **JWT зберігається в localStorage**, як дозволяє технічне завдання. Перехід на httpOnly-cookie - кандидат на частину 3.
- **Видалення користувачів і замовлень** не передбачене: записи блокуються або скасовуються, щоб історія лишалася цілою.
- **Завантаження файлів** (фото відправлення, документи) не реалізоване.
- **Frontend-тестів** немає: перевірка частини 1 спирається на backend-тести й ручні сценарії.
- **Лічильник номерів** працює через окрему таблицю з блокуванням рядка. Для очікуваного навантаження локальної компанії цього достатньо.

---

## План частин 2 і 3

### Частина 2: кур'єри, призначення й доставка

- Профіль кур'єра: зона роботи, графік, транспорт, поточне завантаження.
- Призначення замовлення кур'єру - вручну диспетчером і напівавтоматично.
- Активація статусів `COURIER_ASSIGNED`, `PICKED_UP`, `IN_TRANSIT`, `DELIVERED`, `DELIVERY_FAILED`.
- Мобільний інтерфейс кур'єра: список доставок на день, зміна статусу з телефону.
- Підтвердження доставки: підпис або фото, причина невдалої доставки.
- Відстеження замовлення клієнтом за `tracking_number` без входу в систему.

### Частина 3: карти, маршрути, тарифи й аналітика

- Геокодування адрес і карта з поточним станом доставок.
- Оптимізація маршруту для кур'єра на день.
- Тарифна сітка: вартість за вагою, розміром, типом доставки й відстанню.
- Онлайн-оплата й формування рахунків.
- Email- і SMS-сповіщення про зміну статусу.
- Розширена аналітика: графіки навантаження, KPI кур'єрів, звіти з експортом.
- Продакшн-розгортання: Vercel для frontend, Render для backend, Supabase PostgreSQL для бази, CI/CD через GitHub Actions.

---

## Ліцензія

Навчальний проєкт.

# 🚀 Alfa Copilot - AI-Ассистент для Малого Бизнеса
## Ссылка на репо https://github.com/Stepan-af/Alfa-hak
jfvhdfdfvhdf
Умный веб-ассистент с искусственным интеллектом для владельцев малого бизнеса. Автоматизирует ежедневные задачи: финансы, документы, маркетинг и планирование. Выполнен в фирменном стиле Alfa-Bank.

## ✨ Возможности

### 📊 Финансовый модуль
- Учёт доходов и расходов
- Анализ движения денежных средств
- Финансовые прогнозы и рекомендации
- Загрузка CSV с транзакциями
- Интерактивные графики и дашборды

### 📄 Управление документами
- Генерация контрактов и договоров
- Создание счетов и накладных
- AI-анализ документов
- Экспорт в PDF/DOCX
- Библиотека шаблонов

### 📱 Маркетинговые инструменты
- Генерация постов для соцсетей с AI
- Создание рекламных кампаний
- Идеи промо-акций
- Аналитика эффективности
- Планирование публикаций

### ✅ Планировщик задач
- Kanban-доска задач
- Подзадачи и чек-листы
- Повторяющиеся задачи
- Напоминания
- Фильтры по приоритету и категории

### 💬 AI-Чат Ассистент
- Контекстно-зависимые ответы
- Интеграция с модулями
- История разговоров
- Локальная LLM (llama3.2:3b)
- Быстрые ответы (до 60 сек)

## 🛠 Технологический стек

### Frontend
- **Vue 3** + **Vite** + **TypeScript** - современный реактивный UI
- **Pinia** - управление состоянием
- **Vuetify 3** - Material Design компоненты
- **GSAP** - плавные анимации (360ms/240ms, Alfa-Bank стиль)
- **Chart.js** - визуализация данных
- **Axios** - HTTP клиент

### Backend
- **FastAPI** (Python 3.11) - высокопроизводительный REST API
- **PostgreSQL 16** + **pgvector** - основная БД с векторным поиском
- **Redis 7** - кэш и очередь задач
- **Celery** - асинхронные задачи
- **SQLAlchemy 2.0** - ORM
- **Alembic** - миграции БД
- **Pydantic** - валидация данных

### AI/LLM
- **Ollama** - локальный LLM сервер
- **llama3.2:3b** - основная модель (2GB, быстрая)
- **LiteLLM** - единый интерфейс для разных LLM
- Ограничения: 1000 токенов на ответ (~700 слов), 8-16K контекст

### DevOps
- **Docker** + **Docker Compose** - контейнеризация
- **Nginx** - reverse proxy и статика
- **Make** - автоматизация команд

## 📋 Требования

### Для Docker (рекомендуется)
- **Docker** 24.0+ и **Docker Compose** v2.20+
- **Минимум 8 GB RAM** (для Ollama с llama3.2:3b)
- **10 GB свободного места** (Docker образы + модели)
- macOS, Linux или Windows (с WSL2)

### Для локальной разработки (опционально)
Если хотите запускать без Docker:

**Backend:**
- **Python** 3.11+ (рекомендуется 3.11.6+)
- **PostgreSQL** 16+
- **Redis** 7+

**Frontend:**
- **Node.js** 20+ (рекомендуется 20.9.0+)
- **npm** 10+

**Проверка версий:**
```bash
# Docker
docker --version          # Должна быть 24.0+
docker-compose --version  # Должна быть v2.20+

# Локальная разработка
python --version          # Должна быть 3.11+
node --version           # Должна быть v20+
npm --version            # Должна быть 10+
psql --version           # Должна быть 16+
redis-cli --version      # Должна быть 7+
```

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Stepan-af/Alfa-hak.git
cd Alfa-hak
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# Основные настройки
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true

# База данных
POSTGRES_USER=alfacopilot
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=alfacopilot
DATABASE_URL=postgresql://alfacopilot:your-secure-password@postgres:5432/alfacopilot

# Redis
REDIS_URL=redis://redis:6379/0

# Authentication (MVP)
# Для режима MVP аутентификация отключена — приложение работает без входа.
# В production можно включить email/magic-link аутентификацию (см. EMAIL_SETUP.md).

# LLM
OLLAMA_BASE_URL=http://ollama:11434
LITELLM_BASE_URL=http://litellm:4000
```

<!-- Authentication / Email setup removed for MVP (no auth). -->

### 3. Запуск всех сервисов

```bash
# Сборка и запуск
docker-compose up -d --build

# Или с Make
make up
```

Это запустит:
- **Frontend**: http://localhost:3000 (Vue.js UI)
- **Backend API**: http://localhost:8000 (FastAPI)
- **Ollama**: http://localhost:11434 (LLM сервер)
- **LiteLLM**: http://localhost:4000 (LLM прокси)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost:80 (реверс-прокси)

### 4. Установка LLM модели

**Первый запуск (автоматически):**
```bash
# Docker Compose автоматически скачает llama3.2:3b при первом старте
# Это займёт 5-10 минут (скачивание ~2GB)
```

**Проверка статуса:**
```bash
# Проверить логи Ollama
docker logs alfacopilot-ollama

# Проверить установленные модели
docker exec alfacopilot-ollama ollama list

# Должна быть: llama3.2:3b (2GB)
```

**Альтернативные модели:**
```bash
# Более мощная модель (требует 16+ GB RAM)
docker exec alfacopilot-ollama ollama pull llama3.1:8b

# Быстрая модель (1GB)
docker exec alfacopilot-ollama ollama pull phi3:mini
```

### 5. Применение миграций БД

```bash
# Создание таблиц
docker exec alfacopilot-api alembic upgrade head

# Проверка
docker exec alfacopilot-api alembic current
```

### 6. Открыть приложение

Откройте браузер: **http://localhost:3000**

**Авторизация:**
В режиме MVP аутентификация отключена — приложение открыто и доступно без входа. Просто откройте интерфейс и пользуйтесь функциями.

## 📱 Использование

### Главная страница
- Дашборд с основными метриками
- Быстрый доступ к модулям
- Анимированные статистические карточки

### Модуль "Финансы"
1. **Добавить транзакцию**: Кнопка "+ Добавить транзакцию"
2. **Загрузить CSV**: Импорт данных из банковской выписки
3. **Аналитика**: Графики доходов/расходов, категории, тренды
4. **Прогнозы**: AI-рекомендации по оптимизации финансов

### Модуль "Документы"
1. **Создать документ**: Выбрать шаблон (договор, счёт, акт)
2. **Заполнить данные**: AI помогает с содержимым
3. **Экспорт**: PDF или DOCX
4. **AI-анализ**: Проверка юридической корректности

### Модуль "Маркетинг"
1. **Новая кампания**: Указать цель и аудиторию
2. **Генерация контента**: AI создаёт посты для соцсетей
3. **Идеи промо**: Предложения акций и спецпредложений
4. **Аналитика**: Отслеживание эффективности

### Модуль "Задачи"
1. **Kanban доска**: Перетаскивание карточек
2. **Создать задачу**: Название, описание, приоритет, дата
3. **Подзадачи**: Разбивка на этапы
4. **Напоминания**: Уведомления о дедлайнах

### Модуль "Чат с AI"
1. **Новый разговор**: Задайте вопрос
2. **Контекст**: AI знает о ваших финансах, задачах, кампаниях
3. **Команды**: "Проанализируй расходы", "Создай пост о распродаже"
4. **История**: Все разговоры сохраняются

## 🔧 Полезные команды

### Docker

```bash
# Запуск сервисов
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск одного сервиса
docker-compose restart api

# Просмотр логов
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f ollama

# Очистка и пересборка
docker-compose down -v
docker-compose up -d --build
```bash
make setup
```

Or without Make:
```bash
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.scripts.seed
```

4. **Access the application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api/v1

## 📁 Project Structure

```
Alfa-hak/
├── backend/                # FastAPI Backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   └── main.py        # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Vue 3 Frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page views
│   │   ├── stores/        # Pinia stores
│   │   ├── router/        # Vue Router
│   │   ├── design/        # Design tokens & styles
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
```

### Makefile команды

```bash
make up          # Запустить все сервисы
make down        # Остановить все сервисы
make restart     # Перезапустить сервисы
make logs        # Показать логи всех сервисов
make clean       # Очистить volumes и пересобрать
```

### База данных

```bash
# Создать новую миграцию
docker exec alfacopilot-api alembic revision --autogenerate -m "описание"

# Применить миграции
docker exec alfacopilot-api alembic upgrade head

# Откатить миграцию
docker exec alfacopilot-api alembic downgrade -1

# Подключиться к БД
docker exec -it alfacopilot-postgres psql -U alfacopilot -d alfacopilot
```

### LLM

```bash
# Список моделей
docker exec alfacopilot-ollama ollama list

# Скачать новую модель
docker exec alfacopilot-ollama ollama pull mistral:7b

# Тест модели
docker exec alfacopilot-ollama ollama run llama3.2:3b "Привет"

# Удалить модель
docker exec alfacopilot-ollama ollama rm llama3.2:3b
```

## 🐛 Решение проблем

### Проблема: Контейнеры не запускаются

```bash
# Проверить логи
docker-compose logs

# Проверить ресурсы Docker
docker system df

# Освободить место
docker system prune -a --volumes
```

### Проблема: Frontend не открывается

```bash
# Проверить логи frontend
docker logs alfacopilot-frontend

# Перезапустить
docker-compose restart frontend

# Проверить порт 3000
lsof -i :3000
```

### Проблема: API ошибки 500

```bash
# Проверить логи API
docker logs alfacopilot-api -f

# Проверить подключение к БД
docker exec alfacopilot-api python -c "from app.database import engine; engine.connect()"

# Проверить миграции
docker exec alfacopilot-api alembic current
```

### Проблема: LLM не отвечает

```bash
# Проверить Ollama
docker logs alfacopilot-ollama

# Проверить модель установлена
docker exec alfacopilot-ollama ollama list

# Тест модели
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Hello"
}'
```

### Проблема: Magic Link не приходит

Авторизация отключена в MVP; если вы ожидаете magic links — они выводятся в логах при включённом режиме email в production. Для MVP используйте встроенный доступ.

### Проблема: Навигация не работает

Это была баг с динамическими импортами. **Исправлено**: используются прямые импорты в `router/index.ts`.

Если проблема осталась:
```bash
# Очистить кэш браузера (Cmd+Shift+R или Ctrl+Shift+R)
# Или пересобрать frontend
docker-compose up -d --build frontend
```

## 📊 API Документация

После запуска доступна Swagger документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

<!-- Authentication endpoints are available but not required in MVP -->

**Финансы:**
- `GET /api/v1/finance` - Список транзакций
- `POST /api/v1/finance` - Создать транзакцию
- `GET /api/v1/finance/{id}` - Получить транзакцию
- `PUT /api/v1/finance/{id}` - Обновить
- `DELETE /api/v1/finance/{id}` - Удалить
- `POST /api/v1/finance/upload-csv` - Загрузить CSV
- `GET /api/v1/finance/analytics` - Аналитика

**Документы:**
- `GET /api/v1/documents` - Список документов
- `POST /api/v1/documents` - Создать документ
- `POST /api/v1/documents/analyze` - AI анализ
- `GET /api/v1/documents/templates` - Шаблоны
- `POST /api/v1/documents/{id}/export` - Экспорт

**Маркетинг:**
- `GET /api/v1/marketing/campaigns` - Кампании
- `POST /api/v1/marketing/campaigns` - Создать кампанию
- `POST /api/v1/marketing/generate-post` - Сгенерировать пост
- `GET /api/v1/marketing/ideas` - Идеи промо

**Задачи:**
- `GET /api/v1/tasks` - Список задач
- `POST /api/v1/tasks` - Создать задачу
- `PUT /api/v1/tasks/{id}` - Обновить
- `DELETE /api/v1/tasks/{id}` - Удалить

**Чат:**
- `GET /api/v1/chat/conversations` - Список разговоров
- `POST /api/v1/chat/conversations` - Новый разговор
- `POST /api/v1/chat/conversations/{id}/messages` - Отправить сообщение
- `GET /api/v1/chat/conversations/{id}/messages` - История

## 📁 Структура проекта

```
Alfa-hak/
├── frontend/              # Vue 3 приложение
│   ├── src/
│   │   ├── views/        # Страницы (Home, Finance, Chat, ...)
│   │   ├── components/   # Компоненты (StatCard, ChatMessage, ...)
│   │   ├── composables/  # Composables (useAnimations, ...)
│   │   ├── stores/       # Pinia stores (finance, ...)
│   │   ├── router/       # Vue Router
│   │   ├── assets/       # Статика (CSS, изображения)
│   │   └── design/       # Design tokens (цвета, шрифты)
│   ├── Dockerfile
│   └── package.json
│
├── backend/              # FastAPI приложение
│   ├── app/
│   │   ├── main.py      # Точка входа
│   │   ├── config.py    # Конфигурация
│   │   ├── database.py  # Подключение к БД
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── schemas/     # Pydantic схемы
│   │   ├── api/v1/      # API эндпоинты
│   │   └── services/    # Бизнес-логика
│   ├── alembic/         # Миграции БД
│   ├── tests/           # Тесты
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml    # Оркестрация сервисов
├── nginx.conf           # Reverse proxy
├── litellm_config.yaml  # LLM конфигурация
├── Makefile            # Автоматизация
├── .env.example        # Пример переменных окружения
│
└── docs/               # Документация
    ├── EMAIL_SETUP.md    # Настройка email
    ├── LLM_SETUP.md      # Настройка LLM
    ├── ANIMATIONS.md     # Гайд по анимациям
    ├── DOCKER_GUIDE.md   # Docker инструкции
    └── QUICKSTART.md     # Быстрый старт
```

## 🎨 Дизайн и анимации

Проект выполнен в фирменном стиле **Alfa-Bank**:

### Цвета
- **Primary Red**: `#ef3124` - основной акцент
- **Dark Background**: `#0f0f10` - фон
- **Surface**: `#1a1b1e` - карточки
- **Success Green**: `#22c55e`
- **Warning Yellow**: `#f59e0b`
- **Error Red**: `#ef4444`

### Анимации
- **Enter**: 360ms с `easeOutCubic`
- **Exit**: 240ms с `easeInCubic`
- **Hover**: Scale 1.02, подъём 4px, 200ms
- **Поддержка**: `prefers-reduced-motion`

Подробнее: [ANIMATIONS.md](./ANIMATIONS.md)

## 🔐 Безопасность

### Production чеклист

1. **Изменить SECRET_KEY** в `.env`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Установить DEBUG=false**

3. **Использовать сильные пароли БД**

4. **Настроить CORS** в `backend/app/main.py`:
```python
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

5. **HTTPS**: Настроить SSL сертификат в Nginx

6. **Rate limiting**: Ограничить количество запросов

7. **Backup БД**: Настроить регулярные бэкапы

## 🚀 Деплой в Production

### Docker Registry Images

Приложение доступно в Docker Hub:
- **Backend**: `docker.io/stepanpd/alfa-hak-backend:latest`
- **Frontend**: `docker.io/stepanpd/alfa-hak-frontend:latest`

### Быстрый деплой

```bash
# 1. Скачать образы из registry
docker-compose pull

# 2. Запустить production версию
docker-compose up -d

# 3. Применить миграции
docker exec alfacopilot-api alembic upgrade head

# 4. Проверить статус
docker-compose ps
```

### Сборка и публикация образов

Если вы разработчик и хотите опубликовать новую версию:

```bash
# 1. Авторизоваться в Docker Hub
docker login

# 2. Собрать и опубликовать образы
./build-and-push.sh docker.io/stepanpd v1.0.0
```

Скрипт `build-and-push.sh` автоматически:
- Соберёт backend и frontend образы
- Присвоит версионные теги (v1.0.0) и latest
- Опубликует в Docker Registry

### Обновление до новой версии

```bash
# 1. Соберите новые образы
./build-and-push.sh docker.io/stepanpd v1.0.1

# 2. Обновите docker-compose.yml (замените :latest на :v1.0.1 при необходимости)

# 3. Скачайте новые образы
docker-compose pull

# 4. Пересоздайте контейнеры
docker-compose up -d

# 5. Примените миграции (если есть)
docker exec alfacopilot-api alembic upgrade head
```

### Production чеклист безопасности

**Обязательно перед production:**

1. **SECRET_KEY**: Сгенерируйте уникальный ключ
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **DEBUG=false**: Отключите debug режим в `.env`

3. **Пароли БД**: Используйте сильные случайные пароли

4. **CORS**: Ограничьте allowed origins в `backend/app/main.py`
```python
ALLOWED_ORIGINS = ["https://yourdomain.com"]
```

5. **HTTPS**: Настройте SSL сертификат в Nginx

6. **Backup**: Настройте регулярные бэкапы PostgreSQL
```bash
docker exec alfacopilot-postgres pg_dump -U alfacopilot alfacopilot > backup.sql
```

### Размеры образов

```bash
# Проверьте размеры
docker images | grep alfa-hak

# Ожидаемые размеры:
# backend: ~500-800 MB
# frontend: ~150-300 MB (multi-stage build)
```

### Мониторинг Production

```bash
# Проверка логов
docker-compose logs -f api
docker-compose logs -f frontend

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

## 🤝 Вклад в проект

Мы приветствуем вклад! См. [CONTRIBUTING.md](./CONTRIBUTING.md)

### Локальная разработка

Для локальной разработки с hot reload:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

**Или используйте docker-compose в dev режиме:**

Создайте `docker-compose.dev.yml` с локальными билдами:
```yaml
api:
  build:
    context: ./backend
    dockerfile: Dockerfile
  volumes:
    - ./backend:/app
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend:
  build:
    context: ./frontend
  volumes:
    - ./frontend:/app
    - /app/node_modules
  command: npm run dev -- --host 0.0.0.0
```

Затем: `docker-compose -f docker-compose.dev.yml up -d`

## 📄 Лицензия

MIT License - см. [LICENSE](./LICENSE)

## 📞 Контакты

- **GitHub**: [Stepan-af/Alfa-hak](https://github.com/Stepan-af/Alfa-hak)
- **Email**: support@alfacopilot.ru

## 🙏 Благодарности

- **Alfa-Bank** - за вдохновение дизайном
- **FastAPI** - за отличный фреймворк
- **Vue.js** - за реактивность
- **Ollama** - за локальные LLM

---

**Сделано с ❤️ для малого бизнеса**

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint and format
npm run lint
npm run format
```

## 🎨 Design System

The application follows Alfa-Bank design guidelines:

- **Dark theme** with bright accent colors
- **Smooth animations** (280-360ms enter, 220-260ms exit)
- **Large typography** and bold CTAs
- **Rounded corners** (20px default)
- **GSAP-powered** motion effects
- **Accessible** with keyboard navigation and ARIA labels

Design tokens are defined in `/frontend/src/design/tokens.css`

## 🐳 Docker Commands

```bash
# Build all containers
make build

# Start services
make up

# Stop services
make down

# View logs
make logs

# Run tests
make test

# Seed database
make seed

# Clean everything
make clean
```

## 📡 API Endpoints

### Authentication
Authentication is disabled for the MVP — the application is open and most API endpoints are available without login. Authentication-related endpoints exist but are not required in MVP mode.

### Finance
- `POST /api/v1/finance/upload_csv` - Upload financial data
- `GET /api/v1/finance/summary` - Get finance summary
- `GET /api/v1/finance/forecast` - Get cash flow forecast
- `GET /api/v1/finance/recommendations` - Get recommendations

### Documents
- `POST /api/v1/docs/generate` - Generate document
- `GET /api/v1/docs/templates` - List templates
- `POST /api/v1/docs/upload` - Upload document
- `GET /api/v1/docs/{id}/summary` - Get document summary

### Marketing
- `POST /api/v1/marketing/generate_post` - Generate post
- `POST /api/v1/marketing/promo_idea` - Get promo ideas
- `GET /api/v1/marketing/checklist` - Get marketing checklist

### Tasks
- `POST /api/v1/tasks/create` - Create task
- `GET /api/v1/tasks/today` - Get today's tasks
- `POST /api/v1/tasks/reminders` - Set reminders

### Chat
- `POST /api/v1/chat/message` - Send message to AI
- `GET /api/v1/chat/history` - Get chat history

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm run test
```

## 🔐 Authentication Setup
Authentication and email/magic-link configuration have been disabled for the MVP. For production use, see `EMAIL_SETUP.md` in the docs (this is disabled by default in the MVP branch).

## 🔒 Security

- Authentication is disabled in MVP (enable in production configuration)
- HTTPS enforced in production
- CORS configuration
- Rate limiting on auth endpoints
- File upload validation
- Encrypted sensitive data in database

## 📚 Documentation

- API Documentation: `/docs` (Swagger UI)
- Alternative API Docs: `/redoc` (ReDoc)
- Component Library: Run `npm run storybook` in frontend


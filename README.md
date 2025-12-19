# Помощник-бот (Помогатор)

### 1. Цель  
Создать Telegram-бота, который позволит пользователям взаимодействовать с рядом AI-ассистентов: ChatGPT, Perplexity и DeepSeek.

### 2. Бизнес-логика  

###### 2.1 Пользователь POV

Пользователь будет взаимодействовать с приложением через Telegram-бота.  

Начало работы — с inline-кнопки `/start`. Пользователю будут доступны inline-кнопки, которые позволят:  
- `/start` (начать диалог с ИИ)  
- `/status` (покажет, является ли пользователь VIP или нет)  
- `/help` (стандартное справочное сообщение)  
- `/settings` (можно проверить профиль и информацию о VIP-статусе)  
- `/model` (выбрать между ChatGPT: (Instant, Thinking, GPT-5), Perplexity: (Search, Research, Laboratory) и DeepSeek: (Standard, Thinking))  

В бесплатной версии будет ограниченное количество разрешённых сообщений (10), а в VIP-версии (с ежемесячной подпиской), не будет.  

###### 2.2 Основная бизнес-логика

```mermaid
graph TD
  A[User opens helper bot] --> B{/start}
  B -->|Yes| C[Welcome + Menu]

  %% FREE TRIAL ENTRY LOGIC
  D{Free trial?}
  D -->|Not Started| FT[Offer free trial]
  D -->|Active| T2
  
  X[Offer subscription]

  FT --> FT2{User accepts trial?}
  FT2 -->|Yes| FT3[Activate free trial with limited msg]
  FT2 -->|No| C

  FT3 --> T2

  %% READY STATE
  H[Ready to chat]

  %% MAIN SUBSCRIPTION CHECK
  C --> E{Has subscription?}
  E -->|Yes| K
  E -->|No| D

  X --> S[Subscription options]

  %% SUBSCRIPTION PURCHASE FLOW
  S --> P1{User pays?}
  P1 -->|Yes| P2[Activate subscription]
  P1 -->|No| C
  P2 --> K

  %% ACCESS GATE FOR BOTH PAID & TRIAL USERS
  K{Subscription active?}
  K -->|No| S
  K -->|Yes| H

  %% MAIN CHAT FLOW
  H --> I[User sends message]
  I --> J[Bot receives message]

  J --> L[Send request]

  L --> M{Error?}
  M -->|Yes| N[Retry / error message]
  N --> H
  M -->|No| O[Send AI reply]

  O --> P[Log interaction]
  P --> H

  %% FREE TRIAL COUNTER
  T2{Trial messages left?}
  T2 -->|No| X
  T2 -->|Yes| H
```

### 3. Архитектура и стек   

###### 3.1 Arch 

```mermaid
flowchart TD
    U[User via Telegram] --> TG[Telegram API]

    subgraph VPS[Host Server VPS]
        subgraph Docker[Docker Compose Environment]
            direction TB

            NGINX[NGINX SSL / Routing]

            subgraph BotProcess[Telegram Bot Service]
                BOT[Bot Main Process]
                subgraph BotCore[Bot Components]
                    AUTH[Auth Middleware]
                    SUBCHECK[Subscription Middleware]
                    ROUTER[Handlers / Router]
                    ERROR[Error Handler]
                    LOG[Logging]
                end
                BOT --> AUTH
                BOT --> SUBCHECK
                BOT --> ROUTER
                BOT --> ERROR
                BOT --> LOG
            end

            subgraph BackendProcess[FastAPI Backend Service]
                API[Backend API]
                subgraph BackendCore[Backend Layers]
                    ROUTES[Routes Layer]
                    SERVICES[Core Services]
                    AGENT[AI Orchestration / Agent]
                end
                API --> ROUTES
                ROUTES --> SERVICES
                SERVICES --> AGENT
            end

            subgraph Data[PostgreSQL Database]
                DB[(PostgreSQL)]
            end
        end
    end

    %% Connections
    TG --> NGINX
    NGINX --> BOT
    NGINX --> API
    AUTH --> DB
    SUBCHECK --> DB
    SERVICES --> DB
    LOG --> DB

    AGENT --> AI[AI Services]
    AI --> ChatGPT[ChatGPT API]
    AI --> DeepSeek[DeepSeek API]
    AI --> Perplexity[Perplexity API]

```

###### 3.2 Stack
Планируется упаковать проект в Docker Compose/Docker.  

**Язык:** Python  
**Телеграм-бот:**
<br> Aiogram (асинхронность, FSM, промежуточное ПО, инлайн-кнопки).  
**Backend API:**
<br> FastAPI (REST API для обработки сообщений и бизнес-логики).  
**AI / LLM:** 
<br> OpenAI, Perplexity, DeepSeek.  
**База данных:**
<br> PostgreSQL (пользователи, сообщения, кредиты, подписки, платежи).  
**ORM и миграции:**
<br> SQLAlchemy, Alembic.  
**Платежи:** 
<br> Telegram Bot Payments API, провайдер платежей в Telegram:
**Инфраструктура:**
<br> Docker, Docker Compose, NGINX (SSL).  
**Тестирование:**
<br> Pytest.

### 4. Структура базы данных

###### Структура 

```mermaid
erDiagram
    CURRENCY_CODE {
        ENUM values "('RUB', 'USD', 'EUR')"
    }
    
    AI_PROVIDER_TYPE {
        ENUM values "('chatgpt', 'perplexity', 'deepseek')"
    }
    
    SUBSCRIPTION_PLAN_TYPE {
        ENUM values "('trial', 'premium')"
    }
    
    USERS {
        BIGSERIAL id PK
        BIGINT telegram_id UK "unique constraint"
        INT trial_messages_left
        BOOLEAN is_vip
        TIMESTAMP last_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    ACTIVE_USERS {
        BIGINT user_id PK "Primary Key"
        TIMESTAMP updated_at 
    }
    
    MESSAGE_HISTORY {
        BIGSERIAL id PK
        BIGINT user_id FK
        AI_PROVIDER_TYPE ai_provider "ENUM type"
        VARCHAR ai_model
        TEXT user_message
        TEXT ai_response
        TIMESTAMP created_at
    }
    
    SUBSCRIPTIONS {
        BIGSERIAL id PK
        BIGINT user_id FK
        SUBSCRIPTION_PLAN_TYPE plan "ENUM type"
        DATE start_date
        DATE end_date
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    PAYMENTS {
        BIGSERIAL id PK
        BIGINT user_id FK
        DECIMAL amount
        CURRENCY_CODE currency "ENUM type"
        DATE payment_date
        BOOLEAN success
        VARCHAR telegram_payment_id
        TIMESTAMP created_at
    }
    
    CURRENCY_CODE ||--o{ PAYMENTS : "used_in"
    AI_PROVIDER_TYPE ||--o{ MESSAGE_HISTORY : "used_in"
    SUBSCRIPTION_PLAN_TYPE ||--o{ SUBSCRIPTIONS : "used_in"
    
    USERS ||--|| ACTIVE_USERS : "active_status"
    USERS ||--o{ MESSAGE_HISTORY : writes
    USERS ||--o{ SUBSCRIPTIONS : has
    USERS ||--o{ PAYMENTS : makes
    
    ACTIVE_USERS }|--|| USERS : "references"
```

###### 4.2 Предложение шифрования данных в БД

Стоит задуматься о внедрение шифрования чувствительных данных. В качестве первого уровня защиты имеет смысл использовать шифрование диска на сервере и SSL/TLS для всех соединений с PostgreSQL (хотя признаюсь что как это реализовать я пока не полноценно осознал).

 Дополнительно, для таких полей, как telegram_id, сообщения пользователей, ответы ИИ и идентификаторы платежей, можно применять шифрование на уровне базы данных или приложения. Ключи шифрования при этом не хранятся в БД и передаются через переменные окружения или систему секретов (например, Docker Secrets).

### 5. Структура кода

##### 5.1 Cтруктура (на этап 1)

<pre>
helper-bot/
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
├── nginx/
├── bot/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── handlers.py
│   │   ├── keyboards.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── .env
│   └── main.py
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── webhook.py
│   │   ├── process_message.py
│   │   ├── credits.py
│   │   ├── payments.py
│   │   ├── users.py
│   │   └── trial.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── subscription_service.py
│   │   ├── payment_service.py
│   │   └── user_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── enums.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── crud.py
│   │   └── migrations/
│   │       ├── versions/
│   │       └── alembic.ini
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_services.py
│       └── test_database.py
├── images/
├── scripts/
└── .idea/
    ├── inspectionProfiles/
    │   └── profiles_settings.xml
    ├── .gitignore
    ├── helper-bot-imi
    ├── misc.xml
    ├── modules.xml
    └── ves.xml
</pre>

##### 5.2 Cтруктруа (на этап 2)

<pre>
helper-bot/
├── docker-compose.yml        # Оркестрация всех сервисов (бот, бэкенд, база данных, nginx) в виде контейнеров
├── .env.example              # Определение переменных окружения, необходимых всем сервисам
├── README.md                 
├── nginx/                    # Входной обратный прокси-сервер и слой терминации SSL
│   ├── nginx.conf            # Маршрутизация внешнего трафика к сервисам бота и бэкенда
│   └── ssl/                  # TLS-сертификаты для HTTPS / защищённых вебхуков
├── bot/                      # Сервис для взаимодействия с Telegram (уровень представления и взаимодействия)
│   ├── Dockerfile            # Сборка контейнера Telegram-бота
│   ├── requirements.txt      # Зависимости сервиса бота
│   ├── main.py               # Точка входа в приложение и инициализация бота
│   ├── config.py             # Конфигурация бота и загрузка переменных окружения
│   ├── handlers/             # Логика маршрутизации сообщений и взаимодействия с пользователем
│   │   ├── __init__.py
│   │   ├── start.py          # Обработка команд начала работы и онбординга
│   │   ├── chat.py           # Обработка пользовательских сообщений и чат-взаимодействий
│   │   ├── payments.py       # Инициация платёжных потоков и запросов пользователю
│   │   ├── profile.py        # Управление профилем пользователя и просмотром аккаунта
│   │   └── errors.py         # Централизованные ответы на ошибки для пользователя
│   ├── keyboards/            # UI-компоненты для взаимодействия в Telegram
│   │   ├── __init__.py
│   │   ├── main_menu.py      # Основные навигационные меню
│   │   └── payments.py       # Кнопки и меню, связанные с платежами
│   ├── middlewares/          # Скрещивающиеся аспекты, применяемые ко всем сообщениям
│   │   ├── __init__.py
│   │   ├── auth.py           # Проверка идентичности пользователя и валидности сессии
│   │   └── subscription.py   # Проверка ограничений подписки и пробного периода
│   ├── utils/                # Общие утилиты, используемые в сервисе бота
│   │   ├── __init__.py
│   │   ├── logger.py         # Логирование и диагностика для уровня бота
│   │   └── states.py         # Управление состоянием пользователя и определения FSM
│   └── tests/                # Автоматизированные тесты логики бота и промежуточного ПО
│       ├── __init__.py
│       ├── test_handlers.py
│       └── test_middlewares.py
├── backend/                  # Слой основной бизнес-логики и API
│   ├── Dockerfile            # Сборка контейнера сервиса бэкенда
│   ├── requirements.txt      # Зависимости бэкенда
│   ├── main.py               # Точка входа в бэкенд-приложение
│   ├── config.py             # Конфигурация бэкенда и загрузка переменных окружения
│   ├── api/                  # Конечные точки HTTP API, доступные боту и вебхукам
│   │   ├── __init__.py
│   │   ├── dependencies.py   # Общие зависимости API (аутентификация, сессии БД)
│   │   ├── webhook.py        # Обработка входящих вебхуков от Telegram или платёжных провайдеров
│   │   ├── process_message.py # Обработка сообщений, делегированных ботом
│   │   ├── credits.py        # Управление кредитами использования и квотами
│   │   ├── payments.py       # Конечные точки платежей и коллбэки
│   │   ├── users.py          # Конечные точки аккаунта пользователя и профиля
│   │   └── trial.py          # Жизненный цикл бесплатного пробного периода и валидация
│   ├── services/             # Уровень доменной и бизнес-логики
│   │   ├── __init__.py
│   │   ├── ai_service.py     # Оркестрация AI/LLM и логика инференса
│   │   ├── subscription_service.py # Управление состоянием подписки и тарифами
│   │   ├── payment_service.py # Логика интеграции с платёжным провайдером
│   │   └── user_service.py   # Бизнес-правила, связанные с пользователями
│   ├── models/               # Доменные модели и схемы данных
│   │   ├── __init__.py
│   │   ├── database.py       # Движок базы данных и базовые определения моделей
│   │   ├── schemas.py        # Схемы API и валидации
│   │   └── enums.py          # Общие перечисления для согласованности домена
│   ├── database/             # Уровень хранения и доступа к данным
│   │   ├── __init__.py
│   │   ├── session.py        # Управление сессиями и подключениями к базе данных
│   │   ├── crud.py           # Повторно используемые операции доступа к базе данных
│   │   └── migrations/       # Эволюция схемы и управление версиями
│   │       ├── versions/
│   │       └── alembic.ini
│   ├── utils/                # Общие утилиты для бэкенда
│   │   ├── __init__.py
│   │   ├── logger.py         # Логирование и мониторинг бэкенда
│   │   └── exceptions.py     # Централизованные определения ошибок
│   └── tests/                # Тесты компонентов бэкенда
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_services.py
│       └── test_database.py
└── scripts/                  # Инструменты для эксплуатации и обслуживания
    ├── init_db.py            # Инициализация схемы базы данных и начальных данных
    ├── deploy.sh             # Скрипт автоматизации развёртывания
    └── backup.sh             # Скрипт резервного копирования и восстановления базы данных
</pre>

### 6. План разработки и распределение задач

---

###### 6.1 Devs

Dev 1 (Telegram Bot): Создаёт и поддерживает Telegram-бота, обрабатывает команды, инлайн-меню, промежуточное ПО (middleware) и интеграцию с бэкендом. [@Mahmadmurod](https://t.me/Mahmadmurod)

Dev 2 и TL (Backend): Реализует бэкенд на FastAPI, включая API-маршруты, интеграцию AI-сервисов, логику пробного периода и подписок, а также систему логирования. [@local_dan](https://t.me/local_dan)

Dev 3 (База данных): Проектирует, создаёт и управляет базой данных PostgreSQL, миграциями, асинхронными операциями и обеспечивает целостность данных. [@Ufpngh5](https://t.me/Ufpngh5)

Dev 4 (Инфраструктура): Отвечает за развёртывание Docker, настройку Nginx и SSL, централизованное логирование и интеграцию Telegram Payments. [@ne_necoffeee](https://t.me/ne_necoffeee)

---

###### 6.2 Stages 

#### Этап 1 

**Цель:** Запустить работающее ядро: бот принимает сообщение, бэкенд обрабатывает через ИИ, данные сохраняются в БД.

| Порядок | Разработчик | Ответственность | Задачи |
|---------|------------|----------------|--------|
| **1**   | **Dev 3**   | Схема и доступ к данным   | • Настройка PostgreSQL в Docker<br>• Создание базовых таблиц: `users`, `message_history`, `active_users`<br>• Настройка ENUM-типов (`ai_provider_type`)<br>• Конфигурация SQLAlchemy + Alembic<br>• Реализация базового CRUD-слоя                                                        |
| **2**   | **Dev 2**   | Бизнес-логика и API       | • Инициализация FastAPI-проекта<br>• Реализация API-эндпоинтов: `/users/register`, `/trial/start`, `/process_message`<br>• Интеграция AI-провайдеров (ChatGPT, Perplexity, DeepSeek)<br>• Логика пробного периода (лимит сообщений)<br>• Централизованная обработка ошибок и логирование |
| **3**   | **Dev 1**   | Telegram-интерфейс        | • Регистрация бота через BotFather<br>• Команды `/start`, `/help`, базовое меню<br>• Middleware: регистрация пользователя, проверка пробного периода<br>• FSM / состояние пользователя<br>• Отправка сообщений в бэкенд и обработка ответов и ошибок                                     |
| **4**   | **Dev 4**   | Инфраструктура и доставка | • Docker Compose (bot, backend, postgres, nginx)<br>• Настройка Nginx (reverse proxy, SSL)<br>• Переменные окружения и secrets<br>• Базовое централизованное логирование                                                                                  |


---

#### Этап 2 

**Цель:** Добавить монетизацию (Telegram Payments), систему подписок/кредитов.

##### Процесс работы с платежной системой

**Пользователь инициирует оплату.**  
Когда пользователь нажимает кнопку для покупки подписки, бот вызывает API платежного провайдера. Пользователь видит стандартную форму оплаты, предоставляемую платежной системой, и завершает транзакцию.

**Обработка успешного платежа.**  
После завершения оплаты платежный провайдер отправляет уведомление на заранее настроенный адрес нашего сервиса. Мы проверяем подлинность этого уведомления и убеждаемся, что данный платеж еще не был обработан ранее. Затем сохраняем полные детали транзакции в нашу базу данных.

**Активация подписки для пользователя.**  
После подтверждения платежа система обновляет статус пользователя. Создается новая или обновляется существующая запись о подписке с указанием даты начала и окончания. Флаг, определяющий доступ к платным функциям, активируется. Пользователь получает немедленное подтверждение и доступ к сервису.

**Проверка доступа при каждом использовании.**  
Каждый раз, когда пользователь обращается к основному функционалу, система проверяет наличие активной подписки. Для этого выполняется запрос к бд, где хранится текущий статус и срок действия подписки. Доступ предоставляется только при наличии действующей подписки.

**Управление жизненным циклом подписки.**  
Система отслеживает сроки действия всех подписок. Пользователь может получить напоминание перед истечением срока. После окончания подписки доступ к платным функциям автоматически прекращается. Для восстановления доступа необходимо оформить новую подписку.

**Хранение данных.**  
Вся информация о платежах и подписках хранится в нашей собственной базе данных. Мы сохраняем детали транзакций, историю подписок и их связь с пользователями. Эта база является основным источником данных для управления доступом.

**Архитектурный подход.**  
Платежная система используется исключительно как канал для приема средств. Вся бизнес-логика, включая проверки прав доступа и управление сроками подписок, контролируется приложением на основе данных в нашей базе.

---


| Порядок | Разработчик | Ответственность | Задачи |
|---------|------------|----------------|--------|
| **1**   | **Dev 3**   | Схема подписок и платежей              | • Создание таблиц: `subscriptions`, `payments`<br>• Добавление ENUM-типов (`subscription_plan_type`, `currency_code`)<br>• Индексы, внешние ключи и ограничения целостности<br>• Миграции Alembic для платёжной схемы<br>• CRUD-запросы для подписок и платежей                                                  |
| **2**   | **Dev 2**   | Бизнес-логика подписок и платежей      | • Реализация API-эндпоинтов подписок и платежей<br>• Логика жизненного цикла подписки (start / renew / expire)<br>• Валидация платёжных статусов и идемпотентность<br>• Ограничения доступа по подписке (VIP / trial)<br>• Расширенное логирование и обработка ошибок                                            |
| **3**   | **Dev 4**   | Инфраструктура платежей                | • Настройка Telegram Payments (provider token, callbacks)<br>• Конфигурация безопасного проксирования платёжных запросов через Nginx<br>• Управление secrets и переменными окружения для платежей<br>• Централизованный сбор логов (бот / бэкенд / платежи) |
| **4**   | **Dev 1**   | Пользовательский интерфейс монетизации | • UI выбора тарифа и подписки (inline-кнопки)<br>• Инициация платёжного потока Telegram Payments<br>• Обработка статусов платежа (успех / ошибка / отмена)<br>• Отображение VIP-статуса и срока подписки<br>• Сообщения об ограничениях и лимитах                                                                |


---

###### Этап 3

**Цель:** Убедиться в работоспособности всей системы. Надо тоже осущесвить покрытие тестами, (боже найти бы время).




#### Важное примечание:  
Исходный файл README был написан на английском языке и переведён на русский с помощью DeepSeek для экономии времени. Данное примечание добавлено для прозрачности.
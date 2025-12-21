-- Скрипт инициализации ENUM-типов для базы данных Telegram бота-помощника
-- Выполняется при первом запуске контейнера PostgreSQL
-- Таблицы создаются через Alembic миграции
-- Создаём ENUM-типы, которые будут использоваться в таблицах

-- Тип для AI-провайдеров
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ai_provider_type') THEN
        CREATE TYPE ai_provider_type AS ENUM ('chatgpt', 'perplexity', 'deepseek');
        RAISE NOTICE 'Тип ai_provider_type создан';
    ELSE
        RAISE NOTICE 'Тип ai_provider_type уже существует';
    END IF;
END$$;

-- Тип для видов подписки
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscription_plan_type') THEN
        CREATE TYPE subscription_plan_type AS ENUM ('trial', 'premium');
        RAISE NOTICE 'Тип subscription_plan_type создан';
    ELSE
        RAISE NOTICE 'Тип subscription_plan_type уже существует';
    END IF;
END$$;


-- Тип для валют
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'currency_code') THEN
        CREATE TYPE currency_code AS ENUM ('RUB', 'USD', 'EUR');
        RAISE NOTICE 'Тип currency_code создан';
    ELSE
        RAISE NOTICE 'Тип currency_code уже существует';
    END IF;
END$$;

-- Выводим итоговое сообщение
DO $$ 
BEGIN
    RAISE NOTICE 'Инициализация ENUM-типов завершена. Таблицы будут созданы через Alembic.';
END $$;
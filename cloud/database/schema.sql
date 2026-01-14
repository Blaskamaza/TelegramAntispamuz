-- ============================================================
-- UZ AI Factory — RDS PostgreSQL Schema
-- Узел «Diary & Memory»
-- 
-- Alibaba RDS PostgreSQL Free Tier: 20GB, 12 месяцев
-- ============================================================

-- Включаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Для полнотекстового поиска

-- ============================================================
-- 1. PROJECTS — Проекты/MVP
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Основная информация
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'idea',
    -- Статусы: idea → research → prototype → launch → monetize → archived
    
    -- Метрики
    pain_id UUID REFERENCES market_pains(id),
    estimated_revenue DECIMAL(12,2) DEFAULT 0,
    actual_revenue DECIMAL(12,2) DEFAULT 0,
    
    -- Технические данные
    tech_stack JSONB DEFAULT '[]',
    repository_url VARCHAR(500),
    deploy_url VARCHAR(500),
    
    -- Геймификация
    xp_earned INTEGER DEFAULT 0,
    quest_level INTEGER DEFAULT 1,
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    launched_at TIMESTAMP WITH TIME ZONE,
    
    -- Индексы
    CONSTRAINT valid_status CHECK (status IN ('idea', 'research', 'prototype', 'launch', 'monetize', 'archived'))
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created ON projects(created_at DESC);

-- ============================================================
-- 2. MARKET_PAINS — Найденные боли рынка
-- ============================================================

CREATE TABLE IF NOT EXISTS market_pains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Описание боли
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    -- Категории: work, education, finance, tech, health, housing, shopping, family
    
    -- Метрики
    frequency INTEGER DEFAULT 1,
    pain_score INTEGER CHECK (pain_score >= 1 AND pain_score <= 10),
    monetization_potential INTEGER CHECK (monetization_potential >= 1 AND monetization_potential <= 10),
    estimated_price_min DECIMAL(10,2),
    estimated_price_max DECIMAL(10,2),
    
    -- Источники
    sources JSONB DEFAULT '[]',
    -- Формат: [{"type": "telegram", "channel": "@name", "count": 10}]
    
    keywords TEXT[],
    examples TEXT[],
    
    -- Связи
    business_idea TEXT,
    project_id UUID REFERENCES projects(id),
    
    -- Временные метки
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Статус
    status VARCHAR(20) DEFAULT 'new',
    -- new → analyzing → validated → converted → rejected
    
    CONSTRAINT valid_category CHECK (category IN ('work', 'education', 'finance', 'tech', 'health', 'housing', 'shopping', 'family', 'other'))
);

CREATE INDEX idx_pains_category ON market_pains(category);
CREATE INDEX idx_pains_score ON market_pains(pain_score DESC);
CREATE INDEX idx_pains_discovered ON market_pains(discovered_at DESC);
CREATE INDEX idx_pains_keywords ON market_pains USING GIN(keywords);

-- ============================================================
-- 3. AGENT_LOGS — Дневник действий агентов
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Агент
    agent_type VARCHAR(50) NOT NULL,
    -- Типы: scout, analyzer, builder, deployer, marketer
    agent_instance VARCHAR(100),
    
    -- Действие
    action VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'started',
    -- started → running → completed → failed
    
    -- Данные
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    
    -- Ресурсы
    duration_ms INTEGER,
    memory_mb INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    
    -- Связи
    project_id UUID REFERENCES projects(id),
    pain_id UUID REFERENCES market_pains(id),
    parent_log_id UUID REFERENCES agent_logs(id),
    
    -- Временные метки
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_status CHECK (status IN ('started', 'running', 'completed', 'failed'))
);

CREATE INDEX idx_logs_agent ON agent_logs(agent_type, started_at DESC);
CREATE INDEX idx_logs_status ON agent_logs(status);
CREATE INDEX idx_logs_project ON agent_logs(project_id);

-- ============================================================
-- 4. FINANCIAL_METRICS — Финансовые метрики
-- ============================================================

CREATE TABLE IF NOT EXISTS financial_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Связь с проектом
    project_id UUID REFERENCES projects(id) NOT NULL,
    
    -- Период
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20) DEFAULT 'daily',
    -- daily, weekly, monthly
    
    -- Доходы
    revenue DECIMAL(12,2) DEFAULT 0,
    transactions_count INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    
    -- Расходы (Cloud)
    cloud_cost DECIMAL(10,4) DEFAULT 0,
    ai_tokens_cost DECIMAL(10,4) DEFAULT 0,
    marketing_cost DECIMAL(10,4) DEFAULT 0,
    
    -- Метрики
    mrr DECIMAL(12,2) DEFAULT 0,  -- Monthly Recurring Revenue
    churn_rate DECIMAL(5,4) DEFAULT 0,
    cac DECIMAL(10,2) DEFAULT 0,  -- Customer Acquisition Cost
    ltv DECIMAL(10,2) DEFAULT 0,  -- Lifetime Value
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(project_id, period_start, period_end)
);

CREATE INDEX idx_metrics_project ON financial_metrics(project_id, period_start DESC);

-- ============================================================
-- 5. DISCOVERED_SOURCES — Автообнаруженные источники
-- ============================================================

CREATE TABLE IF NOT EXISTS discovered_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Источник
    source_type VARCHAR(50) NOT NULL,
    -- telegram, facebook, instagram, youtube, website, rss
    url VARCHAR(1000) NOT NULL UNIQUE,
    name VARCHAR(255),
    
    -- Метрики
    subscribers INTEGER,
    posts_per_day DECIMAL(5,2),
    pain_relevance_score INTEGER CHECK (pain_relevance_score >= 1 AND pain_relevance_score <= 10),
    
    -- Статус
    status VARCHAR(20) DEFAULT 'discovered',
    -- discovered → active → paused → blocked
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    
    -- Временные метки
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by VARCHAR(50) DEFAULT 'auto_discover'
);

CREATE INDEX idx_sources_type ON discovered_sources(source_type);
CREATE INDEX idx_sources_status ON discovered_sources(status);

-- ============================================================
-- TRIGGERS — Автообновление updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_projects_updated
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- VIEWS — Полезные представления
-- ============================================================

-- Топ болей по потенциалу
CREATE OR REPLACE VIEW v_top_pains AS
SELECT 
    mp.id,
    mp.title,
    mp.category,
    mp.frequency,
    mp.pain_score,
    mp.monetization_potential,
    mp.business_idea,
    (mp.pain_score * mp.monetization_potential * mp.frequency / 100.0) AS composite_score
FROM market_pains mp
WHERE mp.status NOT IN ('rejected')
ORDER BY composite_score DESC;

-- Статистика по агентам
CREATE OR REPLACE VIEW v_agent_stats AS
SELECT 
    agent_type,
    DATE(started_at) as date,
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_runs,
    AVG(duration_ms) as avg_duration_ms,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost
FROM agent_logs
GROUP BY agent_type, DATE(started_at)
ORDER BY date DESC, agent_type;

-- Финансовый дашборд
CREATE OR REPLACE VIEW v_financial_dashboard AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.status,
    COALESCE(SUM(fm.revenue), 0) as total_revenue,
    COALESCE(SUM(fm.cloud_cost + fm.ai_tokens_cost + fm.marketing_cost), 0) as total_cost,
    COALESCE(SUM(fm.revenue) - SUM(fm.cloud_cost + fm.ai_tokens_cost + fm.marketing_cost), 0) as profit
FROM projects p
LEFT JOIN financial_metrics fm ON p.id = fm.project_id
GROUP BY p.id, p.name, p.status;

-- ============================================================
-- SEED DATA — Начальные данные
-- ============================================================

-- Вставляем найденные боли из нашего анализа
INSERT INTO market_pains (title, category, frequency, pain_score, monetization_potential, business_idea, estimated_price_min, estimated_price_max)
VALUES 
    ('Поиск удалённой работы', 'work', 136, 8, 9, 'Телеграм-бот для поиска удалённой работы в Узбекистане', 20000, 40000),
    ('Сравнение микрокредитов', 'finance', 41, 7, 8, 'Агрегатор микрокредитов с рейтингом и отзывами', 20000, 40000),
    ('Поиск скидок в Instagram', 'shopping', 18, 6, 7, 'Бот-агрегатор скидок из Instagram-магазинов', 10000, 25000),
    ('Техподдержка приложений', 'tech', 16, 7, 8, 'Сервис техподдержки на узбекском языке', 30000, 50000),
    ('Подготовка к DTM', 'education', 11, 9, 9, 'Платформа подготовки к DTM с AI-репетитором', 30000, 50000)
ON CONFLICT DO NOTHING;

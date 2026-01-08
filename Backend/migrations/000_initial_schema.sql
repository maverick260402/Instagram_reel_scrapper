-- ============================================================================
-- Instagram Reel Scraper - Initial Database Schema
-- ============================================================================
-- Description: Creates all base tables from scratch for fresh deployment
-- Version: 1.0.0
-- Date: 2025-12-28
-- Run this BEFORE 001_multi_user_system.sql on fresh deployments
-- ============================================================================

-- ============================================================================
-- 1. BASE TABLES (No Foreign Key Dependencies)
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Credit system fields
    daily_credit_limit INTEGER DEFAULT 2000 NOT NULL,
    credits_used_today INTEGER DEFAULT 0 NOT NULL,
    last_credit_reset_date DATE DEFAULT CURRENT_DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================================================

-- Instagram Accounts Pool
CREATE TABLE IF NOT EXISTS instagram_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,

    -- Authentication data (from Playwright cookie extraction)
    cookies JSONB,
    cookie_string TEXT,
    x_csrf_token VARCHAR(255),

    -- Status flags
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_paused BOOLEAN DEFAULT FALSE NOT NULL,

    -- Usage tracking
    daily_scrape_count INTEGER DEFAULT 0 NOT NULL,
    last_reset_date DATE DEFAULT CURRENT_DATE NOT NULL,
    total_scrapes INTEGER DEFAULT 0 NOT NULL,
    success_count INTEGER DEFAULT 0 NOT NULL,
    failure_count INTEGER DEFAULT 0 NOT NULL,

    -- Timestamps
    last_used_at TIMESTAMP WITH TIME ZONE,
    cookies_updated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_instagram_accounts_active ON instagram_accounts(is_active, is_paused);
CREATE INDEX IF NOT EXISTS idx_instagram_accounts_daily_count ON instagram_accounts(daily_scrape_count);
CREATE INDEX IF NOT EXISTS idx_instagram_accounts_last_used ON instagram_accounts(last_used_at);

-- ============================================================================

-- API Keys for Cookie Update Authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    permissions JSONB DEFAULT '["update_cookies"]'::jsonb NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- ============================================================================

-- Admin Users (Separate from regular users)
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);

-- ============================================================================
-- 2. TABLES WITH FOREIGN KEYS TO USERS
-- ============================================================================

-- User Groups
CREATE TABLE IF NOT EXISTS user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    usernames TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_used TIMESTAMP WITH TIME ZONE,
    times_used INTEGER DEFAULT 0 NOT NULL,

    CONSTRAINT check_usernames_not_empty CHECK (array_length(usernames, 1) >= 1)
);

CREATE INDEX IF NOT EXISTS idx_user_groups_user_id ON user_groups(user_id);

-- ============================================================================

-- Scraping Jobs
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL,
    usernames TEXT[] NOT NULL,
    reel_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0 NOT NULL,
    credits_consumed INTEGER DEFAULT 0 NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_job_id ON scraping_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_instagram_account_id ON scraping_jobs(instagram_account_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_start_time ON scraping_jobs(start_time);

-- ============================================================================

-- Scraped Reels
CREATE TABLE IF NOT EXISTS scraped_reels (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL REFERENCES scraping_jobs(job_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL,
    instagram_username VARCHAR(100) NOT NULL,
    reel_pk VARCHAR(100) NOT NULL,
    reel_code VARCHAR(50),
    play_count BIGINT DEFAULT 0 NOT NULL,
    comment_count INTEGER DEFAULT 0 NOT NULL,
    like_count BIGINT DEFAULT 0 NOT NULL,
    is_reel_pinned VARCHAR(3),
    reel_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    raw_data JSONB,

    CONSTRAINT check_user_reel_not_null CHECK (user_id IS NOT NULL AND reel_pk IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_reels_user_id ON scraped_reels(user_id);
CREATE INDEX IF NOT EXISTS idx_reels_instagram_account_id ON scraped_reels(instagram_account_id);
CREATE INDEX IF NOT EXISTS idx_reels_instagram_username ON scraped_reels(instagram_username);
CREATE INDEX IF NOT EXISTS idx_reels_play_count ON scraped_reels(play_count);
CREATE INDEX IF NOT EXISTS idx_reels_like_count ON scraped_reels(like_count);
CREATE INDEX IF NOT EXISTS idx_reels_comment_count ON scraped_reels(comment_count);
CREATE INDEX IF NOT EXISTS idx_reels_scraped_at ON scraped_reels(scraped_at);

-- ============================================================================

-- Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL,
    job_id VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_event ON activity_logs(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_instagram_account ON activity_logs(instagram_account_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created ON activity_logs(created_at DESC);

-- ============================================================================
-- 3. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at for instagram_accounts
DROP TRIGGER IF EXISTS trigger_instagram_accounts_updated_at ON instagram_accounts;
CREATE TRIGGER trigger_instagram_accounts_updated_at
    BEFORE UPDATE ON instagram_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at for user_groups
DROP TRIGGER IF EXISTS trigger_user_groups_updated_at ON user_groups;
CREATE TRIGGER trigger_user_groups_updated_at
    BEFORE UPDATE ON user_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. INSERT DEFAULT ADMIN USER
-- ============================================================================

-- Default admin (password: admin123) - CHANGE THIS IN PRODUCTION!
INSERT INTO admin_users (username, email, password_hash)
VALUES (
    'admin',
    'admin@instascraper.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQEhQgkKq'
)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 5. UTILITY VIEWS
-- ============================================================================

-- View: Active Instagram Accounts with Usage Stats
CREATE OR REPLACE VIEW v_instagram_accounts_status AS
SELECT
    ia.id,
    ia.username,
    ia.email,
    ia.is_active,
    ia.is_paused,
    ia.daily_scrape_count,
    ia.total_scrapes,
    ia.success_count,
    ia.failure_count,
    CASE
        WHEN ia.failure_count = 0 THEN 100.0
        ELSE ROUND((ia.success_count::DECIMAL / (ia.success_count + ia.failure_count)) * 100, 2)
    END as success_rate_percent,
    ia.last_used_at,
    ia.cookies_updated_at,
    CASE
        WHEN ia.cookies_updated_at IS NULL THEN 'Never'
        WHEN ia.cookies_updated_at < NOW() - INTERVAL '7 days' THEN 'Stale'
        WHEN ia.cookies_updated_at < NOW() - INTERVAL '5 days' THEN 'Expiring Soon'
        ELSE 'Fresh'
    END as cookie_health,
    ia.created_at
FROM instagram_accounts ia
ORDER BY ia.daily_scrape_count ASC, ia.last_used_at ASC NULLS FIRST;

-- View: User Credit Summary
CREATE OR REPLACE VIEW v_user_credits_summary AS
SELECT
    u.id,
    u.username,
    u.email,
    u.daily_credit_limit,
    u.credits_used_today,
    (u.daily_credit_limit - u.credits_used_today) as credits_remaining,
    ROUND((u.credits_used_today::DECIMAL / NULLIF(u.daily_credit_limit, 0)) * 100, 2) as usage_percent,
    u.last_credit_reset_date,
    CASE
        WHEN u.last_credit_reset_date < CURRENT_DATE THEN true
        ELSE false
    END as needs_reset
FROM users u
ORDER BY u.credits_used_today DESC;

-- View: Daily Activity Summary
CREATE OR REPLACE VIEW v_daily_activity_summary AS
SELECT
    DATE(al.created_at) as activity_date,
    al.event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT al.user_id) as unique_users,
    COUNT(DISTINCT al.instagram_account_id) as unique_instagram_accounts
FROM activity_logs al
WHERE al.created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(al.created_at), al.event_type
ORDER BY activity_date DESC, event_count DESC;

-- ============================================================================
-- 6. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts for authentication and credit tracking';
COMMENT ON TABLE instagram_accounts IS 'Pool of Instagram accounts used for rotating scraping requests';
COMMENT ON TABLE api_keys IS 'API keys for authenticating remote cookie update requests';
COMMENT ON TABLE admin_users IS 'Admin panel user accounts (separate from regular users)';
COMMENT ON TABLE user_groups IS 'User-created groups of Instagram usernames for quick loading';
COMMENT ON TABLE scraping_jobs IS 'Tracks all scraping jobs with status and progress';
COMMENT ON TABLE scraped_reels IS 'Stores scraped Instagram reel metadata';
COMMENT ON TABLE activity_logs IS 'Comprehensive activity and event logging';

COMMENT ON COLUMN users.daily_credit_limit IS 'Maximum reels user can scrape per day';
COMMENT ON COLUMN users.credits_used_today IS 'Number of reels scraped today (resets at midnight IST)';
COMMENT ON COLUMN users.last_credit_reset_date IS 'Last date when credits were reset';

-- ============================================================================
-- 7. VERIFICATION
-- ============================================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND table_name IN (
        'users',
        'instagram_accounts',
        'api_keys',
        'admin_users',
        'user_groups',
        'scraping_jobs',
        'scraped_reels',
        'activity_logs'
    );

    IF table_count = 8 THEN
        RAISE NOTICE '==============================================';
        RAISE NOTICE 'Initial schema created successfully!';
        RAISE NOTICE 'All 8 tables created:';
        RAISE NOTICE '  - users';
        RAISE NOTICE '  - instagram_accounts';
        RAISE NOTICE '  - api_keys';
        RAISE NOTICE '  - admin_users';
        RAISE NOTICE '  - user_groups';
        RAISE NOTICE '  - scraping_jobs';
        RAISE NOTICE '  - scraped_reels';
        RAISE NOTICE '  - activity_logs';
        RAISE NOTICE '==============================================';
        RAISE NOTICE 'Default admin created:';
        RAISE NOTICE '  Username: admin';
        RAISE NOTICE '  Password: admin123';
        RAISE NOTICE '  >>> CHANGE THIS PASSWORD IMMEDIATELY! <<<';
        RAISE NOTICE '==============================================';
    ELSE
        RAISE WARNING 'Schema creation incomplete. Expected 8 tables, found %', table_count;
    END IF;
END $$;

-- ============================================================================
-- Instagram Reel Scraper - Multi-User System Database Migration
-- ============================================================================
-- Description: Adds multi-user support with Instagram account rotation,
--              credit system, admin panel, and activity tracking
-- Version: 1.0.0
-- Date: 2025-12-18
-- ============================================================================

-- ============================================================================
-- 1. CREATE NEW TABLES
-- ============================================================================

-- Instagram Accounts Pool
-- Stores multiple Instagram accounts for rotation
CREATE TABLE IF NOT EXISTS instagram_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,

    -- Authentication data (from Playwright cookie extraction)
    cookies JSONB,                          -- Full cookie object
    cookie_string TEXT,                     -- Formatted for HTTP headers
    x_csrf_token VARCHAR(255),              -- Extracted CSRF token

    -- Status flags
    is_active BOOLEAN DEFAULT TRUE,         -- Can be used for scraping
    is_paused BOOLEAN DEFAULT FALSE,        -- Temporarily disabled

    -- Usage tracking (per Instagram account)
    daily_scrape_count INTEGER DEFAULT 0,   -- Resets daily at midnight
    last_reset_date DATE DEFAULT CURRENT_DATE,
    total_scrapes INTEGER DEFAULT 0,        -- Lifetime counter
    success_count INTEGER DEFAULT 0,        -- Successful scrapes
    failure_count INTEGER DEFAULT 0,        -- Failed scrapes

    -- Timestamps
    last_used_at TIMESTAMP,                 -- Last time used for scraping
    cookies_updated_at TIMESTAMP,           -- Last cookie update
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_instagram_accounts_active
    ON instagram_accounts(is_active, is_paused);
CREATE INDEX idx_instagram_accounts_daily_count
    ON instagram_accounts(daily_scrape_count);
CREATE INDEX idx_instagram_accounts_last_used
    ON instagram_accounts(last_used_at);

-- ============================================================================

-- API Keys for Cookie Update Authentication
-- Allows remote cookie updates from Windows PC
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,   -- Hashed with bcrypt
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSONB DEFAULT '["update_cookies"]'::jsonb,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- ============================================================================

-- Admin Users
-- Separate authentication for admin panel access
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,    -- Bcrypt hashed
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX idx_admin_users_username ON admin_users(username);

-- ============================================================================

-- Activity Logs
-- Comprehensive logging for monitoring and debugging
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    -- Event types: 'scrape_success', 'scrape_failed', 'credit_limit_reached',
    --              'account_rotated', 'cookies_updated', 'admin_action', etc.

    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL,
    job_id VARCHAR(100),

    details JSONB,                          -- Flexible JSON for event-specific data
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_activity_logs_user
    ON activity_logs(user_id, created_at DESC);
CREATE INDEX idx_activity_logs_event
    ON activity_logs(event_type, created_at DESC);
CREATE INDEX idx_activity_logs_instagram_account
    ON activity_logs(instagram_account_id, created_at DESC);
CREATE INDEX idx_activity_logs_created
    ON activity_logs(created_at DESC);

-- ============================================================================
-- 2. ALTER EXISTING TABLES
-- ============================================================================

-- Add credit system fields to users table
DO $$
BEGIN
    -- Add daily_credit_limit column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='daily_credit_limit'
    ) THEN
        ALTER TABLE users ADD COLUMN daily_credit_limit INTEGER DEFAULT 2000;
    END IF;

    -- Add credits_used_today column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='credits_used_today'
    ) THEN
        ALTER TABLE users ADD COLUMN credits_used_today INTEGER DEFAULT 0;
    END IF;

    -- Add last_credit_reset_date column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='users' AND column_name='last_credit_reset_date'
    ) THEN
        ALTER TABLE users ADD COLUMN last_credit_reset_date DATE DEFAULT CURRENT_DATE;
    END IF;
END $$;

-- ============================================================================

-- Add Instagram account tracking to scraping_jobs table
DO $$
BEGIN
    -- Add instagram_account_id foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='scraping_jobs' AND column_name='instagram_account_id'
    ) THEN
        ALTER TABLE scraping_jobs
        ADD COLUMN instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL;
    END IF;

    -- Add credits_consumed column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='scraping_jobs' AND column_name='credits_consumed'
    ) THEN
        ALTER TABLE scraping_jobs ADD COLUMN credits_consumed INTEGER DEFAULT 0;
    END IF;
END $$;

-- Create index for job queries by Instagram account
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_instagram_account
    ON scraping_jobs(instagram_account_id);

-- ============================================================================

-- Add Instagram account tracking to scraped_reels table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='scraped_reels' AND column_name='instagram_account_id'
    ) THEN
        ALTER TABLE scraped_reels
        ADD COLUMN instagram_account_id INTEGER REFERENCES instagram_accounts(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Create index for reel queries by Instagram account
CREATE INDEX IF NOT EXISTS idx_scraped_reels_instagram_account
    ON scraped_reels(instagram_account_id);

-- ============================================================================
-- 3. INSERT SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert a default admin user (password: admin123)
-- Note: This should be changed in production!
INSERT INTO admin_users (username, email, password_hash)
VALUES (
    'admin',
    'admin@instascraper.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQEhQgkKq'  -- bcrypt hash of 'admin123'
)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 4. UTILITY VIEWS (Optional)
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

-- ============================================================================

-- View: User Credit Summary
CREATE OR REPLACE VIEW v_user_credits_summary AS
SELECT
    u.id,
    u.username,
    u.email,
    u.daily_credit_limit,
    u.credits_used_today,
    (u.daily_credit_limit - u.credits_used_today) as credits_remaining,
    ROUND((u.credits_used_today::DECIMAL / u.daily_credit_limit) * 100, 2) as usage_percent,
    u.last_credit_reset_date,
    CASE
        WHEN u.last_credit_reset_date < CURRENT_DATE THEN true
        ELSE false
    END as needs_reset
FROM users u
ORDER BY u.credits_used_today DESC;

-- ============================================================================

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
-- 5. FUNCTIONS & TRIGGERS
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

-- ============================================================================
-- 6. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE instagram_accounts IS 'Pool of Instagram accounts used for rotating scraping requests';
COMMENT ON TABLE api_keys IS 'API keys for authenticating remote cookie update requests';
COMMENT ON TABLE admin_users IS 'Admin panel user accounts (separate from regular users)';
COMMENT ON TABLE activity_logs IS 'Comprehensive activity and event logging';

COMMENT ON COLUMN users.daily_credit_limit IS 'Maximum reels user can scrape per day (configurable by admin)';
COMMENT ON COLUMN users.credits_used_today IS 'Number of reels scraped today (resets at midnight)';
COMMENT ON COLUMN users.last_credit_reset_date IS 'Last date when credits were reset';

COMMENT ON COLUMN scraping_jobs.instagram_account_id IS 'Which Instagram account was used for this job';
COMMENT ON COLUMN scraping_jobs.credits_consumed IS 'Total credits consumed by this job';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify migration
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name IN ('instagram_accounts', 'api_keys', 'admin_users', 'activity_logs');

    IF table_count = 4 THEN
        RAISE NOTICE 'Migration completed successfully! All 4 new tables created.';
    ELSE
        RAISE WARNING 'Migration incomplete. Expected 4 tables, found %', table_count;
    END IF;
END $$;

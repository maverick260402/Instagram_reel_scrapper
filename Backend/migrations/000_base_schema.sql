-- ============================================================
-- BASE SCHEMA - Foundation Tables
-- ============================================================
-- This migration creates the core database schema
-- Run this BEFORE 001_multi_user_system.sql
--
-- Tables created:
--   - users (core user authentication)
--   - user_groups (Instagram username grouping)
--   - scraping_jobs (job tracking)
--   - scraped_reels (reel data)
--   - activity_logs (system logging)
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    -- Credit system fields (for Phase 1)
    daily_credit_limit INTEGER DEFAULT 2000 NOT NULL,
    credits_used_today INTEGER DEFAULT 0 NOT NULL,
    last_credit_reset_date DATE DEFAULT CURRENT_DATE NOT NULL
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

COMMENT ON TABLE users IS 'User accounts with authentication and credit system';
COMMENT ON COLUMN users.daily_credit_limit IS '1 credit = 1 reel scraped. Default: 2000 reels/day';
COMMENT ON COLUMN users.credits_used_today IS 'Credits consumed today. Resets daily at midnight';

-- ============================================================
-- 2. USER GROUPS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    usernames TEXT[] NOT NULL,  -- Array of Instagram usernames
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_used TIMESTAMP WITH TIME ZONE,
    times_used INTEGER DEFAULT 0 NOT NULL,

    -- Constraints
    CONSTRAINT check_usernames_not_empty CHECK (array_length(usernames, 1) >= 1)
);

-- Indexes for user_groups table
CREATE INDEX IF NOT EXISTS idx_user_groups_user_id ON user_groups(user_id);

COMMENT ON TABLE user_groups IS 'User-created groups for organizing Instagram usernames';

-- ============================================================
-- 3. SCRAPING JOBS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS scraping_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instagram_account_id INTEGER,  -- Added in Phase 1, will link later
    usernames TEXT[] NOT NULL,  -- Instagram usernames being scraped
    reel_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,  -- running, completed, failed
    progress FLOAT DEFAULT 0 NOT NULL,
    credits_consumed INTEGER DEFAULT 0 NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,  -- Duration in seconds
    error_message TEXT
);

-- Indexes for scraping_jobs table
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON scraping_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_start_time ON scraping_jobs(start_time);

COMMENT ON TABLE scraping_jobs IS 'Tracks scraping job execution and status';
COMMENT ON COLUMN scraping_jobs.credits_consumed IS 'Number of credits consumed by this job';

-- ============================================================
-- 4. SCRAPED REELS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS scraped_reels (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL REFERENCES scraping_jobs(job_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instagram_account_id INTEGER,  -- Added in Phase 1, will link later
    instagram_username VARCHAR(100) NOT NULL,
    reel_pk VARCHAR(100) NOT NULL,  -- Instagram reel primary key
    reel_code VARCHAR(50),  -- Short code
    play_count BIGINT DEFAULT 0 NOT NULL,
    comment_count INTEGER DEFAULT 0 NOT NULL,
    like_count BIGINT DEFAULT 0 NOT NULL,
    is_reel_pinned VARCHAR(3),  -- "Yes" or "No"
    reel_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    raw_data JSONB,  -- Store full Instagram API response

    -- Constraints
    CONSTRAINT check_user_reel_not_null CHECK (user_id IS NOT NULL AND reel_pk IS NOT NULL)
);

-- Indexes for scraped_reels table (analytics queries)
CREATE INDEX IF NOT EXISTS idx_reels_job_id ON scraped_reels(job_id);
CREATE INDEX IF NOT EXISTS idx_reels_user_id ON scraped_reels(user_id);
CREATE INDEX IF NOT EXISTS idx_reels_instagram_username ON scraped_reels(instagram_username);
CREATE INDEX IF NOT EXISTS idx_reels_play_count ON scraped_reels(play_count);
CREATE INDEX IF NOT EXISTS idx_reels_like_count ON scraped_reels(like_count);
CREATE INDEX IF NOT EXISTS idx_reels_comment_count ON scraped_reels(comment_count);
CREATE INDEX IF NOT EXISTS idx_reels_scraped_at ON scraped_reels(scraped_at);

COMMENT ON TABLE scraped_reels IS 'Instagram reel metadata scraped from various accounts';
COMMENT ON COLUMN scraped_reels.raw_data IS 'Full JSON response from Instagram API';

-- ============================================================
-- 5. ACTIVITY LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    instagram_account_id INTEGER,  -- Will link to instagram_accounts in Phase 1
    job_id VARCHAR(100),
    details JSONB,  -- Flexible JSON for event-specific data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for activity_logs table
CREATE INDEX IF NOT EXISTS idx_activity_logs_event_type ON activity_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_event ON activity_logs(event_type, created_at);

COMMENT ON TABLE activity_logs IS 'System-wide event and activity logging';
COMMENT ON COLUMN activity_logs.event_type IS 'Event types: scrape_success, scrape_failed, credit_limit_reached, account_rotated, cookies_updated, admin_action, etc.';

-- ============================================================
-- 6. UTILITY FUNCTIONS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user_groups
DROP TRIGGER IF EXISTS trigger_user_groups_updated_at ON user_groups;
CREATE TRIGGER trigger_user_groups_updated_at
    BEFORE UPDATE ON user_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 7. VERIFICATION
-- ============================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    -- Count base tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('users', 'user_groups', 'scraping_jobs', 'scraped_reels', 'activity_logs');

    IF table_count = 5 THEN
        RAISE NOTICE '[OK] Base schema created successfully. 5/5 tables exist.';
    ELSE
        RAISE WARNING 'Base schema incomplete. Expected 5 tables, found %.', table_count;
    END IF;
END $$;

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
-- Next step: Run 001_multi_user_system.sql to add Phase 1 features
-- ============================================================

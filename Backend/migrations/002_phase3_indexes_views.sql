-- Phase 3 Database Optimizations: Indexes and Views
-- Run this migration after Phase 1 and Phase 2 are complete
-- Date: December 18, 2025

-- ==================== INDEXES FOR PERFORMANCE ====================

-- Activity logs indexes (for faster filtering and sorting)
CREATE INDEX IF NOT EXISTS idx_activity_logs_event_type
ON activity_logs(event_type);

CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at
ON activity_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id
ON activity_logs(user_id)
WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_activity_logs_instagram_account_id
ON activity_logs(instagram_account_id)
WHERE instagram_account_id IS NOT NULL;

-- Scraped reels indexes (for faster time-based queries)
CREATE INDEX IF NOT EXISTS idx_scraped_reels_scraped_at
ON scraped_reels(scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_scraped_reels_user_id_scraped_at
ON scraped_reels(user_id, scraped_at DESC);

-- Scraping jobs indexes (for faster status queries)
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status
ON scraping_jobs(status);

CREATE INDEX IF NOT EXISTS idx_jobs_created_at
ON scraping_jobs(start_time DESC);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_user_id
ON scraping_jobs(user_id);

-- Users indexes (for faster active user queries)
CREATE INDEX IF NOT EXISTS idx_users_is_active
ON users(is_active);

-- Instagram accounts indexes (for faster rotation queries)
CREATE INDEX IF NOT EXISTS idx_instagram_accounts_active_paused
ON instagram_accounts(is_active, is_paused, daily_scrape_count);

-- ==================== DATABASE VIEWS ====================

-- View: Daily Statistics
-- Aggregates daily scraping metrics
CREATE OR REPLACE VIEW v_daily_stats AS
SELECT
    DATE(scraped_at) as date,
    COUNT(*) as total_reels,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT instagram_account_id) as accounts_used,
    AVG(play_count) as avg_plays,
    AVG(like_count) as avg_likes,
    AVG(comment_count) as avg_comments
FROM scraped_reels
GROUP BY DATE(scraped_at)
ORDER BY DATE(scraped_at) DESC;

-- View: User Summary
-- Shows user statistics with credit usage
CREATE OR REPLACE VIEW v_user_summary AS
SELECT
    u.id,
    u.email,
    u.username,
    u.daily_credit_limit,
    u.credits_used_today,
    (u.daily_credit_limit - u.credits_used_today) as credits_remaining,
    ROUND((u.credits_used_today::numeric / NULLIF(u.daily_credit_limit, 0)) * 100, 1) as usage_percent,
    u.is_active,
    COUNT(DISTINCT sj.id) as total_jobs,
    COUNT(DISTINCT CASE WHEN sj.status = 'completed' THEN sj.id END) as successful_jobs,
    COUNT(DISTINCT sr.id) as total_reels_scraped,
    MAX(sj.start_time) as last_job_date
FROM users u
LEFT JOIN scraping_jobs sj ON u.id = sj.user_id
LEFT JOIN scraped_reels sr ON u.id = sr.user_id
GROUP BY u.id, u.email, u.username, u.daily_credit_limit, u.credits_used_today, u.is_active;

-- View: Instagram Account Health
-- Shows account status and cookie health
CREATE OR REPLACE VIEW v_instagram_account_health AS
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
        WHEN (ia.success_count + ia.failure_count) > 0 THEN
            ROUND((ia.success_count::numeric / (ia.success_count + ia.failure_count)) * 100, 1)
        ELSE 0
    END as success_rate,
    ia.cookies_updated_at,
    CASE
        WHEN ia.cookies_updated_at IS NULL THEN 'NO_COOKIES'
        WHEN ia.cookies_updated_at < (NOW() - INTERVAL '7 days') THEN 'EXPIRED'
        WHEN ia.cookies_updated_at < (NOW() - INTERVAL '5 days') THEN 'EXPIRING_SOON'
        ELSE 'HEALTHY'
    END as cookie_health,
    EXTRACT(DAY FROM (NOW() - ia.cookies_updated_at)) as cookie_age_days,
    ia.last_used_at
FROM instagram_accounts ia;

-- View: Recent Activity
-- Shows recent system activity with details
CREATE OR REPLACE VIEW v_recent_activity AS
SELECT
    al.id,
    al.event_type,
    al.created_at,
    u.username as user_username,
    u.email as user_email,
    ia.username as instagram_account_username,
    sj.job_id,
    al.details
FROM activity_logs al
LEFT JOIN users u ON al.user_id = u.id
LEFT JOIN instagram_accounts ia ON al.instagram_account_id = ia.id
LEFT JOIN scraping_jobs sj ON al.job_id = sj.job_id
ORDER BY al.created_at DESC;

-- View: Job Performance
-- Aggregates job performance metrics
CREATE OR REPLACE VIEW v_job_performance AS
SELECT
    sj.job_id,
    sj.user_id,
    u.username,
    sj.status,
    sj.usernames,
    sj.reel_count,
    sj.credits_consumed,
    sj.instagram_account_id,
    ia.username as instagram_account_username,
    sj.start_time,
    sj.end_time,
    EXTRACT(EPOCH FROM (sj.end_time - sj.start_time)) as duration_seconds
FROM scraping_jobs sj
LEFT JOIN users u ON sj.user_id = u.id
LEFT JOIN instagram_accounts ia ON sj.instagram_account_id = ia.id
WHERE sj.end_time IS NOT NULL;

-- View: Hourly Usage Pattern
-- Shows usage patterns by hour for optimization
CREATE OR REPLACE VIEW v_hourly_usage_pattern AS
SELECT
    EXTRACT(HOUR FROM scraped_at) as hour_of_day,
    COUNT(*) as total_reels,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(play_count) as avg_plays
FROM scraped_reels
WHERE scraped_at >= (NOW() - INTERVAL '30 days')
GROUP BY EXTRACT(HOUR FROM scraped_at)
ORDER BY hour_of_day;

-- ==================== GRANT PERMISSIONS ====================

-- Grant SELECT on all views to the scraper_user
GRANT SELECT ON v_daily_stats TO scraper_user;
GRANT SELECT ON v_user_summary TO scraper_user;
GRANT SELECT ON v_instagram_account_health TO scraper_user;
GRANT SELECT ON v_recent_activity TO scraper_user;
GRANT SELECT ON v_job_performance TO scraper_user;
GRANT SELECT ON v_hourly_usage_pattern TO scraper_user;

-- ==================== VERIFICATION ====================

-- Verify indexes were created
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE tablename IN ('activity_logs', 'scraped_reels', 'scraping_jobs', 'users', 'instagram_accounts')
ORDER BY tablename, indexname;

-- Verify views were created
SELECT
    viewname
FROM pg_views
WHERE schemaname = 'public'
    AND viewname LIKE 'v_%'
ORDER BY viewname;

-- Test views
SELECT 'v_daily_stats' as view_name, COUNT(*) as row_count FROM v_daily_stats
UNION ALL
SELECT 'v_user_summary', COUNT(*) FROM v_user_summary
UNION ALL
SELECT 'v_instagram_account_health', COUNT(*) FROM v_instagram_account_health
UNION ALL
SELECT 'v_recent_activity', COUNT(*) FROM v_recent_activity
UNION ALL
SELECT 'v_job_performance', COUNT(*) FROM v_job_performance
UNION ALL
SELECT 'v_hourly_usage_pattern', COUNT(*) FROM v_hourly_usage_pattern;

-- ==================== NOTES ====================

/*
PERFORMANCE IMPACT:
- Indexes will speed up filtering and sorting operations by 10-100x
- Views provide precomputed complex queries
- Cookie health view helps identify accounts needing refresh

MAINTENANCE:
- Indexes are automatically updated on INSERT/UPDATE/DELETE
- Views are virtual (no storage cost, computed on query)
- Run VACUUM ANALYZE periodically for optimal performance

USAGE EXAMPLES:

-- Get daily statistics for last 7 days
SELECT * FROM v_daily_stats LIMIT 7;

-- Find users with high credit usage
SELECT * FROM v_user_summary
WHERE usage_percent > 80
ORDER BY usage_percent DESC;

-- Check Instagram account cookie health
SELECT * FROM v_instagram_account_health
WHERE cookie_health != 'HEALTHY';

-- View recent system activity
SELECT * FROM v_recent_activity LIMIT 50;

-- Analyze job performance
SELECT
    username,
    AVG(duration_seconds) as avg_duration,
    AVG(reels_scraped) as avg_reels
FROM v_job_performance
WHERE status = 'completed'
GROUP BY username;

-- Find peak usage hours
SELECT * FROM v_hourly_usage_pattern
ORDER BY total_reels DESC
LIMIT 5;
*/

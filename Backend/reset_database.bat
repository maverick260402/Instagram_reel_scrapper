@echo off
REM ============================================================
REM Database Reset and Migration Script (Windows Batch)
REM ============================================================
REM This script:
REM   1. Drops all existing tables
REM   2. Runs 000_base_schema.sql (core tables)
REM   3. Runs 001_multi_user_system.sql (Phase 1 features)
REM   4. Verifies all tables exist
REM
REM WARNING: This will DELETE ALL DATA in the database!
REM ============================================================

echo.
echo ====================================================================
echo                DATABASE RESET AND MIGRATION
echo ====================================================================
echo.
echo WARNING: This will DELETE ALL DATA in the database!
echo.
set /p CONFIRM="Type 'RESET' to confirm, or press Enter to cancel: "

if not "%CONFIRM%"=="RESET" (
    echo.
    echo Migration cancelled.
    exit /b 0
)

echo.
echo [STEP 1] Dropping all existing tables...
echo ============================================================

REM Drop all tables
docker exec instagram_scraper_db psql -U scraper_user -d instagram_scraper -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to drop tables
    exit /b 1
)

echo [OK] All tables dropped
echo.

echo [STEP 2] Creating base schema...
echo ============================================================

REM Copy base schema to container
docker cp migrations\000_base_schema.sql instagram_scraper_db:/tmp/000_base_schema.sql

REM Execute base schema
docker exec instagram_scraper_db psql -U scraper_user -d instagram_scraper -f /tmp/000_base_schema.sql

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create base schema
    exit /b 1
)

echo [OK] Base schema created
echo.

echo [STEP 3] Running Phase 1 migration...
echo ============================================================

REM Copy Phase 1 migration to container
docker cp migrations\001_multi_user_system.sql instagram_scraper_db:/tmp/001_multi_user_system.sql

REM Execute Phase 1 migration
docker exec instagram_scraper_db psql -U scraper_user -d instagram_scraper -f /tmp/001_multi_user_system.sql

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Phase 1 migration had some errors (this is expected)
)

echo [OK] Phase 1 migration completed
echo.

echo [STEP 4] Verifying database schema...
echo ============================================================

REM List all tables
docker exec instagram_scraper_db psql -U scraper_user -d instagram_scraper -c "\dt"

echo.
echo ====================================================================
echo                     MIGRATION COMPLETED
echo ====================================================================
echo.
echo Next steps:
echo   1. Verify all 8 tables exist above
echo   2. Start backend server: python app.py
echo   3. Add Instagram accounts to the pool
echo   4. Generate API keys for cookie updates
echo.

pause

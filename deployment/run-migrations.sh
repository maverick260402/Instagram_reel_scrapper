#!/bin/bash

################################################################################
# Instagram Reel Scraper - Database Migration Runner
#
# This script manages database migrations, tracking which migrations have
# been applied and running pending migrations in order.
#
# Usage:
#   ./run-migrations.sh
#
# Prerequisites:
#   - PostgreSQL running (Docker container)
#   - Database connection details in .env file
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/instagram-scraper"
MIGRATION_DIR="${APP_DIR}/Backend/migrations"
STATE_FILE="${APP_DIR}/.migration_state"

# Load database connection from .env
if [ -f "${APP_DIR}/.env" ]; then
    source <(grep DATABASE_URL ${APP_DIR}/.env | sed 's/ *= */=/g')
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

# Extract database connection details from DATABASE_URL
# Format: postgresql://user:password@host:port/database
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    PGUSER="${BASH_REMATCH[1]}"
    PGPASSWORD="${BASH_REMATCH[2]}"
    PGHOST="${BASH_REMATCH[3]}"
    PGPORT="${BASH_REMATCH[4]}"
    PGDATABASE="${BASH_REMATCH[5]}"
else
    echo -e "${RED}✗ Invalid DATABASE_URL format${NC}"
    exit 1
fi

export PGUSER PGPASSWORD PGHOST PGPORT PGDATABASE

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}=================================="
    echo -e "$1"
    echo -e "==================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Migration Functions
################################################################################

check_database_connection() {
    print_header "Checking Database Connection"

    if pg_isready -h ${PGHOST} -p ${PGPORT} -U ${PGUSER} > /dev/null 2>&1; then
        print_success "Database is ready"
    else
        print_error "Cannot connect to database"
        print_info "Make sure PostgreSQL container is running"
        exit 1
    fi
}

get_applied_migrations() {
    # Read state file if it exists
    if [ -f "${STATE_FILE}" ]; then
        cat ${STATE_FILE}
    else
        echo ""
    fi
}

is_migration_applied() {
    local migration_file=$1
    local applied_migrations=$(get_applied_migrations)

    if echo "${applied_migrations}" | grep -q "^${migration_file}$"; then
        return 0  # Migration already applied
    else
        return 1  # Migration not applied
    fi
}

mark_migration_applied() {
    local migration_file=$1
    echo "${migration_file}" >> ${STATE_FILE}
    print_success "Marked ${migration_file} as applied"
}

run_migration() {
    local migration_path=$1
    local migration_name=$(basename ${migration_path})

    print_info "Running migration: ${migration_name}"

    # Execute migration
    if psql -h ${PGHOST} -p ${PGPORT} -U ${PGUSER} -d ${PGDATABASE} -f ${migration_path} > /dev/null 2>&1; then
        print_success "${migration_name} completed successfully"
        mark_migration_applied ${migration_name}
        return 0
    else
        print_error "${migration_name} failed"
        print_info "Check database logs for details"
        return 1
    fi
}

run_all_migrations() {
    print_header "Running Database Migrations"

    # Check if migration directory exists
    if [ ! -d "${MIGRATION_DIR}" ]; then
        print_error "Migration directory not found: ${MIGRATION_DIR}"
        exit 1
    fi

    # Find all SQL migration files (sorted)
    local migration_files=$(find ${MIGRATION_DIR} -name "*.sql" -type f | sort)

    if [ -z "$migration_files" ]; then
        print_warning "No migration files found"
        return 0
    fi

    # Count migrations
    local total_migrations=$(echo "$migration_files" | wc -l)
    local applied_count=0
    local skipped_count=0
    local failed_count=0

    print_info "Found ${total_migrations} migration file(s)"
    echo ""

    # Run each migration
    while IFS= read -r migration_path; do
        local migration_name=$(basename ${migration_path})

        if is_migration_applied ${migration_name}; then
            print_warning "Skipped ${migration_name} (already applied)"
            skipped_count=$((skipped_count + 1))
        else
            if run_migration ${migration_path}; then
                applied_count=$((applied_count + 1))
            else
                failed_count=$((failed_count + 1))
                # Stop on first failure
                break
            fi
        fi
    done <<< "$migration_files"

    # Show summary
    echo ""
    print_header "Migration Summary"
    echo "Total migrations: ${total_migrations}"
    echo "Applied: ${applied_count}"
    echo "Skipped: ${skipped_count}"
    echo "Failed: ${failed_count}"
    echo ""

    if [ ${failed_count} -gt 0 ]; then
        print_error "Some migrations failed"
        return 1
    else
        print_success "All migrations completed successfully"
        return 0
    fi
}

show_migration_status() {
    print_header "Migration Status"

    local migration_files=$(find ${MIGRATION_DIR} -name "*.sql" -type f | sort)
    local applied_migrations=$(get_applied_migrations)

    echo "Migration files:"
    while IFS= read -r migration_path; do
        local migration_name=$(basename ${migration_path})

        if is_migration_applied ${migration_name}; then
            echo -e "  ${GREEN}✓${NC} ${migration_name}"
        else
            echo -e "  ${YELLOW}○${NC} ${migration_name} (pending)"
        fi
    done <<< "$migration_files"
    echo ""
}

reset_migration_state() {
    print_header "Resetting Migration State"

    read -p "This will mark all migrations as not applied. Continue? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f ${STATE_FILE}
        print_success "Migration state reset"
    else
        print_info "Reset cancelled"
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse command line arguments
    case "${1:-run}" in
        run)
            check_database_connection
            run_all_migrations
            ;;
        status)
            show_migration_status
            ;;
        reset)
            reset_migration_state
            ;;
        *)
            echo "Usage: $0 {run|status|reset}"
            echo ""
            echo "Commands:"
            echo "  run    - Run pending migrations (default)"
            echo "  status - Show migration status"
            echo "  reset  - Reset migration state"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

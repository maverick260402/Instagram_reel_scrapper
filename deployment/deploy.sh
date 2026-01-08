#!/bin/bash

################################################################################
# Instagram Reel Scraper - Deployment Script
#
# This script is executed by GitHub Actions to deploy the application
# to the VPS server. It can also be run manually for testing.
#
# Usage:
#   ./deploy.sh
#
# Prerequisites:
#   - Server setup completed (setup-server.sh)
#   - .env file exists with production values
#   - Git repository cloned
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
BACKUP_DIR="${APP_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

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
# Pre-deployment Checks
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check if app directory exists
    if [ ! -d "${APP_DIR}" ]; then
        print_error "Application directory ${APP_DIR} not found"
        print_info "Run setup-server.sh first"
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f "${APP_DIR}/.env" ]; then
        print_error ".env file not found"
        print_info "Create .env file with production configuration"
        exit 1
    fi

    # Check if venv exists
    if [ ! -d "${APP_DIR}/venv" ]; then
        print_error "Python virtual environment not found"
        print_info "Run setup-server.sh first"
        exit 1
    fi

    print_success "All prerequisites met"
}

################################################################################
# Backup Functions
################################################################################

create_backup() {
    print_header "Creating Backup"

    # Create backup directory
    mkdir -p ${BACKUP_DIR}

    # Backup current code
    if [ -d "${APP_DIR}/Backend" ]; then
        tar -czf ${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz \
            -C ${APP_DIR} \
            Backend Frontend deployment \
            2>/dev/null || true
        print_success "Backup created: backup_${TIMESTAMP}.tar.gz"
    else
        print_warning "No existing code to backup"
    fi

    # Keep only last 5 backups
    cd ${BACKUP_DIR}
    ls -t backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    print_info "Keeping last 5 backups"
}

################################################################################
# Deployment Functions
################################################################################

pull_latest_code() {
    print_header "Pulling Latest Code"

    cd ${APP_DIR}

    # Get current commit hash
    OLD_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")

    # Pull latest code
    git fetch origin main
    git reset --hard origin/main

    # Get new commit hash
    NEW_COMMIT=$(git rev-parse HEAD)

    if [ "$OLD_COMMIT" = "$NEW_COMMIT" ]; then
        print_warning "No new changes to deploy"
    else
        print_success "Updated from ${OLD_COMMIT:0:7} to ${NEW_COMMIT:0:7}"
    fi

    # Set correct permissions
    chown -R instagram-scraper:instagram-scraper ${APP_DIR}
}

install_dependencies() {
    print_header "Installing Dependencies"

    cd ${APP_DIR}

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip --quiet

    # Install/update requirements
    if [ -f "Backend/requirements.txt" ]; then
        pip install -r Backend/requirements.txt --quiet
        print_success "Dependencies installed"
    else
        print_error "Backend/requirements.txt not found"
        exit 1
    fi
}

run_migrations() {
    print_header "Running Database Migrations"

    cd ${APP_DIR}/deployment

    # Check if migration script exists
    if [ -f "run-migrations.sh" ]; then
        chmod +x run-migrations.sh
        ./run-migrations.sh
        print_success "Database migrations completed"
    else
        print_warning "Migration script not found - skipping"
    fi
}

restart_application() {
    print_header "Restarting Application"

    # Stop service
    print_info "Stopping service..."
    sudo systemctl stop instagram-scraper || true

    # Wait a moment
    sleep 2

    # Start service
    print_info "Starting service..."
    sudo systemctl start instagram-scraper

    # Check if started successfully
    sleep 3
    if sudo systemctl is-active --quiet instagram-scraper; then
        print_success "Service started successfully"
    else
        print_error "Service failed to start"
        print_info "Check logs: sudo journalctl -u instagram-scraper -n 50"
        exit 1
    fi
}

perform_health_check() {
    print_header "Performing Health Check"

    # Wait for app to fully start
    print_info "Waiting for application to start..."
    sleep 10

    # Check health endpoint
    MAX_RETRIES=5
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f -s http://localhost:8080/docs > /dev/null 2>&1; then
            print_success "Health check passed!"
            print_success "Application is running at http://localhost:8080"
            return 0
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                print_warning "Health check attempt $RETRY_COUNT failed, retrying..."
                sleep 5
            fi
        fi
    done

    print_error "Health check failed after $MAX_RETRIES attempts"
    print_info "Rolling back to previous version..."
    rollback
    exit 1
}

################################################################################
# Rollback Function
################################################################################

rollback() {
    print_header "Rolling Back Deployment"

    # Find most recent backup
    LATEST_BACKUP=$(ls -t ${BACKUP_DIR}/backup_*.tar.gz 2>/dev/null | head -n 1)

    if [ -z "$LATEST_BACKUP" ]; then
        print_error "No backup found to rollback to"
        return 1
    fi

    print_info "Restoring from backup: $(basename $LATEST_BACKUP)"

    # Stop service
    sudo systemctl stop instagram-scraper || true

    # Restore backup
    cd ${APP_DIR}
    tar -xzf ${LATEST_BACKUP} -C ${APP_DIR}

    # Restart service
    sudo systemctl start instagram-scraper

    print_success "Rollback completed"
}

################################################################################
# Post-deployment Tasks
################################################################################

cleanup() {
    print_header "Cleaning Up"

    # Remove old log files (keep last 30 days)
    find ${APP_DIR}/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true

    # Remove __pycache__ directories
    find ${APP_DIR}/Backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

    # Remove .pyc files
    find ${APP_DIR}/Backend -type f -name "*.pyc" -delete 2>/dev/null || true

    print_success "Cleanup completed"
}

show_deployment_info() {
    print_header "Deployment Summary"

    echo -e "${GREEN}Deployment completed successfully!${NC}\n"

    echo "Current Status:"
    echo "  - Service: $(sudo systemctl is-active instagram-scraper)"
    echo "  - Commit: $(cd ${APP_DIR} && git rev-parse --short HEAD)"
    echo "  - Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    echo "Useful Commands:"
    echo "  - Check status: sudo systemctl status instagram-scraper"
    echo "  - View logs: sudo journalctl -u instagram-scraper -f"
    echo "  - Restart: sudo systemctl restart instagram-scraper"
    echo "  - Application: http://localhost:8080"
    echo "  - API docs: http://localhost:8080/docs"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "Instagram Reel Scraper - Deployment"

    print_info "Starting deployment at $(date '+%Y-%m-%d %H:%M:%S')"
    print_info "Target directory: ${APP_DIR}"
    echo ""

    # Execute deployment steps
    check_prerequisites
    create_backup
    pull_latest_code
    install_dependencies
    run_migrations
    restart_application
    perform_health_check
    cleanup
    show_deployment_info

    print_header "Deployment Complete!"
}

# Handle errors
trap 'print_error "Deployment failed at line $LINENO"' ERR

# Run main function
main

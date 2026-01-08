#!/bin/bash

################################################################################
# Instagram Reel Scraper - VPS Server Setup Script
#
# This script performs one-time initialization of a VPS server for hosting
# the Instagram Reel Scraper application.
#
# Usage:
#   sudo bash setup-server.sh
#
# Prerequisites:
#   - Ubuntu 20.04+ or Debian 11+ server
#   - Root or sudo access
#   - Internet connection
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="instagram-scraper"
APP_DIR="/opt/instagram-scraper"
PYTHON_VERSION="3.11"
POSTGRES_VERSION="15"

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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

################################################################################
# Main Setup Functions
################################################################################

update_system() {
    print_header "Updating System Packages"
    apt-get update -y
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        ufw \
        software-properties-common \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        postgresql-client
    print_success "System packages updated"
}

install_python() {
    print_header "Installing Python ${PYTHON_VERSION}"

    # Add deadsnakes PPA for latest Python
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update -y

    # Install Python and pip
    apt-get install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev \
        python3-pip

    # Set as default python3
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

    # Verify installation
    python3 --version
    print_success "Python ${PYTHON_VERSION} installed"
}

install_docker() {
    print_header "Installing Docker and Docker Compose"

    # Remove old Docker versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh

    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Start Docker service
    systemctl start docker
    systemctl enable docker

    # Verify installation
    docker --version
    docker-compose --version
    print_success "Docker and Docker Compose installed"
}

create_app_user() {
    print_header "Creating Application User"

    # Create user if doesn't exist
    if id "${APP_USER}" &>/dev/null; then
        print_warning "User ${APP_USER} already exists"
    else
        useradd -r -m -s /bin/bash ${APP_USER}
        print_success "User ${APP_USER} created"
    fi

    # Add user to docker group
    usermod -aG docker ${APP_USER}
    print_success "User ${APP_USER} added to docker group"
}

setup_directory_structure() {
    print_header "Setting Up Directory Structure"

    # Create application directory
    mkdir -p ${APP_DIR}
    mkdir -p ${APP_DIR}/Backend
    mkdir -p ${APP_DIR}/Frontend
    mkdir -p ${APP_DIR}/deployment
    mkdir -p ${APP_DIR}/logs

    # Set ownership
    chown -R ${APP_USER}:${APP_USER} ${APP_DIR}

    print_success "Directory structure created at ${APP_DIR}"
}

clone_repository() {
    print_header "Cloning Repository"

    # Prompt for repository URL
    read -p "Enter GitHub repository URL (or press Enter to skip): " REPO_URL

    if [ -z "$REPO_URL" ]; then
        print_warning "Repository cloning skipped - you'll need to clone manually"
        return
    fi

    # Clone as app user
    su - ${APP_USER} -c "cd /opt && git clone ${REPO_URL} instagram-scraper || true"
    print_success "Repository cloned"
}

setup_python_venv() {
    print_header "Setting Up Python Virtual Environment"

    # Create virtual environment as app user
    su - ${APP_USER} -c "cd ${APP_DIR} && python3 -m venv venv"

    # Upgrade pip
    su - ${APP_USER} -c "cd ${APP_DIR} && source venv/bin/activate && pip install --upgrade pip"

    print_success "Python virtual environment created"
}

setup_postgresql() {
    print_header "Setting Up PostgreSQL Docker Container"

    # Create production docker-compose file if not exists
    if [ ! -f "${APP_DIR}/deployment/docker-compose.prod.yml" ]; then
        cat > ${APP_DIR}/deployment/docker-compose.prod.yml <<'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: instagram_scraper_db_prod
    environment:
      POSTGRES_USER: scraper_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-scraper_password_123}
      POSTGRES_DB: instagram_scraper
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U scraper_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - scraper_network

volumes:
  postgres_data:
    name: instagram_scraper_postgres_data

networks:
  scraper_network:
    driver: bridge
EOF
        chown ${APP_USER}:${APP_USER} ${APP_DIR}/deployment/docker-compose.prod.yml
        print_success "docker-compose.prod.yml created"
    fi

    # Start PostgreSQL container
    cd ${APP_DIR}/deployment
    docker-compose -f docker-compose.prod.yml up -d

    print_success "PostgreSQL container started"
}

setup_systemd_service() {
    print_header "Setting Up Systemd Service"

    # Create systemd service file
    cat > /etc/systemd/system/instagram-scraper.service <<EOF
[Unit]
Description=Instagram Reel Scraper - FastAPI Application
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}/Backend
EnvironmentFile=${APP_DIR}/.env

ExecStartPre=/bin/sleep 5
ExecStart=${APP_DIR}/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4

Restart=always
RestartSec=10
StandardOutput=append:${APP_DIR}/logs/app.log
StandardError=append:${APP_DIR}/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload

    # Enable service (don't start yet - needs .env file)
    systemctl enable instagram-scraper

    print_success "Systemd service configured"
}

configure_firewall() {
    print_header "Configuring Firewall (UFW)"

    # Install ufw if not present
    apt-get install -y ufw

    # Configure firewall rules
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH (be careful!)
    ufw allow 22/tcp comment 'SSH'

    # Allow application port
    ufw allow 8080/tcp comment 'Instagram Scraper App'

    # Allow HTTP/HTTPS (if using Nginx)
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'

    # Enable firewall
    ufw --force enable

    print_success "Firewall configured and enabled"
}

setup_ssh_for_github_actions() {
    print_header "Setting Up SSH for GitHub Actions"

    print_warning "Generate SSH key pair for GitHub Actions deployment:"
    echo ""
    echo "Run these commands on your LOCAL machine:"
    echo "  ssh-keygen -t ed25519 -C 'github-actions-deploy' -f ~/.ssh/instagram_scraper_deploy"
    echo ""
    echo "Then add the PUBLIC key to this server:"
    echo "  cat ~/.ssh/instagram_scraper_deploy.pub | ssh user@${HOSTNAME} 'cat >> ~/.ssh/authorized_keys'"
    echo ""
    echo "And add the PRIVATE key to GitHub Secrets as VPS_SSH_KEY:"
    echo "  cat ~/.ssh/instagram_scraper_deploy"
    echo ""

    # Ensure .ssh directory exists for app user
    su - ${APP_USER} -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"

    print_success "SSH directory prepared for ${APP_USER}"
}

create_env_template() {
    print_header "Creating Environment Template"

    # Create .env.example
    cat > ${APP_DIR}/.env.example <<'EOF'
# Database Configuration
DATABASE_URL=postgresql://scraper_user:YOUR_STRONG_PASSWORD@localhost:5432/instagram_scraper

# JWT Authentication
SECRET_KEY=GENERATE_WITH_openssl_rand_-hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Application Settings
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,http://yourdomain.com
MAX_REQUESTS_PER_MINUTE=60

# Optional: Instagram Credentials (if needed)
INSTAGRAM_EMAIL=
INSTAGRAM_PASSWORD=
COOKIE_UPDATER_API_KEY=
EOF

    chown ${APP_USER}:${APP_USER} ${APP_DIR}/.env.example

    print_warning "Created .env.example - You MUST create .env with actual values!"
    print_warning "Generate SECRET_KEY with: openssl rand -hex 32"

    print_success "Environment template created"
}

print_next_steps() {
    print_header "Setup Complete!"

    echo -e "${GREEN}Server setup completed successfully!${NC}\n"

    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Create production .env file:"
    echo "   sudo cp ${APP_DIR}/.env.example ${APP_DIR}/.env"
    echo "   sudo nano ${APP_DIR}/.env  # Edit with actual values"
    echo "   sudo chown ${APP_USER}:${APP_USER} ${APP_DIR}/.env"
    echo ""
    echo "2. Clone/update repository:"
    echo "   sudo su - ${APP_USER}"
    echo "   cd ${APP_DIR}"
    echo "   git clone YOUR_REPO_URL ."
    echo ""
    echo "3. Install Python dependencies:"
    echo "   source venv/bin/activate"
    echo "   pip install -r Backend/requirements.txt"
    echo ""
    echo "4. Run database migrations:"
    echo "   cd deployment"
    echo "   ./run-migrations.sh"
    echo ""
    echo "5. Start the application:"
    echo "   sudo systemctl start instagram-scraper"
    echo "   sudo systemctl status instagram-scraper"
    echo ""
    echo "6. Configure GitHub Secrets:"
    echo "   - VPS_HOST: $(hostname -I | awk '{print $1}')"
    echo "   - VPS_USER: ${APP_USER}"
    echo "   - VPS_SSH_KEY: (generate and add SSH key)"
    echo "   - VPS_PORT: 22"
    echo "   - DATABASE_URL: (from .env file)"
    echo "   - SECRET_KEY: (from .env file)"
    echo "   - ALLOWED_ORIGINS: (from .env file)"
    echo ""
    echo "7. Test deployment:"
    echo "   curl http://localhost:8080/docs"
    echo ""
    echo -e "${BLUE}Deployment scripts location: ${APP_DIR}/deployment${NC}"
    echo -e "${BLUE}Application logs: ${APP_DIR}/logs/${NC}"
    echo -e "${BLUE}Service logs: sudo journalctl -u instagram-scraper -f${NC}"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear

    print_header "Instagram Reel Scraper - VPS Server Setup"

    echo "This script will set up your VPS server for hosting the application."
    echo ""
    read -p "Continue? (y/n): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled"
        exit 1
    fi

    check_root

    # Execute setup steps
    update_system
    install_python
    install_docker
    create_app_user
    setup_directory_structure
    clone_repository
    setup_python_venv
    setup_postgresql
    setup_systemd_service
    configure_firewall
    setup_ssh_for_github_actions
    create_env_template

    # Show next steps
    print_next_steps
}

# Run main function
main

# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with user authentication, group management, and analytics. Built with FastAPI backend and vanilla JavaScript frontend.

## Features

- **User Authentication** - JWT-based authentication with secure password hashing
- **Group Management** - Organize Instagram usernames into reusable groups
- **Async Job Processing** - Long-running scraping jobs with real-time progress tracking
- **Multi-User Scraping** - Process multiple Instagram accounts simultaneously
- **Data Persistence** - PostgreSQL database for storing users, jobs, and scraped data
- **Data Export** - Automatic JSON and CSV export of scraped data
- **Analytics Dashboard** - View scraping history and statistics
- **Dark Theme UI** - Modern interface with black, purple, and white color scheme

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **JWT** - Secure authentication
- **Uvicorn** - ASGI server

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Modern responsive design
- **Fetch API** - Backend communication

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** - Usually included with Docker Desktop
- **Git** - [Install Git](https://git-scm.com/downloads/)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Instagram_reel_scrapper
```

### 2. Set Up PostgreSQL with Docker

#### Option A: Using Docker Compose (Recommended)

Create a `docker-compose.yml` file in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: instagram_scraper_db
    environment:
      POSTGRES_USER: scraper_user
      POSTGRES_PASSWORD: scraper_password_123
      POSTGRES_DB: instagram_scraper
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Start the database:

```bash
docker-compose up -d
```

To stop the database:

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```

#### Option B: Using Docker CLI

```bash
# Pull PostgreSQL image
docker pull postgres:15-alpine

# Create and run PostgreSQL container
docker run -d \
  --name instagram_scraper_db \
  -e POSTGRES_USER=scraper_user \
  -e POSTGRES_PASSWORD=scraper_password_123 \
  -e POSTGRES_DB=instagram_scraper \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Check if container is running
docker ps

# View logs
docker logs instagram_scraper_db

# Stop container
docker stop instagram_scraper_db

# Start container
docker start instagram_scraper_db

# Remove container
docker rm instagram_scraper_db
```

### 3. Set Up Python Environment

```bash
# Navigate to Backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `Backend` directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://scraper_user:scraper_password_123@localhost:5432/instagram_scraper

# JWT Authentication
# Generate a secure key with: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Application Settings
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60

# User Limits
MAX_GROUPS_PER_USER=10
```

**Important:** Generate a secure SECRET_KEY:

```bash
# Using OpenSSL (recommended)
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize the Database

```bash
# Make sure you're in the Backend directory with venv activated
cd Backend

# Initialize database tables
python -c "from database import init_db; init_db()"
```

You should see: "Database tables created successfully!"

## Running the Application

### 1. Start PostgreSQL (if not already running)

```bash
docker-compose up -d
# or
docker start instagram_scraper_db
```

### 2. Start the Backend Server

```bash
# Make sure you're in the Backend directory
cd Backend

# Activate virtual environment if not already active
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run the server
python app.py
```

The server will start at `http://localhost:8000`

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Access the Application

Open your browser and navigate to:
- **Main Application:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs:** `http://localhost:8000/redoc`

## Project Structure

```
Instagram_reel_scrapper/
├── Backend/
│   ├── Scripts/
│   │   └── pipeline.py          # Core scraping logic
│   ├── app.py                    # FastAPI application
│   ├── auth.py                   # JWT authentication
│   ├── config.py                 # Configuration settings
│   ├── database.py               # Database connection
│   ├── models.py                 # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── crud.py                   # Database operations
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (create this)
│   ├── .env.example              # Environment template
│   └── output_json/              # Scraped data output
│
├── Frontend/
│   ├── index.html                # Main page
│   ├── login.html                # Login/signup page
│   ├── script.js                 # Main app logic
│   ├── auth.js                   # Authentication logic
│   ├── groups.js                 # Group management
│   ├── analytics.js              # Analytics dashboard
│   └── styles.css                # Styling
│
├── docker-compose.yml            # Docker setup (create this)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Usage Guide

### First Time Setup

1. **Create an Account**
   - Navigate to `http://localhost:8000`
   - Click "Sign Up"
   - Enter your email, username, and password
   - Click "Create Account"

2. **Login**
   - Enter your credentials
   - Click "Login"
   - You'll be redirected to the main application

### Scraping Instagram Reels

#### Method 1: Single Username Entry
1. Enter an Instagram username in the input field
2. Click "Add" button
3. Repeat for multiple accounts
4. Set the number of reels to scrape
5. Click "Start Scraping"

#### Method 2: Bulk Username Entry
1. Click the textarea for "Add Multiple Usernames"
2. Enter usernames, one per line
3. Click "Submit All"

#### Method 3: Using Groups
1. Create a group with frequently used usernames
2. Save the group with a name
3. Load the group whenever needed
4. Start scraping

### Managing Groups

- **Create Group:** Add usernames, enter group name, click "Save as Group"
- **Load Group:** Select from dropdown, click "Load Group"
- **View Groups:** See all your saved groups in the sidebar
- **Delete Group:** Click delete icon next to group name

### Viewing Analytics

1. Click "Analytics" tab
2. View scraping history
3. See total reels scraped
4. Check success/failure rates
5. Export data as needed

## API Endpoints

### Authentication

```bash
# Register new user
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "myusername",
  "password": "SecurePass123"
}

# Login
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=myusername&password=SecurePass123

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Scraping

```bash
# Start scraping job
POST /api/scrape
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "usernames": ["instagram_user1", "instagram_user2"],
  "reel_count": 20
}

# Response
{
  "job_id": "abc123",
  "status": "running"
}

# Check job status
GET /api/jobs/{job_id}
Authorization: Bearer <your-token>

# Response
{
  "job_id": "abc123",
  "status": "completed",
  "progress": 100,
  "results": [...]
}
```

### Groups

```bash
# Create group
POST /api/groups
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "My Favorite Accounts",
  "usernames": ["user1", "user2", "user3"]
}

# Get all groups
GET /api/groups
Authorization: Bearer <your-token>

# Get specific group
GET /api/groups/{group_id}
Authorization: Bearer <your-token>

# Delete group
DELETE /api/groups/{group_id}
Authorization: Bearer <your-token>
```

## Database Management

### Connect to PostgreSQL

```bash
# Using Docker exec
docker exec -it instagram_scraper_db psql -U scraper_user -d instagram_scraper

# View tables
\dt

# View table structure
\d users
\d scraping_jobs
\d scraped_reels

# Query data
SELECT * FROM users;
SELECT * FROM scraping_jobs ORDER BY start_time DESC LIMIT 10;

# Exit
\q
```

### Backup Database

```bash
# Backup
docker exec -t instagram_scraper_db pg_dump -U scraper_user instagram_scraper > backup.sql

# Restore
docker exec -i instagram_scraper_db psql -U scraper_user instagram_scraper < backup.sql
```

### Reset Database

```bash
# Stop the application
# Then remove and recreate container
docker-compose down -v
docker-compose up -d

# Reinitialize database
cd Backend
python -c "from database import init_db; init_db()"
```

## Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server: Connection refused`

```bash
# Check if PostgreSQL container is running
docker ps

# If not running, start it
docker start instagram_scraper_db

# Check logs for errors
docker logs instagram_scraper_db

# Verify port is not in use
# Windows:
netstat -ano | findstr :5432
# macOS/Linux:
lsof -i :5432
```

**Error:** `FATAL: password authentication failed`

- Check DATABASE_URL in `.env` file
- Ensure username and password match container environment variables
- Recreate container with correct credentials

### Backend Server Issues

**Error:** `Address already in use`

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Error:** `ModuleNotFoundError`

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Scraping Issues

**Error:** `Could not find target_id`

- Username may be incorrect or account doesn't exist
- Account might be private
- Instagram may have changed their HTML structure
- Try adding a valid Instagram session cookie

**Error:** `Rate limit exceeded`

- Instagram is blocking requests
- Increase sleep time between requests
- Use valid session cookies
- Wait before retrying

### Frontend Issues

**Error:** `CORS policy blocked`

- Ensure CORS is enabled in `app.py`
- Check ALLOWED_ORIGINS in `.env` file
- Clear browser cache and cookies

## Development

### Running in Development Mode

```bash
# Backend with auto-reload
cd Backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or using the app directly
python app.py
```

### Database Migrations

This project uses SQLAlchemy for database schema management. For production, consider using Alembic for migrations.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| SECRET_KEY | JWT signing key | Required |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry time | 10080 (7 days) |
| DEBUG | Debug mode | True |
| ALLOWED_ORIGINS | CORS allowed origins | localhost:8000 |

## Security Considerations

- **Never commit `.env` file** to version control
- **Change SECRET_KEY** in production
- **Use HTTPS** in production
- **Restrict CORS origins** in production
- **Enable rate limiting** to prevent abuse
- **Regular backups** of database
- **Update dependencies** regularly for security patches

## Docker Commands Cheat Sheet

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs instagram_scraper_db
docker logs -f instagram_scraper_db  # Follow logs

# Enter container shell
docker exec -it instagram_scraper_db bash

# Stop container
docker stop instagram_scraper_db

# Start container
docker start instagram_scraper_db

# Restart container
docker restart instagram_scraper_db

# Remove container
docker rm instagram_scraper_db

# Remove container and volume
docker rm -v instagram_scraper_db

# View volumes
docker volume ls

# Remove volume
docker volume rm postgres_data

# Docker Compose commands
docker-compose up -d        # Start in detached mode
docker-compose down         # Stop and remove containers
docker-compose down -v      # Stop, remove containers and volumes
docker-compose logs -f      # Follow logs
docker-compose restart      # Restart services
docker-compose ps           # List containers
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. Please respect Instagram's Terms of Service when using this tool.

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the API documentation at `http://localhost:8000/docs`
3. Check Docker logs: `docker logs instagram_scraper_db`
4. Check application logs in the terminal where you ran `python app.py`

---

**Built with FastAPI, PostgreSQL, and Docker**

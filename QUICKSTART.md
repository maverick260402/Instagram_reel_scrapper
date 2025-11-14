# Quick Start Guide

Get the Instagram Reel Scraper running in 5 minutes!

## Prerequisites

- Python 3.8+
- Docker Desktop (running)

## Steps

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

Wait 10 seconds for the database to initialize.

### 2. Set Up Backend

```bash
# Navigate to Backend
cd Backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies (takes 1-2 minutes)
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Generate a secure key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

### 3. Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

You should see: **"Database tables created successfully!"**

### 4. Run the Application

```bash
python app.py
```

### 5. Open Your Browser

Navigate to: **http://localhost:8000**

## First Use

1. Click **"Sign Up"**
2. Create an account with:
   - Email: `your@email.com`
   - Username: `yourusername`
   - Password: `YourSecurePassword123`
3. Click **"Create Account"**
4. Login with your credentials

## Start Scraping

1. Enter Instagram usernames (e.g., `instagram`, `nasa`, `natgeo`)
2. Set number of reels (e.g., `20`)
3. Click **"Start Scraping"**
4. Watch the progress bar
5. View results!

## Stop Everything

```bash
# Stop backend: Press Ctrl+C in terminal

# Stop database:
docker-compose down
```

## Troubleshooting

**Database won't start?**
```bash
docker-compose down -v
docker-compose up -d
```

**Backend errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

**Can't access localhost:8000?**
- Check if backend is running
- Try http://127.0.0.1:8000

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [API Documentation](http://localhost:8000/docs) when server is running
- Create groups to organize your favorite Instagram accounts
- View analytics to see your scraping history

---

Need help? Check the [Troubleshooting](README.md#troubleshooting) section in the main README.

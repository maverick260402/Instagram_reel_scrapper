# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with a modern, dark-themed user interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Frontend Guide](#frontend-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This application allows users to scrape Instagram reel metadata from multiple accounts with a sleek, user-friendly interface. The backend uses FastAPI for high performance, while the frontend provides an intuitive experience with a black, purple, and white color scheme.

## ✨ Features

### Backend Features
- **FastAPI Server** - High-performance async API
- **Pagination Support** - Efficiently fetch large numbers of reels
- **Multi-User Scraping** - Process multiple Instagram accounts in one request
- **Data Export** - Automatically saves data as JSON and CSV
- **Error Handling** - Robust error management with detailed feedback
- **Rate Limiting Protection** - Built-in delays to avoid Instagram rate limits

### Frontend Features
- **Dual Input Modes**:
  - Single username input with "Add" button
  - Bulk username input via textarea (one per line)
- **Interactive Username Management** - Add, view, and remove usernames dynamically
- **Configurable Reel Count** - Specify how many reels to scrape per account
- **Real-time Progress Tracking** - Visual progress bar during scraping
- **Results Dashboard** - Detailed success/failure status for each account
- **Dark Theme UI** - Black background, white text, purple accents
- **Responsive Design** - Works on desktop and mobile devices

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Requests** - HTTP library for API calls
- **Pandas** - Data manipulation and CSV export
- **Zstandard** - Compression handling
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with animations
- **HTML5** - Semantic markup
- **Fetch API** - Backend communication

## 📁 Project Structure

```
Instagram_reel_scrapper/
├── Backend/
│   ├── Scripts/
│   │   └── pipeline.py          # Core scraping logic
│   ├── app.py                    # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   └── output_json/              # Generated data (created at runtime)
│       └── {username}/
│           ├── meta_data.json    # Raw Instagram API response
│           └── scrapped_data.csv # Extracted reel metadata
│
└── Frontend/
    ├── index.html                # Main application page
    ├── styles.css                # UI styling
    └── script.js                 # Frontend logic
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Step 1: Clone or Navigate to Project
```bash
cd "d:\ThunderBolts\Project Tres\Script_Based_Solution\Instagram_reel_scrapper"
```

### Step 2: Install Backend Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import fastapi, uvicorn, pandas; print('All dependencies installed!')"
```

## 📖 Usage

### Starting the Application

1. **Start the Backend Server**:
   ```bash
   cd Backend
   python app.py
   ```
   The server will start on `http://localhost:8000`

2. **Open the Frontend**:
   - Open `Frontend/index.html` in your web browser
   - Or visit `http://localhost:8000` if configured to serve frontend

### Using the Web Interface

#### Method 1: Single Username Entry
1. Enter an Instagram username in the "Add Single Username" field
2. Click the "Add" button
3. Repeat for multiple accounts
4. View added usernames as purple tags
5. Remove individual usernames by clicking the "×" button

#### Method 2: Bulk Username Entry
1. Click in the "Add Multiple Usernames" textarea
2. Enter usernames, one per line:
   ```
   username1
   username2
   username3
   ```
3. Click "Submit All" to add all usernames at once

#### Scraping Reels
1. Add usernames using either method
2. Set the "Number of Reels" (default: 20)
3. Click "Start Scraping"
4. Monitor progress in the progress bar
5. View results when complete

### Output Files

For each username, the system creates:
- `Backend/output_json/{username}/meta_data.json` - Complete Instagram API response
- `Backend/output_json/{username}/scrapped_data.csv` - Extracted data with columns:
  - `pk` - Post ID
  - `code` - Short code
  - `play_count` - Number of plays
  - `comment_count` - Number of comments
  - `like_count` - Number of likes
  - `url` - Direct URL to the reel

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET `/`
Serves the main application page.

**Response**: HTML page

---

#### POST `/api/scrape`
Scrapes Instagram reels for specified usernames.

**Request Body**:
```json
{
  "usernames": ["username1", "username2"],
  "reel_count": 20
}
```

**Response**:
```json
{
  "status": "completed",
  "results": [
    {
      "username": "username1",
      "status": "success",
      "reels_scraped": 20,
      "csv_path": "path/to/scrapped_data.csv",
      "json_path": "path/to/meta_data.json"
    }
  ]
}
```

**Error Response**:
```json
{
  "username": "username1",
  "status": "failed",
  "error": "Error message"
}
```

## 🎨 Frontend Guide

### Color Scheme
- **Background**: `#000000` (Black)
- **Text**: `#FFFFFF` (White)
- **Primary Accent**: `#9333ea` (Purple)
- **Hover State**: `#a855f7` (Light Purple)
- **Success**: `#10b981` (Green)
- **Error**: `#ef4444` (Red)

### Key Components

#### Username Tags
- Display added usernames as purple pill-shaped tags
- Click "×" to remove individual usernames
- Animated entry with slide-in effect

#### Progress Bar
- Gradient purple fill
- Smooth width transitions
- Percentage display when active

#### Results Display
- Color-coded status badges (green for success, red for error)
- File paths in monospace font
- Collapsible details per username

### Customization

To modify the API endpoint, edit `Frontend/script.js`:
```javascript
const API_URL = 'http://localhost:8000'; // Change this
```

## ⚙️ Configuration

### Backend Configuration

Edit `Backend/app.py` to customize:

**Server Port**:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

**CORS Settings**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Scraping Configuration

Edit `Backend/Scripts/pipeline.py` for:

**Sleep Between Requests** (avoid rate limiting):
```python
fetch_reels_paginated(..., sleep_seconds=3.0)  # Adjust timing
```

**Max Reels Per Page**:
```python
fetch_reels_paginated(..., max_per_page=50)  # Change batch size
```

**Session Cookies**:
Update the `cookie` field in headers with your Instagram session cookie for authenticated requests.

## 🔧 Troubleshooting

### Common Issues

**1. "Could not find target_id" Error**
- **Cause**: Invalid username or Instagram changed their HTML structure
- **Solution**: Verify username exists, check if account is public, update session cookie

**2. Rate Limiting / Blocked Requests**
- **Cause**: Too many requests to Instagram
- **Solution**: Increase `sleep_seconds` parameter, use valid session cookies

**3. CORS Errors in Browser**
- **Cause**: Frontend trying to access backend from different origin
- **Solution**: Ensure CORS is enabled in `app.py`, or serve frontend from same server

**4. Empty Results**
- **Cause**: Private account or no reels available
- **Solution**: Verify account has public reels, check account privacy settings

**5. Server Won't Start**
- **Cause**: Port already in use or missing dependencies
- **Solution**:
  ```bash
  # Check port usage
  netstat -ano | findstr :8000

  # Reinstall dependencies
  pip install -r requirements.txt --force-reinstall
  ```

### Debug Mode

Enable FastAPI debug mode in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="debug")
```

View console logs in:
- **Backend**: Terminal where `python app.py` is running
- **Frontend**: Browser Developer Tools (F12) → Console tab

## 📝 Notes

- **Instagram Session**: For better reliability, provide a valid Instagram session cookie in the headers
- **Rate Limits**: Instagram may rate limit requests. Adjust sleep timings as needed
- **Data Privacy**: Be mindful of Instagram's Terms of Service when scraping data
- **Session Expiry**: Cookies expire periodically and need to be refreshed

## 🤝 Contributing

When modifying the code:
1. Test thoroughly with various usernames
2. Handle edge cases (private accounts, deleted accounts, etc.)
3. Update this documentation for new features
4. Follow the existing code style

## 📄 License

This project is for educational purposes. Respect Instagram's Terms of Service and robots.txt when using this tool.

---

**Created with Claude Code** 🤖

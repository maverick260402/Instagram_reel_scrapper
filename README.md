# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with a modern, dark-themed user interface.

## Features

- **FastAPI Backend** - High-performance async API for scraping Instagram reels
- **Modern Frontend** - Dark-themed UI with real-time progress tracking
- **Multi-User Support** - Process multiple Instagram accounts in one request
- **Data Export** - Automatically saves data as JSON and CSV
- **Line Counter** - Track production-ready code metrics

## Project Structure

```
Instagram_reel_scrapper/
├── Backend/
│   ├── Scripts/          # Helper scripts for scraping
│   ├── app.py           # FastAPI application
│   ├── pipeline.py      # Core scraping logic
│   └── requirements.txt # Python dependencies
├── Frontend/
│   ├── index.html       # Main application page
│   ├── script.js        # Frontend logic
│   └── styles.css       # UI styling
└── count_lines.py       # Production code line counter
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Setup

1. **Install Backend Dependencies**:
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```bash
   cd Backend
   python app.py
   ```
   The server will start on `http://localhost:8000`

3. **Open the Frontend**:
   - Open `Frontend/index.html` in your web browser

## Usage

### Scraping Instagram Reels

1. Enter Instagram username(s) in the web interface
2. Specify the number of reels to scrape (default: 20)
3. Click "Start Scraping"
4. View results and download CSV/JSON files

### Counting Production Lines

To count the number of lines in production-ready code:

```bash
python count_lines.py
```

This will generate a detailed report showing:
- Line count per file
- Total lines, code lines, and non-code lines (comments/blanks)
- Code percentage statistics

**Example output:**
```
================================================================================
PRODUCTION-READY CODE LINE COUNT REPORT
================================================================================

File                                                    Total       Code   Non-Code
--------------------------------------------------------------------------------
Backend/app.py                                            144        116         28
Backend/pipeline.py                                       394        311         83
Frontend/index.html                                       222        193         29
Frontend/script.js                                        655        510        145
Frontend/styles.css                                       807        665        142
--------------------------------------------------------------------------------
TOTAL                                                    2689       2158        531

================================================================================
SUMMARY
================================================================================
Number of production files: 9
Total lines: 2689
Code lines (excluding comments/blanks): 2158
Non-code lines (comments + blank): 531
Code percentage: 80.3%
================================================================================
```

The line counter automatically:
- Excludes test files, sample data, and documentation
- Counts code lines separately from comments and blank lines
- Provides detailed per-file statistics

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

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

## Output Files

For each username, the system creates:
- `Backend/output_json/{username}/meta_data.json` - Complete Instagram API response
- `Backend/output_json/{username}/scrapped_data.csv` - Extracted data with columns:
  - `pk` - Post ID
  - `code` - Short code
  - `play_count` - Number of plays
  - `comment_count` - Number of comments
  - `like_count` - Number of likes
  - `url` - Direct URL to the reel

## Development

### Code Metrics

Run the line counter to track code growth and maintain code quality:

```bash
python count_lines.py
```

This helps monitor:
- Codebase size and complexity
- Code vs. documentation ratio
- Production-ready file count

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- Requests - HTTP library
- Pandas - Data manipulation
- Zstandard - Compression handling

**Frontend:**
- Vanilla JavaScript
- CSS3 with animations
- HTML5 semantic markup
- Fetch API

## Notes

- **Instagram Session**: For better reliability, provide a valid Instagram session cookie in the headers
- **Rate Limits**: Instagram may rate limit requests. Adjust sleep timings as needed
- **Data Privacy**: Be mindful of Instagram's Terms of Service when scraping data

## License

This project is for educational purposes. Respect Instagram's Terms of Service and robots.txt when using this tool.

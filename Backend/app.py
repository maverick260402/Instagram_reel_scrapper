from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path
from datetime import datetime
import asyncio
from pipeline import get_target_id, fetch_reels_paginated, get_meta_data
# Add Scripts directory to path
scripts_dir = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

app = FastAPI(title="Instagram Reel Scraper API")

# In-memory job storage (use Redis/database in production)
jobs_db: Dict[str, dict] = {}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

class ScrapeRequest(BaseModel):
    usernames: List[str]
    reel_count: int = 20

class ScrapeResult(BaseModel):
    username: str
    status: str
    reels_scraped: int = None
    csv_path: str = None
    json_path: str = None
    error: str = None

def run_scraping_job(job_id: str, usernames: List[str], reel_count: int):
    """Background task to run the scraping job"""
    import time as time_module
    start_time = time_module.time()

    print(f"\n{'='*60}")
    print(f"🚀 STARTING BACKGROUND JOB: {job_id}")
    print(f"   Usernames: {usernames}")
    print(f"   Reel count: {reel_count}")
    print(f"   Time: {time_module.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    results = []

    for idx, username in enumerate(usernames, 1):
        # Update job progress
        jobs_db[job_id]['progress'] = (idx - 1) / len(usernames) * 100
        jobs_db[job_id]['current_username'] = username

        print(f"\n[{idx}/{len(usernames)}] Processing username: {username}")
        try:
            # Get target ID
            target_id = get_target_id(username)
            if not target_id:
                result = {
                    'username': username,
                    'status': 'failed',
                    'error': 'Could not find target ID'
                }
                results.append(result)
                continue

            # Fetch reels with pagination
            meta_output_path = fetch_reels_paginated(
                target_id,
                username,
                desired_count=reel_count,
                sleep_seconds=3.0,
                max_per_page=50
            )

            if meta_output_path:
                # Extract metadata to DataFrame and save CSV
                df_result = get_meta_data(str(meta_output_path))

                result = {
                    'username': username,
                    'status': 'success',
                    'reels_scraped': len(df_result),
                    'csv_path': str(Path(meta_output_path).parent / "scrapped_data.csv"),
                    'json_path': str(meta_output_path)
                }
                results.append(result)
            else:
                result = {
                    'username': username,
                    'status': 'failed',
                    'error': 'Failed to retrieve meta data'
                }
                results.append(result)

        except Exception as e:
            result = {
                'username': username,
                'status': 'failed',
                'error': str(e)
            }
            results.append(result)

    elapsed_time = time_module.time() - start_time

    # Update job status to completed
    jobs_db[job_id]['status'] = 'completed'
    jobs_db[job_id]['progress'] = 100
    jobs_db[job_id]['results'] = results
    jobs_db[job_id]['end_time'] = datetime.now().isoformat()
    jobs_db[job_id]['duration'] = elapsed_time

    print(f"\n{'='*60}")
    print(f"✅ BACKGROUND JOB COMPLETED: {job_id}")
    print(f"   Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"   Successful: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
    print(f"   Failed: {sum(1 for r in results if r['status'] == 'failed')}/{len(results)}")
    print(f"{'='*60}\n")

@app.get("/")
async def read_root():
    html_path = Path(__file__).parent / "templates" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Instagram Reel Scraper API"}

@app.post("/api/scrape")
async def scrape_reels(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start a scraping job and return immediately with job_id"""
    try:
        usernames = request.usernames
        reel_count = request.reel_count

        if not usernames:
            raise HTTPException(status_code=400, detail="No usernames provided")

        # Generate unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create job record
        jobs_db[job_id] = {
            'job_id': job_id,
            'status': 'running',
            'progress': 0,
            'usernames': usernames,
            'reel_count': reel_count,
            'start_time': datetime.now().isoformat(),
            'current_username': None,
            'results': [],
            'end_time': None,
            'duration': None
        }

        print(f"\n📥 SCRAPE REQUEST RECEIVED - Job ID: {job_id}")
        print(f"   Usernames: {usernames}")
        print(f"   Reel count: {reel_count}\n")

        # Start background task
        background_tasks.add_task(run_scraping_job, job_id, usernames, reel_count)

        # Return immediately with job ID
        return {
            'job_id': job_id,
            'status': 'started',
            'message': 'Scraping job started. Use /api/job/{job_id} to check status'
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a scraping job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = jobs_db[job_id]

    return {
        'job_id': job['job_id'],
        'status': job['status'],
        'progress': job['progress'],
        'usernames': job['usernames'],
        'reel_count': job['reel_count'],
        'start_time': job['start_time'],
        'current_username': job['current_username'],
        'results': job['results'],
        'end_time': job['end_time'],
        'duration': job['duration']
    }

if __name__ == '__main__':
    import uvicorn
    # Configure uvicorn with longer timeout for long-running scraping requests
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=600,  # 10 minutes keepalive timeout
        timeout_graceful_shutdown=30
    )

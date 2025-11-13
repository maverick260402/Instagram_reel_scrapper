from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path
from pipeline import get_target_id, fetch_reels_paginated, get_meta_data
# Add Scripts directory to path
scripts_dir = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

app = FastAPI(title="Instagram Reel Scraper API")

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

@app.get("/")
async def read_root():
    html_path = Path(__file__).parent / "templates" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Instagram Reel Scraper API"}

@app.post("/api/scrape")
async def scrape_reels(request: ScrapeRequest):
    try:
        import time as time_module
        start_time = time_module.time()

        usernames = request.usernames
        reel_count = request.reel_count

        print(f"\n{'='*60}")
        print(f"📥 SCRAPE REQUEST RECEIVED")
        print(f"   Usernames: {usernames}")
        print(f"   Reel count: {reel_count}")
        print(f"   Time: {time_module.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        if not usernames:
            raise HTTPException(status_code=400, detail="No usernames provided")

        results = []

        for idx, username in enumerate(usernames, 1):
            print(f"\n[{idx}/{len(usernames)}] Processing username: {username}")
            try:

                # Get target ID
                target_id = get_target_id(username)
                if not target_id:
                    results.append(ScrapeResult(
                        username=username,
                        status='failed',
                        error='Could not find target ID'
                    ))
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

                    results.append(ScrapeResult(
                        username=username,
                        status='success',
                        reels_scraped=len(df_result),
                        csv_path=str(Path(meta_output_path).parent / "scrapped_data.csv"),
                        json_path=str(meta_output_path)
                    ))
                else:
                    results.append(ScrapeResult(
                        username=username,
                        status='failed',
                        error='Failed to retrieve meta data'
                    ))

            except Exception as e:
                results.append(ScrapeResult(
                    username=username,
                    status='failed',
                    error=str(e)
                ))

        elapsed_time = time_module.time() - start_time
        print(f"\n{'='*60}")
        print(f"✅ SCRAPE REQUEST COMPLETED")
        print(f"   Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"   Successful: {sum(1 for r in results if r.status == 'success')}/{len(results)}")
        print(f"   Failed: {sum(1 for r in results if r.status == 'failed')}/{len(results)}")
        print(f"{'='*60}\n")

        return {
            'status': 'completed',
            'results': results
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

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

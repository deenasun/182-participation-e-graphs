#!/usr/bin/env python3
"""
Standalone script to fetch latest Ed posts and run the data ingestion pipeline.

By default this script will:
  1. Use the Ed webscraper to fetch the latest participation posts.
  2. Append only *new* posts (by Ed thread `id`) to backend/ed_posts.json.
  3. Run the ingestion pipeline to generate backend/processed_posts.json.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion import run_ingestion_pipeline


if __name__ == "__main__":
    import argparse
    import json

    # Import webscraper lazily so this script still works even if Ed env vars
    # are not configured. We only use it when scraping is enabled.
    try:
        import webscraper
    except ImportError:
        webscraper = None
    
    parser = argparse.ArgumentParser(description='Run EECS 182 post ingestion pipeline')
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save processed_posts.json (default: ./processed_posts.json in backend directory)'
    )
    parser.add_argument(
        '--skip-scrape',
        action='store_true',
        help='Skip fetching latest Ed posts with the webscraper before ingestion'
    )
    
    args = parser.parse_args()

    # Resolve input JSON path
    backend_dir = Path(__file__).parent
    json_path = backend_dir / "ed_posts.json"

    # Optionally fetch latest posts from Ed and append only new ones
    if not args.skip_scrape and webscraper is not None and json_path == backend_dir / "ed_posts.json":
        ED_API_TOKEN = getattr(webscraper, "ED_API_TOKEN", None)
        ED_COURSE_ID = getattr(webscraper, "ED_COURSE_ID", None)
        SEARCH_STRING = getattr(webscraper, "SEARCH_STRING", None)

        if not ED_API_TOKEN or ED_API_TOKEN == "YOUR_TOKEN_HERE" or not ED_COURSE_ID:
            print("Skipping Ed scrape: ED_API_TOKEN / ED_COURSE_ID not configured.")
        else:
            print("\nStep 0: Fetching latest Ed posts via webscraper...")

            # Load existing posts, if any
            existing_posts = []
            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        existing_posts = json.load(f)
                    print(f"  Loaded {len(existing_posts)} existing posts from {json_path}")
                except Exception as e:
                    print(f"  Warning: Could not load existing {json_path}: {e}")
                    existing_posts = []

            existing_ids = {post.get('id') for post in existing_posts}

            # Fetch latest matching posts from Ed
            try:
                scraped_posts = webscraper.process_threads(SEARCH_STRING)
            except Exception as e:
                print(f"  Error while scraping Ed posts: {e}")
                scraped_posts = []

            # Keep only posts whose Ed thread id we haven't seen before
            new_posts = [p for p in scraped_posts if p.get('id') not in existing_ids]

            if new_posts:
                print(f"  Found {len(new_posts)} new posts (out of {len(scraped_posts)} matching).")
                existing_posts.extend(new_posts)
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_posts, f, indent=2, ensure_ascii=False)
                    print(f"  Saved updated posts JSON to {json_path}")
                except Exception as e:
                    print(f"  Error writing {json_path}: {e}")
            else:
                print("  No new posts found. Using existing posts JSON.")
    elif not args.skip_scrape and webscraper is None:
        print("Warning: webscraper module not available; skipping Ed scrape.")
    
    # Run the ingestion pipeline
    try:
        run_ingestion_pipeline(json_path=str(json_path), output_path=args.output)
        print("\nIngestion pipeline completed successfully!")
    except Exception as e:
        print(f"\nError running ingestion pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

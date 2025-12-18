#!/usr/bin/env python3
"""
Standalone script to run the data ingestion pipeline.
Processes ed_posts.json and generates processed_posts.json with embeddings and layouts.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion import run_ingestion_pipeline

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run EECS 182 post ingestion pipeline')
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to ed_posts.json (default: ../ed_posts.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save processed_posts.json (default: ./processed_posts.json in backend directory)'
    )
    
    args = parser.parse_args()
    
    try:
        run_ingestion_pipeline(json_path=args.input, output_path=args.output)
        print("\nIngestion pipeline completed successfully!")
    except Exception as e:
        print(f"\nError running ingestion pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

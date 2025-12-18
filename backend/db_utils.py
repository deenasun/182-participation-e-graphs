"""
Database utility script for managing Supabase data
Run this script to load data from processed_posts.json into Supabase
"""

import json
import sys
from pathlib import Path
from database import SupabaseClient


def load_data_from_json(json_path: Path = None):
    """
    Load processed posts from JSON file into Supabase
    
    Args:
        json_path: Path to processed_posts.json (defaults to ./processed_posts.json)
    """
    # Initialize database
    try:
        db = SupabaseClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    # Determine JSON file path
    if json_path is None:
        json_path = Path(__file__).parent / "processed_posts.json"
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        print("Please run the ingestion pipeline first to generate processed_posts.json")
        return False
    
    print(f"Loading data from: {json_path}")
    
    # Load JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    posts = data.get('posts', [])
    layout_data = data.get('layout_data', {})
    
    print(f"Found {len(posts)} posts in JSON file")
    
    # Insert posts
    print("\nInserting posts into database...")
    successful_posts = 0
    failed_posts = 0
    
    for i, post in enumerate(posts):
        try:
            db.insert_post(post)
            successful_posts += 1
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Inserted {i + 1}/{len(posts)} posts")
                
        except Exception as e:
            failed_posts += 1
            if failed_posts <= 3:  # Only show first 3 errors
                print(f"  Error inserting post {post.get('ed_post_id')}: {e}")
    
    print(f"\nPosts inserted: {successful_posts}/{len(posts)}")
    if failed_posts > 0:
        print(f"Failed posts: {failed_posts}")
    
    # Insert similarities
    print("\nInserting similarities...")
    for view_mode in ['topic', 'tool', 'llm']:
        similarities = layout_data.get(f'{view_mode}_similarities', [])
        print(f"\n  Processing {view_mode} view ({len(similarities)} edges)...")
        
        successful_sims = 0
        failed_sims = 0
        
        for i, (idx1, idx2, sim) in enumerate(similarities):
            try:
                post_id_1 = posts[idx1]['ed_post_id']
                post_id_2 = posts[idx2]['ed_post_id']
                db.insert_similarity(post_id_1, post_id_2, view_mode, sim)
                successful_sims += 1
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"    Inserted {i + 1}/{len(similarities)} edges")
                    
            except Exception as e:
                failed_sims += 1
                if failed_sims <= 3:  # Only show first 3 errors
                    print(f"    Error inserting similarity: {e}")
        
        print(f"  {view_mode} edges inserted: {successful_sims}/{len(similarities)}")
        if failed_sims > 0:
            print(f"  Failed edges: {failed_sims}")
    
    # Show final stats
    print("\n" + "=" * 50)
    print("Final Database Statistics")
    print("=" * 50)
    
    try:
        stats = db.get_stats()
        print(f"Posts:        {stats['posts']}")
        print(f"Layouts:      {stats['layouts']}")
        print(f"Similarities: {stats['similarities']}")
        print("=" * 50)
        print("Data load complete!")
    except Exception as e:
        print(f"Could not fetch final stats: {e}")
    
    return True


def clear_database():
    """Clear all data from the database"""
    try:
        db = SupabaseClient()
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
    print("WARNING: This will delete ALL data from the database!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled")
        return False
    
    print("Clearing database...")
    try:
        db.clear_all_data()
        print("Database cleared successfully")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False


def show_stats():
    """Show database statistics"""
    try:
        db = SupabaseClient()
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
    try:
        stats = db.get_stats()
        print("\n" + "=" * 50)
        print("Database Statistics")
        print("=" * 50)
        print(f"Posts:        {stats['posts']}")
        print(f"Layouts:      {stats['layouts']}")
        print(f"Similarities: {stats['similarities']}")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return False


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("=" * 50)
        print("Database Utility for EECS 182 Post Graph")
        print("=" * 50)
        print("\nUsage:")
        print("  python db_utils.py load    - Load data from processed_posts.json")
        print("  python db_utils.py clear   - Clear all data from database")
        print("  python db_utils.py stats   - Show database statistics")
        print("=" * 50)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'load':
        load_data_from_json()
    elif command == 'clear':
        clear_database()
    elif command == 'stats':
        show_stats()
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: load, clear, stats")


if __name__ == "__main__":
    main()

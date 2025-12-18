"""
FastAPI application for EECS 182 Post Graph API
Provides endpoints for graph visualization, search, and data management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import os

from database import SupabaseClient
from schemas import (
    PostDetail, GraphData, SearchRequest, SearchResponse,
    StatsResponse, RefreshResponse, HealthResponse, ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="EECS 182 Post Graph API",
    description="API for visualizing and exploring EECS 182 participation posts",
    version="1.0.0"
)

# CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database client
try:
    db = SupabaseClient()
except ValueError as e:
    print(f"Warning: Database client initialization failed: {e}")
    db = None


# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "message": "EECS 182 Post Graph API is running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database client not initialized"
        )
    
    try:
        # Test database connection
        stats = db.get_stats()
        return {
            "status": "healthy",
            "message": f"API running with {stats['posts']} posts in database",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


# Posts endpoints
@app.get("/api/posts", response_model=List[PostDetail])
async def get_all_posts():
    """
    Get all posts
    
    Returns:
        List of all posts with full details
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        posts = db.get_all_posts()
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch posts: {str(e)}"
        )


@app.get("/api/posts/{post_id}", response_model=PostDetail)
async def get_post(post_id: int):
    """
    Get a specific post by ID
    
    Args:
        post_id: Database ID of the post
        
    Returns:
        Post details
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        post = db.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch post: {str(e)}"
        )


# Graph data endpoint
@app.get("/api/graph-data/{view_mode}", response_model=GraphData)
async def get_graph_data(view_mode: str):
    """
    Get graph data for visualization
    
    Args:
        view_mode: View mode ('topic', 'tool', or 'llm')
        
    Returns:
        Graph data with nodes and edges
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Validate view mode
    if view_mode not in ['topic', 'tool', 'llm']:
        raise HTTPException(
            status_code=400,
            detail="Invalid view_mode. Must be 'topic', 'tool', or 'llm'"
        )
    
    try:
        data = db.get_graph_data(view_mode)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch graph data: {str(e)}"
        )


# Search endpoint
@app.post("/api/search", response_model=SearchResponse)
async def search_posts(request: SearchRequest):
    """
    Search posts by keyword or semantic similarity
    
    Args:
        request: Search request with query and optional view mode
        
    Returns:
        Search results
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        results = db.search_posts(
            query=request.query,
            view_mode=request.view_mode,
            limit=request.limit
        )
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/api/search", response_model=SearchResponse)
async def search_posts_get(
    q: str = Query(..., description="Search query"),
    view_mode: str = Query('content', description="View mode"),
    limit: int = Query(20, ge=1, le=100, description="Max results")
):
    """
    Search posts via GET request (alternative to POST)
    
    Args:
        q: Search query
        view_mode: View mode for semantic search
        limit: Maximum number of results
        
    Returns:
        Search results
    """
    request = SearchRequest(query=q, view_mode=view_mode, limit=limit)
    return await search_posts(request)


# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get database statistics
    
    Returns:
        Statistics about posts, layouts, and similarities
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        stats = db.get_stats()
        return {
            **stats,
            "view_modes": ["topic", "tool", "llm"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stats: {str(e)}"
        )


# Data refresh endpoint
@app.post("/api/refresh", response_model=RefreshResponse)
async def trigger_refresh(background_tasks: BackgroundTasks):
    """
    Manually trigger data refresh from processed_posts.json
    
    This endpoint loads data from the processed JSON file and updates the database.
    The operation runs in the background.
    
    Returns:
        Confirmation message
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    def refresh_data():
        """Background task to refresh database"""
        import json
        from pathlib import Path
        
        try:
            # Load processed posts from backend directory
            processed_file = Path(__file__).parent / "processed_posts.json"
            
            if not processed_file.exists():
                print(f"Error: {processed_file} not found")
                return
            
            with open(processed_file, 'r') as f:
                data = json.load(f)
            
            posts = data.get('posts', [])
            layout_data = data.get('layout_data', {})
            
            print(f"Loading {len(posts)} posts into database...")
            
            # Insert posts
            for i, post in enumerate(posts):
                try:
                    db.insert_post(post)
                    if (i + 1) % 10 == 0:
                        print(f"  Inserted {i + 1}/{len(posts)} posts")
                except Exception as e:
                    print(f"  Error inserting post {post.get('ed_post_id')}: {e}")
            
            # Insert similarities
            print("Loading similarities...")
            for view_mode in ['topic', 'tool', 'llm']:
                similarities = layout_data.get(f'{view_mode}_similarities', [])
                print(f"  Loading {len(similarities)} {view_mode} similarities...")
                
                for i, (idx1, idx2, sim) in enumerate(similarities):
                    try:
                        post_id_1 = posts[idx1]['ed_post_id']
                        post_id_2 = posts[idx2]['ed_post_id']
                        db.insert_similarity(post_id_1, post_id_2, view_mode, sim)
                    except Exception as e:
                        if i < 5:  # Only print first few errors
                            print(f"    Error inserting similarity: {e}")
            
            print("Database refresh complete!")
            
        except Exception as e:
            print(f"Error during refresh: {e}")
    
    # Add task to background
    background_tasks.add_task(refresh_data)
    
    return {
        "message": "Data refresh started in background",
        "status": "processing"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not found",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found"
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 50)
    print("EECS 182 Post Graph API Starting...")
    print("=" * 50)
    
    if db is None:
        print("Warning: Database client not initialized")
        print("    Set SUPABASE_URL and SUPABASE_KEY environment variables")
    else:
        try:
            stats = db.get_stats()
            print(f"Database connected")
            print(f"  - Posts: {stats['posts']}")
            print(f"  - Layouts: {stats['layouts']}")
            print(f"  - Similarities: {stats['similarities']}")
        except Exception as e:
            print(f"Warning: Database connection test failed: {e}")
    
    print("=" * 50)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("EECS 182 Post Graph API Shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PostBase(BaseModel):
    """Base post model with common fields"""
    id: int
    ed_post_id: int
    title: str
    content: str
    author: str
    date: str
    topics: List[str]
    tools: List[str]
    llms: List[str]
    impressiveness_score: float
    
    class Config:
        from_attributes = True


class PostDetail(PostBase):
    """Detailed post model including attachments and URLs"""
    attachment_urls: List[str] = []
    attachment_summaries: str = ""
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    num_reactions: int = 0
    num_replies: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GraphNode(PostBase):
    """Post with graph position data"""
    x: float
    y: float
    cluster_id: int
    attachment_urls: List[str] = []
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class GraphEdge(BaseModel):
    """Edge between two posts in graph"""
    source: int
    target: int
    similarity: float


class GraphData(BaseModel):
    """Complete graph data for visualization"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(..., min_length=1, description="Search query")
    view_mode: Optional[str] = Field(
        default='content',
        pattern='^(content|topic|tool|llm)$',
        description="View mode for semantic search"
    )
    limit: Optional[int] = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    """Search results"""
    results: List[PostDetail]
    count: int


class StatsResponse(BaseModel):
    """Database statistics"""
    posts: int
    layouts: int
    similarities: int
    view_modes: List[str] = ['topic', 'tool', 'llm']


class RefreshResponse(BaseModel):
    """Response for data refresh endpoint"""
    message: str
    status: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None

"""
Database client for Supabase integration.
Handles CRUD operations for posts, layouts, and similarities.
"""

from supabase import create_client, Client
import os
from typing import List, Dict, Optional
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def insert_post(self, post_data: Dict) -> int:
        """
        Insert post with embeddings and layouts
        
        Args:
            post_data: Dictionary containing all post information
            
        Returns:
            Database ID of the inserted post
        """
        # Prepare post row
        post_row = {
            'ed_post_id': post_data['ed_post_id'],
            'title': post_data['title'],
            'content': post_data['content'],
            'author': post_data['author'],
            'date': post_data['date'],
            'attachment_urls': post_data.get('attachment_urls', []),
            'attachment_summaries': post_data.get('attachment_summaries', ''),
            'github_url': post_data.get('github_url'),
            'website_url': post_data.get('website_url'),
            'linkedin_url': post_data.get('linkedin_url'),
            'topics': post_data['topics'],
            'tools': post_data['tools'],
            'llms': post_data['llms'],
            'content_embedding': post_data['content_embedding'] if isinstance(post_data['content_embedding'], list) else post_data['content_embedding'].tolist(),
            'topic_view_embedding': post_data['topic_view_embedding'] if isinstance(post_data['topic_view_embedding'], list) else post_data['topic_view_embedding'].tolist(),
            'tool_view_embedding': post_data['tool_view_embedding'] if isinstance(post_data['tool_view_embedding'], list) else post_data['tool_view_embedding'].tolist(),
            'llm_view_embedding': post_data['llm_view_embedding'] if isinstance(post_data['llm_view_embedding'], list) else post_data['llm_view_embedding'].tolist(),
            'impressiveness_score': post_data['impressiveness_score'],
            'num_reactions': post_data.get('num_reactions', 0),
            'num_replies': post_data.get('num_replies', 0)
        }
        
        # Insert post
        result = self.client.table('posts').upsert(
            post_row,
            on_conflict='ed_post_id'
        ).execute()
        
        post_id = result.data[0]['id']
        
        # Insert layouts for each view mode
        for view_mode in ['topic', 'tool', 'llm']:
            layout = post_data[f'{view_mode}_layout']
            
            # Delete existing layout if any
            self.client.table('graph_layouts').delete().eq(
                'post_id', post_id
            ).eq('view_mode', view_mode).execute()
            
            # Insert new layout
            self.client.table('graph_layouts').insert({
                'post_id': post_id,
                'view_mode': view_mode,
                'x': float(layout['x']),
                'y': float(layout['y']),
                'cluster_id': int(layout['cluster_id'])
            }).execute()
        
        return post_id
    
    def insert_similarity(
        self, 
        post_id_1: int, 
        post_id_2: int, 
        view_mode: str, 
        similarity: float
    ):
        """
        Insert edge similarity between two posts
        
        Args:
            post_id_1: First post's ed_post_id
            post_id_2: Second post's ed_post_id
            view_mode: View mode ('topic', 'tool', or 'llm')
            similarity: Similarity score (0-1)
        """
        # Get internal IDs
        p1 = self.client.table('posts').select('id').eq(
            'ed_post_id', post_id_1
        ).execute()
        p2 = self.client.table('posts').select('id').eq(
            'ed_post_id', post_id_2
        ).execute()
        
        if p1.data and p2.data:
            id1, id2 = p1.data[0]['id'], p2.data[0]['id']
            
            # Ensure id1 < id2 for consistency
            if id1 > id2:
                id1, id2 = id2, id1
            
            # Upsert similarity
            self.client.table('post_similarities').upsert({
                'post_id_1': id1,
                'post_id_2': id2,
                'view_mode': view_mode,
                'similarity': float(similarity)
            }, on_conflict='post_id_1,post_id_2,view_mode').execute()
    
    def get_all_posts(self) -> List[Dict]:
        """
        Get all posts from database
        
        Returns:
            List of post dictionaries
        """
        result = self.client.table('posts').select('*').execute()
        return result.data
    
    def get_post_by_id(self, post_id: int) -> Optional[Dict]:
        """
        Get a single post by database ID
        
        Args:
            post_id: Database ID of the post
            
        Returns:
            Post dictionary or None if not found
        """
        result = self.client.table('posts').select('*').eq('id', post_id).execute()
        return result.data[0] if result.data else None
    
    def get_graph_data(self, view_mode: str) -> Dict:
        """
        Get nodes and edges for graph visualization
        
        Args:
            view_mode: View mode ('topic', 'tool', or 'llm')
            
        Returns:
            Dictionary with 'nodes' and 'edges' keys
        """
        # Get all posts
        posts = self.client.table('posts').select('*').execute()
        
        # Get layouts for this view
        layouts = self.client.table('graph_layouts').select('*').eq(
            'view_mode', view_mode
        ).execute()
        
        # Create a map of post_id to layout
        layout_map = {l['post_id']: l for l in layouts.data}
        
        # Combine posts with their layouts
        nodes = []
        for post in posts.data:
            layout = layout_map.get(post['id'])
            if layout:
                node = {
                    **post,
                    'x': layout['x'],
                    'y': layout['y'],
                    'cluster_id': layout['cluster_id']
                }
                # Remove embeddings from node data to reduce payload size
                for key in ['content_embedding', 'topic_view_embedding', 
                           'tool_view_embedding', 'llm_view_embedding']:
                    node.pop(key, None)
                nodes.append(node)
        
        # Get edges for this view
        edges_result = self.client.table('post_similarities').select('*').eq(
            'view_mode', view_mode
        ).execute()
        
        edges = [
            {
                'source': edge['post_id_1'],
                'target': edge['post_id_2'],
                'similarity': edge['similarity']
            }
            for edge in edges_result.data
        ]
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def search_posts(
        self, 
        query: str, 
        view_mode: str = 'content',
        limit: int = 20
    ) -> List[Dict]:
        """
        Hybrid search: keyword + semantic
        
        Args:
            query: Search query string
            view_mode: View mode for semantic search ('content', 'topic', 'tool', or 'llm')
            limit: Maximum number of results
            
        Returns:
            List of matching posts
        """
        # Keyword search using PostgreSQL text search
        keyword_results = self.client.table('posts').select('*').or_(
            f'title.ilike.%{query}%,content.ilike.%{query}%,author.ilike.%{query}%'
        ).limit(limit).execute()
        
        results = keyword_results.data
        
        # Semantic search if query is long enough
        if len(query.split()) > 2:
            try:
                from ingestion.embedder import PostEmbedder
                embedder = PostEmbedder()
                query_emb = embedder.embed_content(query).tolist()
                
                # Determine which embedding column to use
                emb_column = f'{view_mode}_view_embedding' if view_mode != 'content' else 'content_embedding'
                
                # Use RPC function for vector similarity
                semantic_results = self.client.rpc('match_posts', {
                    'query_embedding': query_emb,
                    'match_threshold': 0.7,
                    'match_count': limit,
                    'view_column': emb_column
                }).execute()
                
                # Merge results (avoid duplicates)
                existing_ids = {p['id'] for p in results}
                for post in semantic_results.data:
                    if post['id'] not in existing_ids:
                        # Fetch full post data
                        full_post = self.get_post_by_id(post['id'])
                        if full_post:
                            results.append(full_post)
                
            except Exception as e:
                print(f"Semantic search failed: {e}")
                # Continue with keyword results only
        
        return results
    
    def clear_all_data(self):
        """Clear all posts, layouts, and similarities (for testing)"""
        self.client.table('post_similarities').delete().neq('id', 0).execute()
        self.client.table('graph_layouts').delete().neq('id', 0).execute()
        self.client.table('posts').delete().neq('id', 0).execute()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        posts_count = len(self.client.table('posts').select('id').execute().data)
        layouts_count = len(self.client.table('graph_layouts').select('id').execute().data)
        similarities_count = len(self.client.table('post_similarities').select('id').execute().data)
        
        return {
            'posts': posts_count,
            'layouts': layouts_count,
            'similarities': similarities_count
        }

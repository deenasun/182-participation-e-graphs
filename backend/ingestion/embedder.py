"""
Embedding generation using SentenceTransformers.
Creates both content embeddings and view-specific embeddings for graph visualization.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

class PostEmbedder:
    """Generate embeddings for posts using SentenceTransformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder with specified model.
        
        Args:
            model_name: Name of SentenceTransformer model to use
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
    
    def embed_content(self, text: str) -> np.ndarray:
        """
        Generate embedding for text content.
        
        Args:
            text: Text to embed
            
        Returns:
            Normalized embedding vector
        """
        return self.model.encode(text, normalize_embeddings=True)
    
    def create_view_specific_embedding(
        self, 
        content: str,
        categories: List[str],
        alpha: float = 0.4
    ) -> np.ndarray:
        """
        Fuse content and category embeddings to create view-specific embeddings.
        
        This creates embeddings that are influenced by both the content and the
        assigned categories, making different views (topic/tool/llm) produce
        meaningfully different graph layouts.
        
        Args:
            content: Post text content
            categories: List of category labels (e.g., ['RNN', 'Transformer'])
            alpha: Weight for category information (0-1). Higher = more category influence
        
        Returns:
            Normalized fused embedding
        """
        content_emb = self.embed_content(content)
        
        if not categories:
            return content_emb
        
        category_text = " ".join(categories)
        category_emb = self.embed_content(category_text)
        
        # Weighted fusion
        fused = (1 - alpha) * content_emb + alpha * category_emb
        
        # L2 normalize
        return fused / np.linalg.norm(fused)
    
    def embed_post(self, post_data: Dict, alpha: float = 0.4) -> Dict:
        """
        Generate all embeddings for a post.
        
        Creates:
        - content_embedding: General-purpose embedding
        - topic_view_embedding: Influenced by extracted topics
        - tool_view_embedding: Influenced by tool types
        - llm_view_embedding: Influenced by LLMs used
        
        Args:
            post_data: Dictionary containing post content and categories
            alpha: Category influence weight
            
        Returns:
            Dictionary with all embedding types
        """
        # Combine content with attachment summaries
        full_content = post_data['content'] + " " + post_data.get('attachment_summaries', '')
        
        return {
            'content_embedding': self.embed_content(full_content),
            'topic_view_embedding': self.create_view_specific_embedding(
                full_content, post_data.get('topics', []), alpha
            ),
            'tool_view_embedding': self.create_view_specific_embedding(
                full_content, post_data.get('tools', []), alpha
            ),
            'llm_view_embedding': self.create_view_specific_embedding(
                full_content, post_data.get('llms', []), alpha
            )
        }

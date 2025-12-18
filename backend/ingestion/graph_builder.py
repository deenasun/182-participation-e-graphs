"""
Graph layout computation using UMAP and HDBSCAN.
Computes 2D positions and clusters for graph visualization.
"""

from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple

class GraphBuilder:
    """Build graph layouts and compute similarities for visualization."""
    
    def __init__(self):
        """Initialize UMAP and HDBSCAN with default parameters."""
        self.umap = UMAP(
            n_components=2,
            n_neighbors=15,
            min_dist=0.1,
            metric='cosine',
            random_state=42
        )
        self.clusterer = HDBSCAN(min_cluster_size=5, metric='euclidean')
    
    def compute_layout(
        self, 
        embeddings: np.ndarray,
        view_mode: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute 2D positions and clusters for graph visualization.
        
        Uses UMAP for dimensionality reduction to 2D, then HDBSCAN for clustering.
        
        Args:
            embeddings: (N, D) array of embeddings
            view_mode: View mode name (for logging)
        
        Returns:
            positions: (N, 2) array of x, y coordinates
            clusters: (N,) array of cluster IDs
        """
        # Reduce to 2D using UMAP
        positions = self.umap.fit_transform(embeddings)
        
        # Cluster using HDBSCAN
        clusters = self.clusterer.fit_predict(positions)
        
        # Count clusters (excluding noise cluster -1)
        unique_clusters = set(clusters)
        n_clusters = len(unique_clusters - {-1})
        n_noise = sum(1 for c in clusters if c == -1)
        
        print(f"    Clusters: {n_clusters}, Noise points: {n_noise}")
        
        return positions, clusters
    
    def compute_similarities(
        self,
        embeddings: np.ndarray,
        threshold: float = 0.6,
        top_k: int = 5
    ) -> List[Tuple[int, int, float]]:
        """
        Compute pairwise similarities above threshold for graph edges.
        
        For each node, finds top-k most similar nodes above the threshold.
        
        Args:
            embeddings: (N, D) array of embeddings
            threshold: Minimum similarity to create an edge
            top_k: Number of most similar nodes to consider per node
        
        Returns:
            List of (post_i, post_j, similarity) tuples
        """
        # Compute pairwise cosine similarities
        similarities = cosine_similarity(embeddings)
        edges = []
        
        for i in range(len(embeddings)):
            # Get top-k most similar (excluding self)
            sim_scores = similarities[i].copy()
            sim_scores[i] = -1  # Exclude self
            
            # Get top-k indices
            top_indices = np.argsort(sim_scores)[-top_k:]
            
            for j in top_indices:
                if sim_scores[j] > threshold:
                    edges.append((
                        min(i, j),
                        max(i, j),
                        float(sim_scores[j])
                    ))
        
        # Remove duplicates (since we create edges from both directions)
        edges = list(set(edges))
        
        return edges

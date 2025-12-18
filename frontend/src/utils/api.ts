// API client for EECS 182 Post Graph backend

import axios from 'axios';
import { GraphData, Post, ViewMode, SearchRequest, SearchResponse, StatsResponse } from '../types';

// Get API URL from environment variable or default to localhost
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

export const api = {
  /**
   * Get graph data for visualization (nodes + edges)
   */
  getGraphData: async (viewMode: ViewMode): Promise<GraphData> => {
    const response = await apiClient.get(`/api/graph-data/${viewMode}`);
    return response.data;
  },

  /**
   * Get all posts
   */
  getAllPosts: async (): Promise<Post[]> => {
    const response = await apiClient.get('/api/posts');
    return response.data;
  },

  /**
   * Get a specific post by ID
   */
  getPost: async (postId: number): Promise<Post> => {
    const response = await apiClient.get(`/api/posts/${postId}`);
    return response.data;
  },

  /**
   * Search posts by keyword or semantic similarity
   */
  searchPosts: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post('/api/search', request);
    return response.data;
  },

  /**
   * Get database statistics
   */
  getStats: async (): Promise<StatsResponse> => {
    const response = await apiClient.get('/api/stats');
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Trigger data refresh (background task)
   */
  refreshData: async (): Promise<{ message: string }> => {
    const response = await apiClient.post('/api/refresh');
    return response.data;
  },
};

export default api;

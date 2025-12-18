// Custom React hooks for data fetching

import { useQuery } from '@tanstack/react-query';
import { api } from '../utils/api';
import { ViewMode, SearchRequest } from '../types';

/**
 * Hook to fetch graph data for a specific view mode
 */
export const useGraphData = (viewMode: ViewMode) => {
  return useQuery({
    queryKey: ['graphData', viewMode],
    queryFn: () => api.getGraphData(viewMode),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

/**
 * Hook to search posts
 */
export const useSearchPosts = (query: string, viewMode: string = 'content') => {
  return useQuery({
    queryKey: ['search', query, viewMode],
    queryFn: () => api.searchPosts({ query, view_mode: viewMode }),
    enabled: query.length > 0, // Only run if query is not empty
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to fetch all posts
 */
export const useAllPosts = () => {
  return useQuery({
    queryKey: ['allPosts'],
    queryFn: () => api.getAllPosts(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook to fetch database statistics
 */
export const useStats = () => {
  return useQuery({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

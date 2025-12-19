// Type definitions for EECS 182 Post Graph Application

export interface Post {
  id: number;
  ed_post_id: number;
  title: string;
  content: string;
  author: string;
  date: string;
  topics: string[];
  tools: string[];
  llms: string[];
  github_url?: string;
  website_url?: string;
  linkedin_url?: string;
  attachment_urls?: string[];
  attachment_summaries?: string;
  impressiveness_score: number;
  num_reactions?: number;
  num_replies?: number;
}

export interface GraphNode extends Post {
  x?: number;
  y?: number;
  cluster_id?: number;
}

export interface GraphEdge {
  source: number;
  target: number;
  similarity: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  cluster_names?: Record<number, string>;
}

export type ViewMode = 'topic' | 'tool' | 'llm';

export interface SearchRequest {
  query: string;
  view_mode?: string;
  limit?: number;
}

export interface SearchResponse {
  results: Post[];
  count: number;
}

export interface StatsResponse {
  posts: number;
  layouts: number;
  similarities: number;
  view_modes: string[];
}

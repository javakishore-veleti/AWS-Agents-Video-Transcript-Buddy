export interface QueryRequest {
  question: string;
  transcript_ids?: string[];
  max_results?: number;
  include_sources?: boolean;
}

export interface QuerySource {
  transcript_id: string;
  chunk_index: number;
  score: number;
  preview: string;
}

export interface QueryResponse {
  success: boolean;
  query: string;
  answer: string;
  sources: QuerySource[];
  confidence: number;
  timestamp?: string;
}

export interface SearchRequest {
  query: string;
  transcript_ids?: string[];
  max_results?: number;
  min_score?: number;
}

export interface SearchResult {
  id: string;
  content: string;
  transcript_id: string;
  chunk_index: number;
  score: number;
  highlights?: string[];
}

export interface SearchResponse {
  success: boolean;
  query: string;
  results: SearchResult[];
  total_results: number;
}

export interface SuggestionsResponse {
  success: boolean;
  suggestions: string[];
  transcript_id?: string;
}

export interface ValidationResponse {
  valid: boolean;
  message: string;
  suggestions?: string[];
}
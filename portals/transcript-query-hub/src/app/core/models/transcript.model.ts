export interface Transcript {
  filename: string;
  content?: string;
  size?: number;
  uploaded_at?: string;
  indexed?: boolean;
  chunk_count?: number;
  metadata?: Record<string, any>;
}

export interface TranscriptListResponse {
  success: boolean;
  transcripts: Transcript[];
  count: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  filename: string;
  size: number;
  indexed: boolean;
  chunks_created?: number;
}

export interface DeleteResponse {
  success: boolean;
  message: string;
  filename: string;
}

export interface ReindexResponse {
  success: boolean;
  message: string;
  filename?: string;
  chunks_indexed?: number;
  total_indexed?: number;
}

export interface TranscriptDetailResponse {
  success: boolean;
  transcript: Transcript;
}
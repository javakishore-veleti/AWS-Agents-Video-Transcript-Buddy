export interface Transcript {
  id: string;  // Transcript UUID for querying
  filename: string;
  conversation_id?: string;  // Encrypted conversation ID
  content?: string;
  size?: number;
  file_size?: number;  // Backend uses file_size
  uploaded_at?: string;
  indexed?: boolean;
  is_indexed?: boolean;  // Backend uses is_indexed
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
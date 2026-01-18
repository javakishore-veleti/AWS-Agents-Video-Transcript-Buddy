import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from './api.service';
import { 
  Transcript, 
  TranscriptListResponse, 
  UploadResponse, 
  DeleteResponse,
  ReindexResponse 
} from '../models/transcript.model';

@Injectable({
  providedIn: 'root'
})
export class TranscriptService {
  private transcriptsSubject = new BehaviorSubject<Transcript[]>([]);
  public transcripts$ = this.transcriptsSubject.asObservable();

  private loadingSubject = new BehaviorSubject<boolean>(false);
  public loading$ = this.loadingSubject.asObservable();

  constructor(private api: ApiService) {}

  /**
   * Get all transcripts, optionally filtered by conversation
   * @param conversationId Optional encrypted conversation ID to filter by
   */
  getTranscripts(conversationId?: string): Observable<TranscriptListResponse> {
    this.loadingSubject.next(true);
    let url = '/api/transcripts/';
    if (conversationId) {
      url += `?conversation_id=${encodeURIComponent(conversationId)}`;
    }
    return this.api.get<TranscriptListResponse>(url).pipe(
      tap({
        next: (response) => {
          this.transcriptsSubject.next(response.transcripts || []);
          this.loadingSubject.next(false);
        },
        error: () => this.loadingSubject.next(false)
      })
    );
  }

  /**
   * Alias for getTranscripts
   */
  listTranscripts(conversationId?: string): Observable<TranscriptListResponse> {
    return this.getTranscripts(conversationId);
  }

  /**
   * Get single transcript by filename
   */
  getTranscript(filename: string): Observable<Transcript> {
    return this.api.get<Transcript>(`/api/transcripts/${filename}`);
  }

  /**
   * Upload a new transcript
   * @param file The file to upload
   * @param autoIndex Whether to auto-index the transcript
   * @param conversationId Encrypted conversation ID (from API)
   */
  uploadTranscript(file: File, autoIndex: boolean = true, conversationId?: string): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    // Build URL with query parameters
    let url = `/api/transcripts/upload?auto_index=${autoIndex}`;
    if (conversationId !== undefined && conversationId !== null) {
      url += `&conversation_id=${encodeURIComponent(conversationId)}`;
    }
    
    return this.api.upload<UploadResponse>(url, formData).pipe(
      tap(() => this.getTranscripts().subscribe())
    );
  }

  /**
   * Delete a transcript
   */
  deleteTranscript(filename: string): Observable<DeleteResponse> {
    return this.api.delete<DeleteResponse>(`/api/transcripts/${filename}`).pipe(
      tap(() => this.getTranscripts().subscribe())
    );
  }

  /**
   * Reindex a transcript
   */
  reindexTranscript(filename: string): Observable<ReindexResponse> {
    return this.api.post<ReindexResponse>(`/api/transcripts/${filename}/reindex`, {});
  }

  /**
   * Reindex all transcripts
   */
  reindexAll(): Observable<ReindexResponse> {
    return this.api.post<ReindexResponse>('/api/transcripts/reindex-all', {});
  }

  /**
   * Check if transcript exists
   */
  checkExists(filename: string): Observable<boolean> {
    return this.api.get<boolean>(`/api/transcripts/${filename}/exists`);
  }
}
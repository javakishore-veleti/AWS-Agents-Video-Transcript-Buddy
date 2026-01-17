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
   * Get all transcripts
   */
  getTranscripts(): Observable<TranscriptListResponse> {
    this.loadingSubject.next(true);
    return this.api.get<TranscriptListResponse>('/api/transcripts').pipe(
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
   * Get single transcript by filename
   */
  getTranscript(filename: string): Observable<Transcript> {
    return this.api.get<Transcript>(`/api/transcripts/${filename}`);
  }

  /**
   * Upload a new transcript
   */
  uploadTranscript(file: File, autoIndex: boolean = true): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('auto_index', String(autoIndex));
    
    return this.api.upload<UploadResponse>('/api/transcripts/upload', formData).pipe(
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
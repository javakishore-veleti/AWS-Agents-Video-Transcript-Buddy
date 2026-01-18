import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, finalize } from 'rxjs/operators';
import { ApiService } from './api.service';
import { 
  QueryRequest, 
  QueryResponse, 
  SearchRequest, 
  SearchResponse,
  SuggestionsResponse 
} from '../models/query.model';

@Injectable({
  providedIn: 'root'
})
export class QueryService {
  private loadingSubject = new BehaviorSubject<boolean>(false);
  public loading$ = this.loadingSubject.asObservable();

  private queryHistorySubject = new BehaviorSubject<QueryResponse[]>([]);
  public queryHistory$ = this.queryHistorySubject.asObservable();

  constructor(private api: ApiService) {}

  /**
   * Submit a natural language query
   */
  query(request: QueryRequest): Observable<QueryResponse> {
    this.loadingSubject.next(true);
    
    return this.api.post<QueryResponse>('/api/query/', request).pipe(
      tap((response) => {
        // Add to history
        const history = this.queryHistorySubject.value;
        this.queryHistorySubject.next([response, ...history].slice(0, 20));
      }),
      finalize(() => this.loadingSubject.next(false))
    );
  }

  /**
   * Perform a semantic search
   */
  search(request: SearchRequest): Observable<SearchResponse> {
    this.loadingSubject.next(true);
    
    return this.api.post<SearchResponse>('/api/query/search', request).pipe(
      finalize(() => this.loadingSubject.next(false))
    );
  }

  /**
   * Validate a query
   */
  validateQuery(query: string): Observable<{ valid: boolean; message: string }> {
    return this.api.post<{ valid: boolean; message: string }>(
      '/api/query/validate', 
      { query }
    );
  }

  /**
   * Get suggested questions for a transcript
   */
  getSuggestions(transcriptId?: string): Observable<SuggestionsResponse> {
    const params: { [key: string]: string } = {};
    if (transcriptId) {
      params['transcript_id'] = transcriptId;
    }
    return this.api.get<SuggestionsResponse>('/api/query/suggestions', Object.keys(params).length > 0 ? params : undefined);
  }

  /**
   * Clear query history
   */
  clearHistory(): void {
    this.queryHistorySubject.next([]);
  }

  /**
   * Get loading state
   */
  isLoading(): boolean {
    return this.loadingSubject.value;
  }
}
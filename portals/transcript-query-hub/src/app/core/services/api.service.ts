import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * GET request
   */
  get<T>(endpoint: string, params?: HttpParams | { [key: string]: string }): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, { params })
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  /**
   * POST request
   */
  post<T>(endpoint: string, body: any, options?: { headers?: HttpHeaders }): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * PUT request
   */
  put<T>(endpoint: string, body: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, body)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * PATCH request
   */
  patch<T>(endpoint: string, body: any): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${endpoint}`, body)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * DELETE request
   */
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Upload file with FormData
   */
  upload<T>(endpoint: string, formData: FormData): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, formData, {
      reportProgress: true,
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Error handler
   */
  private handleError(error: any) {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.message || error.message || `Error Code: ${error.status}`;
    }
    
    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
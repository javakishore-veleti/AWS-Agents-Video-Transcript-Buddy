import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ToastService } from '../services/toast.service';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private toast: ToastService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unexpected error occurred';

        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = error.error.message;
        } else {
          // Server-side error
          switch (error.status) {
            case 0:
              errorMessage = 'Unable to connect to server. Please check your connection.';
              break;
            case 400:
              errorMessage = error.error?.message || 'Bad request. Please check your input.';
              break;
            case 401:
              errorMessage = 'Unauthorized. Please login again.';
              break;
            case 403:
              errorMessage = 'Access denied. You don\'t have permission.';
              break;
            case 404:
              errorMessage = error.error?.message || 'Resource not found.';
              break;
            case 422:
              errorMessage = error.error?.message || 'Validation error. Please check your input.';
              break;
            case 429:
              errorMessage = 'Too many requests. Please slow down.';
              break;
            case 500:
              errorMessage = 'Server error. Please try again later.';
              break;
            case 502:
            case 503:
            case 504:
              errorMessage = 'Service unavailable. Please try again later.';
              break;
            default:
              errorMessage = error.error?.message || `Error: ${error.status}`;
          }
        }

        // Show toast notification for errors (except 401 which might redirect)
        if (error.status !== 401) {
          this.toast.error(errorMessage);
        }

        console.error('HTTP Error:', {
          status: error.status,
          message: errorMessage,
          url: request.url,
          error: error.error
        });

        return throwError(() => ({
          status: error.status,
          message: errorMessage,
          originalError: error
        }));
      })
    );
  }
}
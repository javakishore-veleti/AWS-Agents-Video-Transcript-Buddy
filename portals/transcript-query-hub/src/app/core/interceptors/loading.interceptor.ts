import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { LoadingService } from '../services/loading.service';

@Injectable()
export class LoadingInterceptor implements HttpInterceptor {
  private activeRequests = 0;

  constructor(private loadingService: LoadingService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Skip loading indicator for certain requests
    if (this.shouldSkipLoading(request)) {
      return next.handle(request);
    }

    this.activeRequests++;
    
    if (this.activeRequests === 1) {
      this.loadingService.show();
    }

    return next.handle(request).pipe(
      finalize(() => {
        this.activeRequests--;
        
        if (this.activeRequests === 0) {
          this.loadingService.hide();
        }
      })
    );
  }

  private shouldSkipLoading(request: HttpRequest<unknown>): boolean {
    // Skip loading for health checks and background requests
    const skipUrls = ['/health', '/api/query/validate'];
    return skipUrls.some(url => request.url.includes(url));
  }
}
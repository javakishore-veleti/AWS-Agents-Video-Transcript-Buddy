import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpHeaders
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class ApiInterceptor implements HttpInterceptor {
  constructor() {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Clone request and add headers
    const modifiedRequest = request.clone({
      headers: this.addHeaders(request.headers),
    });

    return next.handle(modifiedRequest);
  }

  private addHeaders(headers: HttpHeaders): HttpHeaders {
    // Add common headers
    let modifiedHeaders = headers;

    // Add Content-Type if not FormData
    if (!headers.has('Content-Type') && !(headers.get('Content-Type') === 'multipart/form-data')) {
      modifiedHeaders = modifiedHeaders.set('Content-Type', 'application/json');
    }

    // Add Accept header
    if (!headers.has('Accept')) {
      modifiedHeaders = modifiedHeaders.set('Accept', 'application/json');
    }

    // Add custom headers if needed
    modifiedHeaders = modifiedHeaders.set('X-Client', 'TranscriptQuery-Hub');
    modifiedHeaders = modifiedHeaders.set('X-Client-Version', '1.0.0');

    return modifiedHeaders;
  }
}
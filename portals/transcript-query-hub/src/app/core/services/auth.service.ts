import { Injectable, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap, BehaviorSubject } from 'rxjs';
import { ApiService } from './api.service';
import { StorageService } from './storage.service';
import { AuthResponse, LoginRequest, RegisterRequest, User, TokenResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'user';

  private userSubject = new BehaviorSubject<User | null>(this.getStoredUser());
  public user$ = this.userSubject.asObservable();
  
  private isAuthenticatedSignal = signal(!!this.getToken());
  public isAuthenticated = computed(() => this.isAuthenticatedSignal());

  constructor(
    private api: ApiService,
    private storage: StorageService,
    private router: Router
  ) {}

  /**
   * Login user
   */
  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.api.post<AuthResponse>('/api/auth/login', credentials).pipe(
      tap(response => {
        if (response.success && response.data) {
          this.setSession(response.data);
        }
      })
    );
  }

  /**
   * Register new user
   */
  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.api.post<AuthResponse>('/api/auth/register', data).pipe(
      tap(response => {
        if (response.success && response.data) {
          this.setSession(response.data);
        }
      })
    );
  }

  /**
   * Refresh access token
   */
  refreshToken(): Observable<TokenResponse> {
    const refreshToken = this.storage.getItem(this.REFRESH_TOKEN_KEY);
    return this.api.post<TokenResponse>('/api/auth/refresh', { refresh_token: refreshToken }).pipe(
      tap(response => {
        if (response.success && response.data) {
          this.storage.setItem(this.TOKEN_KEY, response.data.access_token);
        }
      })
    );
  }

  /**
   * Logout user
   */
  logout(): void {
    this.storage.removeItem(this.TOKEN_KEY);
    this.storage.removeItem(this.REFRESH_TOKEN_KEY);
    this.storage.removeItem(this.USER_KEY);
    this.userSubject.next(null);
    this.isAuthenticatedSignal.set(false);
    this.router.navigate(['/login']);
  }

  /**
   * Set user session
   */
  private setSession(data: AuthResponse['data']): void {
    this.storage.setItem(this.TOKEN_KEY, data.access_token);
    this.storage.setItem(this.REFRESH_TOKEN_KEY, data.refresh_token);
    this.storage.setItem(this.USER_KEY, JSON.stringify(data.user));
    this.userSubject.next(data.user);
    this.isAuthenticatedSignal.set(true);
  }

  /**
   * Get access token
   */
  getToken(): string | null {
    return this.storage.getItem(this.TOKEN_KEY);
  }

  /**
   * Get refresh token
   */
  getRefreshToken(): string | null {
    return this.storage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.userSubject.value;
  }

  /**
   * Get stored user from storage
   */
  private getStoredUser(): User | null {
    const userStr = this.storage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if user is authenticated
   */
  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}

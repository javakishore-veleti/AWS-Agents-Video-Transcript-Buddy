import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoadingService {
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private loadingMap = new Map<string, boolean>();

  public loading$: Observable<boolean> = this.loadingSubject.asObservable();

  constructor() {}

  /**
   * Show global loading indicator
   */
  show(): void {
    this.loadingSubject.next(true);
  }

  /**
   * Hide global loading indicator
   */
  hide(): void {
    this.loadingSubject.next(false);
  }

  /**
   * Set loading state for a specific key
   */
  setLoading(key: string, loading: boolean): void {
    if (loading) {
      this.loadingMap.set(key, true);
    } else {
      this.loadingMap.delete(key);
    }
    
    this.loadingSubject.next(this.loadingMap.size > 0);
  }

  /**
   * Check if currently loading
   */
  isLoading(): boolean {
    return this.loadingSubject.value;
  }

  /**
   * Check if specific key is loading
   */
  isLoadingKey(key: string): boolean {
    return this.loadingMap.has(key);
  }

  /**
   * Clear all loading states
   */
  clear(): void {
    this.loadingMap.clear();
    this.loadingSubject.next(false);
  }
}
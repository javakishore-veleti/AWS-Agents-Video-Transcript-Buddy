import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StorageService {
  private prefix = 'tq_hub_';

  /**
   * Set item in localStorage
   */
  set<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(this.prefix + key, serialized);
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  /**
   * Get item from localStorage
   */
  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(this.prefix + key);
      if (item === null) {
        return defaultValue ?? null;
      }
      return JSON.parse(item) as T;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue ?? null;
    }
  }

  /**
   * Remove item from localStorage
   */
  remove(key: string): void {
    localStorage.removeItem(this.prefix + key);
  }

  /**
   * Clear all app-related items from localStorage
   */
  clear(): void {
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.prefix)) {
        keysToRemove.push(key);
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  /**
   * Check if key exists
   */
  has(key: string): boolean {
    return localStorage.getItem(this.prefix + key) !== null;
  }

  /**
   * Get all keys with prefix
   */
  keys(): string[] {
    const keys: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.prefix)) {
        keys.push(key.replace(this.prefix, ''));
      }
    }
    
    return keys;
  }

  // Session Storage methods

  /**
   * Set item in sessionStorage
   */
  setSession<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      sessionStorage.setItem(this.prefix + key, serialized);
    } catch (error) {
      console.error('Error saving to sessionStorage:', error);
    }
  }

  /**
   * Get item from sessionStorage
   */
  getSession<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = sessionStorage.getItem(this.prefix + key);
      if (item === null) {
        return defaultValue ?? null;
      }
      return JSON.parse(item) as T;
    } catch (error) {
      console.error('Error reading from sessionStorage:', error);
      return defaultValue ?? null;
    }
  }

  /**
   * Remove item from sessionStorage
   */
  removeSession(key: string): void {
    sessionStorage.removeItem(this.prefix + key);
  }
}
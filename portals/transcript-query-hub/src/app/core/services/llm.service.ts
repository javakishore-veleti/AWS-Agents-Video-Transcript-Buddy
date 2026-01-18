import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export type ProviderStatus = 'available' | 'coming_soon' | 'beta' | 'deprecated';

export interface LLMProviderInfo {
  provider: string;
  name: string;
  description: string;
  available: boolean;
  status: ProviderStatus;
  models: string[];
  requires_api_key: boolean;
  is_local: boolean;
  endpoint?: string;
  eta?: string;  // For coming soon features
}

export interface ModelInfo {
  name: string;
  description?: string;
}

export interface RecommendedModels {
  openai: ModelInfo[];
  ollama: ModelInfo[];
  lmstudio: ModelInfo[];
}

export interface TestConnectionResponse {
  success: boolean;
  message: string;
  models?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class LLMService {
  private http = inject(HttpClient);
  private baseUrl = '/api/llm';

  /**
   * List all available LLM providers
   */
  listProviders(): Observable<LLMProviderInfo[]> {
    return this.http.get<LLMProviderInfo[]>(`${this.baseUrl}/providers/`);
  }

  /**
   * Get available models for a specific provider
   */
  getProviderModels(provider: string, baseUrl?: string): Observable<string[]> {
    let url = `${this.baseUrl}/providers/${provider}/models/`;
    if (baseUrl) {
      url += `?base_url=${encodeURIComponent(baseUrl)}`;
    }
    return this.http.get<string[]>(url);
  }

  /**
   * Test connection to a provider
   */
  testConnection(provider: string, baseUrl?: string, apiKey?: string): Observable<TestConnectionResponse> {
    return this.http.post<TestConnectionResponse>(`${this.baseUrl}/providers/test/`, {
      provider,
      base_url: baseUrl,
      api_key: apiKey
    });
  }

  /**
   * Get recommended models for each provider
   */
  getRecommendedModels(): Observable<RecommendedModels> {
    return this.http.get<RecommendedModels>(`${this.baseUrl}/recommended-models/`);
  }
}

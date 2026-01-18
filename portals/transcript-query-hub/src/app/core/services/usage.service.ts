import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { UsageSummary, UsageLimits, PricingInfo, UsageResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class UsageService {
  constructor(private api: ApiService) {}

  /**
   * Get usage summary for current month
   */
  getSummary(month?: number, year?: number): Observable<UsageResponse<UsageSummary>> {
    const params: any = {};
    if (month) params.month = month.toString();
    if (year) params.year = year.toString();
    
    return this.api.get<UsageResponse<UsageSummary>>('/api/usage/summary', params);
  }

  /**
   * Get usage limits
   */
  getLimits(): Observable<UsageResponse<UsageLimits>> {
    return this.api.get<UsageResponse<UsageLimits>>('/api/usage/limits');
  }

  /**
   * Get pricing information
   */
  getPricing(): Observable<UsageResponse<PricingInfo>> {
    return this.api.get<UsageResponse<PricingInfo>>('/api/usage/pricing');
  }
}

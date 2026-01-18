import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsageService, ToastService, AuthService } from '../../core/services';
import { UsageSummary, UsageLimits, PricingInfo } from '../../core/models';

@Component({
  selector: 'app-usage',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Usage & Billing</h1>
          <p class="mt-2 text-gray-600">Track your usage, costs, and subscription limits</p>
        </div>

        <!-- Current Tier -->
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-6 mb-8 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-blue-100 uppercase tracking-wide">Current Plan</p>
              <h2 class="text-3xl font-bold mt-1">{{ user?.tier || 'FREE' }}</h2>
              <p class="text-blue-100 mt-2" *ngIf="pricingInfo">
                {{ getTierPrice() }}
              </p>
            </div>
            <button class="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors">
              Upgrade Plan
            </button>
          </div>
        </div>

        <!-- Usage Summary -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          
          <!-- Total Cost -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="flex items-center">
              <div class="p-3 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Total Cost This Month</p>
                <p class="text-2xl font-bold text-gray-900">
                  \${{ summary?.total_cost?.toFixed(2) || '0.00' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Uploads -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="flex items-center">
              <div class="p-3 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Uploads This Month</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ summary?.uploads?.count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  \${{ summary?.uploads?.cost?.toFixed(2) || '0.00' }} cost
                </p>
              </div>
            </div>
          </div>

          <!-- Queries -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="flex items-center">
              <div class="p-3 bg-purple-100 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Queries This Month</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ summary?.queries?.total_count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  \${{ summary?.queries?.cost?.toFixed(2) || '0.00' }} cost
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Usage Limits -->
        <div class="bg-white rounded-xl shadow-sm p-6 mb-8" *ngIf="limits">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Usage Limits</h3>
          
          <div class="space-y-6">
            <!-- Upload Limits -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-medium text-gray-700">Uploads</span>
                <span class="text-sm text-gray-600">
                  {{ limits.uploads.current }} / {{ limits.uploads.limit === -1 || limits.uploads.limit === 'unlimited' ? '∞' : limits.uploads.limit }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all"
                  [class.bg-green-500]="getUsagePercent(limits.uploads) < 70"
                  [class.bg-yellow-500]="getUsagePercent(limits.uploads) >= 70 && getUsagePercent(limits.uploads) < 90"
                  [class.bg-red-500]="getUsagePercent(limits.uploads) >= 90"
                  [style.width.%]="getUsagePercent(limits.uploads)"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1" *ngIf="limits.uploads.remaining !== 'unlimited'">
                {{ limits.uploads.remaining }} remaining
              </p>
            </div>

            <!-- Query Limits -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-medium text-gray-700">Queries</span>
                <span class="text-sm text-gray-600">
                  {{ limits.queries.current }} / {{ limits.queries.limit === -1 || limits.queries.limit === 'unlimited' ? '∞' : limits.queries.limit }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all"
                  [class.bg-green-500]="getUsagePercent(limits.queries) < 70"
                  [class.bg-yellow-500]="getUsagePercent(limits.queries) >= 70 && getUsagePercent(limits.queries) < 90"
                  [class.bg-red-500]="getUsagePercent(limits.queries) >= 90"
                  [style.width.%]="getUsagePercent(limits.queries)"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1" *ngIf="limits.queries.remaining !== 'unlimited'">
                {{ limits.queries.remaining }} remaining
              </p>
            </div>
          </div>
        </div>

        <!-- Pricing Information -->
        <div class="bg-white rounded-xl shadow-sm p-6" *ngIf="pricingInfo">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Pricing Details</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Pay-as-you-go -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-3">Pay-as-you-go Rates</h4>
              <dl class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <dt class="text-gray-600">Upload (per MB)</dt>
                  <dd class="font-medium text-gray-900">\${{ pricingInfo.pay_as_you_go.upload_per_mb.toFixed(2) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-gray-600">Simple Query</dt>
                  <dd class="font-medium text-gray-900">\${{ pricingInfo.pay_as_you_go.query_simple.toFixed(2) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-gray-600">Complex Query</dt>
                  <dd class="font-medium text-gray-900">\${{ pricingInfo.pay_as_you_go.query_complex.toFixed(2) }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-gray-600">Innovation Fee</dt>
                  <dd class="font-medium text-gray-900">{{ (pricingInfo.pay_as_you_go.innovation_fee_percent * 100).toFixed(0) }}%</dd>
                </div>
              </dl>
            </div>

            <!-- Available Tiers -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-3">Available Plans</h4>
              <div class="space-y-2">
                <div *ngFor="let tier of getAvailableTiers()" 
                     class="p-3 rounded-lg border"
                     [class.border-blue-500]="tier.name === user?.tier"
                     [class.bg-blue-50]="tier.name === user?.tier"
                     [class.border-gray-200]="tier.name !== user?.tier">
                  <div class="flex justify-between items-start">
                    <div>
                      <p class="font-medium text-gray-900">{{ tier.name }}</p>
                      <p class="text-xs text-gray-600 mt-1">
                        {{ tier.info.max_uploads === -1 ? '∞' : tier.info.max_uploads }} uploads, 
                        {{ tier.info.max_queries === -1 ? '∞' : tier.info.max_queries }} queries/mo
                      </p>
                    </div>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ tier.info.monthly_price === -1 ? 'Custom' : '$' + tier.info.monthly_price + '/mo' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div *ngIf="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p class="text-gray-600 mt-4">Loading usage data...</p>
        </div>
      </div>
    </div>
  `
})
export class UsageComponent implements OnInit {
  summary: UsageSummary | null = null;
  limits: UsageLimits | null = null;
  pricingInfo: PricingInfo | null = null;
  loading = false;
  user = this.authService.getCurrentUser();

  constructor(
    private usageService: UsageService,
    private authService: AuthService,
    private toast: ToastService
  ) {}

  ngOnInit(): void {
    this.loadUsageData();
  }

  loadUsageData(): void {
    this.loading = true;

    // Load all usage data in parallel
    Promise.all([
      this.usageService.getSummary().toPromise(),
      this.usageService.getLimits().toPromise(),
      this.usageService.getPricing().toPromise()
    ]).then(([summaryRes, limitsRes, pricingRes]) => {
      this.summary = summaryRes?.data || null;
      this.limits = limitsRes?.data || null;
      this.pricingInfo = pricingRes?.data || null;
      this.loading = false;
    }).catch(error => {
      this.toast.error('Failed to load usage data', error.message);
      this.loading = false;
    });
  }

  getUsagePercent(limit: any): number {
    if (limit.limit === -1 || limit.limit === 'unlimited') {
      return 0;
    }
    return Math.min((limit.current / limit.limit) * 100, 100);
  }

  getTierPrice(): string {
    if (!this.pricingInfo || !this.user) return '';
    const tierInfo = this.pricingInfo.tiers[this.user.tier];
    if (!tierInfo) return '';
    return tierInfo.monthly_price === -1 ? 'Custom Pricing' : tierInfo.monthly_price === 0 ? 'Free' : `$${tierInfo.monthly_price}/month`;
  }

  getAvailableTiers(): Array<{name: string, info: any}> {
    if (!this.pricingInfo) return [];
    return Object.entries(this.pricingInfo.tiers).map(([name, info]) => ({
      name,
      info
    }));
  }
}

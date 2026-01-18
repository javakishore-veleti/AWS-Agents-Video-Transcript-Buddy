export interface UsageSummary {
  user_id: string;
  period: string;
  uploads: {
    count: number;
    cost: number;
  };
  queries: {
    simple_count: number;
    complex_count: number;
    total_count: number;
    cost: number;
  };
  total_cost: number;
}

export interface UsageLimits {
  tier: string;
  uploads: {
    allowed: boolean;
    current: number;
    limit: number | string;
    remaining: number | string;
    reason?: string;
  };
  queries: {
    allowed: boolean;
    current: number;
    limit: number | string;
    remaining: number | string;
    reason?: string;
  };
}

export interface TierInfo {
  monthly_price: number;
  max_uploads: number;
  max_queries: number;
  max_file_size_mb: number;
}

export interface PricingInfo {
  tiers: Record<string, TierInfo>;
  pay_as_you_go: {
    upload_per_mb: number;
    query_simple: number;
    query_complex: number;
    transcription_per_minute: number;
    model_surcharge: Record<string, number>;
    innovation_fee_percent: number;
  };
}

export interface UsageResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

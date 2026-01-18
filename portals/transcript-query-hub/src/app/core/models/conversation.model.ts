/**
 * Conversation Models
 * 
 * Note: id and user_id are encrypted strings for security.
 * The backend encrypts these IDs using per-user encryption keys.
 */

// Extended to include coming soon providers
export type LLMProvider = 
  | 'openai' 
  | 'ollama' 
  | 'lmstudio' 
  | 'gemini'   // Coming Soon
  | 'claude'   // Coming Soon
  | 'copilot'  // Coming Soon
  | 'n8n'      // Coming Soon
  | 'mcp';     // Coming Soon

export interface Conversation {
  id: string;  // Encrypted ID
  name: string;
  user_id: string;  // Encrypted user ID
  description?: string;
  // LLM Settings
  llm_provider?: LLMProvider;
  llm_model?: string;
  llm_temperature?: number;
  llm_base_url?: string;
  // MCP Server (Coming Soon)
  mcp_server_id?: string;
  // Lock status (for tier downgrades)
  is_locked?: boolean;
  lock_reason?: string;
  locked_at?: string;
  // Statistics
  file_count: number;
  query_count: number;
  total_size_mb: number;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
}

export interface CreateConversationRequest {
  name?: string;
  description?: string;
  llm_provider?: LLMProvider;
  llm_model?: string;
  llm_temperature?: number;
  llm_base_url?: string;
}

export interface UpdateConversationRequest {
  name?: string;
  description?: string;
  llm_provider?: LLMProvider;
  llm_model?: string;
  llm_temperature?: number;
  llm_base_url?: string;
}

export interface ConversationLimits {
  max_conversations: number;
  max_files_per_conversation: number;
  max_queries_per_conversation: number;
  max_query_time_seconds: number;
}

export interface DowngradeValidation {
  can_downgrade: boolean;
  reason?: string;
  current_count?: number;
  max_allowed?: number;
  excess_count?: number;
  action_required?: string;
  violations?: Array<{
    conversation_id: string;  // Encrypted ID
    conversation_name: string;
    current_files: number;
    max_allowed: number;
    excess: number;
  }>;
  message?: string;
}

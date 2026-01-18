import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranscriptService, QueryService, ToastService, ConversationService } from '../../core/services';
import { LLMService, LLMProviderInfo } from '../../core/services/llm.service';
import { Transcript } from '../../core/models';
import { LLMProvider } from '../../core/models/conversation.model';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="min-h-screen bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-2xl shadow-lg overflow-hidden" style="height: calc(100vh - 8rem);">
          
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white">
            <div class="flex items-center justify-between">
              <div>
                <h1 class="text-2xl font-bold">Transcript Chat</h1>
                <p class="text-sm text-blue-100 mt-1">
                  @if (selectedConversation()) {
                    {{ selectedConversation()!.name }} • {{ selectedConversation()!.file_count }} files
                  } @else {
                    No conversation selected
                  }
                </p>
              </div>
              <a routerLink="/conversations" class="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm transition-colors">
                Change Conversation
              </a>
            </div>
          </div>

          <div class="flex h-full" style="height: calc(100% - 80px);">
            
            <!-- Sidebar - File Selection & AI Settings -->
            <div class="w-80 border-r border-gray-200 bg-gray-50 overflow-y-auto">
              <div class="p-4">
                <!-- AI Model Settings -->
                <div class="mb-6">
                  <h2 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    AI Model
                  </h2>
                  
                  <!-- Available Providers -->
                  <div class="mb-3">
                    <label class="block text-xs font-medium text-gray-600 mb-1">Provider</label>
                    <div class="space-y-1">
                      @for (provider of availableProviders(); track provider.provider) {
                        <button
                          type="button"
                          (click)="selectProvider(provider)"
                          [class.ring-2]="formProvider === provider.provider"
                          [class.ring-blue-500]="formProvider === provider.provider"
                          [class.bg-blue-50]="formProvider === provider.provider"
                          [disabled]="!provider.available"
                          class="w-full p-2 border rounded text-left transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 text-xs flex items-center justify-between">
                          <div>
                            <span class="font-medium">{{ provider.name }}</span>
                            <span class="text-gray-500 ml-1">{{ provider.description }}</span>
                          </div>
                          <span [class.text-green-600]="provider.available" [class.text-gray-400]="!provider.available">
                            {{ provider.available ? (provider.is_local ? '✓ Local' : '✓ Cloud') : '✗' }}
                          </span>
                        </button>
                      }
                    </div>
                  </div>
                  
                  <!-- Coming Soon Providers (collapsed) -->
                  <details class="mb-3">
                    <summary class="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                      More providers coming soon...
                    </summary>
                    <div class="mt-2 space-y-1">
                      @for (provider of comingSoonProviders(); track provider.provider) {
                        <div class="p-2 border border-dashed rounded text-xs text-gray-400 flex items-center justify-between">
                          <div>
                            <span class="font-medium">{{ provider.name }}</span>
                            <span class="ml-1">{{ provider.description }}</span>
                          </div>
                          <span class="bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded text-[10px] font-medium">
                            {{ provider.eta || 'Coming Soon' }}
                          </span>
                        </div>
                      }
                    </div>
                  </details>
                  
                  <!-- Model Selection -->
                  <div class="mb-3">
                    <label class="block text-xs font-medium text-gray-600 mb-1">Model</label>
                    @if (loadingModels()) {
                      <div class="text-gray-500 text-xs">Loading...</div>
                    } @else if (availableModels().length > 0) {
                      <select
                        [(ngModel)]="formModel"
                        (ngModelChange)="saveConversationSettings()"
                        class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        @for (model of availableModels(); track model) {
                          <option [value]="model">{{ model }}</option>
                        }
                      </select>
                    } @else {
                      <div class="text-gray-500 text-xs">
                        @if (formProvider === 'ollama') {
                          Run: <code class="bg-gray-100 px-1 rounded">ollama pull llama3.2</code>
                        } @else if (formProvider === 'lmstudio') {
                          Load a model in LM Studio
                        } @else {
                          No models available
                        }
                      </div>
                    }
                  </div>
                  
                  <!-- Temperature -->
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">
                      Temperature: {{ formTemperature }}
                    </label>
                    <input
                      type="range"
                      [(ngModel)]="formTemperature"
                      (ngModelChange)="saveConversationSettings()"
                      min="0"
                      max="1"
                      step="0.1"
                      class="w-full h-1.5">
                    <div class="flex justify-between text-xs text-gray-400">
                      <span>Precise</span>
                      <span>Creative</span>
                    </div>
                  </div>
                  
                  @if (selectedProviderInfo()?.is_local) {
                    <p class="text-xs text-green-600 mt-2">🔒 Local - Free & Private</p>
                  } @else if (selectedProviderInfo() && !selectedProviderInfo()?.is_local) {
                    <p class="text-xs text-amber-600 mt-2">☁️ Cloud - API costs may apply</p>
                  }
                </div>
                
                <hr class="mb-4 border-gray-200">
                
                <!-- Transcript Selection -->
                <h2 class="text-lg font-semibold text-gray-900 mb-2">Select Transcripts</h2>
                @if (selectedConversation()) {
                  <p class="text-xs text-gray-600 mb-4">From: {{ selectedConversation()!.name }}</p>
                } @else {
                  <div class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p class="text-sm text-yellow-800">No conversation selected</p>
                    <a routerLink="/conversations" class="text-sm text-yellow-900 font-medium hover:underline">
                      Select a conversation →
                    </a>
                  </div>
                }
                
                <div *ngIf="loading" class="text-center py-8">
                  <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p class="text-sm text-gray-600 mt-2">Loading transcripts...</p>
                </div>

                <div *ngIf="!loading && transcripts.length === 0" class="text-center py-8 text-gray-500">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  <p class="mt-2">No transcripts found</p>
                  <a href="/upload" class="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block">Upload some transcripts</a>
                </div>

                <div class="space-y-2" *ngIf="!loading">
                  <div 
                    *ngFor="let transcript of transcripts"
                    (click)="toggleTranscript(transcript.id)"
                    class="p-3 rounded-lg border cursor-pointer transition-all"
                    [class.border-blue-500]="selectedTranscriptIds().includes(transcript.id)"
                    [class.bg-blue-50]="selectedTranscriptIds().includes(transcript.id)"
                    [class.border-gray-200]="!selectedTranscriptIds().includes(transcript.id)"
                    [class.hover:border-gray-300]="!selectedTranscriptIds().includes(transcript.id)"
                  >
                    <div class="flex items-start">
                      <input
                        type="checkbox"
                        [checked]="selectedTranscriptIds().includes(transcript.id)"
                        (click)="$event.stopPropagation()"
                        (change)="toggleTranscript(transcript.id)"
                        class="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                      />
                      <div class="ml-3 flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">
                          {{ transcript.filename }}
                        </p>
                        <p class="text-xs text-gray-500 mt-1">
                          {{ formatSize(transcript.file_size || transcript.size || 0) }}
                          <span *ngIf="transcript.chunk_count" class="ml-2">
                            • {{ transcript.chunk_count }} chunks
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-4 p-3 bg-blue-50 rounded-lg" *ngIf="selectedTranscriptIds().length > 0">
                  <p class="text-sm font-medium text-blue-900">
                    {{ selectedTranscriptIds().length }} file(s) selected
                  </p>
                  <button
                    (click)="clearSelection()"
                    class="text-xs text-blue-600 hover:text-blue-700 mt-1"
                  >
                    Clear selection
                  </button>
                </div>
              </div>
            </div>

            <!-- Chat Area -->
            <div class="flex-1 flex flex-col">
              
              <!-- Messages -->
              <div class="flex-1 overflow-y-auto p-6 space-y-4" #messageContainer>
                
                <div *ngIf="messages.length === 0" class="flex items-center justify-center h-full">
                  <div class="text-center">
                    <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">Start a conversation</h3>
                    <p class="mt-2 text-sm text-gray-500">
                      Select transcript files and ask questions about them
                    </p>
                  </div>
                </div>

                <div *ngFor="let message of messages" 
                     [class.flex-row-reverse]="message.role === 'user'"
                     class="flex gap-3">
                  <div [class.bg-blue-600]="message.role === 'user'"
                       [class.bg-gray-200]="message.role === 'assistant'"
                       class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
                    <span [class.text-white]="message.role === 'user'"
                          [class.text-gray-600]="message.role === 'assistant'"
                          class="text-sm font-semibold">
                      {{ message.role === 'user' ? 'You' : 'AI' }}
                    </span>
                  </div>
                  <div [class.bg-blue-600]="message.role === 'user'"
                       [class.bg-white]="message.role === 'assistant'"
                       [class.text-white]="message.role === 'user'"
                       [class.text-gray-900]="message.role === 'assistant'"
                       class="max-w-xl px-4 py-3 rounded-2xl shadow-sm">
                    <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
                    
                    <div *ngIf="message.sources && message.sources.length > 0" class="mt-3 pt-3 border-t border-gray-200">
                      <p class="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
                      <div class="space-y-1">
                        <div *ngFor="let source of message.sources" class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                          {{ source.transcript_id }} - Chunk {{ source.chunk_index }}
                        </div>
                      </div>
                    </div>
                    
                    <p class="text-xs mt-2 opacity-70">
                      {{ formatTime(message.timestamp) }}
                    </p>
                  </div>
                </div>

                <div *ngIf="querying" class="flex gap-3">
                  <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <span class="text-sm font-semibold text-gray-600">AI</span>
                  </div>
                  <div class="bg-white px-4 py-3 rounded-2xl shadow-sm">
                    <div class="flex items-center gap-2">
                      <div class="flex gap-1">
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                      </div>
                      <span class="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Input Area -->
              <div class="border-t border-gray-200 p-4 bg-white">
                <form (submit)="sendMessage($event)" class="flex gap-3">
                  <input
                    [(ngModel)]="currentMessage"
                    name="message"
                    type="text"
                    placeholder="Ask anything about your transcripts..."
                    [disabled]="selectedTranscriptIds().length === 0 || querying"
                    class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    [disabled]="!currentMessage.trim() || selectedTranscriptIds().length === 0 || querying"
                    class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                    </svg>
                  </button>
                </form>
                <p class="text-xs text-gray-500 mt-2" *ngIf="selectedTranscriptIds().length === 0">
                  Please select at least one transcript to start chatting
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    @keyframes bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-6px); }
    }
  `]
})
export class ChatComponent implements OnInit {
  private conversationService = inject(ConversationService);
  private llmService = inject(LLMService);
  
  transcripts: Transcript[] = [];
  selectedTranscriptIds = signal<string[]>([]);  // Track by transcript ID (UUID)
  messages: Message[] = [];
  currentMessage = '';
  loading = false;
  querying = false;
  
  selectedConversation = this.conversationService.selectedConversation;
  
  // LLM settings
  formProvider: LLMProvider = 'openai';
  formModel = 'gpt-4';
  formTemperature = 0.7;
  
  // LLM provider data
  llmProviders = signal<LLMProviderInfo[]>([]);
  availableModels = signal<string[]>([]);
  loadingModels = signal(false);
  
  // Computed: available providers (status = 'available')
  availableProviders = computed(() => 
    this.llmProviders().filter(p => p.status === 'available' || !p.status)
  );
  
  // Computed: coming soon providers
  comingSoonProviders = computed(() => 
    this.llmProviders().filter(p => p.status === 'coming_soon')
  );
  
  selectedProviderInfo = computed(() => 
    this.llmProviders().find(p => p.provider === this.formProvider)
  );

  constructor(
    private transcriptService: TranscriptService,
    private queryService: QueryService,
    private toast: ToastService
  ) {}

  ngOnInit(): void {
    this.loadTranscripts();
    this.loadLLMProviders();
    this.loadConversationSettings();
  }
  
  loadLLMProviders() {
    this.llmService.listProviders().subscribe({
      next: (providers) => {
        this.llmProviders.set(providers);
        // Set default provider to first available if not set
        if (!this.formProvider) {
          const available = providers.find(p => p.available && p.status !== 'coming_soon');
          if (available) {
            this.formProvider = available.provider as LLMProvider;
            this.loadModelsForProvider(available.provider);
          }
        } else {
          this.loadModelsForProvider(this.formProvider);
        }
      },
      error: () => {
        this.llmProviders.set([
          { provider: 'openai', name: 'OpenAI', description: 'GPT-4, GPT-3.5', available: false, status: 'available', models: [], requires_api_key: true, is_local: false },
          { provider: 'ollama', name: 'Ollama', description: 'Local LLMs', available: false, status: 'available', models: [], requires_api_key: false, is_local: true },
          { provider: 'lmstudio', name: 'LM Studio', description: 'Local', available: false, status: 'available', models: [], requires_api_key: false, is_local: true },
          { provider: 'gemini', name: 'Google Gemini', description: 'Gemini Pro', available: false, status: 'coming_soon', models: [], requires_api_key: true, is_local: false, eta: 'Q2 2026' },
          { provider: 'claude', name: 'Anthropic Claude', description: 'Claude 3', available: false, status: 'coming_soon', models: [], requires_api_key: true, is_local: false, eta: 'Q2 2026' },
          { provider: 'copilot', name: 'MS Copilot', description: 'Azure', available: false, status: 'coming_soon', models: [], requires_api_key: true, is_local: false, eta: 'Q3 2026' },
          { provider: 'n8n', name: 'n8n Agentic', description: 'Workflows', available: false, status: 'coming_soon', models: [], requires_api_key: true, is_local: false, eta: 'Q3 2026' },
          { provider: 'mcp', name: 'MCP Server', description: 'Tools', available: false, status: 'coming_soon', models: [], requires_api_key: false, is_local: false, eta: 'Q2 2026' }
        ]);
      }
    });
  }
  
  loadConversationSettings() {
    const conv = this.selectedConversation();
    if (conv) {
      this.formProvider = (conv.llm_provider || 'openai') as LLMProvider;
      this.formModel = conv.llm_model || 'gpt-4';
      this.formTemperature = conv.llm_temperature ?? 0.7;
    }
  }
  
  selectProvider(provider: LLMProviderInfo) {
    if (!provider.available) return;
    
    this.formProvider = provider.provider as LLMProvider;
    this.formModel = '';
    this.loadModelsForProvider(provider.provider);
    this.saveConversationSettings();
  }
  
  loadModelsForProvider(provider: string) {
    this.loadingModels.set(true);
    this.llmService.getProviderModels(provider).subscribe({
      next: (models) => {
        this.availableModels.set(models);
        if (models.length > 0 && !this.formModel) {
          this.formModel = models[0];
        }
        this.loadingModels.set(false);
      },
      error: () => {
        this.availableModels.set([]);
        this.loadingModels.set(false);
      }
    });
  }
  
  saveConversationSettings() {
    const conv = this.selectedConversation();
    if (!conv) return;
    
    this.conversationService.updateConversation(conv.id, {
      llm_provider: this.formProvider,
      llm_model: this.formModel,
      llm_temperature: this.formTemperature
    }).subscribe();
  }

  loadTranscripts(): void {
    this.loading = true;
    
    // Get the selected conversation ID to filter transcripts on server-side
    const currentConvId = this.selectedConversation()?.id;
    
    this.transcriptService.listTranscripts(currentConvId || undefined).subscribe({
      next: (response: any) => {
        // Backend filters by conversation and returns data field
        this.transcripts = response.data || response.transcripts || [];
        console.log('Loaded transcripts for conversation:', currentConvId, this.transcripts);
      },
      error: (error) => {
        this.toast.error('Failed to load transcripts', error.message);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  toggleTranscript(transcriptId: string): void {
    const current = this.selectedTranscriptIds();
    const index = current.indexOf(transcriptId);
    
    if (index > -1) {
      this.selectedTranscriptIds.set(current.filter(id => id !== transcriptId));
    } else {
      this.selectedTranscriptIds.set([...current, transcriptId]);
    }
  }

  clearSelection(): void {
    this.selectedTranscriptIds.set([]);
  }

  sendMessage(event: Event): void {
    event.preventDefault();
    
    if (!this.currentMessage.trim() || this.selectedTranscriptIds().length === 0) {
      return;
    }

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: this.currentMessage,
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    const question = this.currentMessage;
    this.currentMessage = '';
    this.querying = true;

    // Send query to backend with transcript IDs (UUIDs) and LLM settings
    const request = { 
      question: question, 
      transcript_ids: this.selectedTranscriptIds(),
      llm_provider: this.formProvider,
      llm_model: this.formModel,
      llm_temperature: this.formTemperature
    };
    this.queryService.query(request).subscribe({
      next: (response: any) => {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources,
          timestamp: new Date()
        };
        this.messages.push(assistantMessage);
      },
      error: (error) => {
        this.toast.error('Query failed', error.message);
        const errorMessage: Message = {
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your question. Please try again.',
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
      },
      complete: () => {
        this.querying = false;
        this.scrollToBottom();
      }
    });
  }

  scrollToBottom(): void {
    setTimeout(() => {
      const container = document.querySelector('[class*="overflow-y-auto"]');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }

  formatSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  formatTime(date: Date): string {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }
}

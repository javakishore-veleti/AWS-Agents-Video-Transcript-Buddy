import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranscriptService, QueryService, ToastService } from '../../core/services';
import { Transcript } from '../../core/models';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-h-screen bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-2xl shadow-lg overflow-hidden" style="height: calc(100vh - 8rem);">
          
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white">
            <h1 class="text-2xl font-bold">Transcript Chat</h1>
            <p class="text-sm text-blue-100 mt-1">Ask questions about your transcripts</p>
          </div>

          <div class="flex h-full" style="height: calc(100% - 80px);">
            
            <!-- Sidebar - File Selection -->
            <div class="w-80 border-r border-gray-200 bg-gray-50 overflow-y-auto">
              <div class="p-4">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">Select Transcripts</h2>
                
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
                    (click)="toggleTranscript(transcript.filename)"
                    class="p-3 rounded-lg border cursor-pointer transition-all"
                    [class.border-blue-500]="selectedFiles().includes(transcript.filename)"
                    [class.bg-blue-50]="selectedFiles().includes(transcript.filename)"
                    [class.border-gray-200]="!selectedFiles().includes(transcript.filename)"
                    [class.hover:border-gray-300]="!selectedFiles().includes(transcript.filename)"
                  >
                    <div class="flex items-start">
                      <input
                        type="checkbox"
                        [checked]="selectedFiles().includes(transcript.filename)"
                        (click)="$event.stopPropagation()"
                        (change)="toggleTranscript(transcript.filename)"
                        class="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                      />
                      <div class="ml-3 flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">
                          {{ transcript.filename }}
                        </p>
                        <p class="text-xs text-gray-500 mt-1">
                          {{ formatSize(transcript.size || 0) }}
                          <span *ngIf="transcript.chunk_count" class="ml-2">
                            • {{ transcript.chunk_count }} chunks
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-4 p-3 bg-blue-50 rounded-lg" *ngIf="selectedFiles().length > 0">
                  <p class="text-sm font-medium text-blue-900">
                    {{ selectedFiles().length }} file(s) selected
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
                    [disabled]="selectedFiles().length === 0 || querying"
                    class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    [disabled]="!currentMessage.trim() || selectedFiles().length === 0 || querying"
                    class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                    </svg>
                  </button>
                </form>
                <p class="text-xs text-gray-500 mt-2" *ngIf="selectedFiles().length === 0">
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
  transcripts: Transcript[] = [];
  selectedFiles = signal<string[]>([]);
  messages: Message[] = [];
  currentMessage = '';
  loading = false;
  querying = false;

  constructor(
    private transcriptService: TranscriptService,
    private queryService: QueryService,
    private toast: ToastService
  ) {}

  ngOnInit(): void {
    this.loadTranscripts();
  }

  loadTranscripts(): void {
    this.loading = true;
    this.transcriptService.listTranscripts().subscribe({
      next: (response: any) => {
        this.transcripts = response.data || [];
      },
      error: (error) => {
        this.toast.error('Failed to load transcripts', error.message);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  toggleTranscript(filename: string): void {
    const current = this.selectedFiles();
    const index = current.indexOf(filename);
    
    if (index > -1) {
      this.selectedFiles.set(current.filter(f => f !== filename));
    } else {
      this.selectedFiles.set([...current, filename]);
    }
  }

  clearSelection(): void {
    this.selectedFiles.set([]);
  }

  sendMessage(event: Event): void {
    event.preventDefault();
    
    if (!this.currentMessage.trim() || this.selectedFiles().length === 0) {
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

    // Send query to backend
    const request = { query: question, transcript_ids: this.selectedFiles() };
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

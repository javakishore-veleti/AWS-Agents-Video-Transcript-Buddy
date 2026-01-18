import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ConversationService, AuthService, ToastService } from '../../core/services';
import { Conversation } from '../../core/models/conversation.model';

@Component({
  selector: 'app-conversations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">My Conversations</h1>
          <p class="text-gray-600 mt-2">Organize your transcripts into conversation workspaces</p>
        </div>
        <button
          (click)="showCreateDialog = true"
          [disabled]="!canCreateMore()"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          + New Conversation
        </button>
      </div>

      <!-- Tier Limits Info -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div class="flex items-center gap-4">
          <div class="text-sm text-blue-900">
            <span class="font-semibold">{{ conversationCount() }}</span> / 
            <span>{{ maxConversations() === -1 ? '∞' : maxConversations() }}</span> 
            Conversations
          </div>
          @if (!canCreateMore() && maxConversations() !== -1) {
            <div class="text-sm text-orange-600">
              Limit reached. Upgrade your plan or delete existing conversations.
            </div>
          }
        </div>
      </div>

      <!-- Conversations Grid -->
      @if (isLoading()) {
        <div class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading conversations...</p>
        </div>
      } @else if (conversations().length === 0) {
        <div class="text-center py-12 bg-gray-50 rounded-lg">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No conversations yet</h3>
          <p class="mt-2 text-gray-500">Create your first conversation to start organizing transcripts</p>
          <button
            (click)="showCreateDialog = true"
            class="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Create Conversation
          </button>
        </div>
      } @else {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          @for (conv of conversations(); track conv.id) {
            <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
                 [class.ring-2]="isSelected(conv)"
                 [class.ring-blue-500]="isSelected(conv)"
                 (click)="selectConversation(conv)">
              <!-- Name -->
              <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ conv.name }}</h3>
              
              <!-- Description -->
              @if (conv.description) {
                <p class="text-gray-600 text-sm mb-4">{{ conv.description }}</p>
              }
              
              <!-- Stats -->
              <div class="flex gap-4 mb-4 text-sm text-gray-500">
                <div>
                  <span class="font-medium">{{ conv.file_count }}</span> files
                </div>
                <div>
                  <span class="font-medium">{{ conv.query_count }}</span> queries
                </div>
                <div>
                  <span class="font-medium">{{ conv.total_size_mb }}</span> MB
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex flex-col gap-2 pt-4 border-t border-gray-100">
                <div class="flex gap-2">
                  <button
                    (click)="navigateToUpload(conv); $event.stopPropagation()"
                    class="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Upload Files
                  </button>
                  <button
                    (click)="navigateToChat(conv); $event.stopPropagation()"
                    class="flex-1 px-3 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    [disabled]="conv.file_count === 0">
                    Chat
                  </button>
                </div>
                <div class="flex gap-2">
                  <button
                    (click)="editConversation(conv); $event.stopPropagation()"
                    class="text-sm text-blue-600 hover:text-blue-700">
                    Edit
                  </button>
                  <button
                    (click)="deleteConversation(conv); $event.stopPropagation()"
                    class="text-sm text-red-600 hover:text-red-700">
                    Delete
                  </button>
                </div>
              </div>
              
              <!-- Last activity -->
              <div class="mt-2 text-xs text-gray-400">
                Updated {{ formatDate(conv.updated_at) }}
              </div>
            </div>
          }
        </div>
      }

      <!-- Create/Edit Dialog -->
      @if (showCreateDialog || editingConversation()) {
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" (click)="closeDialog()">
          <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto" (click)="$event.stopPropagation()">
            <h2 class="text-2xl font-bold mb-4">
              {{ editingConversation() ? 'Edit' : 'New' }} Conversation
            </h2>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  [(ngModel)]="formName"
                  placeholder="Leave empty for auto-generated name"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Description (optional)</label>
                <textarea
                  [(ngModel)]="formDescription"
                  rows="2"
                  placeholder="Describe what this conversation is about"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
              </div>
            </div>
            
            <div class="flex gap-3 mt-6">
              <button
                (click)="saveConversation()"
                [disabled]="isSaving()"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
                {{ isSaving() ? 'Saving...' : 'Save' }}
              </button>
              <button
                (click)="closeDialog()"
                class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class ConversationsComponent implements OnInit {
  private conversationService = inject(ConversationService);
  private authService = inject(AuthService);
  private toastService = inject(ToastService);
  private router = inject(Router);
  
  conversations = this.conversationService.conversations;
  selectedConv = this.conversationService.selectedConversation;
  
  isLoading = signal(false);
  isSaving = signal(false);
  showCreateDialog = false;
  editingConversation = signal<Conversation | null>(null);
  
  // Basic form fields
  formName = '';
  formDescription = '';
  
  conversationCount = computed(() => this.conversations().length);
  maxConversations = computed(() => {
    // This should come from user's tier - hardcoded for now
    const user = this.authService.getCurrentUser();
    if (user?.tier === 'FREE') return 3;
    if (user?.tier === 'STARTER') return 10;
    if (user?.tier === 'PRO') return 50;
    return -1; // Enterprise
  });
  
  canCreateMore = computed(() => {
    const max = this.maxConversations();
    return max === -1 || this.conversationCount() < max;
  });

  ngOnInit() {
    this.loadConversations();
  }

  loadConversations() {
    this.isLoading.set(true);
    this.conversationService.listConversations().subscribe({
      next: () => this.isLoading.set(false),
      error: (error) => {
        this.isLoading.set(false);
        this.toastService.error('Failed to load conversations');
      }
    });
  }

  selectConversation(conv: Conversation) {
    this.conversationService.selectConversation(conv);
  }

  isSelected(conv: Conversation): boolean {
    return this.selectedConv()?.id === conv.id;
  }

  navigateToUpload(conv: Conversation) {
    this.conversationService.selectConversation(conv);
    this.router.navigate(['/upload']);
  }

  navigateToChat(conv: Conversation) {
    this.conversationService.selectConversation(conv);
    this.router.navigate(['/chat']);
  }

  editConversation(conv: Conversation) {
    this.editingConversation.set(conv);
    this.formName = conv.name;
    this.formDescription = conv.description || '';
  }

  deleteConversation(conv: Conversation) {
    if (!confirm(`Delete "${conv.name}" and all its ${conv.file_count} files?`)) {
      return;
    }
    
    this.conversationService.deleteConversation(conv.id).subscribe({
      next: () => this.toastService.success('Conversation deleted'),
      error: () => this.toastService.error('Failed to delete conversation')
    });
  }

  saveConversation() {
    this.isSaving.set(true);
    
    const request = {
      name: this.formName || undefined,
      description: this.formDescription || undefined
    };
    
    const operation = this.editingConversation()
      ? this.conversationService.updateConversation(this.editingConversation()!.id, request)
      : this.conversationService.createConversation(request);
    
    operation.subscribe({
      next: () => {
        this.toastService.success(
          this.editingConversation() ? 'Conversation updated' : 'Conversation created'
        );
        this.closeDialog();
        this.isSaving.set(false);
      },
      error: (error) => {
        this.toastService.error(error.error?.detail || 'Operation failed');
        this.isSaving.set(false);
      }
    });
  }

  closeDialog() {
    this.showCreateDialog = false;
    this.editingConversation.set(null);
    this.formName = '';
    this.formDescription = '';
  }

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }
}

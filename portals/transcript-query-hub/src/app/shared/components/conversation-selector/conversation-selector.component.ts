import { Component, inject, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../../core/services';
import { Conversation } from '../../../core/models/conversation.model';

@Component({
  selector: 'app-conversation-selector',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="conversation-selector">
      @if (conversations().length === 0) {
        <div class="text-center py-4 bg-gray-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-2">No conversations yet</p>
          <a routerLink="/conversations" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
            Create your first conversation →
          </a>
        </div>
      } @else {
        <div class="flex items-center gap-2">
          <div class="flex-1">
            <select 
              [value]="selectedConversation()?.id || ''"
              (change)="onConversationChange($event)"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="">Select conversation...</option>
              @for (conv of conversations(); track conv.id) {
                <option [value]="conv.id">
                  {{ conv.name }}
                  @if (conv.file_count > 0) {
                    <span>({{ conv.file_count }} files)</span>
                  }
                </option>
              }
            </select>
          </div>
          <a 
            routerLink="/conversations"
            class="px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 whitespace-nowrap">
            Manage
          </a>
        </div>
        
        @if (selectedConversation()) {
          <div class="mt-2 text-xs text-gray-500">
            {{ selectedConversation()!.file_count }} files • 
            {{ selectedConversation()!.query_count }} queries • 
            {{ selectedConversation()!.total_size_mb }} MB
          </div>
        }
      }
    </div>
  `,
  styles: [`
    .conversation-selector {
      width: 100%;
    }
  `]
})
export class ConversationSelectorComponent implements OnInit {
  private conversationService = inject(ConversationService);
  
  conversations = this.conversationService.conversations;
  selectedConversation = this.conversationService.selectedConversation;

  ngOnInit() {
    if (this.conversations().length === 0) {
      this.conversationService.listConversations().subscribe();
    }
  }

  onConversationChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    const convId = select.value;  // Keep as string (encrypted ID)
    const conv = this.conversations().find(c => c.id === convId);
    if (conv) {
      this.conversationService.selectConversation(conv);
    }
  }
}

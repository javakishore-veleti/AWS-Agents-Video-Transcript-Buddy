import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { 
  Conversation, 
  CreateConversationRequest, 
  UpdateConversationRequest,
  DowngradeValidation 
} from '../models/conversation.model';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private http = inject(HttpClient);
  private baseUrl = '/api/conversations/';
  
  // Current conversations list
  conversations = signal<Conversation[]>([]);
  
  // Currently selected conversation
  selectedConversation = signal<Conversation | null>(null);

  /**
   * Create a new conversation
   */
  createConversation(request: CreateConversationRequest): Observable<Conversation> {
    return this.http.post<Conversation>(this.baseUrl, request).pipe(
      tap(conversation => {
        this.conversations.update(list => [...list, conversation]);
        this.selectedConversation.set(conversation);
      })
    );
  }

  /**
   * List all conversations
   */
  listConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(this.baseUrl).pipe(
      tap(conversations => {
        this.conversations.set(conversations);
        // Auto-select first conversation if none selected
        if (!this.selectedConversation() && conversations.length > 0) {
          this.selectedConversation.set(conversations[0]);
        }
      })
    );
  }

  /**
   * Get a specific conversation
   */
  getConversation(conversationId: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.baseUrl}${conversationId}`);
  }

  /**
   * Update conversation
   */
  updateConversation(
    conversationId: string, 
    request: UpdateConversationRequest
  ): Observable<Conversation> {
    return this.http.put<Conversation>(`${this.baseUrl}${conversationId}`, request).pipe(
      tap(updated => {
        this.conversations.update(list => 
          list.map(c => c.id === conversationId ? updated : c)
        );
        if (this.selectedConversation()?.id === conversationId) {
          this.selectedConversation.set(updated);
        }
      })
    );
  }

  /**
   * Delete conversation
   */
  deleteConversation(conversationId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${conversationId}`).pipe(
      tap(() => {
        this.conversations.update(list => list.filter(c => c.id !== conversationId));
        if (this.selectedConversation()?.id === conversationId) {
          const remaining = this.conversations();
          this.selectedConversation.set(remaining.length > 0 ? remaining[0] : null);
        }
      })
    );
  }

  /**
   * Validate if user can downgrade subscription
   */
  validateDowngrade(newTier: string): Observable<DowngradeValidation> {
    return this.http.post<DowngradeValidation>(
      `${this.baseUrl}/validate-downgrade`,
      null,
      { params: { new_tier: newTier } }
    );
  }

  /**
   * Select a conversation
   */
  selectConversation(conversation: Conversation | null): void {
    this.selectedConversation.set(conversation);
  }

  /**
   * Get current conversation ID (encrypted)
   */
  getCurrentConversationId(): string | null {
    return this.selectedConversation()?.id || null;
  }
}

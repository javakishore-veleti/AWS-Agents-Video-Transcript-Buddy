import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faLightbulb, 
  faQuoteLeft,
  faFileLines,
  faClock,
  faThumbsUp,
  faThumbsDown,
  faCopy,
  faCheck,
  faRotate
} from '@fortawesome/free-solid-svg-icons';
import { SearchBoxComponent } from '../../shared/components/search-box/search-box.component';
import { SourceBadgeComponent } from '../../shared/components/source-badge/source-badge.component';
import { SkeletonLoaderComponent } from '../../shared/components/skeleton-loader/skeleton-loader.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { QueryService } from '../../core/services/query.service';
import { ToastService } from '../../core/services/toast.service';
import { QueryResponse, QuerySource } from '../../core/models/query.model';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';
import { HighlightPipe } from '../../shared/pipes/highlight.pipe';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    CommonModule, 
    FontAwesomeModule, 
    SearchBoxComponent, 
    SourceBadgeComponent,
    SkeletonLoaderComponent,
    EmptyStateComponent,
    TruncatePipe,
    HighlightPipe
  ],
  template: `
    <div class="min-h-[80vh] bg-gray-50">
      <!-- Search Header -->
      <div class="bg-white border-b border-gray-200 sticky top-16 md:top-20 z-40">
        <div class="container-app py-6">
          <app-search-box
            [initialQuery]="currentQuery()"
            [loading]="isLoading()"
            [suggestions]="suggestions"
            [showSuggestions]="!currentQuery()"
            placeholder="Ask a question about your transcripts..."
            (search)="onSearch($event)">
          </app-search-box>
        </div>
      </div>

      <div class="container-app py-8">
        @if (isLoading()) {
          <!-- Loading State -->
          <div class="max-w-3xl">
            <div class="card p-6 mb-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-8 h-8 rounded-full bg-tq-primary-100 flex items-center justify-center">
                  <div class="w-4 h-4 border-2 border-tq-primary-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <span class="text-gray-600">Searching transcripts...</span>
              </div>
              <app-skeleton-loader type="text" [count]="4"></app-skeleton-loader>
            </div>
            <app-skeleton-loader type="search-result" [count]="2"></app-skeleton-loader>
          </div>
        } @else if (result()) {
          <!-- Results -->
          <div class="max-w-3xl">
            <!-- Answer Card -->
            <div class="card p-6 mb-6 animate-fade-in">
              <!-- Answer Header -->
              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-tq-primary-500 to-tq-secondary-500 
                              flex items-center justify-center shadow-lg shadow-tq-primary-500/25">
                    <fa-icon [icon]="faLightbulb" class="text-white"></fa-icon>
                  </div>
                  <div>
                    <h2 class="font-semibold text-gray-900">AI Answer</h2>
                    <p class="text-sm text-gray-500">Based on {{ result()!.sources.length }} source(s)</p>
                  </div>
                </div>
                
                <!-- Confidence Badge -->
                <div class="flex items-center gap-2">
                  <span class="badge"
                        [class.badge-success]="result()!.confidence >= 0.7"
                        [class.badge-warning]="result()!.confidence >= 0.4 && result()!.confidence < 0.7"
                        [class.badge-error]="result()!.confidence < 0.4">
                    {{ (result()!.confidence * 100).toFixed(0) }}% confident
                  </span>
                </div>
              </div>

              <!-- Answer Content -->
              <div class="prose prose-gray max-w-none mb-6">
                <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{{ result()!.answer }}</p>
              </div>

              <!-- Sources -->
              @if (result()!.sources.length > 0) {
                <div class="pt-4 border-t border-gray-100">
                  <p class="text-sm font-medium text-gray-500 mb-3">Sources:</p>
                  <div class="flex flex-wrap gap-2">
                    @for (source of result()!.sources; track source.transcript_id + source.chunk_index) {
                      <app-source-badge
                        [transcriptId]="source.transcript_id"
                        [chunkIndex]="source.chunk_index"
                        [score]="source.score">
                      </app-source-badge>
                    }
                  </div>
                </div>
              }

              <!-- Actions -->
              <div class="flex items-center justify-between pt-4 mt-4 border-t border-gray-100">
                <div class="flex items-center gap-2">
                  <button class="btn btn-sm btn-ghost" (click)="copyAnswer()" [disabled]="copied()">
                    <fa-icon [icon]="copied() ? faCheck : faCopy"></fa-icon>
                    {{ copied() ? 'Copied!' : 'Copy' }}
                  </button>
                  <button class="btn btn-sm btn-ghost" (click)="onSearch(currentQuery())">
                    <fa-icon [icon]="faRotate"></fa-icon>
                    Regenerate
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-400">Was this helpful?</span>
                  <button class="btn-icon btn-sm btn-ghost text-gray-400 hover:text-green-600" 
                          (click)="rateFeedback(true)">
                    <fa-icon [icon]="faThumbsUp"></fa-icon>
                  </button>
                  <button class="btn-icon btn-sm btn-ghost text-gray-400 hover:text-red-600"
                          (click)="rateFeedback(false)">
                    <fa-icon [icon]="faThumbsDown"></fa-icon>
                  </button>
                </div>
              </div>
            </div>

            <!-- Source Previews -->
            @if (result()!.sources.length > 0) {
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900">Source Excerpts</h3>
                @for (source of result()!.sources; track source.transcript_id + source.chunk_index) {
                  <div class="card p-5 hover:shadow-lg transition-shadow animate-fade-in-up">
                    <div class="flex items-start gap-4">
                      <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                        <fa-icon [icon]="faFileLines" class="text-gray-500"></fa-icon>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-2">
                          <span class="font-medium text-gray-900">{{ source.transcript_id }}</span>
                          <span class="text-sm text-gray-400">Chunk #{{ source.chunk_index }}</span>
                          <span class="badge badge-info text-xs">
                            {{ (source.score * 100).toFixed(0) }}% match
                          </span>
                        </div>
                        <p class="text-gray-600 text-sm leading-relaxed"
                           [innerHTML]="source.preview | highlight:currentQuery()"></p>
                      </div>
                    </div>
                  </div>
                }
              </div>
            }
          </div>
        } @else if (!currentQuery()) {
          <!-- Empty State -->
          <div class="max-w-3xl">
            <app-empty-state
              type="no-results"
              title="Start Your Search"
              description="Enter a question above to search through your transcripts. Our AI will find the most relevant answers."
              [showAction]="false">
            </app-empty-state>

            <!-- Sample Questions -->
            <div class="mt-8">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 text-center">Try these sample questions</h3>
              <div class="grid sm:grid-cols-2 gap-3">
                @for (question of suggestions; track question) {
                  <button 
                    (click)="onSearch(question)"
                    class="card p-4 text-left hover:border-tq-primary-300 hover:shadow-md transition-all group">
                    <fa-icon [icon]="faQuoteLeft" class="text-tq-primary-300 mb-2"></fa-icon>
                    <p class="text-gray-700 group-hover:text-tq-primary-600 transition-colors">{{ question }}</p>
                  </button>
                }
              </div>
            </div>
          </div>
        } @else if (hasSearched() && !result()) {
          <!-- No Results -->
          <div class="max-w-3xl">
            <app-empty-state
              type="no-results"
              title="No Results Found"
              description="We couldn't find any relevant information for your query. Try rephrasing or using different keywords."
              [showAction]="false">
            </app-empty-state>
          </div>
        }

        <!-- Query History -->
        @if (queryHistory().length > 0 && !isLoading()) {
          <div class="max-w-3xl mt-12">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <fa-icon [icon]="faClock" class="text-gray-400"></fa-icon>
              Recent Searches
            </h3>
            <div class="space-y-2">
              @for (item of queryHistory().slice(0, 5); track item.query) {
                <button 
                  (click)="onSearch(item.query)"
                  class="w-full text-left px-4 py-3 rounded-lg bg-white border border-gray-200 
                         hover:border-tq-primary-300 hover:shadow-sm transition-all group">
                  <p class="text-gray-700 group-hover:text-tq-primary-600">{{ item.query }}</p>
                </button>
              }
            </div>
          </div>
        }
      </div>
    </div>
  `
})
export class SearchComponent implements OnInit {
  // Icons
  faLightbulb = faLightbulb;
  faQuoteLeft = faQuoteLeft;
  faFileLines = faFileLines;
  faClock = faClock;
  faThumbsUp = faThumbsUp;
  faThumbsDown = faThumbsDown;
  faCopy = faCopy;
  faCheck = faCheck;
  faRotate = faRotate;

  // State
  currentQuery = signal('');
  result = signal<QueryResponse | null>(null);
  isLoading = signal(false);
  hasSearched = signal(false);
  copied = signal(false);
  queryHistory = signal<QueryResponse[]>([]);

  // Suggestions
  suggestions = [
    'What are the main topics discussed in the transcripts?',
    'Summarize the key points from the last meeting',
    'What questions were asked during the presentation?',
    'Find mentions of budget or pricing'
  ];

  constructor(
    private route: ActivatedRoute,
    private queryService: QueryService,
    private toast: ToastService
  ) {}

  ngOnInit(): void {
    // Check for query param
    this.route.queryParams.subscribe(params => {
      if (params['q']) {
        this.currentQuery.set(params['q']);
        this.onSearch(params['q']);
      }
    });

    // Subscribe to query history
    this.queryService.queryHistory$.subscribe(history => {
      this.queryHistory.set(history);
    });
  }

  onSearch(query: string): void {
    if (!query || query.trim().length === 0) return;

    this.currentQuery.set(query);
    this.isLoading.set(true);
    this.hasSearched.set(true);
    this.result.set(null);

    this.queryService.query({ query, include_sources: true }).subscribe({
      next: (response) => {
        this.result.set(response);
        this.isLoading.set(false);
      },
      error: (error) => {
        this.isLoading.set(false);
        this.toast.error('Failed to search. Please try again.');
        console.error('Search error:', error);
      }
    });
  }

  copyAnswer(): void {
    if (this.result()?.answer) {
      navigator.clipboard.writeText(this.result()!.answer).then(() => {
        this.copied.set(true);
        this.toast.success('Answer copied to clipboard');
        setTimeout(() => this.copied.set(false), 2000);
      });
    }
  }

  rateFeedback(positive: boolean): void {
    this.toast.info(positive ? 'Thanks for the feedback!' : 'We\'ll work on improving');
    // TODO: Send feedback to backend
  }
}
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faMagnifyingGlass, 
  faCloudArrowUp, 
  faRotate,
  faTrash,
  faFilter,
  faSort,
  faTableCells,
  faList
} from '@fortawesome/free-solid-svg-icons';
import { TranscriptCardComponent } from '../../shared/components/transcript-card/transcript-card.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { SkeletonLoaderComponent } from '../../shared/components/skeleton-loader/skeleton-loader.component';
import { ConfirmDialogComponent, ConfirmDialogData } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { TranscriptService } from '../../core/services/transcript.service';
import { ToastService } from '../../core/services/toast.service';
import { Transcript } from '../../core/models/transcript.model';

@Component({
  selector: 'app-transcripts',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    FormsModule,
    FontAwesomeModule, 
    MatDialogModule,
    TranscriptCardComponent,
    EmptyStateComponent,
    SkeletonLoaderComponent
  ],
  template: `
    <div class="min-h-[80vh]">
      <!-- Header -->
      <div class="bg-white border-b border-gray-200">
        <div class="container-app py-8">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Transcripts</h1>
              <p class="text-gray-600 mt-1">
                Manage your uploaded video transcripts
              </p>
            </div>
            <div class="flex items-center gap-3">
              <button 
                class="btn btn-secondary"
                (click)="refreshTranscripts()"
                [disabled]="isLoading()">
                <fa-icon [icon]="faRotate" [class.animate-spin]="isLoading()"></fa-icon>
                Refresh
              </button>
              <a routerLink="/upload" class="btn btn-primary">
                <fa-icon [icon]="faCloudArrowUp"></fa-icon>
                Upload New
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="bg-white border-b border-gray-100 sticky top-16 md:top-20 z-30">
        <div class="container-app py-4">
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <!-- Search -->
            <div class="relative flex-1 max-w-md">
              <fa-icon [icon]="faMagnifyingGlass" 
                       class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></fa-icon>
              <input 
                type="text"
                [(ngModel)]="searchQuery"
                (ngModelChange)="onSearchChange($event)"
                placeholder="Search transcripts..."
                class="input pl-10"
              />
            </div>
            
            <!-- Actions -->
            <div class="flex items-center gap-2">
              <!-- View Toggle -->
              <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                <button 
                  (click)="viewMode.set('grid')"
                  class="p-2 transition-colors"
                  [class.bg-tq-primary-50]="viewMode() === 'grid'"
                  [class.text-tq-primary-600]="viewMode() === 'grid'"
                  [class.text-gray-400]="viewMode() !== 'grid'">
                  <fa-icon [icon]="faGrid"></fa-icon>
                </button>
                <button 
                  (click)="viewMode.set('list')"
                  class="p-2 transition-colors"
                  [class.bg-tq-primary-50]="viewMode() === 'list'"
                  [class.text-tq-primary-600]="viewMode() === 'list'"
                  [class.text-gray-400]="viewMode() !== 'list'">
                  <fa-icon [icon]="faList"></fa-icon>
                </button>
              </div>

              <!-- Sort -->
              <select 
                [(ngModel)]="sortBy"
                (ngModelChange)="onSortChange($event)"
                class="input py-2 w-auto">
                <option value="name">Name</option>
                <option value="date">Date</option>
                <option value="size">Size</option>
              </select>
            </div>
          </div>

          <!-- Stats -->
          <div class="flex items-center gap-4 mt-4 text-sm text-gray-500">
            <span>{{ filteredTranscripts().length }} transcript(s)</span>
            @if (searchQuery) {
              <span>• Filtered from {{ transcripts().length }}</span>
            }
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="container-app py-8">
        @if (isLoading()) {
          <!-- Loading -->
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            @for (i of [1,2,3,4,5,6]; track i) {
              <app-skeleton-loader type="card"></app-skeleton-loader>
            }
          </div>
        } @else if (transcripts().length === 0) {
          <!-- Empty State -->
          <app-empty-state
            type="no-transcripts"
            title="No Transcripts Yet"
            description="Upload your first transcript to get started with AI-powered search."
            actionLabel="Upload Transcript"
            actionRoute="/upload"
            [actionIcon]="faCloudArrowUp">
          </app-empty-state>
        } @else if (filteredTranscripts().length === 0) {
          <!-- No Search Results -->
          <app-empty-state
            type="no-results"
            title="No Matching Transcripts"
            description="No transcripts match your search. Try different keywords."
            [showAction]="false">
          </app-empty-state>
        } @else if (viewMode() === 'grid') {
          <!-- Grid View -->
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            @for (transcript of filteredTranscripts(); track transcript.filename) {
              <app-transcript-card
                [transcript]="transcript"
                [reindexing]="reindexingId() === transcript.filename"
                [deleting]="deletingId() === transcript.filename"
                (delete)="onDelete($event)"
                (reindex)="onReindex($event)">
              </app-transcript-card>
            }
          </div>
        } @else {
          <!-- List View -->
          <div class="card overflow-hidden">
            <table class="w-full">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Chunks</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Date</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                @for (transcript of filteredTranscripts(); track transcript.filename) {
                  <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4">
                      <a [routerLink]="['/transcripts', transcript.filename]" 
                         class="font-medium text-gray-900 hover:text-tq-primary-600">
                        {{ transcript.filename }}
                      </a>
                    </td>
                    <td class="px-6 py-4 hidden md:table-cell">
                      @if (transcript.indexed) {
                        <span class="badge badge-success">Indexed</span>
                      } @else {
                        <span class="badge badge-warning">Pending</span>
                      }
                    </td>
                    <td class="px-6 py-4 text-gray-500 hidden lg:table-cell">
                      {{ transcript.chunk_count || '-' }}
                    </td>
                    <td class="px-6 py-4 text-gray-500 text-sm hidden sm:table-cell">
                      {{ transcript.uploaded_at | date:'short' }}
                    </td>
                    <td class="px-6 py-4 text-right">
                      <div class="flex items-center justify-end gap-2">
                        <button 
                          (click)="onReindex(transcript)"
                          [disabled]="reindexingId() === transcript.filename"
                          class="btn btn-sm btn-ghost">
                          <fa-icon [icon]="faRotate" 
                                   [class.animate-spin]="reindexingId() === transcript.filename"></fa-icon>
                        </button>
                        <button 
                          (click)="onDelete(transcript)"
                          [disabled]="deletingId() === transcript.filename"
                          class="btn btn-sm btn-ghost text-red-600 hover:bg-red-50">
                          <fa-icon [icon]="faTrash"></fa-icon>
                        </button>
                      </div>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        }
      </div>
    </div>
  `
})
export class TranscriptsComponent implements OnInit {
  // Icons
  faMagnifyingGlass = faMagnifyingGlass;
  faCloudArrowUp = faCloudArrowUp;
  faRotate = faRotate;
  faTrash = faTrash;
  faFilter = faFilter;
  faSort = faSort;
  faGrid = faTableCells;
  faList = faList;

  // State
  transcripts = signal<Transcript[]>([]);
  filteredTranscripts = signal<Transcript[]>([]);
  isLoading = signal(true);
  reindexingId = signal<string | null>(null);
  deletingId = signal<string | null>(null);
  viewMode = signal<'grid' | 'list'>('grid');
  
  // Filters
  searchQuery = '';
  sortBy = 'date';

  constructor(
    private transcriptService: TranscriptService,
    private toast: ToastService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadTranscripts();
  }

  loadTranscripts(): void {
    this.isLoading.set(true);
    this.transcriptService.getTranscripts().subscribe({
      next: (response) => {
        this.transcripts.set(response.transcripts || []);
        this.applyFilters();
        this.isLoading.set(false);
      },
      error: (error) => {
        this.isLoading.set(false);
        this.toast.error('Failed to load transcripts');
        console.error('Load error:', error);
      }
    });
  }

  refreshTranscripts(): void {
    this.loadTranscripts();
  }

  onSearchChange(query: string): void {
    this.searchQuery = query;
    this.applyFilters();
  }

  onSortChange(sortBy: string): void {
    this.sortBy = sortBy;
    this.applyFilters();
  }

  applyFilters(): void {
    let result = [...this.transcripts()];

    // Search filter
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      result = result.filter(t => 
        t.filename.toLowerCase().includes(query)
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (this.sortBy) {
        case 'name':
          return a.filename.localeCompare(b.filename);
        case 'size':
          return (b.size || 0) - (a.size || 0);
        case 'date':
        default:
          return new Date(b.uploaded_at || 0).getTime() - new Date(a.uploaded_at || 0).getTime();
      }
    });

    this.filteredTranscripts.set(result);
  }

  onDelete(transcript: Transcript): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Transcript',
        message: `Are you sure you want to delete "${transcript.filename}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel',
        type: 'danger'
      } as ConfirmDialogData
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (confirmed) {
        this.deletingId.set(transcript.filename);
        this.transcriptService.deleteTranscript(transcript.filename).subscribe({
          next: () => {
            this.toast.success('Transcript deleted');
            this.deletingId.set(null);
            this.loadTranscripts();
          },
          error: () => {
            this.toast.error('Failed to delete transcript');
            this.deletingId.set(null);
          }
        });
      }
    });
  }

  onReindex(transcript: Transcript): void {
    this.reindexingId.set(transcript.filename);
    this.transcriptService.reindexTranscript(transcript.filename).subscribe({
      next: () => {
        this.toast.success('Transcript reindexed');
        this.reindexingId.set(null);
        this.loadTranscripts();
      },
      error: () => {
        this.toast.error('Failed to reindex transcript');
        this.reindexingId.set(null);
      }
    });
  }
}
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faArrowLeft,
  faFileLines,
  faRotate,
  faTrash,
  faMagnifyingGlass,
  faCopy,
  faCheck,
  faDownload,
  faClock,
  faDatabase
} from '@fortawesome/free-solid-svg-icons';
import { SkeletonLoaderComponent } from '../../shared/components/skeleton-loader/skeleton-loader.component';
import { ConfirmDialogComponent, ConfirmDialogData } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { TranscriptService } from '../../core/services/transcript.service';
import { ToastService } from '../../core/services/toast.service';
import { Transcript } from '../../core/models/transcript.model';
import { FileSizePipe } from '../../shared/pipes/file-size.pipe';
import { TimeAgoPipe } from '../../shared/pipes/time-ago.pipe';

@Component({
  selector: 'app-transcript-detail',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    FontAwesomeModule, 
    MatDialogModule,
    SkeletonLoaderComponent,
    FileSizePipe,
    TimeAgoPipe
  ],
  template: `
    <div class="min-h-[80vh] bg-gray-50">
      <!-- Header -->
      <div class="bg-white border-b border-gray-200">
        <div class="container-app py-6">
          <!-- Back Link -->
          <a routerLink="/transcripts" 
             class="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-tq-primary-600 mb-4">
            <fa-icon [icon]="faArrowLeft"></fa-icon>
            Back to Transcripts
          </a>

          @if (isLoading()) {
            <div class="space-y-3">
              <div class="skeleton h-8 w-1/3 rounded"></div>
              <div class="skeleton h-4 w-1/4 rounded"></div>
            </div>
          } @else if (transcript()) {
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div class="flex items-start gap-4">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-tq-primary-100 to-tq-secondary-100 
                            flex items-center justify-center">
                  <fa-icon [icon]="faFileLines" class="text-tq-primary-600 text-2xl"></fa-icon>
                </div>
                <div>
                  <h1 class="text-2xl font-bold text-gray-900">{{ transcript()!.filename }}</h1>
                  <div class="flex flex-wrap items-center gap-3 mt-2 text-sm text-gray-500">
                    @if (transcript()!.size) {
                      <span class="flex items-center gap-1">
                        <fa-icon [icon]="faDatabase" class="text-xs"></fa-icon>
                        {{ transcript()!.size | fileSize }}
                      </span>
                    }
                    @if (transcript()!.uploaded_at) {
                      <span class="flex items-center gap-1">
                        <fa-icon [icon]="faClock" class="text-xs"></fa-icon>
                        {{ transcript()!.uploaded_at | timeAgo }}
                      </span>
                    }
                    @if (transcript()!.indexed) {
                      <span class="badge badge-success">Indexed</span>
                    } @else {
                      <span class="badge badge-warning">Pending</span>
                    }
                    @if (transcript()!.chunk_count) {
                      <span>{{ transcript()!.chunk_count }} chunks</span>
                    }
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2">
                <button 
                  (click)="searchTranscript()"
                  class="btn btn-secondary">
                  <fa-icon [icon]="faMagnifyingGlass"></fa-icon>
                  Search
                </button>
                <button 
                  (click)="copyContent()"
                  [disabled]="copied()"
                  class="btn btn-secondary">
                  <fa-icon [icon]="copied() ? faCheck : faCopy"></fa-icon>
                  {{ copied() ? 'Copied!' : 'Copy' }}
                </button>
                <button 
                  (click)="reindexTranscript()"
                  [disabled]="isReindexing()"
                  class="btn btn-secondary">
                  <fa-icon [icon]="faRotate" [class.animate-spin]="isReindexing()"></fa-icon>
                  Reindex
                </button>
                <button 
                  (click)="deleteTranscript()"
                  class="btn btn-ghost text-red-600 hover:bg-red-50">
                  <fa-icon [icon]="faTrash"></fa-icon>
                </button>
              </div>
            </div>
          }
        </div>
      </div>

      <!-- Content -->
      <div class="container-app py-8">
        @if (isLoading()) {
          <div class="card p-6">
            <app-skeleton-loader type="text" [count]="10"></app-skeleton-loader>
          </div>
        } @else if (transcript()?.content) {
          <div class="card">
            <div class="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 class="font-semibold text-gray-900">Content</h2>
              <span class="text-sm text-gray-500">
                {{ transcript()!.content!.length | number }} characters
              </span>
            </div>
            <div class="p-6">
              <pre class="whitespace-pre-wrap text-sm text-gray-700 font-mono leading-relaxed 
                          max-h-[600px] overflow-y-auto scrollbar-thin">{{ transcript()!.content }}</pre>
            </div>
          </div>
        } @else {
          <div class="card p-8 text-center">
            <fa-icon [icon]="faFileLines" class="text-4xl text-gray-300 mb-4"></fa-icon>
            <p class="text-gray-500">No content available</p>
          </div>
        }

        <!-- Metadata -->
        @if (transcript()?.metadata && hasMetadata()) {
          <div class="card mt-6">
            <div class="p-4 border-b border-gray-200">
              <h2 class="font-semibold text-gray-900">Metadata</h2>
            </div>
            <div class="p-6">
              <dl class="grid grid-cols-2 gap-4">
                @for (item of metadataEntries(); track item.key) {
                  <div>
                    <dt class="text-sm text-gray-500">{{ item.key }}</dt>
                    <dd class="text-gray-900">{{ item.value }}</dd>
                  </div>
                }
              </dl>
            </div>
          </div>
        }
      </div>
    </div>
  `
})
export class TranscriptDetailComponent implements OnInit {
  // Icons
  faArrowLeft = faArrowLeft;
  faFileLines = faFileLines;
  faRotate = faRotate;
  faTrash = faTrash;
  faMagnifyingGlass = faMagnifyingGlass;
  faCopy = faCopy;
  faCheck = faCheck;
  faDownload = faDownload;
  faClock = faClock;
  faDatabase = faDatabase;

  // State
  transcript = signal<Transcript | null>(null);
  isLoading = signal(true);
  isReindexing = signal(false);
  copied = signal(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private transcriptService: TranscriptService,
    private toast: ToastService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.loadTranscript(params['id']);
      }
    });
  }

  loadTranscript(filename: string): void {
    this.isLoading.set(true);
    this.transcriptService.getTranscript(filename).subscribe({
      next: (transcript) => {
        this.transcript.set(transcript);
        this.isLoading.set(false);
      },
      error: (error) => {
        this.isLoading.set(false);
        this.toast.error('Failed to load transcript');
        console.error('Load error:', error);
      }
    });
  }

  metadataEntries(): { key: string; value: any }[] {
    if (!this.transcript()?.metadata) return [];
    return Object.entries(this.transcript()!.metadata!).map(([key, value]) => ({
      key,
      value: typeof value === 'object' ? JSON.stringify(value) : value
    }));
  }

  hasMetadata(): boolean {
    return this.transcript()?.metadata ? Object.keys(this.transcript()!.metadata!).length > 0 : false;
  }

  searchTranscript(): void {
    this.router.navigate(['/search'], { 
      queryParams: { transcript: this.transcript()?.filename } 
    });
  }

  copyContent(): void {
    if (this.transcript()?.content) {
      navigator.clipboard.writeText(this.transcript()!.content!).then(() => {
        this.copied.set(true);
        this.toast.success('Content copied to clipboard');
        setTimeout(() => this.copied.set(false), 2000);
      });
    }
  }

  reindexTranscript(): void {
    if (!this.transcript()) return;
    
    this.isReindexing.set(true);
    this.transcriptService.reindexTranscript(this.transcript()!.filename).subscribe({
      next: () => {
        this.toast.success('Transcript reindexed');
        this.isReindexing.set(false);
        this.loadTranscript(this.transcript()!.filename);
      },
      error: () => {
        this.toast.error('Failed to reindex');
        this.isReindexing.set(false);
      }
    });
  }

  deleteTranscript(): void {
    if (!this.transcript()) return;

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Transcript',
        message: `Are you sure you want to delete "${this.transcript()!.filename}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel',
        type: 'danger'
      } as ConfirmDialogData
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (confirmed) {
        this.transcriptService.deleteTranscript(this.transcript()!.filename).subscribe({
          next: () => {
            this.toast.success('Transcript deleted');
            this.router.navigate(['/transcripts']);
          },
          error: () => {
            this.toast.error('Failed to delete transcript');
          }
        });
      }
    });
  }
}
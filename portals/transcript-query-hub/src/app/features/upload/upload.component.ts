import { Component, ViewChild, signal, inject, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faCloudArrowUp, 
  faCheck,
  faXmark,
  faArrowRight,
  faFileLines,
  faCircleInfo,
  faComments
} from '@fortawesome/free-solid-svg-icons';
import { FileUploadComponent, UploadedFile } from '../../shared/components/file-upload/file-upload.component';
import { TranscriptService } from '../../core/services/transcript.service';
import { ToastService } from '../../core/services/toast.service';
import { ConversationService } from '../../core/services/conversation.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    FormsModule,
    FontAwesomeModule, 
    FileUploadComponent
  ],
  template: `
    <div class="min-h-[80vh] bg-gray-50">
      <!-- Header -->
      <div class="bg-white border-b border-gray-200">
        <div class="container-app py-8">
          <h1 class="text-3xl font-bold text-gray-900">Upload Transcripts</h1>
          <p class="text-gray-600 mt-1">
            Upload your video transcripts to start searching with AI
          </p>
        </div>
      </div>

      <div class="container-app py-8">
        <div class="max-w-3xl mx-auto">
          <!-- Conversation Selection -->
          <div class="card p-6 mb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Select Conversation</h3>
            
            @if (conversations().length === 0) {
              <div class="text-center py-8 bg-gray-50 rounded-lg">
                <p class="text-gray-600 mb-4">No conversations yet. Create one to upload files.</p>
                <a routerLink="/conversations" class="btn btn-primary">Create Conversation</a>
              </div>
            } @else {
              <div class="flex gap-3 items-center">
                <select 
                  [(ngModel)]="selectedConversationId"
                  class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option [value]="null">Select a conversation...</option>
                  @for (conv of conversations(); track conv.id) {
                    <option [value]="conv.id">
                      {{ conv.name }} ({{ conv.file_count }} files)
                    </option>
                  }
                </select>
                <a routerLink="/conversations" class="btn btn-secondary whitespace-nowrap">
                  + New
                </a>
              </div>
              
              @if (selectedConversationId && selectedConversation()) {
                <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div class="flex justify-between items-start">
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ selectedConversation()!.name }}</p>
                      @if (selectedConversation()!.description) {
                        <p class="text-sm text-gray-600 mt-1">{{ selectedConversation()!.description }}</p>
                      }
                    </div>
                    <div class="text-sm text-gray-600">
                      {{ selectedConversation()!.file_count }} / {{ maxFilesPerConversation() === -1 ? '∞' : maxFilesPerConversation() }} files
                    </div>
                  </div>
                </div>
              }
            }
          </div>

          <!-- Upload Card -->
          <div class="card p-8 mb-8" [class.opacity-50]="!selectedConversationId">
            @if (!selectedConversationId) {
              <div class="text-center py-12 bg-gray-50 rounded-lg">
                <p class="text-gray-500">Please select a conversation first</p>
              </div>
            } @else {
              <app-file-upload
                #fileUpload
                [acceptedTypes]="'.txt,.srt,.vtt,.json'"
                [maxSize]="52428800"
                [maxFiles]="10"
                (filesSelected)="onFilesSelected($event)"
                (fileRemoved)="onFileRemoved($event)">
              </app-file-upload>
            }

            <!-- Options -->
            <div class="mt-6 pt-6 border-t border-gray-200">
              <div class="flex items-center gap-3">
                <input 
                  type="checkbox" 
                  id="autoIndex" 
                  [(ngModel)]="autoIndex"
                  class="w-4 h-4 rounded border-gray-300 text-tq-primary-600 
                         focus:ring-tq-primary-500"
                />
                <label for="autoIndex" class="text-sm text-gray-700">
                  Automatically index for search after upload
                </label>
              </div>
            </div>

            <!-- Upload Button -->
            @if (selectedFiles().length > 0) {
              <div class="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
                <p class="text-sm text-gray-500">
                  {{ selectedFiles().length }} file(s) ready to upload
                </p>
                <button 
                  (click)="uploadFiles()"
                  [disabled]="isUploading() || !selectedConversationId"
                  class="btn btn-primary">
                  @if (isUploading()) {
                    <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Uploading...
                  } @else {
                    <fa-icon [icon]="faCloudArrowUp"></fa-icon>
                    Upload Files
                  }
                </button>
              </div>
            }
          </div>

          <!-- Upload Progress -->
          @if (uploadResults().length > 0) {
            <div class="card p-6 mb-8">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Upload Results</h3>
              <div class="space-y-3">
                @for (result of uploadResults(); track result.filename) {
                  <div class="flex items-center gap-4 p-3 rounded-lg"
                       [class.bg-green-50]="result.success"
                       [class.bg-red-50]="!result.success">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center"
                         [class.bg-green-100]="result.success"
                         [class.bg-red-100]="!result.success">
                      <fa-icon [icon]="result.success ? faCheck : faXmark"
                               [class.text-green-600]="result.success"
                               [class.text-red-600]="!result.success"></fa-icon>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-gray-900 truncate">{{ result.filename }}</p>
                      <p class="text-sm" 
                         [class.text-green-600]="result.success"
                         [class.text-red-600]="!result.success">
                        {{ result.message }}
                      </p>
                    </div>
                  </div>
                }
              </div>

              <!-- Actions after upload -->
              @if (successCount() > 0) {
                <div class="mt-6 pt-6 border-t border-gray-200 flex flex-wrap gap-3">
                  <button (click)="goToChat()" class="btn btn-primary">
                    <fa-icon [icon]="faComments"></fa-icon>
                    Chat with Files
                  </button>
                  <a routerLink="/transcripts" class="btn btn-secondary">
                    <fa-icon [icon]="faFileLines"></fa-icon>
                    View All Transcripts
                  </a>
                </div>
              }
            </div>
          }

          <!-- Info Card -->
          <div class="card p-6 bg-tq-primary-50 border-tq-primary-200">
            <div class="flex gap-4">
              <div class="w-10 h-10 rounded-full bg-tq-primary-100 flex items-center justify-center flex-shrink-0">
                <fa-icon [icon]="faCircleInfo" class="text-tq-primary-600"></fa-icon>
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 mb-2">Supported Formats</h4>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li><strong>.txt</strong> - Plain text transcripts</li>
                  <li><strong>.srt</strong> - SubRip subtitle files</li>
                  <li><strong>.vtt</strong> - WebVTT subtitle files</li>
                  <li><strong>.json</strong> - JSON formatted transcripts</li>
                </ul>
                <p class="text-sm text-gray-500 mt-3">
                  Maximum file size: 50MB per file. Up to 10 files at once.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class UploadComponent implements OnInit {
  @ViewChild('fileUpload') fileUpload!: FileUploadComponent;

  private conversationService = inject(ConversationService);
  
  // Icons
  faCloudArrowUp = faCloudArrowUp;
  faCheck = faCheck;
  faXmark = faXmark;
  faArrowRight = faArrowRight;
  faFileLines = faFileLines;
  faCircleInfo = faCircleInfo;
  faComments = faComments;

  // State
  conversations = this.conversationService.conversations;
  selectedConversationId: string | null = null;  // Encrypted conversation ID
  selectedFiles = signal<File[]>([]);
  isUploading = signal(false);
  uploadResults = signal<{ filename: string; success: boolean; message: string }[]>([]);
  autoIndex = true;

  selectedConversation = computed(() => {
    return this.conversations().find(c => c.id === this.selectedConversationId) || null;
  });
  
  maxFilesPerConversation = computed(() => {
    // TODO: Get from tier limits
    return 5; // FREE tier default
  });

  constructor(
    private transcriptService: TranscriptService,
    private toast: ToastService,
    private router: Router
  ) {}
  
  ngOnInit() {
    this.conversationService.listConversations().subscribe({
      next: () => {
        // Auto-select first conversation if available
        if (this.conversations().length > 0) {
          this.selectedConversationId = this.conversations()[0].id;
        }
      }
    });
  }

  get successCount(): () => number {
    return () => this.uploadResults().filter(r => r.success).length;
  }

  onFilesSelected(files: File[]): void {
    this.selectedFiles.set(files);
    this.uploadResults.set([]);
  }

  onFileRemoved(file: UploadedFile): void {
    this.selectedFiles.update(files => files.filter(f => f.name !== file.name));
  }

  async uploadFiles(): Promise<void> {
    if (this.selectedFiles().length === 0 || !this.selectedConversationId) return;

    this.isUploading.set(true);
    this.uploadResults.set([]);
    const results: { filename: string; success: boolean; message: string }[] = [];

    for (const file of this.selectedFiles()) {
      try {
        // Update progress in file upload component
        this.fileUpload.updateFileStatus(file.name, 'uploading');
        this.fileUpload.updateFileProgress(file.name, 50);

        const response = await this.transcriptService
          .uploadTranscript(file, this.autoIndex, this.selectedConversationId)
          .toPromise();

        this.fileUpload.updateFileStatus(file.name, 'success');
        results.push({
          filename: file.name,
          success: true,
          message: response?.indexed 
            ? 'Uploaded and indexed (' + response.chunks_created + ' chunks)' 
            : 'Uploaded successfully'
        });
      } catch (error: any) {
        this.fileUpload.updateFileStatus(file.name, 'error', error.message || 'Upload failed');
        results.push({
          filename: file.name,
          success: false,
          message: error.message || 'Upload failed'
        });
      }
    }

    this.uploadResults.set(results);
    this.isUploading.set(false);

    const successCount = results.filter(r => r.success).length;
    if (successCount === results.length) {
      this.toast.success('All ' + successCount + ' file(s) uploaded successfully!');
    } else if (successCount > 0) {
      this.toast.warning(successCount + ' of ' + results.length + ' files uploaded');
    } else {
      this.toast.error('Upload failed. Please try again.');
    }

    // Refresh conversations to update file counts
    if (successCount > 0) {
      this.conversationService.listConversations().subscribe();
    }

    // Clear selected files
    this.selectedFiles.set([]);
  }

  goToChat(): void {
    // Select the conversation and navigate to chat
    const conversation = this.selectedConversation();
    if (conversation) {
      this.conversationService.selectConversation(conversation);
    }
    this.router.navigate(['/chat']);
  }
}

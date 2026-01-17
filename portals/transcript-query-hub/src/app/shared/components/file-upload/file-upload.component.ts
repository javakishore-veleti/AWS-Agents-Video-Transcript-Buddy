import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faCloudArrowUp, 
  faFile, 
  faXmark,
  faCheck,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';
import { FileSizePipe } from '../../pipes/file-size.pipe';

export interface UploadedFile {
  file: File;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, FontAwesomeModule, FileSizePipe],
  template: `
    <div class="w-full">
      <!-- Drop Zone -->
      <div 
        class="relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 cursor-pointer"
        [class.border-gray-300]="!isDragging() && !hasFiles()"
        [class.bg-gray-50]="!isDragging() && !hasFiles()"
        [class.border-tq-primary-500]="isDragging()"
        [class.bg-tq-primary-50]="isDragging()"
        [class.border-green-500]="hasFiles() && !isDragging()"
        [class.bg-green-50]="hasFiles() && !isDragging()"
        (dragover)="onDragOver($event)"
        (dragleave)="onDragLeave($event)"
        (drop)="onDrop($event)"
        (click)="fileInput.click()">
        
        <input 
          #fileInput
          type="file"
          [accept]="acceptedTypes"
          [multiple]="multiple"
          (change)="onFileSelect($event)"
          class="hidden"
        />
        
        <div class="flex flex-col items-center">
          <div class="w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-all duration-300"
               [class.bg-gray-200]="!isDragging()"
               [class.bg-tq-primary-200]="isDragging()">
            <fa-icon [icon]="faCloudArrowUp" 
                     class="text-3xl transition-colors duration-300"
                     [class.text-gray-400]="!isDragging()"
                     [class.text-tq-primary-600]="isDragging()"></fa-icon>
          </div>
          
          <p class="text-lg font-medium text-gray-700 mb-1">
            @if (isDragging()) {
              Drop files here
            } @else {
              Drag & drop files here
            }
          </p>
          <p class="text-sm text-gray-500 mb-4">or click to browse</p>
          
          <div class="flex flex-wrap items-center justify-center gap-2 text-xs text-gray-400">
            <span>Accepted: {{ acceptedTypesDisplay }}</span>
            <span class="w-1 h-1 rounded-full bg-gray-300"></span>
            <span>Max: {{ maxSize | fileSize }}</span>
          </div>
        </div>
      </div>
      
      <!-- File List -->
      @if (files().length > 0) {
        <div class="mt-4 space-y-3">
          @for (uploadedFile of files(); track uploadedFile.name) {
            <div class="flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-200
                        shadow-sm transition-all duration-300 hover:shadow-md">
              <!-- Icon -->
              <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                   [class.bg-tq-primary-100]="uploadedFile.status === 'pending'"
                   [class.bg-blue-100]="uploadedFile.status === 'uploading'"
                   [class.bg-green-100]="uploadedFile.status === 'success'"
                   [class.bg-red-100]="uploadedFile.status === 'error'">
                @if (uploadedFile.status === 'success') {
                  <fa-icon [icon]="faCheck" class="text-green-600"></fa-icon>
                } @else if (uploadedFile.status === 'error') {
                  <fa-icon [icon]="faExclamationTriangle" class="text-red-600"></fa-icon>
                } @else {
                  <fa-icon [icon]="faFile" class="text-tq-primary-600"></fa-icon>
                }
              </div>
              
              <!-- Info -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ uploadedFile.name }}</p>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <span>{{ uploadedFile.size | fileSize }}</span>
                  @if (uploadedFile.error) {
                    <span class="text-red-500">{{ uploadedFile.error }}</span>
                  }
                </div>
                
                <!-- Progress Bar -->
                @if (uploadedFile.status === 'uploading') {
                  <div class="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-tq-primary-600 transition-all duration-300 rounded-full"
                         [style.width.%]="uploadedFile.progress"></div>
                  </div>
                }
              </div>
              
              <!-- Remove Button -->
              <button 
                (click)="removeFile(uploadedFile)"
                class="p-2 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors">
                <fa-icon [icon]="faXmark"></fa-icon>
              </button>
            </div>
          }
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
export class FileUploadComponent {
  @Input() acceptedTypes: string = '.txt,.srt,.vtt,.json';
  @Input() multiple: boolean = true;
  @Input() maxSize: number = 50 * 1024 * 1024; // 50MB
  @Input() maxFiles: number = 10;

  @Output() filesSelected = new EventEmitter<File[]>();
  @Output() fileRemoved = new EventEmitter<UploadedFile>();

  // Icons
  faCloudArrowUp = faCloudArrowUp;
  faFile = faFile;
  faXmark = faXmark;
  faCheck = faCheck;
  faExclamationTriangle = faExclamationTriangle;

  // State
  isDragging = signal(false);
  files = signal<UploadedFile[]>([]);

  get acceptedTypesDisplay(): string {
    return this.acceptedTypes.split(',').join(', ');
  }

  hasFiles(): boolean {
    return this.files().length > 0;
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
    
    const files = event.dataTransfer?.files;
    if (files) {
      this.processFiles(Array.from(files));
    }
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.processFiles(Array.from(input.files));
      input.value = ''; // Reset input
    }
  }

  private processFiles(fileList: File[]): void {
    const validFiles: File[] = [];
    const currentFiles = this.files();
    
    for (const file of fileList) {
      // Check max files
      if (currentFiles.length + validFiles.length >= this.maxFiles) {
        break;
      }
      
      // Check file size
      if (file.size > this.maxSize) {
        this.addFile(file, 'error', 'File too large');
        continue;
      }
      
      // Check file type
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!this.acceptedTypes.includes(ext)) {
        this.addFile(file, 'error', 'Invalid file type');
        continue;
      }
      
      // Check duplicate
      if (currentFiles.some(f => f.name === file.name)) {
        continue;
      }
      
      this.addFile(file, 'pending');
      validFiles.push(file);
    }
    
    if (validFiles.length > 0) {
      this.filesSelected.emit(validFiles);
    }
  }

  private addFile(file: File, status: UploadedFile['status'], error?: string): void {
    const uploadedFile: UploadedFile = {
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status,
      error
    };
    
    this.files.update(files => [...files, uploadedFile]);
  }

  removeFile(uploadedFile: UploadedFile): void {
    this.files.update(files => files.filter(f => f.name !== uploadedFile.name));
    this.fileRemoved.emit(uploadedFile);
  }

  updateFileProgress(fileName: string, progress: number): void {
    this.files.update(files => 
      files.map(f => f.name === fileName ? { ...f, progress, status: 'uploading' as const } : f)
    );
  }

  updateFileStatus(fileName: string, status: UploadedFile['status'], error?: string): void {
    this.files.update(files => 
      files.map(f => f.name === fileName ? { ...f, status, error, progress: status === 'success' ? 100 : f.progress } : f)
    );
  }

  clearFiles(): void {
    this.files.set([]);
  }
}
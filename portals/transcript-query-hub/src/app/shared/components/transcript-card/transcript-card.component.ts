import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faFileLines, 
  faTrash, 
  faEye, 
  faRotate,
  faEllipsisV,
  faCheck,
  faClock
} from '@fortawesome/free-solid-svg-icons';
import { Transcript } from '../../../core/models/transcript.model';
import { TimeAgoPipe } from '../../pipes/time-ago.pipe';
import { FileSizePipe } from '../../pipes/file-size.pipe';

@Component({
  selector: 'app-transcript-card',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule, TimeAgoPipe, FileSizePipe],
  template: `
    <div class="card card-hover group" 
         [class.border-tq-primary-300]="selected"
         [class.ring-2]="selected"
         [class.ring-tq-primary-500]="selected">
      <div class="p-5">
        <!-- Header -->
        <div class="flex items-start justify-between gap-3 mb-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center
                        bg-gradient-to-br from-tq-primary-100 to-tq-secondary-100
                        group-hover:from-tq-primary-200 group-hover:to-tq-secondary-200
                        transition-colors duration-300">
              <fa-icon [icon]="faFileLines" class="text-tq-primary-600 text-xl"></fa-icon>
            </div>
            <div class="min-w-0">
              <h3 class="font-semibold text-gray-900 truncate group-hover:text-tq-primary-600 
                         transition-colors">
                {{ transcript.filename }}
              </h3>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                @if (transcript.size) {
                  <span>{{ transcript.size | fileSize }}</span>
                  <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                }
                @if (transcript.uploaded_at) {
                  <span class="flex items-center gap-1">
                    <fa-icon [icon]="faClock" class="text-xs"></fa-icon>
                    {{ transcript.uploaded_at | timeAgo }}
                  </span>
                }
              </div>
            </div>
          </div>
          
          <!-- Status Badge -->
          <div>
            @if (transcript.indexed) {
              <span class="badge badge-success">
                <fa-icon [icon]="faCheck" class="mr-1"></fa-icon>
                Indexed
              </span>
            } @else {
              <span class="badge badge-warning">Pending</span>
            }
          </div>
        </div>
        
        <!-- Stats -->
        @if (transcript.chunk_count) {
          <div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
            <span>{{ transcript.chunk_count }} chunks</span>
          </div>
        }
        
        <!-- Actions -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-100">
          <div class="flex items-center gap-2">
            <a [routerLink]="['/transcripts', transcript.filename]" 
               class="btn btn-sm btn-ghost text-gray-600 hover:text-tq-primary-600">
              <fa-icon [icon]="faEye"></fa-icon>
              View
            </a>
            <button 
              (click)="onReindex()"
              [disabled]="reindexing"
              class="btn btn-sm btn-ghost text-gray-600 hover:text-tq-accent-600">
              <fa-icon [icon]="faRotate" [class.animate-spin]="reindexing"></fa-icon>
              Reindex
            </button>
          </div>
          <button 
            (click)="onDelete()"
            [disabled]="deleting"
            class="btn btn-sm btn-ghost text-gray-400 hover:text-red-600 hover:bg-red-50">
            <fa-icon [icon]="faTrash"></fa-icon>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class TranscriptCardComponent {
  @Input({ required: true }) transcript!: Transcript;
  @Input() selected: boolean = false;
  @Input() reindexing: boolean = false;
  @Input() deleting: boolean = false;

  @Output() delete = new EventEmitter<Transcript>();
  @Output() reindex = new EventEmitter<Transcript>();
  @Output() view = new EventEmitter<Transcript>();

  // Icons
  faFileLines = faFileLines;
  faTrash = faTrash;
  faEye = faEye;
  faRotate = faRotate;
  faEllipsisV = faEllipsisV;
  faCheck = faCheck;
  faClock = faClock;

  onDelete(): void {
    this.delete.emit(this.transcript);
  }

  onReindex(): void {
    this.reindex.emit(this.transcript);
  }

  onView(): void {
    this.view.emit(this.transcript);
  }
}
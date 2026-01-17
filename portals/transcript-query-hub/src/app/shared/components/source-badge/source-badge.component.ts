import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faFileLines, faExternalLink } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-source-badge',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
  template: `
    <a [routerLink]="['/transcripts', transcriptId]"
       class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm
              bg-tq-primary-50 text-tq-primary-700 border border-tq-primary-200
              hover:bg-tq-primary-100 hover:border-tq-primary-300
              transition-all duration-200 group">
      <fa-icon [icon]="faFileLines" class="text-xs opacity-70"></fa-icon>
      <span class="font-medium truncate max-w-[150px]">{{ transcriptId }}</span>
      @if (chunkIndex !== undefined) {
        <span class="text-xs text-tq-primary-500">#{{ chunkIndex }}</span>
      }
      @if (score !== undefined) {
        <span class="text-xs px-1.5 py-0.5 rounded-full"
              [class.bg-green-100]="score >= 0.7"
              [class.text-green-700]="score >= 0.7"
              [class.bg-yellow-100]="score >= 0.4 && score < 0.7"
              [class.text-yellow-700]="score >= 0.4 && score < 0.7"
              [class.bg-gray-100]="score < 0.4"
              [class.text-gray-600]="score < 0.4">
          {{ (score * 100).toFixed(0) }}%
        </span>
      }
      <fa-icon [icon]="faExternalLink" 
               class="text-xs opacity-0 group-hover:opacity-70 transition-opacity"></fa-icon>
    </a>
  `
})
export class SourceBadgeComponent {
  @Input({ required: true }) transcriptId!: string;
  @Input() chunkIndex?: number;
  @Input() score?: number;

  faFileLines = faFileLines;
  faExternalLink = faExternalLink;
}
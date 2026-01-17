import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faFolderOpen, 
  faSearch, 
  faCloudArrowUp,
  faPlus
} from '@fortawesome/free-solid-svg-icons';

type EmptyStateType = 'no-data' | 'no-results' | 'no-transcripts' | 'error' | 'custom';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
  template: `
    <div class="flex flex-col items-center justify-center py-12 px-4 text-center"
         [class.py-16]="size === 'lg'"
         [class.py-8]="size === 'sm'">
      <!-- Icon -->
      <div class="w-20 h-20 rounded-full flex items-center justify-center mb-6
                  bg-gradient-to-br from-gray-100 to-gray-200"
           [class.w-16]="size === 'sm'"
           [class.h-16]="size === 'sm'"
           [class.w-24]="size === 'lg'"
           [class.h-24]="size === 'lg'">
        <fa-icon [icon]="displayIcon" 
                 class="text-gray-400"
                 [class.text-3xl]="size === 'md'"
                 [class.text-2xl]="size === 'sm'"
                 [class.text-4xl]="size === 'lg'"></fa-icon>
      </div>
      
      <!-- Title -->
      <h3 class="text-xl font-semibold text-gray-900 mb-2"
          [class.text-lg]="size === 'sm'"
          [class.text-2xl]="size === 'lg'">
        {{ displayTitle }}
      </h3>
      
      <!-- Description -->
      <p class="text-gray-500 max-w-md mb-6"
         [class.text-sm]="size === 'sm'">
        {{ displayDescription }}
      </p>
      
      <!-- Action Button -->
      @if (showAction) {
        @if (actionRoute) {
          <a [routerLink]="actionRoute" class="btn btn-primary">
            <fa-icon [icon]="actionIcon"></fa-icon>
            {{ actionLabel }}
          </a>
        } @else {
          <button (click)="onAction()" class="btn btn-primary">
            <fa-icon [icon]="actionIcon"></fa-icon>
            {{ actionLabel }}
          </button>
        }
      }
    </div>
  `
})
export class EmptyStateComponent {
  @Input() type: EmptyStateType = 'no-data';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() title: string = '';
  @Input() description: string = '';
  @Input() icon: any = null;
  @Input() showAction: boolean = true;
  @Input() actionLabel: string = '';
  @Input() actionRoute: string = '';
  @Input() actionIcon: any = faPlus;

  @Output() action = new EventEmitter<void>();

  // Icons
  faFolderOpen = faFolderOpen;
  faSearch = faSearch;
  faCloudArrowUp = faCloudArrowUp;
  faPlus = faPlus;

  get displayIcon(): any {
    if (this.icon) return this.icon;
    
    const icons: Record<EmptyStateType, any> = {
      'no-data': faFolderOpen,
      'no-results': faSearch,
      'no-transcripts': faCloudArrowUp,
      'error': faFolderOpen,
      'custom': faFolderOpen
    };
    
    return icons[this.type];
  }

  get displayTitle(): string {
    if (this.title) return this.title;
    
    const titles: Record<EmptyStateType, string> = {
      'no-data': 'No Data Found',
      'no-results': 'No Results Found',
      'no-transcripts': 'No Transcripts Yet',
      'error': 'Something Went Wrong',
      'custom': 'Nothing Here'
    };
    
    return titles[this.type];
  }

  get displayDescription(): string {
    if (this.description) return this.description;
    
    const descriptions: Record<EmptyStateType, string> = {
      'no-data': 'There\'s nothing here yet. Get started by adding some data.',
      'no-results': 'We couldn\'t find anything matching your search. Try different keywords.',
      'no-transcripts': 'Upload your first transcript to start searching and querying.',
      'error': 'We encountered an error. Please try again later.',
      'custom': 'This area is empty.'
    };
    
    return descriptions[this.type];
  }

  onAction(): void {
    this.action.emit();
  }
}
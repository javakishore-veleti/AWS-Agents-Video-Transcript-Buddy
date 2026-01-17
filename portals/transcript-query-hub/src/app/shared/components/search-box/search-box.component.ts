import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faMagnifyingGlass, 
  faXmark, 
  faMicrophone,
  faPaperPlane
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-search-box',
  standalone: true,
  imports: [CommonModule, FormsModule, FontAwesomeModule],
  template: `
    <div class="relative" [class]="containerClass">
      <!-- Search Icon -->
      <div class="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
        <fa-icon [icon]="faMagnifyingGlass" 
                 class="text-gray-400"
                 [class.text-lg]="size === 'lg'"
                 [class.text-base]="size === 'md'"></fa-icon>
      </div>
      
      <!-- Input -->
      <input
        type="text"
        [placeholder]="placeholder"
        [(ngModel)]="query"
        (ngModelChange)="onQueryChange($event)"
        (keyup.enter)="onSearch()"
        (focus)="isFocused.set(true)"
        (blur)="isFocused.set(false)"
        class="w-full bg-white border-2 rounded-2xl transition-all duration-300
               focus:outline-none focus:ring-0"
        [class.pl-12]="size === 'lg'"
        [class.pl-10]="size === 'md'"
        [class.pr-24]="showSubmitButton"
        [class.pr-12]="!showSubmitButton"
        [class.py-4]="size === 'lg'"
        [class.py-3]="size === 'md'"
        [class.text-lg]="size === 'lg'"
        [class.border-gray-200]="!isFocused()"
        [class.border-tq-primary-500]="isFocused()"
        [class.shadow-tq-glow]="isFocused()"
        [disabled]="disabled"
        [attr.aria-label]="placeholder"
      />
      
      <!-- Clear Button -->
      @if (query && query.length > 0) {
        <button 
          type="button"
          (click)="clearSearch()"
          class="absolute right-16 top-1/2 -translate-y-1/2 p-1.5 rounded-full
                 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all"
          [class.right-20]="showSubmitButton"
          [class.right-4]="!showSubmitButton"
          aria-label="Clear search">
          <fa-icon [icon]="faXmark"></fa-icon>
        </button>
      }
      
      <!-- Voice Button (optional) -->
      @if (showVoice && !query) {
        <button 
          type="button"
          class="absolute right-16 top-1/2 -translate-y-1/2 p-1.5 rounded-full
                 text-gray-400 hover:text-tq-primary-600 hover:bg-tq-primary-50 transition-all"
          [class.right-20]="showSubmitButton"
          [class.right-4]="!showSubmitButton"
          aria-label="Voice search">
          <fa-icon [icon]="faMicrophone"></fa-icon>
        </button>
      }
      
      <!-- Submit Button -->
      @if (showSubmitButton) {
        <button 
          type="button"
          (click)="onSearch()"
          [disabled]="disabled || !query || query.trim().length === 0"
          class="absolute right-2 top-1/2 -translate-y-1/2 btn btn-primary
                 disabled:opacity-50 disabled:cursor-not-allowed"
          [class.btn-sm]="size === 'md'"
          [class.px-4]="size === 'lg'"
          [class.py-2]="size === 'lg'">
          @if (loading) {
            <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          } @else {
            <fa-icon [icon]="faPaperPlane"></fa-icon>
          }
          @if (size === 'lg') {
            <span class="hidden sm:inline">Search</span>
          }
        </button>
      }
    </div>
    
    <!-- Suggestions -->
    @if (showSuggestions && suggestions.length > 0 && isFocused()) {
      <div class="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-tq-lg 
                  border border-gray-100 overflow-hidden z-50 animate-fade-in-down">
        <div class="p-2">
          <p class="text-xs text-gray-500 px-3 py-1">Suggestions</p>
          @for (suggestion of suggestions; track suggestion) {
            <button 
              type="button"
              (click)="selectSuggestion(suggestion)"
              class="w-full text-left px-3 py-2 text-sm text-gray-700 rounded-lg
                     hover:bg-tq-primary-50 hover:text-tq-primary-600 transition-colors">
              <fa-icon [icon]="faMagnifyingGlass" class="mr-2 text-gray-400"></fa-icon>
              {{ suggestion }}
            </button>
          }
        </div>
      </div>
    }
  `,
  styles: [`
    :host {
      display: block;
      position: relative;
    }
  `]
})
export class SearchBoxComponent {
  @Input() placeholder: string = 'Ask a question about your transcripts...';
  @Input() size: 'md' | 'lg' = 'lg';
  @Input() showSubmitButton: boolean = true;
  @Input() showVoice: boolean = false;
  @Input() showSuggestions: boolean = false;
  @Input() suggestions: string[] = [];
  @Input() disabled: boolean = false;
  @Input() loading: boolean = false;
  @Input() containerClass: string = '';
  @Input() initialQuery: string = '';

  @Output() search = new EventEmitter<string>();
  @Output() queryChange = new EventEmitter<string>();
  @Output() suggestionSelected = new EventEmitter<string>();

  // Icons
  faMagnifyingGlass = faMagnifyingGlass;
  faXmark = faXmark;
  faMicrophone = faMicrophone;
  faPaperPlane = faPaperPlane;

  // State
  query: string = '';
  isFocused = signal(false);

  ngOnInit(): void {
    if (this.initialQuery) {
      this.query = this.initialQuery;
    }
  }

  onQueryChange(value: string): void {
    this.queryChange.emit(value);
  }

  onSearch(): void {
    if (this.query && this.query.trim().length > 0) {
      this.search.emit(this.query.trim());
    }
  }

  clearSearch(): void {
    this.query = '';
    this.queryChange.emit('');
  }

  selectSuggestion(suggestion: string): void {
    this.query = suggestion;
    this.suggestionSelected.emit(suggestion);
    this.search.emit(suggestion);
  }
}
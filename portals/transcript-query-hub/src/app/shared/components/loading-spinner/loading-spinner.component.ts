import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex flex-col items-center justify-center gap-3" 
         [class.py-8]="!inline"
         [class.py-2]="inline">
      <!-- Spinner -->
      <div class="relative" [ngClass]="sizeClasses">
        <div class="absolute inset-0 rounded-full border-4 border-gray-200"></div>
        <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-tq-primary-600 
                    animate-spin"></div>
        @if (showLogo && size !== 'sm') {
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-tq-primary-600 font-bold" [class.text-xs]="size === 'md'" [class.text-sm]="size === 'lg'">TQ</span>
          </div>
        }
      </div>
      
      <!-- Message -->
      @if (message && !inline) {
        <p class="text-sm text-gray-500 animate-pulse">{{ message }}</p>
      }
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class LoadingSpinnerComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() message: string = '';
  @Input() inline: boolean = false;
  @Input() showLogo: boolean = true;

  get sizeClasses(): string {
    const sizes = {
      sm: 'w-6 h-6',
      md: 'w-12 h-12',
      lg: 'w-16 h-16'
    };
    return sizes[this.size];
  }
}
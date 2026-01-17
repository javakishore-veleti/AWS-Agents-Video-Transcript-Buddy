import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-skeleton-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    @switch (type) {
      @case ('text') {
        <div class="space-y-2">
          @for (line of lines; track $index) {
            <div class="skeleton h-4 rounded"
                 [style.width]="getRandomWidth()"></div>
          }
        </div>
      }
      @case ('card') {
        <div class="card p-5">
          <div class="flex items-start gap-4">
            <div class="skeleton w-12 h-12 rounded-xl"></div>
            <div class="flex-1 space-y-2">
              <div class="skeleton h-5 w-3/4 rounded"></div>
              <div class="skeleton h-4 w-1/2 rounded"></div>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-100">
            <div class="skeleton h-8 w-24 rounded-lg"></div>
          </div>
        </div>
      }
      @case ('list') {
        <div class="space-y-4">
          @for (item of items; track $index) {
            <div class="flex items-center gap-4">
              <div class="skeleton w-10 h-10 rounded-full"></div>
              <div class="flex-1 space-y-2">
                <div class="skeleton h-4 w-3/4 rounded"></div>
                <div class="skeleton h-3 w-1/2 rounded"></div>
              </div>
            </div>
          }
        </div>
      }
      @case ('search-result') {
        <div class="space-y-4">
          @for (item of items; track $index) {
            <div class="card p-4">
              <div class="skeleton h-5 w-2/3 rounded mb-2"></div>
              <div class="space-y-1.5">
                <div class="skeleton h-3 w-full rounded"></div>
                <div class="skeleton h-3 w-5/6 rounded"></div>
                <div class="skeleton h-3 w-4/6 rounded"></div>
              </div>
              <div class="flex gap-2 mt-3">
                <div class="skeleton h-6 w-20 rounded-full"></div>
                <div class="skeleton h-6 w-16 rounded-full"></div>
              </div>
            </div>
          }
        </div>
      }
      @case ('avatar') {
        <div class="skeleton rounded-full"
             [style.width.px]="width"
             [style.height.px]="height"></div>
      }
      @case ('image') {
        <div class="skeleton rounded-lg"
             [style.width]="width ? width + 'px' : '100%'"
             [style.height.px]="height || 200"></div>
      }
      @default {
        <div class="skeleton rounded"
             [style.width]="width ? width + 'px' : '100%'"
             [style.height.px]="height || 20"></div>
      }
    }
  `,
  styles: [`
    .skeleton {
      @apply animate-pulse bg-gray-200;
    }
  `]
})
export class SkeletonLoaderComponent {
  @Input() type: 'text' | 'card' | 'list' | 'search-result' | 'avatar' | 'image' | 'custom' = 'text';
  @Input() count: number = 3;
  @Input() width?: number;
  @Input() height?: number;

  get lines(): number[] {
    return Array(this.count).fill(0);
  }

  get items(): number[] {
    return Array(this.count).fill(0);
  }

  getRandomWidth(): string {
    const widths = ['100%', '90%', '80%', '95%', '85%'];
    return widths[Math.floor(Math.random() * widths.length)];
  }
}
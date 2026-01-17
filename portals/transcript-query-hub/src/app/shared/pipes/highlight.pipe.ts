import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'highlight',
  standalone: true
})
export class HighlightPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(text: string | null | undefined, search: string | null | undefined): SafeHtml {
    if (!text) return '';
    if (!search || search.trim() === '') return text;

    // Escape special regex characters
    const escapedSearch = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // Create regex for case-insensitive search
    const regex = new RegExp(`(${escapedSearch})`, 'gi');
    
    // Replace matches with highlighted span
    const highlighted = text.replace(regex, '<mark class="bg-yellow-200 text-yellow-900 px-0.5 rounded">$1</mark>');
    
    return this.sanitizer.bypassSecurityTrustHtml(highlighted);
  }
}
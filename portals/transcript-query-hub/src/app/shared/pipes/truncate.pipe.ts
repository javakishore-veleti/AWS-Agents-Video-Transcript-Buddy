import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncate',
  standalone: true
})
export class TruncatePipe implements PipeTransform {
  transform(value: string | null | undefined, limit: number = 100, ellipsis: string = '...'): string {
    if (!value) return '';
    
    if (value.length <= limit) {
      return value;
    }
    
    // Try to truncate at word boundary
    const truncated = value.substring(0, limit);
    const lastSpace = truncated.lastIndexOf(' ');
    
    if (lastSpace > limit * 0.8) {
      return truncated.substring(0, lastSpace) + ellipsis;
    }
    
    return truncated + ellipsis;
  }
}
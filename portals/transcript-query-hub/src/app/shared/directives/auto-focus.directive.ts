import { Directive, ElementRef, AfterViewInit, Input } from '@angular/core';

@Directive({
  selector: '[appAutoFocus]',
  standalone: true
})
export class AutoFocusDirective implements AfterViewInit {
  @Input() appAutoFocus: boolean = true;
  @Input() focusDelay: number = 0;

  constructor(private elementRef: ElementRef) {}

  ngAfterViewInit(): void {
    if (this.appAutoFocus) {
      setTimeout(() => {
        this.elementRef.nativeElement.focus();
      }, this.focusDelay);
    }
  }
}
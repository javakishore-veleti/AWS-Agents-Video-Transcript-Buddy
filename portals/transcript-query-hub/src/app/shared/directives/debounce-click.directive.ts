import { Directive, EventEmitter, HostListener, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

@Directive({
  selector: '[appDebounceClick]',
  standalone: true
})
export class DebounceClickDirective implements OnInit, OnDestroy {
  @Input() debounceTime: number = 300;
  @Output() debounceClick = new EventEmitter<Event>();

  private clicks = new Subject<Event>();
  private subscription!: Subscription;

  ngOnInit(): void {
    this.subscription = this.clicks
      .pipe(debounceTime(this.debounceTime))
      .subscribe(event => this.debounceClick.emit(event));
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  @HostListener('click', ['$event'])
  onClick(event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.clicks.next(event);
  }
}
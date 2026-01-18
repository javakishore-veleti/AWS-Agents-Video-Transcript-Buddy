import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Angular Material Modules
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatBadgeModule } from '@angular/material/badge';
import { MatRippleModule } from '@angular/material/core';

// Font Awesome
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Components
// import { HeaderComponent } from './components/header/header.component'; // Now standalone
import { FooterComponent } from './components/footer/footer.component';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';
import { SearchBoxComponent } from './components/search-box/search-box.component';
import { TranscriptCardComponent } from './components/transcript-card/transcript-card.component';
import { EmptyStateComponent } from './components/empty-state/empty-state.component';
import { ConfirmDialogComponent } from './components/confirm-dialog/confirm-dialog.component';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { SourceBadgeComponent } from './components/source-badge/source-badge.component';
import { SkeletonLoaderComponent } from './components/skeleton-loader/skeleton-loader.component';

// Pipes
import { TimeAgoPipe } from './pipes/time-ago.pipe';
import { TruncatePipe } from './pipes/truncate.pipe';
import { FileSizePipe } from './pipes/file-size.pipe';
import { HighlightPipe } from './pipes/highlight.pipe';

// Directives
import { ClickOutsideDirective } from './directives/click-outside.directive';
import { AutoFocusDirective } from './directives/auto-focus.directive';
import { DebounceClickDirective } from './directives/debounce-click.directive';

const MATERIAL_MODULES = [
  MatButtonModule,
  MatIconModule,
  MatInputModule,
  MatFormFieldModule,
  MatCardModule,
  MatProgressSpinnerModule,
  MatProgressBarModule,
  MatChipsModule,
  MatTooltipModule,
  MatMenuModule,
  MatDialogModule,
  MatSnackBarModule,
  MatTabsModule,
  MatExpansionModule,
  MatBadgeModule,
  MatRippleModule,
];

const COMPONENTS = [
  // HeaderComponent, // Now standalone, imported directly where needed
  FooterComponent,
  LoadingSpinnerComponent,
  SearchBoxComponent,
  TranscriptCardComponent,
  EmptyStateComponent,
  ConfirmDialogComponent,
  FileUploadComponent,
  SourceBadgeComponent,
  SkeletonLoaderComponent,
];

const PIPES = [
  TimeAgoPipe,
  TruncatePipe,
  FileSizePipe,
  HighlightPipe,
];

const DIRECTIVES = [
  ClickOutsideDirective,
  AutoFocusDirective,
  DebounceClickDirective,
];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    FontAwesomeModule,
    ...MATERIAL_MODULES,
    ...COMPONENTS,
    ...PIPES,
    ...DIRECTIVES,
  ],
  exports: [
    // Modules
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    FontAwesomeModule,
    ...MATERIAL_MODULES,
    // Components, Pipes, Directives
    ...COMPONENTS,
    ...PIPES,
    ...DIRECTIVES,
  ],
})
export class SharedModule {}
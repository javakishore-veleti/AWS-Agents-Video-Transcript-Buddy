import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { 
  faExclamationTriangle, 
  faQuestionCircle,
  faInfoCircle,
  faCheckCircle
} from '@fortawesome/free-solid-svg-icons';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'danger' | 'info' | 'success';
  showCancel?: boolean;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, FontAwesomeModule],
  template: `
    <div class="p-6 max-w-md">
      <!-- Icon -->
      <div class="flex justify-center mb-4">
        <div class="w-16 h-16 rounded-full flex items-center justify-center"
             [class.bg-yellow-100]="data.type === 'warning'"
             [class.bg-red-100]="data.type === 'danger'"
             [class.bg-blue-100]="data.type === 'info'"
             [class.bg-green-100]="data.type === 'success'">
          <fa-icon [icon]="getIcon()" 
                   class="text-3xl"
                   [class.text-yellow-600]="data.type === 'warning'"
                   [class.text-red-600]="data.type === 'danger'"
                   [class.text-blue-600]="data.type === 'info'"
                   [class.text-green-600]="data.type === 'success'"></fa-icon>
        </div>
      </div>
      
      <!-- Title -->
      <h2 class="text-xl font-semibold text-gray-900 text-center mb-2">
        {{ data.title }}
      </h2>
      
      <!-- Message -->
      <p class="text-gray-600 text-center mb-6">
        {{ data.message }}
      </p>
      
      <!-- Actions -->
      <div class="flex items-center justify-center gap-3">
        @if (data.showCancel !== false) {
          <button 
            mat-button
            (click)="onCancel()"
            class="btn btn-secondary">
            {{ data.cancelText || 'Cancel' }}
          </button>
        }
        <button 
          mat-raised-button
          (click)="onConfirm()"
          class="btn"
          [class.btn-primary]="data.type === 'info' || data.type === 'success'"
          [class.bg-red-600]="data.type === 'danger'"
          [class.hover:bg-red-700]="data.type === 'danger'"
          [class.text-white]="data.type === 'danger'"
          [class.bg-yellow-600]="data.type === 'warning'"
          [class.hover:bg-yellow-700]="data.type === 'warning'"
          [class.text-white]="data.type === 'warning'">
          {{ data.confirmText || 'Confirm' }}
        </button>
      </div>
    </div>
  `
})
export class ConfirmDialogComponent {
  faExclamationTriangle = faExclamationTriangle;
  faQuestionCircle = faQuestionCircle;
  faInfoCircle = faInfoCircle;
  faCheckCircle = faCheckCircle;

  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData
  ) {
    // Set default type
    if (!data.type) {
      data.type = 'warning';
    }
  }

  getIcon(): any {
    const icons = {
      warning: this.faExclamationTriangle,
      danger: this.faExclamationTriangle,
      info: this.faInfoCircle,
      success: this.faCheckCircle
    };
    return icons[this.data.type || 'warning'];
  }

  onConfirm(): void {
    this.dialogRef.close(true);
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
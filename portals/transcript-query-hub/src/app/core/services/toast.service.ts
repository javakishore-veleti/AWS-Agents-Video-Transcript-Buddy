import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

export interface ToastOptions {
  title?: string;
  duration?: number;
  closeButton?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private defaultOptions = {
    timeOut: 3000,
    closeButton: true,
    progressBar: true,
    positionClass: 'toast-bottom-right',
    enableHtml: true,
  };

  constructor(private toastr: ToastrService) {}

  /**
   * Show success toast
   */
  success(message: string, options?: ToastOptions): void {
    this.toastr.success(message, options?.title || 'Success', {
      ...this.defaultOptions,
      timeOut: options?.duration || this.defaultOptions.timeOut,
    });
  }

  /**
   * Show error toast
   */
  error(message: string, options?: ToastOptions): void {
    this.toastr.error(message, options?.title || 'Error', {
      ...this.defaultOptions,
      timeOut: options?.duration || 5000,
    });
  }

  /**
   * Show warning toast
   */
  warning(message: string, options?: ToastOptions): void {
    this.toastr.warning(message, options?.title || 'Warning', {
      ...this.defaultOptions,
      timeOut: options?.duration || 4000,
    });
  }

  /**
   * Show info toast
   */
  info(message: string, options?: ToastOptions): void {
    this.toastr.info(message, options?.title || 'Info', {
      ...this.defaultOptions,
      timeOut: options?.duration || this.defaultOptions.timeOut,
    });
  }

  /**
   * Show loading toast (stays until cleared)
   */
  loading(message: string = 'Loading...'): number {
    const toast = this.toastr.info(message, '', {
      ...this.defaultOptions,
      timeOut: 0,
      extendedTimeOut: 0,
      tapToDismiss: false,
    });
    return toast.toastId;
  }

  /**
   * Clear specific toast
   */
  clear(toastId?: number): void {
    if (toastId) {
      this.toastr.clear(toastId);
    } else {
      this.toastr.clear();
    }
  }

  /**
   * Clear all toasts
   */
  clearAll(): void {
    this.toastr.clear();
  }
}
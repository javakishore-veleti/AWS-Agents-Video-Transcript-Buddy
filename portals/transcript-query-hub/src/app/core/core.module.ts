import { NgModule, Optional, SkipSelf } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

// Services
import { ApiService } from './services/api.service';
import { TranscriptService } from './services/transcript.service';
import { QueryService } from './services/query.service';
import { StorageService } from './services/storage.service';
import { ToastService } from './services/toast.service';

// Interceptors
import { ApiInterceptor } from './interceptors/api.interceptor';
import { ErrorInterceptor } from './interceptors/error.interceptor';
import { LoadingInterceptor } from './interceptors/loading.interceptor';

// Guards
import { AuthGuard } from './guards/auth.guard';

@NgModule({
  imports: [
    CommonModule,
    HttpClientModule,
  ],
  providers: [
    // Services
    ApiService,
    TranscriptService,
    QueryService,
    StorageService,
    ToastService,
    
    // Guards
    AuthGuard,
    
    // Interceptors
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ApiInterceptor,
      multi: true,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorInterceptor,
      multi: true,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoadingInterceptor,
      multi: true,
    },
  ],
})
export class CoreModule {
  constructor(@Optional() @SkipSelf() parentModule: CoreModule) {
    if (parentModule) {
      throw new Error(
        'CoreModule is already loaded. Import it in the AppModule only.'
      );
    }
  }
}
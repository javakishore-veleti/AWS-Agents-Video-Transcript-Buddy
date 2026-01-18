import { Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent),
    title: 'TranscriptQuery Hub - Home'
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent),
    title: 'Login - TranscriptQuery Hub'
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register.component').then(m => m.RegisterComponent),
    title: 'Register - TranscriptQuery Hub'
  },
  {
    path: 'search',
    loadComponent: () => import('./features/search/search.component').then(m => m.SearchComponent),
    title: 'Search - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: 'chat',
    loadComponent: () => import('./features/chat/chat.component').then(m => m.ChatComponent),
    title: 'Chat - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: 'transcripts',
    loadComponent: () => import('./features/transcripts/transcripts.component').then(m => m.TranscriptsComponent),
    title: 'Transcripts - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: 'transcripts/:id',
    loadComponent: () => import('./features/transcript-detail/transcript-detail.component').then(m => m.TranscriptDetailComponent),
    title: 'Transcript Details - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: 'upload',
    loadComponent: () => import('./features/upload/upload.component').then(m => m.UploadComponent),
    title: 'Upload - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: 'usage',
    loadComponent: () => import('./features/usage/usage.component').then(m => m.UsageComponent),
    title: 'Usage & Billing - TranscriptQuery Hub',
    canActivate: [AuthGuard]
  },
  {
    path: '**',
    redirectTo: ''
  }
];
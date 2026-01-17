import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent),
    title: 'TranscriptQuery Hub - Home'
  },
  {
    path: 'search',
    loadComponent: () => import('./features/search/search.component').then(m => m.SearchComponent),
    title: 'Search - TranscriptQuery Hub'
  },
  {
    path: 'transcripts',
    loadComponent: () => import('./features/transcripts/transcripts.component').then(m => m.TranscriptsComponent),
    title: 'Transcripts - TranscriptQuery Hub'
  },
  {
    path: 'transcripts/:id',
    loadComponent: () => import('./features/transcript-detail/transcript-detail.component').then(m => m.TranscriptDetailComponent),
    title: 'Transcript Details - TranscriptQuery Hub'
  },
  {
    path: 'upload',
    loadComponent: () => import('./features/upload/upload.component').then(m => m.UploadComponent),
    title: 'Upload - TranscriptQuery Hub'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { TranscriptsComponent } from './transcripts.component';

const routes: Routes = [
  { path: '', component: TranscriptsComponent }
];

@NgModule({
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    TranscriptsComponent
  ]
})
export class TranscriptsModule {}
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { SearchComponent } from './search.component';

const routes: Routes = [
  { path: '', component: SearchComponent }
];

@NgModule({
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    SearchComponent
  ]
})
export class SearchModule {}
import { Routes } from '@angular/router';
import { HomePage } from './pages/home.page';
import { CategoriesPage } from './pages/categories.page';
import { ProductsPage } from './pages/products.page';

export const routes: Routes = [
  { path: '', component: HomePage, title: 'Inicio' },
  { path: 'categories', component: CategoriesPage, title: 'Categorias' },
  { path: 'products', component: ProductsPage, title: 'Produtos' },
  { path: '**', redirectTo: '' }
];

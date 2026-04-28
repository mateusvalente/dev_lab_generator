import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <header class="app-header">
      <div>
        <h1>Laboratorio CRUD - Angular SPA</h1>
        <p>Rotas, paginas, servicos e formularios separados para estudar Angular por partes.</p>
      </div>

      <nav class="nav">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Inicio</a>
        <a routerLink="/categories" routerLinkActive="active">Categorias</a>
        <a routerLink="/products" routerLinkActive="active">Produtos</a>
      </nav>
    </header>

    <main class="page-shell">
      <router-outlet />
    </main>
  `
})
export class AppComponent {}

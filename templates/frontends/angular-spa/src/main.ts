import { bootstrapApplication } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

const API = '{{API_BASE_URL}}' || 'http://localhost:8000/api';

async function req(path: string, options: RequestInit = {}) {
  if (!API) throw new Error('Nenhum backend foi configurado para este laboratório.');
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  if (!res.ok) throw new Error(await res.text());
  return res.status === 204 ? null : res.json();
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <main style="font-family: Arial, sans-serif; padding: 24px; max-width: 1200px; margin: 0 auto;">
      <h1>Laboratório CRUD - Angular SPA</h1>
      <p>Uma única página controlando categorias e produtos.</p>
      <div *ngIf="message()" style="margin-bottom: 16px; padding: 12px; background: #eef6ff; border: 1px solid #c9def8; border-radius: 8px;">{{ message() }}</div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <section style="border: 1px solid #ddd; border-radius: 12px; padding: 16px;">
          <h2>Categorias</h2>
          <div style="display: grid; gap: 8px; margin-bottom: 16px;">
            <input [(ngModel)]="category.NAME" placeholder="Nome" />
            <input [(ngModel)]="category.DESCRIPTION" placeholder="Descrição" />
            <div style="display:flex; gap:8px;">
              <button (click)="saveCategory()">{{ category.ID ? 'Atualizar' : 'Adicionar' }}</button>
              <button *ngIf="category.ID" (click)="resetCategory()">Cancelar</button>
            </div>
          </div>
          <table border="1" cellPadding="8" style="width:100%; border-collapse:collapse;">
            <thead><tr><th>ID</th><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
            <tbody>
              <tr *ngFor="let item of categories()">
                <td>{{ item.ID }}</td>
                <td>{{ item.NAME }}</td>
                <td>{{ item.DESCRIPTION }}</td>
                <td>
                  <button (click)="editCategory(item)">Editar</button>
                  <button (click)="removeCategory(item.ID)">Excluir</button>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <section style="border: 1px solid #ddd; border-radius: 12px; padding: 16px;">
          <h2>Produtos</h2>
          <div style="display: grid; gap: 8px; margin-bottom: 16px;">
            <select [(ngModel)]="product.CATEGORY_ID">
              <option [ngValue]="0">Selecione a categoria</option>
              <option *ngFor="let item of categories()" [ngValue]="item.ID">{{ item.NAME }}</option>
            </select>
            <input [(ngModel)]="product.NAME" placeholder="Nome" />
            <input [(ngModel)]="product.PRICE" type="number" step="0.01" placeholder="Preço" />
            <input [(ngModel)]="product.STOCK" type="number" placeholder="Estoque" />
            <div style="display:flex; gap:8px;">
              <button (click)="saveProduct()">{{ product.ID ? 'Atualizar' : 'Adicionar' }}</button>
              <button *ngIf="product.ID" (click)="resetProduct()">Cancelar</button>
            </div>
          </div>
          <table border="1" cellPadding="8" style="width:100%; border-collapse:collapse;">
            <thead><tr><th>ID</th><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ações</th></tr></thead>
            <tbody>
              <tr *ngFor="let item of products()">
                <td>{{ item.ID }}</td>
                <td>{{ item.NAME }}</td>
                <td>{{ item.CATEGORY_NAME || item.CATEGORY_ID }}</td>
                <td>{{ item.PRICE }}</td>
                <td>{{ item.STOCK }}</td>
                <td>
                  <button (click)="editProduct(item)">Editar</button>
                  <button (click)="removeProduct(item.ID)">Excluir</button>
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>
    </main>
  `
})
class AppComponent {
  categories = signal<any[]>([]);
  products = signal<any[]>([]);
  message = signal('');
  category: any = { ID: null, NAME: '', DESCRIPTION: '' };
  product: any = { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 };

  constructor() {
    this.load();
  }

  async load() {
    try {
      this.categories.set(await req('/categories'));
      this.products.set(await req('/products'));
      this.message.set('Dados carregados com sucesso.');
    } catch (error: any) {
      this.message.set(error?.message || 'Falha ao carregar dados.');
    }
  }

  editCategory(item: any) { this.category = { ID: item.ID, NAME: item.NAME, DESCRIPTION: item.DESCRIPTION ?? '' }; }
  resetCategory() { this.category = { ID: null, NAME: '', DESCRIPTION: '' }; }
  async saveCategory() {
    try {
      if (this.category.ID) await req(`/categories/${this.category.ID}`, { method: 'PUT', body: JSON.stringify(this.category) });
      else await req('/categories', { method: 'POST', body: JSON.stringify(this.category) });
      this.resetCategory();
      await this.load();
      this.message.set('Categoria salva com sucesso.');
    } catch (error: any) {
      this.message.set(error?.message || 'Falha ao salvar categoria.');
    }
  }
  async removeCategory(id: number) {
    try {
      await req(`/categories/${id}`, { method: 'DELETE' });
      await this.load();
      this.message.set('Categoria removida com sucesso.');
    } catch (error: any) {
      this.message.set(error?.message || 'Falha ao remover categoria.');
    }
  }

  editProduct(item: any) { this.product = { ID: item.ID, CATEGORY_ID: Number(item.CATEGORY_ID), NAME: item.NAME, PRICE: Number(item.PRICE), STOCK: Number(item.STOCK) }; }
  resetProduct() { this.product = { ID: null, CATEGORY_ID: 0, NAME: '', PRICE: 0, STOCK: 0 }; }
  async saveProduct() {
    try {
      if (this.product.ID) await req(`/products/${this.product.ID}`, { method: 'PUT', body: JSON.stringify(this.product) });
      else await req('/products', { method: 'POST', body: JSON.stringify(this.product) });
      this.resetProduct();
      await this.load();
      this.message.set('Produto salvo com sucesso.');
    } catch (error: any) {
      this.message.set(error?.message || 'Falha ao salvar produto.');
    }
  }
  async removeProduct(id: number) {
    try {
      await req(`/products/${id}`, { method: 'DELETE' });
      await this.load();
      this.message.set('Produto removido com sucesso.');
    } catch (error: any) {
      this.message.set(error?.message || 'Falha ao remover produto.');
    }
  }
}

bootstrapApplication(AppComponent);

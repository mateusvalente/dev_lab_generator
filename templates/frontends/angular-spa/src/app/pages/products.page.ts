import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category, Product } from '../models';
import { ApiService } from '../services/api.service';

@Component({
  standalone: true,
  imports: [FormsModule],
  templateUrl: './products.page.html',
  styleUrl: './products.page.css'
})
export class ProductsPage implements OnInit {
  private readonly api = inject(ApiService);

  categories: Category[] = [];
  products: Product[] = [];
  form: Product = this.emptyForm();
  loading = false;
  error = '';

  ngOnInit(): void {
    void this.load();
  }

  async load(): Promise<void> {
    this.loading = true;
    this.error = '';

    try {
      const [categories, products] = await Promise.all([
        this.api.listCategories(),
        this.api.listProducts()
      ]);

      this.categories = categories;
      this.products = products;
    } catch (error) {
      this.error = this.messageFrom(error);
    } finally {
      this.loading = false;
    }
  }

  edit(product: Product): void {
    this.form = { ...product };
  }

  reset(): void {
    this.form = this.emptyForm();
  }

  async save(): Promise<void> {
    if (!this.form.name.trim() || !this.form.category_id) return;

    try {
      if (this.form.id) {
        await this.api.updateProduct(this.form);
      } else {
        await this.api.createProduct(this.form);
      }

      this.reset();
      await this.load();
    } catch (error) {
      this.error = this.messageFrom(error);
    }
  }

  async remove(product: Product): Promise<void> {
    if (!product.id) return;

    try {
      await this.api.deleteProduct(product.id);
      await this.load();
    } catch (error) {
      this.error = this.messageFrom(error);
    }
  }

  private emptyForm(): Product {
    return { id: null, category_id: 0, name: '', price: 0, stock: 0 };
  }

  private messageFrom(error: unknown): string {
    return error instanceof Error ? error.message : 'Nao foi possivel concluir a operacao.';
  }
}

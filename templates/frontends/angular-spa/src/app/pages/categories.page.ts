import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category } from '../models';
import { ApiService } from '../services/api.service';

@Component({
  standalone: true,
  imports: [FormsModule],
  templateUrl: './categories.page.html',
  styleUrl: './categories.page.css'
})
export class CategoriesPage implements OnInit {
  private readonly api = inject(ApiService);

  categories: Category[] = [];
  form: Category = this.emptyForm();
  loading = false;
  error = '';

  ngOnInit(): void {
    void this.load();
  }

  async load(): Promise<void> {
    this.loading = true;
    this.error = '';

    try {
      this.categories = await this.api.listCategories();
    } catch (error) {
      this.error = this.messageFrom(error);
    } finally {
      this.loading = false;
    }
  }

  edit(category: Category): void {
    this.form = { ...category };
  }

  reset(): void {
    this.form = this.emptyForm();
  }

  async save(): Promise<void> {
    if (!this.form.name.trim()) return;

    try {
      if (this.form.id) {
        await this.api.updateCategory(this.form);
      } else {
        await this.api.createCategory(this.form);
      }

      this.reset();
      await this.load();
    } catch (error) {
      this.error = this.messageFrom(error);
    }
  }

  async remove(category: Category): Promise<void> {
    if (!category.id) return;

    try {
      await this.api.deleteCategory(category.id);
      await this.load();
    } catch (error) {
      this.error = this.messageFrom(error);
    }
  }

  private emptyForm(): Category {
    return { id: null, name: '', description: '' };
  }

  private messageFrom(error: unknown): string {
    return error instanceof Error ? error.message : 'Nao foi possivel concluir a operacao.';
  }
}

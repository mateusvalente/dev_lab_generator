import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { Category, Product } from '../models';

const API_BASE_URL = 'http://localhost:8000/api';

interface ApiCategory {
  ID: number;
  NAME: string;
  DESCRIPTION: string | null;
}

interface ApiProduct {
  ID: number;
  CATEGORY_ID: number;
  NAME: string;
  PRICE: number;
  STOCK: number;
  CATEGORY_NAME?: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  async listCategories(): Promise<Category[]> {
    const categories = await firstValueFrom(this.http.get<ApiCategory[]>(`${API_BASE_URL}/categories`));
    return categories.map((category) => this.toCategory(category));
  }

  createCategory(category: Category): Promise<Category> {
    return firstValueFrom(this.http.post<Category>(`${API_BASE_URL}/categories`, category));
  }

  updateCategory(category: Category): Promise<Category> {
    return firstValueFrom(this.http.put<Category>(`${API_BASE_URL}/categories/${category.id}`, category));
  }

  deleteCategory(id: number): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${API_BASE_URL}/categories/${id}`));
  }

  async listProducts(): Promise<Product[]> {
    const products = await firstValueFrom(this.http.get<ApiProduct[]>(`${API_BASE_URL}/products`));
    return products.map((product) => this.toProduct(product));
  }

  createProduct(product: Product): Promise<Product> {
    return firstValueFrom(this.http.post<Product>(`${API_BASE_URL}/products`, product));
  }

  updateProduct(product: Product): Promise<Product> {
    return firstValueFrom(this.http.put<Product>(`${API_BASE_URL}/products/${product.id}`, product));
  }

  deleteProduct(id: number): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${API_BASE_URL}/products/${id}`));
  }

  private toCategory(category: ApiCategory): Category {
    return {
      id: category.ID,
      name: category.NAME,
      description: category.DESCRIPTION ?? ''
    };
  }

  private toProduct(product: ApiProduct): Product {
    return {
      id: product.ID,
      category_id: product.CATEGORY_ID,
      name: product.NAME,
      price: product.PRICE,
      stock: product.STOCK,
      category_name: product.CATEGORY_NAME ?? ''
    };
  }
}

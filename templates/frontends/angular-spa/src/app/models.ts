export interface Category {
  id: number | null;
  name: string;
  description: string;
}

export interface Product {
  id: number | null;
  category_id: number;
  category_name?: string;
  name: string;
  price: number;
  stock: number;
}

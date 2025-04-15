export interface Product {
  id: string;
  title: string;
  average_rating: number | null;
  rating_number: number | null;
  description?: string | null;
  imageUrls: string[];
  price?: string | null; // TODO - fix types
  store?: string | null;
  createdAt: string;
  modifiedAt: string;
  similarity?: number | null;
}

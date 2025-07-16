'use client';

import { useEffect, useState } from 'react';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  current_stock: number;
  is_available: boolean;
  description: string;
}

export default function VaaniKart() {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    async function fetchProducts() {
      try {
        const res = await fetch('https://remhqhnmphsxufvdpokr.supabase.co/api/products/', {
          cache: 'no-store',
        });

        if (!res.ok) {
          throw new Error('Failed to fetch products');
        }

        const data = await res.json();
        setProducts(data);
      } catch (error) {
        console.error('❌ Fetch error:', error);
      }
    }

    fetchProducts();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">🛒 VaaniKart</h1>
      <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <li key={product.id} className="border p-4 rounded shadow">
            <h2 className="text-xl font-semibold">{product.name}</h2>
            <p className="text-sm text-gray-500">{product.category}</p>
            <p className="text-md mt-1">₹ {product.price}</p>
            <p className="text-sm mt-1">{product.description}</p>
            <p className={`mt-2 ${product.is_available ? 'text-green-600' : 'text-red-600'}`}>
              {product.is_available ? 'In Stock' : 'Out of Stock'}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

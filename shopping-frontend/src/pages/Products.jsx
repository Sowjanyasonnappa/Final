import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import sampleProducts from '../data/sampleProducts';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [sort, setSort] = useState('featured');

  useEffect(() => {
    api.get('/products/').then((res) => {
      const productData = Array.isArray(res.data) && res.data.length > 0 ? res.data : sampleProducts;
      setProducts(productData);
    }).catch(() => setProducts(sampleProducts));
  }, []);

  const visibleProducts = [...products]
    .filter((product) => {
      const matchesSearch = [product.name, product.category, product.description].join(' ').toLowerCase().includes(search.toLowerCase());
      const matchesCategory = category === 'All' || product.category === category;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sort === 'price') return a.price - b.price;
      if (sort === 'rating') return b.rating - a.rating;
      return b.discount - a.discount;
    });

  const categories = ['All', ...new Set(products.map((p) => p.category).filter(Boolean))];

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Products</p>
          <h2 className="mt-2 text-3xl font-semibold text-white">Premium catalog</h2>
          <p className="mt-2 max-w-2xl text-slate-400">A polished storefront experience with rich product cards, filters, and premium actions.</p>
        </div>
      </div>

      <div className="panel mb-8 p-4 sm:p-6">
        <div className="grid gap-4 lg:grid-cols-[1.2fr_0.55fr_0.55fr_0.35fr]">
          <label className="input-shell">
            <span>🔎</span>
            <input className="w-full border-0 bg-transparent outline-none" placeholder="Search products" value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <label className="input-shell">
            <span>▦</span>
            <select className="w-full border-0 bg-transparent outline-none" value={category} onChange={(e) => setCategory(e.target.value)}>
              {categories.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
          </label>
          <label className="input-shell">
            <span>↕</span>
            <select className="w-full border-0 bg-transparent outline-none" value={sort} onChange={(e) => setSort(e.target.value)}>
              <option value="featured">Featured</option>
              <option value="price">Price</option>
              <option value="rating">Rating</option>
            </select>
          </label>
          <button
            className="btn-secondary rounded-2xl"
            type="button"
            onClick={() => {
              setSearch('');
              setCategory('All');
              setSort('featured');
            }}
          >
            Reset
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {visibleProducts.map((product) => (
          <div className="card-surface group overflow-hidden" key={product.id}>
            <div className="mb-4 flex items-center justify-between">
              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">
                {product.category || 'Featured'}
              </span>
              {product.discount ? (
                <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-300">-{product.discount}%</span>
              ) : null}
            </div>
            <div className="mb-4 h-44 overflow-hidden rounded-2xl border border-white/10 bg-linear-to-br from-blue-500/20 via-violet-500/20 to-cyan-400/20 p-3">
              <img src={product.image || product.images?.[0]} alt={product.name} className="h-full w-full rounded-2xl object-cover transition duration-500 group-hover:scale-105" />
            </div>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-xl font-semibold text-white">{product.name}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-400">{product.description}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-slate-400">
              <span>⭐ {product.rating}</span>
              <span>•</span>
              <span>Stock {product.stock}</span>
            </div>
            <div className="mt-5 flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Starting at</p>
                <p className="text-2xl font-semibold text-cyan-300">${product.price}</p>
              </div>
              <div className="flex gap-2">
                <Link className="btn-secondary rounded-xl px-3 py-2 text-sm" to={`/products/${product.id}`}>Quick view</Link>
                <Link className="btn-primary rounded-xl px-3 py-2 text-sm" to={`/products/${product.id}`}>Buy now</Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
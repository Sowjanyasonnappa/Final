import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import sampleProducts from '../data/sampleProducts';

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get(`/products/${id}`).then((res) => setProduct(res.data)).catch(() => {
      const fallback = sampleProducts.find((item) => String(item.id) === String(id));
      setProduct(fallback || null);
    });
  }, [id]);

  const handleQuantityChange = (value) => {
    const nextValue = Number(value);
    if (Number.isNaN(nextValue) || nextValue < 1) return setQuantity(1);
    setQuantity(nextValue);
  };

  const handleAddToCart = async () => {
    if (!product) return;
    setSubmitting(true);
    try {
      await api.post('/cart/items', { product_id: product.id, quantity });
      setMessage('Added to cart successfully.');
      navigate('/cart');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to add item to cart.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBuyNow = async () => {
    if (!product) return;
    setSubmitting(true);
    try {
      await api.post('/cart/items', { product_id: product.id, quantity });
      navigate('/cart');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to place your order.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!product) return <div className="mx-auto max-w-7xl px-4 py-16 text-slate-300 sm:px-6 lg:px-8">Loading...</div>;

  const totalAmount = Number(product.price || 0) * quantity;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="card-surface overflow-hidden p-0">
          <div className="h-[360px] bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-cyan-400/20 p-4">
            <img src={product.image || product.images?.[0]} alt={product.name} className="h-full w-full rounded-[24px] object-cover" />
          </div>
          <div className="grid gap-3 p-4 sm:grid-cols-3">
            {(product.images || [product.image]).slice(0, 3).map((image, index) => (
              <div key={index} className="h-24 overflow-hidden rounded-[18px] border border-white/10 bg-white/8">
                <img src={image} alt={`${product.name} ${index + 1}`} className="h-full w-full object-cover" />
              </div>
            ))}
          </div>
        </div>
        <div className="card-surface space-y-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">{product.category || 'Featured'}</p>
            <h2 className="mt-2 text-3xl font-semibold text-white">{product.name}</h2>
            <p className="mt-3 text-base leading-8 text-slate-400">{product.description || 'A premium product experience with polished presentation and seamless shopping flow.'}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
              <p className="text-sm text-slate-400">Unit price</p>
              <p className="text-2xl font-semibold text-cyan-300">${product.price}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
              <p className="text-sm text-slate-400">Stock</p>
              <p className="text-2xl font-semibold text-white">{product.stock}</p>
            </div>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/8 p-4">
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>Selected quantity</span>
              <span className="font-semibold text-white">{quantity}</span>
            </div>
            <div className="mt-3 flex items-center justify-between text-sm text-slate-300">
              <span>Estimated total</span>
              <span className="font-semibold text-cyan-300">${totalAmount}</span>
            </div>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/8 p-4">
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>Rating</span>
              <span className="font-semibold text-white">⭐ {product.rating}</span>
            </div>
            <div className="mt-3 flex items-center justify-between text-sm text-slate-300">
              <span>Reviews</span>
              <span className="font-semibold text-white">24 reviews</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <label className="input-shell w-28">
              <span>QTY</span>
              <input className="w-full border-0 bg-transparent outline-none" value={quantity} onChange={(e) => handleQuantityChange(e.target.value)} />
            </label>
            <button className="btn-primary" onClick={handleAddToCart} disabled={submitting}>{submitting ? 'Working...' : 'Add to cart'}</button>
            <button className="btn-secondary" onClick={handleBuyNow} disabled={submitting}>Buy now</button>
          </div>
          {message ? <p className="text-sm text-amber-300">{message}</p> : null}
        </div>
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_0.9fr]">
        <div className="card-surface">
          <h3 className="text-xl font-semibold text-white">Specifications</h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {(product.specifications || ['Premium quality', 'Fast shipping', 'Secure checkout']).map((spec) => (
              <div key={spec} className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm text-slate-300">{spec}</div>
            ))}
          </div>
        </div>
        <div className="card-surface">
          <h3 className="text-xl font-semibold text-white">Customer reviews</h3>
          <div className="mt-4 space-y-3">
            {['“Excellent quality and finish.”', '“Perfect for daily productivity.”'].map((review) => (
              <div key={review} className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm text-slate-300">{review}</div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-8 card-surface">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Related products</p>
            <h3 className="text-xl font-semibold text-white">You may also like</h3>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {sampleProducts.slice(0, 3).map((item) => (
            <div key={item.id} className="rounded-[22px] border border-white/10 bg-white/8 p-4">
              <div className="mb-3 h-28 overflow-hidden rounded-[18px] border border-white/10 bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-cyan-400/20">
                <img src={item.image} alt={item.name} className="h-full w-full object-cover" />
              </div>
              <p className="font-semibold text-white">{item.name}</p>
              <p className="mt-1 text-sm text-slate-400">{item.category}</p>
              <p className="mt-3 text-lg font-semibold text-cyan-300">${item.price}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
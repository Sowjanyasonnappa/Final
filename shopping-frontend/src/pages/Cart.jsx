import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Cart() {
  const [cart, setCart] = useState({ items: [], total_items: 0, total_price: 0 });
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const loadCart = () => {
    api.get('/cart/').then((res) => setCart(res.data)).catch(() => setCart({ items: [], total_items: 0, total_price: 0 }));
  };

  useEffect(() => { loadCart(); }, []);

  const handleQuantityChange = async (itemId, quantity) => {
    if (!Number.isInteger(quantity) || quantity < 1) return;
    setBusy(true);
    try {
      await api.put(`/cart/items/${itemId}`, { quantity });
      loadCart();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to update quantity.');
    } finally {
      setBusy(false);
    }
  };

  const handleRemove = async (itemId) => {
    setBusy(true);
    try {
      await api.delete(`/cart/items/${itemId}`);
      setMessage('Item removed from cart.');
      loadCart();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to remove item.');
    } finally {
      setBusy(false);
    }
  };

  const handleCheckout = async () => {
    setBusy(true);
    try {
      await api.post('/orders/checkout', { shipping_address: 'Default shipping address', coupon_code: null });
      setMessage('Order placed successfully.');
      loadCart();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to complete checkout.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-fuchsia-300">Shopping cart</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">Your curated selection</h2>
      </div>

      {message ? <p className="mb-4 rounded-2xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">{message}</p> : null}

      {cart.items.length === 0 ? (
        <div className="card-surface p-10 text-center text-slate-300 shadow-[0_0_40px_rgba(168,85,247,0.15)]">Your cart is empty. Start exploring the premium catalog and add your favorite items.</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="card-surface space-y-4 bg-slate-900/80 shadow-[0_0_40px_rgba(34,211,238,0.08)]">
            {cart.items.map((item) => (
              <div key={item.id} className="flex flex-col gap-4 rounded-2xl border border-fuchsia-500/15 bg-slate-950/70 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-16 w-16 rounded-2xl bg-linear-to-br from-cyan-500/30 via-violet-500/30 to-fuchsia-500/30 shadow-lg shadow-fuchsia-500/10" />
                  <div>
                    <p className="font-semibold text-white">{item.product_name}</p>
                    <p className="text-sm text-slate-400">Unit price: ${item.price}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <label className="input-shell w-24 border-cyan-500/20 bg-slate-900/80 text-slate-200">
                    <span>Qty</span>
                    <input className="w-full border-0 bg-transparent text-white outline-none" value={item.quantity} onChange={(e) => handleQuantityChange(item.id, Number(e.target.value))} />
                  </label>
                  <div className="text-lg font-semibold text-cyan-300">${item.price * item.quantity}</div>
                  <button className="btn-secondary rounded-xl px-3 py-2 text-sm" onClick={() => handleRemove(item.id)} disabled={busy}>Remove</button>
                </div>
              </div>
            ))}
          </div>
          <div className="card-surface space-y-4 bg-linear-to-br from-slate-900 via-slate-900 to-violet-950/80 shadow-[0_0_40px_rgba(168,85,247,0.12)]">
            <h3 className="text-xl font-semibold text-white">Order summary</h3>
            <div className="flex items-center justify-between text-slate-300"><span>Items</span><span>{cart.total_items}</span></div>
            <div className="flex items-center justify-between text-slate-300"><span>Subtotal</span><span>${cart.total_price}</span></div>
            <div className="flex items-center justify-between border-t border-fuchsia-500/20 pt-3 text-lg font-semibold text-white"><span>Total</span><span className="text-cyan-300">${Number(cart.total_price).toFixed(2)}</span></div>
            <button className="btn-primary w-full" onClick={handleCheckout} disabled={busy}>{busy ? 'Processing...' : 'Proceed to checkout'}</button>
            <button className="btn-secondary w-full" onClick={() => loadCart()}>Refresh cart</button>
          </div>
        </div>
      )}
    </div>
  );
}
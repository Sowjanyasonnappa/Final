import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Orders() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    api.get('/orders/').then((res) => setOrders(res.data)).catch(() => setOrders([]));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Orders</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">Recent activity</h2>
      </div>
      {orders.length === 0 ? (
        <div className="card-surface p-10 text-center text-slate-300">No orders yet. Your latest purchases will appear here.</div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div className="card-surface flex flex-col gap-4 rounded-3xl sm:flex-row sm:items-center sm:justify-between" key={order.id}>
              <div>
                <p className="text-lg font-semibold text-white">Order #{order.id}</p>
                <p className="mt-1 text-sm text-slate-400">Status: {order.status}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-400">Total</p>
                <p className="text-xl font-semibold text-cyan-300">${order.total_amount}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
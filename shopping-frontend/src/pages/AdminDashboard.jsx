import { useEffect, useState } from 'react';
import api from '../services/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get('/admin/dashboard').then((res) => setStats(res.data)).catch(() => setStats(null));
  }, []);

  if (!stats) return <div className="mx-auto max-w-7xl px-4 py-16 text-slate-300 sm:px-6 lg:px-8">Loading...</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Admin dashboard</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">Operational command center</h2>
      </div>
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {[
          { label: 'Total users', value: stats.total_users },
          { label: 'Total products', value: stats.total_products },
          { label: 'Total orders', value: stats.total_orders },
          { label: 'Revenue', value: `$${stats.revenue}` }
        ].map((item) => (
          <div className="card-surface" key={item.label}>
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
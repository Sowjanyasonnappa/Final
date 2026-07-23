import { Link } from 'react-router-dom';
import sampleProducts from '../data/sampleProducts';

const stats = [
  { label: 'Total products', value: '128', tone: 'from-cyan-500/20 to-blue-500/20' },
  { label: 'Orders', value: '1.2k', tone: 'from-violet-500/20 to-fuchsia-500/20' },
  { label: 'Revenue', value: '$84k', tone: 'from-emerald-500/20 to-teal-500/20' },
  { label: 'Inventory', value: '97.4%', tone: 'from-amber-500/20 to-orange-500/20' }
];

const quickActions = [
  { label: 'Create product', to: '/products' },
  { label: 'View orders', to: '/orders' },
  { label: 'Open cart', to: '/cart' },
  { label: 'Edit profile', to: '/profile' }
];

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="glow-orb absolute left-[-8%] top-24 h-60 w-60 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="glow-orb-2 absolute right-[-4%] top-36 h-72 w-72 rounded-full bg-violet-500/20 blur-3xl" />
        <div className="glow-orb-3 absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <section className="panel relative overflow-hidden px-6 py-8 sm:px-8 lg:px-10 lg:py-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(6,182,212,0.14),transparent_35%)]" />
          <div className="relative grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm font-medium text-cyan-200">
                <span className="h-2.5 w-2.5 rounded-full bg-cyan-300" />
                Premium commerce intelligence
              </div>
              <div>
                <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Welcome back, your storefront is thriving.</h1>
                <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-300">A refined operating view for products, orders, growth metrics, and customer engagement in one immersive workspace.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link className="btn-primary" to="/products">Browse catalog</Link>
                <Link className="btn-secondary" to="/orders">View orders</Link>
              </div>
            </div>
            <div className="card-surface p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-300">Live performance</p>
                <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-medium text-emerald-300">+18% this month</span>
              </div>
              <div className="mt-4 grid gap-3">
                {['Orders synced', 'Revenue uplift', 'Inventory healthy'].map((item) => (
                  <div key={item} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/8 px-3 py-3 text-sm text-slate-300">
                    <span>{item}</span>
                    <span className="font-semibold text-white">Ready</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className={`card-surface bg-gradient-to-br ${stat.tone}`}>
              <p className="text-sm text-slate-300">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold text-white">{stat.value}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="card-surface">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Latest orders</p>
                <h3 className="text-xl font-semibold text-white">Recent activity</h3>
              </div>
              <Link to="/orders" className="text-sm font-medium text-cyan-300">View all</Link>
            </div>
            <div className="space-y-3">
              {['#1042 • Premium headset', '#1041 • Smart display', '#1040 • Travel backpack'].map((item) => (
                <div key={item} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm text-slate-300">
                  <span>{item}</span>
                  <span className="font-semibold text-white">Completed</span>
                </div>
              ))}
            </div>
          </div>
          <div className="card-surface">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Quick actions</p>
                <h3 className="text-xl font-semibold text-white">Take action fast</h3>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {quickActions.map((action) => (
                <Link key={action.label} to={action.to} className="rounded-2xl border border-white/10 bg-white/8 px-4 py-4 text-sm font-semibold text-slate-200 transition hover:bg-white/12 hover:text-white">
                  {action.label}
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="card-surface">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Recent products</p>
                <h3 className="text-xl font-semibold text-white">Trending items</h3>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {sampleProducts.slice(0, 4).map((product) => (
                <div key={product.id} className="rounded-[22px] border border-white/10 bg-white/8 p-4">
                  <div className="mb-3 h-28 rounded-[18px] bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-cyan-400/20" />
                  <p className="font-semibold text-white">{product.name}</p>
                  <p className="mt-1 text-sm text-slate-400">{product.category}</p>
                  <p className="mt-3 text-lg font-semibold text-cyan-300">${product.price}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="card-surface">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Inventory status</p>
                <h3 className="text-xl font-semibold text-white">Health overview</h3>
              </div>
            </div>
            <div className="space-y-3">
              {['High demand items', 'Restock recommended', 'Low inventory alerts'].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm text-slate-300">{item}</div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
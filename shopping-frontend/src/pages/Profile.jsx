import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <div className="card-surface overflow-hidden p-0">
        <div className="h-36 bg-linear-to-r from-blue-500/30 via-violet-500/25 to-cyan-400/20" />
        <div className="px-6 pb-6 sm:px-8">
          <div className="-mt-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex items-end gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-3xl border border-white/10 bg-slate-950 text-3xl font-semibold text-white shadow-xl">{(user?.email || 'U').slice(0, 1).toUpperCase()}</div>
              <div>
                <h2 className="text-2xl font-semibold text-white">{user?.email || 'User profile'}</h2>
                <p className="text-sm text-slate-400">{user?.role || 'USER'} account</p>
              </div>
            </div>
            <button className="btn-secondary">Edit profile</button>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              { label: 'Email', value: user?.email || 'N/A' },
              { label: 'Role', value: user?.role || 'USER' },
              { label: 'Status', value: 'Active' }
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/10 bg-white/8 p-4">
                <p className="text-sm text-slate-400">{item.label}</p>
                <p className="mt-2 font-semibold text-white">{item.value}</p>
              </div>
            ))}
          </div>
          <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="card-surface">
              <h3 className="text-xl font-semibold text-white">Recent orders</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">#1042 • Premium headset • Completed</div>
                <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">#1041 • Smart display • In transit</div>
              </div>
            </div>
            <div className="card-surface">
              <h3 className="text-xl font-semibold text-white">Activity</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">Updated profile preferences</div>
                <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">Added new shipping address</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
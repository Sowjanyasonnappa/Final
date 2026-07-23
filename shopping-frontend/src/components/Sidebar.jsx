import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const baseItems = [
  { to: '/', label: 'Dashboard', icon: '◈' },
  { to: '/products', label: 'Products', icon: '◫' },
  { to: '/cart', label: 'Cart', icon: '🛒' },
  { to: '/orders', label: 'Orders', icon: '▣' },
  { to: '/ops', label: 'Ops', icon: '⚡' },
  { to: '/profile', label: 'Profile', icon: '◎' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
  { to: '/support', label: 'Support', icon: '✦' }
];

const roleMap = {
  ADMIN: ['Dashboard', 'Products', 'Cart', 'Orders', 'Ops', 'Analytics', 'Profile', 'Settings', 'Support', 'Logout'],
  MANAGER: ['Dashboard', 'Products', 'Orders', 'Profile', 'Settings', 'Support'],
  USER: ['Dashboard', 'Products', 'Cart', 'Orders', 'Profile', 'Support']
};

export default function Sidebar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const role = user?.role || 'USER';
  const allowed = roleMap[role] || roleMap.USER;
  const items = baseItems.filter((item) => allowed.includes(item.label) || item.label === 'Dashboard' || item.label === 'Products');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 z-50 hidden h-screen w-[260px] flex-col border-r border-white/10 bg-slate-950/90 px-4 py-5 backdrop-blur-2xl lg:flex">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-400 text-lg font-semibold shadow-lg shadow-cyan-500/30">
          S
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">StreamSentinel</p>
          <p className="text-sm font-semibold text-white">Commerce Suite</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `group flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition ${isActive ? 'border-cyan-400/40 bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-violet-500/20 text-white shadow-lg shadow-cyan-500/10' : 'border-transparent bg-white/5 text-slate-300 hover:border-white/10 hover:bg-white/10 hover:text-white'}`}
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/10 text-base transition group-hover:scale-110">
              {item.icon}
            </span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-5 rounded-[24px] border border-white/10 bg-white/10 p-4">
        <p className="text-sm font-semibold text-white">Signed in as</p>
        <p className="mt-1 text-sm text-slate-400">{user?.email || 'Guest'}</p>
        <p className="mt-3 inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2.5 py-1 text-xs font-medium text-cyan-200">
          {role}
        </p>
      </div>

      <button onClick={handleLogout} className="mt-4 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/10 hover:text-white">
        <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-rose-500/15 text-base">⇢</span>
        Logout
      </button>
    </aside>
  );
}

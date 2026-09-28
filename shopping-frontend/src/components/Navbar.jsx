import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user } = useAuth();

  return (
    <nav className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-linear-to-br from-blue-500 via-violet-500 to-cyan-400 font-semibold shadow-lg shadow-cyan-500/20">
            S
          </div>
          <div className="hidden sm:block">
            <p className="text-base font-semibold text-white">StreamSentinel</p>
            <p className="text-xs text-slate-400">Enterprise experience</p>
          </div>
        </Link>

        <div className="hidden flex-1 px-4 md:flex">
          <div className="input-shell mx-auto w-full max-w-xl">
            <span>🔎</span>
            <input className="w-full border-0 bg-transparent outline-none" placeholder="Search anything" />
          </div>
        </div>

        {user ? (
          <div className="flex items-center gap-3">
            <button className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-sm transition hover:bg-white/20">🔔</button>
            <Link to="/settings" className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-sm transition hover:bg-white/20">⚙</Link>
            <Link to="/profile" className="flex h-10 w-10 items-center justify-center rounded-full border border-cyan-400/20 bg-linear-to-br from-cyan-500/20 to-violet-500/20 text-sm font-semibold text-white">
              {user.email?.slice(0, 1).toUpperCase() || 'U'}
            </Link>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link to="/login" className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/15">
              Login
            </Link>
            <Link to="/register" className="btn-primary rounded-full px-4 py-2 text-sm">
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
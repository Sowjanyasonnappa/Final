import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/products');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="glow-orb absolute left-[-8%] top-20 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="glow-orb-2 absolute right-[-6%] top-24 h-72 w-72 rounded-full bg-violet-500/20 blur-3xl" />
      </div>

      <div className="mx-auto grid min-h-[calc(100vh-8rem)] max-w-7xl items-center gap-8 px-4 py-16 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm font-medium text-cyan-200">
            Secure access • premium workspace
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Welcome back to StreamSentinel.</h1>
          <p className="max-w-xl text-lg leading-8 text-slate-300">Sign in to manage products, orders, and AI-assisted commerce operations in one elegant control center.</p>
          <div className="rounded-[28px] border border-white/10 bg-slate-900/50 p-6 backdrop-blur-xl">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-sm text-slate-400">Live data</p>
                <p className="text-xl font-semibold text-white">24/7</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-sm text-slate-400">Secure auth</p>
                <p className="text-xl font-semibold text-white">JWT protected</p>
              </div>
            </div>
          </div>
        </div>

        <div className="panel p-6 sm:p-8">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-blue-500 via-violet-500 to-cyan-400 font-semibold shadow-lg shadow-cyan-500/20">S</div>
            <div>
              <p className="text-xl font-semibold text-white">Sign in</p>
              <p className="text-sm text-slate-400">Access your commerce workspace</p>
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-300">Email</span>
              <div className="input-shell">
                <span>✉</span>
                <input className="w-full border-0 bg-transparent outline-none" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </div>
            </label>
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-300">Password</span>
              <div className="input-shell">
                <span>🔒</span>
                <input className="w-full border-0 bg-transparent outline-none" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" />
              </div>
            </label>
            <div className="flex items-center justify-between text-sm text-slate-400">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-white/10 bg-transparent" />
                Remember me
              </label>
              <Link to="/register" className="text-cyan-300 hover:text-cyan-200">Create account</Link>
            </div>
            <button className="btn-primary w-full" type="submit">Login</button>
          </form>
          {message && <p className="mt-4 text-sm text-amber-300">{message}</p>}
        </div>
      </div>
    </div>
  );
}
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(email, password);
      setMessage('Registered successfully. Please login.');
      navigate('/login');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="glow-orb absolute left-[-8%] top-24 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="glow-orb-2 absolute right-[-4%] top-16 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
      </div>

      <div className="mx-auto grid min-h-[calc(100vh-8rem)] max-w-7xl items-center gap-8 px-4 py-16 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-sm font-medium text-violet-200">
            Launch faster • grow smarter
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Create a premium storefront in minutes.</h1>
          <p className="max-w-xl text-lg leading-8 text-slate-300">Join StreamSentinel to manage inventory, cart flows, orders, and insights from a polished enterprise-grade experience.</p>
          <div className="panel p-6">
            <div className="space-y-3 text-sm text-slate-300">
              <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/8 px-3 py-3">✓ Beautiful product discovery</div>
              <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/8 px-3 py-3">✓ Secure authentication and profile management</div>
              <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/8 px-3 py-3">✓ AI-ready dashboard experience</div>
            </div>
          </div>
        </div>

        <div className="panel p-6 sm:p-8">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-400 font-semibold shadow-lg shadow-cyan-500/20">S</div>
            <div>
              <p className="text-xl font-semibold text-white">Create account</p>
              <p className="text-sm text-slate-400">Start your premium commerce journey</p>
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
                <input className="w-full border-0 bg-transparent outline-none" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Choose a strong password" />
              </div>
            </label>
            <button className="btn-primary w-full" type="submit">Register</button>
          </form>
          <p className="mt-4 text-sm text-slate-400">Already have an account? <Link to="/login" className="font-medium text-cyan-300">Sign in</Link></p>
          {message && <p className="mt-4 text-sm text-emerald-300">{message}</p>}
        </div>
      </div>
    </div>
  );
}
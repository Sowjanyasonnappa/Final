import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-7xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <div className="card-surface max-w-xl text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">404</p>
        <h2 className="mt-3 text-4xl font-semibold text-white">Page not found</h2>
        <p className="mt-3 text-slate-400">The route you requested is unavailable, but the premium experience continues on the home page.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link className="btn-primary" to="/">Return home</Link>
          <Link className="btn-secondary" to="/products">Browse products</Link>
        </div>
      </div>
    </div>
  );
}
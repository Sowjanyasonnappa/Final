import { Link } from 'react-router-dom';

export default function AccessDenied() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-5xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <div className="card-surface max-w-xl text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-rose-300">Access denied</p>
        <h2 className="mt-3 text-4xl font-semibold text-white">You do not have permission to view this area.</h2>
        <p className="mt-3 text-slate-400">Your role does not allow access to this page. Please contact an administrator if you believe this is a mistake.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link className="btn-primary" to="/products">Go to products</Link>
          <Link className="btn-secondary" to="/profile">View profile</Link>
        </div>
      </div>
    </div>
  );
}

export default function Support() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Support</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">We’re here to help</h2>
      </div>
      <div className="card-surface p-8">
        <p className="text-lg text-slate-300">Need help with orders, billing, or product access? Our support team can assist with anything from onboarding to troubleshooting.</p>
        <div className="mt-6 grid gap-4 rounded-3xl border border-white/10 bg-white/8 p-6 sm:grid-cols-3">
          <div>
            <p className="text-sm text-slate-400">Team</p>
            <p className="mt-1 font-semibold text-white">Commerce Success Desk</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Email</p>
            <a className="mt-1 block font-semibold text-cyan-300" href="mailto:support@streamsentinel.dev">support@streamsentinel.dev</a>
          </div>
          <div>
            <p className="text-sm text-slate-400">Phone</p>
            <p className="mt-1 font-semibold text-white">+1 (800) 555-0148</p>
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <a className="btn-primary" href="mailto:support@streamsentinel.dev">Contact support</a>
          <a className="btn-secondary" href="https://github.com" target="_blank" rel="noreferrer">Visit docs</a>
        </div>
      </div>
    </div>
  );
}

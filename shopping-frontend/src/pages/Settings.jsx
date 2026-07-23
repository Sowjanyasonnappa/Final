export default function Settings() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Settings</p>
        <h2 className="mt-2 text-3xl font-semibold text-white">Personalize your workspace</h2>
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="card-surface space-y-4">
          <h3 className="text-xl font-semibold text-white">Appearance</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {['Dark UI', 'Compact mode', 'Reduced motion'].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3 text-sm text-slate-300">{item}</div>
            ))}
          </div>
        </div>
        <div className="card-surface space-y-4">
          <h3 className="text-xl font-semibold text-white">Security</h3>
          <div className="space-y-3 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">Password reset</div>
            <div className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3">Two-factor authentication</div>
            <div className="rounded-2xl border border-white/10 bg-white/10 px-4 py-3">Session activity</div>
          </div>
        </div>
      </div>
    </div>
  );
}

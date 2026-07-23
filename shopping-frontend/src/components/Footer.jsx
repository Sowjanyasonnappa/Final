export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1.1fr_0.9fr_0.8fr] lg:px-8">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-400 text-lg font-semibold shadow-lg shadow-cyan-500/20">
              S
            </div>
            <div>
              <p className="text-lg font-semibold text-white">StreamSentinel</p>
              <p className="text-sm text-slate-400">Premium commerce intelligence</p>
            </div>
          </div>
          <p className="mt-4 max-w-md text-sm leading-7 text-slate-400">A polished enterprise experience built to deliver modern storefronts, operational clarity, and premium customer journeys.</p>
        </div>

        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Developed by</p>
          <div className="mt-3 space-y-1 text-sm text-slate-400">
            <p>Your Name</p>
            <p>your.email@example.com</p>
            <p>+1 (555) 123-4567</p>
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Version</p>
          <div className="mt-3 space-y-1 text-sm text-slate-400">
            <p>v1.0.0</p>
            <p>© 2026 StreamSentinel</p>
            <a href="https://github.com" className="inline-flex text-cyan-300 transition hover:text-cyan-200" target="_blank" rel="noreferrer">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

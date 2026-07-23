import { useEffect, useState } from 'react';
import api from '../services/api';

export default function OpsDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [clusters, setClusters] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [sales, setSales] = useState(null);

  const loadDashboard = async () => {
    setLoading(true);
    setError('');

    const requests = [
      api.get('/api/kubernetes/clusters'),
      api.get('/api/alerts?limit=6'),
      api.get('/api/alerts/incidents?limit=6'),
      api.get('/api/ai/knowledge-base?limit=4'),
      api.get('/api/dashboard/sales'),
    ];

    const results = await Promise.allSettled(requests);
    const failures = [];

    const nextClusters = results[0].status === 'fulfilled' ? (results[0].value?.data || []) : [];
    const nextAlerts = results[1].status === 'fulfilled' ? (results[1].value?.data || []) : [];
    const nextIncidents = results[2].status === 'fulfilled' ? (results[2].value?.data || []) : [];
    const nextKnowledgeBase = results[3].status === 'fulfilled' ? (results[3].value?.data || []) : [];
    const nextSales = results[4].status === 'fulfilled' ? (results[4].value?.data || null) : null;

    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        const endpoint = ['clusters', 'alerts', 'incidents', 'knowledge base', 'sales'][index];
        failures.push(endpoint);
      }
    });

    setClusters(nextClusters);
    setAlerts(nextAlerts);
    setIncidents(nextIncidents);
    setKnowledgeBase(nextKnowledgeBase);
    setSales(nextSales);

    if (failures.length > 0) {
      setError(`Some dashboard data could not be loaded. Showing the data that was available for ${failures.join(', ')}.`);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const summaryCards = [
    { label: 'Clusters', value: clusters.length, accent: 'from-cyan-500 to-sky-500' },
    { label: 'Active Alerts', value: alerts.filter((item) => item.status === 'FIRING').length, accent: 'from-rose-500 to-orange-500' },
    { label: 'Open Incidents', value: incidents.filter((item) => item.status !== 'RESOLVED').length, accent: 'from-violet-500 to-fuchsia-500' },
    { label: 'Sales Today', value: sales ? `$${Number(sales.total_revenue_today || 0).toFixed(2)}` : '$0.00', accent: 'from-emerald-500 to-lime-500' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 p-6 text-slate-100 lg:p-8">
        <div className="mx-auto max-w-7xl space-y-6">
          <div className="rounded-3xl border border-white/10 bg-white/10 p-6 shadow-2xl shadow-cyan-500/10 backdrop-blur">
            <div className="h-4 w-32 animate-pulse rounded-full bg-cyan-400/30" />
            <div className="mt-4 h-8 w-3/4 animate-pulse rounded-full bg-slate-700" />
            <div className="mt-3 h-4 w-1/2 animate-pulse rounded-full bg-slate-700" />
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-28 animate-pulse rounded-3xl border border-white/10 bg-slate-900/80" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100 lg:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="rounded-3xl border border-white/10 bg-white/10 p-6 shadow-2xl shadow-cyan-500/10 backdrop-blur">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">AI Ops Command Center</p>
              <h1 className="mt-2 text-3xl font-semibold text-white">Operations, incidents, and commerce intelligence in one view</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-300">Monitor cluster health, review incidents, and track sales momentum without leaving the admin experience.</p>
            </div>
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
              {loading ? 'Loading live data...' : 'Live telemetry connected'}
            </div>
          </div>
        </div>

        {error ? (
          <div className="rounded-2xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-100">{error}</div>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {summaryCards.map((card) => (
            <div key={card.label} className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 shadow-lg shadow-slate-950/30">
              <div className={`h-2 w-20 rounded-full bg-linear-to-r ${card.accent}`} />
              <p className="mt-4 text-sm text-slate-400">{card.label}</p>
              <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Cluster health</h2>
              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-200">{clusters.length} registered</span>
            </div>
            <div className="mt-4 space-y-3">
              {clusters.length === 0 ? (
                <p className="text-sm text-slate-400">No clusters registered yet. Register one from the Kubernetes API to seed telemetry.</p>
              ) : (
                clusters.map((cluster) => (
                  <div key={cluster.id} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-white">{cluster.name}</p>
                        <p className="text-sm text-slate-400">{cluster.context}</p>
                      </div>
                      <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">{cluster.status}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Latest alerts</h2>
              <span className="text-sm text-slate-400">AI-driven signals</span>
            </div>
            <div className="mt-4 space-y-3">
              {alerts.length === 0 ? (
                <p className="text-sm text-slate-400">No alerts generated yet.</p>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-medium text-white">{alert.title}</p>
                        <p className="text-sm text-slate-400">{alert.description}</p>
                      </div>
                      <span className={`rounded-full px-3 py-1 text-xs font-medium ${alert.status === 'FIRING' ? 'bg-rose-500/10 text-rose-200' : 'bg-emerald-500/10 text-emerald-200'}`}>{alert.status}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Open incidents</h2>
              <span className="text-sm text-slate-400">RCA-ready</span>
            </div>
            <div className="mt-4 space-y-3">
              {incidents.length === 0 ? (
                <p className="text-sm text-slate-400">No incidents have been created yet.</p>
              ) : (
                incidents.map((incident) => (
                  <div key={incident.id} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-white">{incident.title}</p>
                        <p className="mt-1 text-sm text-slate-400">{incident.description}</p>
                      </div>
                      <span className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-medium text-violet-200">{incident.priority}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Knowledge base</h2>
              <span className="text-sm text-slate-400">Fast resolution articles</span>
            </div>
            <div className="mt-4 space-y-3">
              {knowledgeBase.length === 0 ? (
                <p className="text-sm text-slate-400">No knowledge base articles are available yet.</p>
              ) : (
                knowledgeBase.map((item) => (
                  <div key={item.id} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
                    <p className="font-medium text-white">{item.title}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.content}</p>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

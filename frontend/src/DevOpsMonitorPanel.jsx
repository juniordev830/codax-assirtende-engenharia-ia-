import { useEffect, useState } from 'react';

/** Read-only public GitHub Actions monitoring panel. Status is unknown until verified. */
export default function DevOpsMonitorPanel({ apiBase = '', repositories = [] }) {
  const [statuses, setStatuses] = useState({});
  useEffect(() => {
    let active = true;
    const names = repositories.map(repo => typeof repo === 'string' ? repo : repo.name).filter(Boolean);
    setStatuses(Object.fromEntries(names.map(name => [name, { state: 'loading' }])));
    // Limit parallel requests to avoid triggering the backend rate limiter.
    async function load() {
      for (const name of names) {
        if (!active) return;
        try {
          const response = await fetch(`${apiBase}/api/github/repos/${encodeURIComponent(name)}/actions`, { credentials: 'include' });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          const latest = data.runs?.[0];
          const state = !latest ? 'unknown' : latest.status === 'success' ? 'success' :
            latest.status === 'failure' ? 'failure' : latest.status === 'running' ? 'running' : 'unknown';
          if (active) setStatuses(previous => ({ ...previous, [name]: { state, latest } }));
        } catch {
          if (active) setStatuses(previous => ({ ...previous, [name]: { state: 'unknown' } }));
        }
      }
    }
    load();
    return () => { active = false; };
  }, [apiBase, repositories]);

  const labels = { loading: 'Consultando', success: 'Última execução aprovada', failure: 'Última execução falhou', running: 'Em execução', unknown: 'Sem dados confirmados' };
  const colors = { loading: '#64748b', success: '#16a34a', failure: '#dc2626', running: '#eab308', unknown: '#64748b' };
  return <section aria-label="Monitoramento de pipelines">
    <h2>Central de pipelines</h2>
    <p>Dados públicos do GitHub Actions. A cor representa apenas a última execução, não a saúde geral do projeto.</p>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 12 }}>
      {repositories.map(repo => {
        const name = typeof repo === 'string' ? repo : repo.name;
        const state = statuses[name]?.state || 'loading';
        return <article key={name} style={{ border: `2px solid ${colors[state]}`, borderRadius: 12, padding: 16 }}>
          <strong>{name}</strong>
          <p role="status">{labels[state]}</p>
        </article>;
      })}
    </div>
  </section>;
}

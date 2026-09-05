import { useCallback, useEffect, useMemo, useState } from 'react';
import { api, ApiError } from '../api.ts';
import type { Lead, Stats } from '../api.ts';
import { NEED_LABELS, BUDGET_LABELS, TIMELINE_LABELS, formatDate } from '../labels.ts';

const STATUSES = ['new', 'contacted', 'qualified', 'dead'] as const;
type SortKey = 'score' | 'created_at' | 'name' | 'company' | 'status';

const COLUMNS: { key: SortKey; label: string; cls?: string }[] = [
  { key: 'score', label: 'Score' },
  { key: 'name', label: 'Lead' },
  { key: 'company', label: 'Company', cls: 'col-company' },
  { key: 'status', label: 'Status' },
  { key: 'created_at', label: 'Received', cls: 'col-when' },
];

export default function Dashboard({ onSignedOut }: { onSignedOut: () => void }) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<Stats>({});
  const [status, setStatus] = useState('');
  const [band, setBand] = useState('');
  const [q, setQ] = useState('');
  const [debouncedQ, setDebouncedQ] = useState('');
  const [sort, setSort] = useState<SortKey>('score');
  const [dir, setDir] = useState<'asc' | 'desc'>('desc');
  const [selected, setSelected] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q), 250);
    return () => clearTimeout(t);
  }, [q]);

  const query = useMemo(() => {
    const p = new URLSearchParams({ sort, dir });
    if (status) p.set('status', status);
    if (band) p.set('band', band);
    if (debouncedQ.trim()) p.set('q', debouncedQ.trim());
    return `?${p.toString()}`;
  }, [status, band, debouncedQ, sort, dir]);

  const load = useCallback(async () => {
    try {
      const data = await api.leads(query);
      setLeads(data.leads);
      setStats(data.stats);
      setError('');
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return onSignedOut();
      setError(err instanceof Error ? err.message : 'Could not load leads');
    } finally {
      setLoading(false);
    }
  }, [query, onSignedOut]);

  useEffect(() => { void load(); }, [load]);

  const toggleSort = (key: SortKey) => {
    if (key === sort) return setDir((d) => (d === 'desc' ? 'asc' : 'desc'));
    setSort(key);
    setDir(key === 'name' || key === 'company' ? 'asc' : 'desc');
  };

  async function patchLead(id: number, body: { status?: string; notes?: string }) {
    try {
      const { lead } = await api.updateLead(id, body);
      setSelected((s) => (s && s.id === id ? lead : s));
      setLeads((rows) => rows.map((r) => (r.id === id ? lead : r)));
      void load();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return onSignedOut();
      setError(err instanceof Error ? err.message : 'Could not save');
    }
  }

  async function removeLead(id: number) {
    if (!window.confirm('Delete this lead permanently?')) return;
    try {
      await api.deleteLead(id);
      setSelected(null);
      void load();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return onSignedOut();
      setError(err instanceof Error ? err.message : 'Could not delete');
    }
  }

  /** Export what is on screen, filters and sort included, not the whole table. */
  function exportCsv() {
    const head = ['id', 'received', 'name', 'email', 'company', 'budget', 'timeline', 'needs', 'score', 'band', 'status', 'notes', 'message'];
    const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const rows = leads.map((l) => [
      l.id, l.created_at, l.name, l.email, l.company,
      BUDGET_LABELS[l.budget] ?? l.budget, TIMELINE_LABELS[l.timeline] ?? l.timeline,
      l.needs.map((n) => NEED_LABELS[n] ?? n).join('; '),
      l.score, l.band, l.status, l.notes, l.message,
    ].map(esc).join(','));
    const blob = new Blob([[head.join(','), ...rows].join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leads-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const filterChip = (key: string, label: string, value: string, current: string, set: (v: string) => void) => (
    <button
      key={key}
      className={current === value ? 'stat on' : 'stat'}
      onClick={() => set(current === value ? '' : value)}
      aria-pressed={current === value}
    >
      <span className="stat-n">{stats[value] ?? 0}</span>
      <span className="stat-k">{label}</span>
    </button>
  );

  return (
    <>
      <div className="page-head">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h1>Triage</h1>
        </div>
        <div className="spacer" />
        <button className="btn" onClick={exportCsv} disabled={!leads.length}>Export CSV</button>
      </div>

      {error && <div className="banner" role="alert">{error}</div>}

      <div className="stats">
        <button className={!status && !band ? 'stat on' : 'stat'} onClick={() => { setStatus(''); setBand(''); }}>
          <span className="stat-n">{stats.total ?? 0}</span>
          <span className="stat-k">All</span>
        </button>
        {filterChip('b-hot', 'Hot', 'hot', band, setBand)}
        {filterChip('b-warm', 'Warm', 'warm', band, setBand)}
        {filterChip('s-new', 'New', 'new', status, setStatus)}
        {filterChip('s-contacted', 'Contacted', 'contacted', status, setStatus)}
        {filterChip('s-qualified', 'Qualified', 'qualified', status, setStatus)}
        {filterChip('s-dead', 'Dead', 'dead', status, setStatus)}
      </div>

      <div className="toolbar">
        <div className="search">
          <input
            type="text" value={q} onChange={(e) => setQ(e.target.value)}
            placeholder="Search name, email, company or description"
            aria-label="Search leads"
          />
        </div>
        <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)} aria-label="Sort by">
          {COLUMNS.map((c) => <option key={c.key} value={c.key}>Sort by {c.label.toLowerCase()}</option>)}
        </select>
        <button className="btn btn-sm" onClick={() => setDir((d) => (d === 'desc' ? 'asc' : 'desc'))}>
          {dir === 'desc' ? 'Descending' : 'Ascending'}
        </button>
        <span className="small muted">{leads.length} shown</span>
      </div>

      <div className="ledger-wrap">
        {loading ? (
          <div className="empty"><span className="spinner" /> Loading</div>
        ) : leads.length === 0 ? (
          <div className="empty">
            <h3>Nothing here</h3>
            <p className="small">
              {status || band || debouncedQ ? 'No lead matches these filters.' : 'No enquiries yet. Share the public form to start collecting them.'}
            </p>
          </div>
        ) : (
          <table className="ledger">
            <thead>
              <tr>
                {COLUMNS.map((c) => (
                  <th
                    key={c.key}
                    className={`sortable ${c.cls ?? ''}`}
                    onClick={() => toggleSort(c.key)}
                    aria-sort={sort === c.key ? (dir === 'asc' ? 'ascending' : 'descending') : 'none'}
                  >
                    {c.label}
                    {sort === c.key && <span className="caret">{dir === 'desc' ? '▼' : '▲'}</span>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {leads.map((l) => (
                <tr
                  key={l.id}
                  className={selected?.id === l.id ? 'on' : ''}
                  onClick={() => setSelected(l)}
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter') setSelected(l); }}
                >
                  <td className={`band-${l.band}`}>
                    <div className="score-cell">
                      <span className="score-value num">{l.score}</span>
                      <span className="gauge"><i style={{ width: `${l.score}%` }} /></span>
                    </div>
                  </td>
                  <td>
                    <div className="who">{l.name}</div>
                    <div className="where">{l.email}</div>
                  </td>
                  <td className="col-company">
                    {l.company || <span className="muted">&mdash;</span>}
                    <div className="where">{l.needs.map((n) => NEED_LABELS[n] ?? n).join(', ')}</div>
                  </td>
                  <td>
                    <span className={`status-pill status-${l.status}`}>{l.status}</span>{' '}
                    <span className={`tag tag-${l.band}`}>{l.band}</span>
                  </td>
                  <td className="col-when small muted">{formatDate(l.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selected && (
        <Drawer
          lead={selected}
          onClose={() => setSelected(null)}
          onPatch={patchLead}
          onDelete={removeLead}
        />
      )}
    </>
  );
}

function Drawer({
  lead, onClose, onPatch, onDelete,
}: {
  lead: Lead;
  onClose: () => void;
  onPatch: (id: number, body: { status?: string; notes?: string }) => void;
  onDelete: (id: number) => void;
}) {
  const [notes, setNotes] = useState(lead.notes);
  const [savedAt, setSavedAt] = useState('');

  useEffect(() => { setNotes(lead.notes); }, [lead.id, lead.notes]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const matched = lead.score_breakdown.filter((b) => b.matched);
  const missed = lead.score_breakdown.filter((b) => !b.matched);

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-label={`Lead: ${lead.name}`}>
        <div className="drawer-head">
          <p className="eyebrow">Lead #{lead.id}</p>
          <h2>{lead.name}</h2>
          <p className="small muted" style={{ margin: 0 }}>
            {lead.company ? `${lead.company} · ` : ''}
            <a href={`mailto:${lead.email}`}>{lead.email}</a>
          </p>
          <button className="btn btn-ghost btn-sm drawer-close" onClick={onClose} aria-label="Close">&#10005;</button>
        </div>

        <div className="drawer-body">
          <div className={`block band-${lead.band}`}>
            <div className="score-hero">
              <span className="n score-value num">{lead.score}</span>
              <span className="of">/ 100</span>
              <span className={`tag tag-${lead.band}`} style={{ marginLeft: 'auto' }}>{lead.band}</span>
            </div>
            <span className="gauge" style={{ display: 'block', marginTop: 8 }}>
              <i style={{ width: `${lead.score}%` }} />
            </span>
          </div>

          <div className="block">
            <span className="eyebrow">Status</span>
            <div className="seg">
              {STATUSES.map((s) => (
                <button
                  key={s}
                  className={lead.status === s ? 'on' : ''}
                  onClick={() => onPatch(lead.id, { status: s })}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="block">
            <span className="eyebrow">Answers</span>
            <dl className="facts">
              <dt>Budget</dt><dd>{BUDGET_LABELS[lead.budget] ?? lead.budget}</dd>
              <dt>Timeline</dt><dd>{TIMELINE_LABELS[lead.timeline] ?? lead.timeline}</dd>
              <dt>Needs</dt><dd>{lead.needs.map((n) => NEED_LABELS[n] ?? n).join(', ') || '—'}</dd>
              <dt>Received</dt><dd>{formatDate(lead.created_at, true)}</dd>
            </dl>
          </div>

          {lead.message && (
            <div className="block">
              <span className="eyebrow">In their words</span>
              <div className="quote">{lead.message}</div>
            </div>
          )}

          <div className="block">
            <span className="eyebrow">Why this score</span>
            <ul className="breakdown">
              {matched.map((b) => (
                <li key={b.rule_id} className="hit">
                  <span className="mark" aria-hidden="true">&#10003;</span>
                  <span className="lbl">{b.label}</span>
                  <span className={`points num ${b.points >= 0 ? 'pos' : 'neg'}`}>
                    {b.points >= 0 ? '+' : ''}{b.points}
                  </span>
                </li>
              ))}
              {missed.map((b) => (
                <li key={b.rule_id} className="miss">
                  <span className="mark" aria-hidden="true">&middot;</span>
                  <span className="lbl">{b.label}</span>
                  <span className="points num">0</span>
                </li>
              ))}
              {!lead.score_breakdown.length && <li className="miss">No rules were active when this lead arrived.</li>}
            </ul>
          </div>

          <div className="block">
            <span className="eyebrow">Notes</span>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What happened on the call, what to do next..."
            />
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 8 }}>
              <button
                className="btn btn-sm"
                disabled={notes === lead.notes}
                onClick={() => { onPatch(lead.id, { notes }); setSavedAt(new Date().toLocaleTimeString()); }}
              >
                Save note
              </button>
              {savedAt && notes === lead.notes && <span className="small muted">Saved {savedAt}</span>}
            </div>
          </div>

          <div className="block" style={{ borderTop: '1px solid var(--rule)', paddingTop: 16 }}>
            <button className="btn btn-sm btn-danger" onClick={() => onDelete(lead.id)}>Delete lead</button>
          </div>
        </div>
      </aside>
    </>
  );
}

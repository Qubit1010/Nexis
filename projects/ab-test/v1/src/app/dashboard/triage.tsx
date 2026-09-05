'use client';

import { useMemo, useState } from 'react';
import { ScoreMeter } from '@/components/score-meter';
import { STATUS_LABELS, StatusPill } from '@/components/status-pill';
import { BUDGETS, SERVICES, TIMELINES, labelFor } from '@/lib/options';
import { LEAD_STATUSES } from '@/types';
import type { Bands, Lead, LeadStatus, StatusCounts } from '@/types';
import styles from './triage.module.css';

interface Props {
  initialLeads: Lead[];
  initialCounts: StatusCounts;
  bands: Bands;
}

type SortKey = 'score' | 'created_at' | 'name';

const STATUS_FILTERS: { value: 'all' | LeadStatus; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'new', label: 'New' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'dead', label: 'Dead' },
];

function formatDate(iso: string): string {
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? '--'
    : date.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: '2-digit' });
}

function money(value: number): string {
  return '$' + value.toLocaleString('en-US');
}

export function Triage({ initialLeads, initialCounts, bands }: Props) {
  const [leads, setLeads] = useState<Lead[]>(initialLeads);
  const [counts, setCounts] = useState<StatusCounts>(initialCounts);
  const [status, setStatus] = useState<'all' | LeadStatus>('all');
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState<SortKey>('score');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [openId, setOpenId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState('');

  function recount(next: Lead[]): StatusCounts {
    const tally: StatusCounts = { all: next.length, new: 0, contacted: 0, qualified: 0, dead: 0 };
    for (const lead of next) tally[lead.status] += 1;
    return tally;
  }

  /* Filtering and sorting happen client-side: the whole list is already in memory, and a
     round trip per keystroke would be slower and no more correct at this size. */
  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const filtered = leads.filter((lead) => {
      if (status !== 'all' && lead.status !== status) return false;
      if (!needle) return true;
      return [lead.name, lead.company, lead.email, lead.needs]
        .join(' ')
        .toLowerCase()
        .includes(needle);
    });

    const direction = order === 'asc' ? 1 : -1;
    return [...filtered].sort((a, b) => {
      if (sort === 'name') return a.name.localeCompare(b.name) * direction;
      if (sort === 'created_at') return a.createdAt.localeCompare(b.createdAt) * direction;
      if (a.score !== b.score) return (a.score - b.score) * direction;
      return b.createdAt.localeCompare(a.createdAt);
    });
  }, [leads, status, query, sort, order]);

  function toggleSort(key: SortKey) {
    if (sort === key) {
      setOrder((current) => (current === 'asc' ? 'desc' : 'asc'));
      return;
    }
    setSort(key);
    setOrder(key === 'name' ? 'asc' : 'desc');
  }

  async function patchLead(id: string, patch: { status?: LeadStatus; notes?: string }) {
    setBusyId(id);
    setError('');
    try {
      const response = await fetch('/api/leads/' + id, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(patch),
      });
      if (!response.ok) {
        const body = (await response.json().catch(() => ({}))) as { error?: string };
        setError(body.error ?? 'Could not save that change.');
        return;
      }
      const body = (await response.json()) as { lead: Lead };
      setLeads((current) => {
        const next = current.map((lead) => (lead.id === id ? body.lead : lead));
        setCounts(recount(next));
        return next;
      });
    } catch {
      setError('We could not reach the server.');
    } finally {
      setBusyId(null);
    }
  }

  async function removeLead(id: string) {
    setBusyId(id);
    setError('');
    try {
      const response = await fetch('/api/leads/' + id, { method: 'DELETE' });
      if (!response.ok) {
        setError('Could not delete that lead.');
        return;
      }
      setLeads((current) => {
        const next = current.filter((lead) => lead.id !== id);
        setCounts(recount(next));
        return next;
      });
    } catch {
      setError('We could not reach the server.');
    } finally {
      setBusyId(null);
    }
  }

  const caret = (key: SortKey) => (sort === key ? (order === 'asc' ? '^' : 'v') : '');
  const ariaSort = (key: SortKey): 'ascending' | 'descending' | 'none' =>
    sort === key ? (order === 'asc' ? 'ascending' : 'descending') : 'none';

  return (
    <div className="shell">
      <div className={styles.header}>
        <div className={styles.headline}>
          <h1>Triage</h1>
          <div className={styles.tally}>
            <span>
              <b>{counts.all}</b> total
            </span>
            <span>
              <b>{counts.new}</b> new
            </span>
            <span>
              hot at <b>{bands.hot}</b>, warm at <b>{bands.warm}</b>
            </span>
          </div>
        </div>
      </div>

      <div className={styles.controls}>
        <input
          className={'control ' + styles.search}
          type="search"
          value={query}
          placeholder="Search name, company, email, needs"
          aria-label="Search leads"
          onChange={(event) => setQuery(event.target.value)}
        />
        <div className={styles.filters} role="group" aria-label="Filter by status">
          {STATUS_FILTERS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={
                styles.filter + (status === option.value ? ' ' + styles.filterOn : '')
              }
              aria-pressed={status === option.value}
              onClick={() => setStatus(option.value)}
            >
              {option.label}
              <span className={styles.count}>
                {option.value === 'all' ? counts.all : counts[option.value]}
              </span>
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <p role="alert" style={{ color: 'var(--danger)', paddingBottom: 'var(--s-3)' }}>
          {error}
        </p>
      ) : null}

      {leads.length === 0 ? (
        <div className={styles.empty}>
          <div className={styles.emptyLines} aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <h2>No leads yet</h2>
          <p className="muted prose">
            Every submission through the public form lands here, already scored against your
            rules. Send someone the link to open the ledger.
          </p>
          <span className={styles.emptyUrl}>/ (the public form)</span>
        </div>
      ) : (
        <div className={styles.scroller}>
          <table className={styles.table}>
            <caption className="eyebrow" style={{ textAlign: 'left', padding: 'var(--s-3) 0' }}>
              {visible.length} of {leads.length} leads
            </caption>
            <thead>
              <tr>
                <th scope="col" aria-sort={ariaSort('score')}>
                  <button
                    type="button"
                    className={styles.sortBtn}
                    onClick={() => toggleSort('score')}
                  >
                    Score <span className={styles.caret}>{caret('score')}</span>
                  </button>
                </th>
                <th scope="col" aria-sort={ariaSort('name')}>
                  <button
                    type="button"
                    className={styles.sortBtn}
                    onClick={() => toggleSort('name')}
                  >
                    Lead <span className={styles.caret}>{caret('name')}</span>
                  </button>
                </th>
                <th scope="col">Budget</th>
                <th scope="col">Timeline</th>
                <th scope="col">Wants</th>
                <th scope="col" aria-sort={ariaSort('created_at')}>
                  <button
                    type="button"
                    className={styles.sortBtn}
                    onClick={() => toggleSort('created_at')}
                  >
                    Received <span className={styles.caret}>{caret('created_at')}</span>
                  </button>
                </th>
                <th scope="col">Status</th>
                <th scope="col">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {visible.map((lead) => {
                const open = openId === lead.id;
                return (
                  <LeadRow
                    key={lead.id}
                    lead={lead}
                    open={open}
                    busy={busyId === lead.id}
                    onToggle={() => setOpenId(open ? null : lead.id)}
                    onPatch={patchLead}
                    onDelete={removeLead}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <p className={styles.pageFoot}>
        Scores come from the rules in{' '}
        <a href="/dashboard/rules">Scoring rules</a>. Change a rule and every lead is
        rescored.
      </p>
    </div>
  );
}

interface RowProps {
  lead: Lead;
  open: boolean;
  busy: boolean;
  onToggle: () => void;
  onPatch: (id: string, patch: { status?: LeadStatus; notes?: string }) => void;
  onDelete: (id: string) => void;
}

function LeadRow({ lead, open, busy, onToggle, onPatch, onDelete }: RowProps) {
  const [note, setNote] = useState(lead.notes);
  const [saved, setSaved] = useState(false);

  return (
    <>
      <tr className={styles.row + (lead.status === 'dead' ? ' ' + styles.rowDead : '')}>
        <td>
          <ScoreMeter score={lead.score} band={lead.band} />
        </td>
        <td>
          <div className={styles.who}>
            <span className={styles.name}>{lead.name}</span>
            {lead.company ? <span className={styles.company}>{lead.company}</span> : null}
            <span className={styles.email}>{lead.email}</span>
          </div>
        </td>
        <td className={styles.figure}>
          {money(lead.budget)}
          <div className={styles.sub}>{labelFor(BUDGETS, lead.budget)}</div>
        </td>
        <td className={styles.sub}>{labelFor(TIMELINES, lead.timeline)}</td>
        <td>
          <div className={styles.tags}>
            {lead.services.map((service) => (
              <span className={styles.tag} key={service}>
                {labelFor(SERVICES, service)}
              </span>
            ))}
          </div>
        </td>
        <td className={styles.figure}>{formatDate(lead.createdAt)}</td>
        <td>
          <StatusPill status={lead.status} />
        </td>
        <td>
          <div className={styles.rowActions}>
            <label className="sr-only" htmlFor={'status-' + lead.id}>
              Status for {lead.name}
            </label>
            <select
              id={'status-' + lead.id}
              className={styles.statusSelect}
              value={lead.status}
              disabled={busy}
              onChange={(event) => onPatch(lead.id, { status: event.target.value as LeadStatus })}
            >
              {LEAD_STATUSES.map((value) => (
                <option key={value} value={value}>
                  {STATUS_LABELS[value]}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onToggle}
              aria-expanded={open}
              aria-controls={'receipt-' + lead.id}
            >
              {open ? 'Hide' : 'Why?'}
            </button>
          </div>
        </td>
      </tr>

      {open ? (
        <tr className={styles.receiptRow} id={'receipt-' + lead.id}>
          <td colSpan={8}>
            <div className={styles.receipt}>
              <section>
                <p className="eyebrow" style={{ paddingBottom: 'var(--s-2)' }}>
                  Scoring receipt
                </p>
                <div className={styles.ledgerLines}>
                  {lead.breakdown.length === 0 ? (
                    <p className="muted" style={{ fontSize: 13 }}>
                      No rules fired for this lead.
                    </p>
                  ) : (
                    lead.breakdown.map((entry) => (
                      <div className={styles.ledgerLine} key={entry.ruleId + entry.label}>
                        <span className={styles.ledgerLabel}>{entry.label}</span>
                        <span
                          className={
                            styles.ledgerPoints +
                            ' ' +
                            (entry.points >= 0 ? styles.plus : styles.minus)
                          }
                        >
                          {entry.points >= 0 ? '+' : ''}
                          {entry.points}
                        </span>
                      </div>
                    ))
                  )}
                  <div className={styles.ledgerTotal}>
                    <span>Total (capped at 100)</span>
                    <span>{lead.score}</span>
                  </div>
                </div>
              </section>

              <section className={styles.detail}>
                <div>
                  <p className="eyebrow" style={{ paddingBottom: 'var(--s-2)' }}>
                    What they said
                  </p>
                  <p className={styles.detailNeeds}>{lead.needs}</p>
                </div>
                {lead.source ? (
                  <p className="muted" style={{ fontSize: 13 }}>
                    Found us via: {lead.source}
                  </p>
                ) : null}
                <div>
                  <label className="eyebrow" htmlFor={'note-' + lead.id}>
                    Your notes
                  </label>
                  <textarea
                    id={'note-' + lead.id}
                    className={'control ' + styles.notes}
                    value={note}
                    onChange={(event) => {
                      setNote(event.target.value);
                      setSaved(false);
                    }}
                  />
                </div>
                <div className={styles.noteRow}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={busy || note === lead.notes}
                    onClick={() => {
                      onPatch(lead.id, { notes: note });
                      setSaved(true);
                    }}
                  >
                    {busy ? 'Saving...' : 'Save note'}
                  </button>
                  {saved && note === lead.notes ? (
                    <span className={styles.saved}>Saved</span>
                  ) : null}
                  <button
                    type="button"
                    className="btn btn-danger"
                    disabled={busy}
                    onClick={() => onDelete(lead.id)}
                  >
                    Delete lead
                  </button>
                </div>
              </section>
            </div>
          </td>
        </tr>
      ) : null}
    </>
  );
}

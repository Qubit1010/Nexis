import { useCallback, useEffect, useState } from 'react';
import { api, ApiError } from '../api.ts';
import type { Rule, RulesMeta } from '../api.ts';

type Settings = { hot_min: number; warm_min: number };

const BLANK: Partial<Rule> = {
  label: '', field: 'budget', op: 'gte', value: '3', points: 10, enabled: true, sort: 0,
};

export default function Rules({ onSignedOut }: { onSignedOut: () => void }) {
  const [rules, setRules] = useState<Rule[]>([]);
  const [meta, setMeta] = useState<RulesMeta | null>(null);
  const [settings, setSettings] = useState<Settings>({ hot_min: 60, warm_min: 30 });
  const [draft, setDraft] = useState<Partial<Rule>>({ ...BLANK });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await api.rules();
      setRules(data.rules);
      setMeta(data.meta);
      setSettings(data.settings);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return onSignedOut();
      setError(err instanceof Error ? err.message : 'Could not load rules');
    }
  }, [onSignedOut]);

  useEffect(() => { void load(); }, [load]);

  const guard = async (fn: () => Promise<void>) => {
    setError('');
    setBusy(true);
    try {
      await fn();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return onSignedOut();
      if (err instanceof ApiError && Object.keys(err.fields).length) {
        setError(Object.entries(err.fields).map(([k, v]) => `${k}: ${v}`).join('. '));
      } else {
        setError(err instanceof Error ? err.message : 'Something went wrong');
      }
    } finally {
      setBusy(false);
    }
  };

  const saveRule = (id: number, patch: Partial<Rule>) =>
    guard(async () => {
      const { rule } = await api.updateRule(id, patch);
      setRules((rs) => rs.map((r) => (r.id === id ? rule : r)));
    });

  const addRule = () =>
    guard(async () => {
      await api.createRule({ ...draft, sort: (rules.at(-1)?.sort ?? 0) + 10 });
      setDraft({ ...BLANK });
      await load();
      setNotice('Rule added. Recompute to apply it to leads you already have.');
    });

  const removeRule = (id: number) =>
    guard(async () => {
      await api.deleteRule(id);
      setRules((rs) => rs.filter((r) => r.id !== id));
      setNotice('Rule deleted. Recompute to apply it to leads you already have.');
    });

  const saveSettings = () =>
    guard(async () => {
      const { settings: s } = await api.updateSettings(settings);
      setSettings(s);
      setNotice('Thresholds saved. Recompute to re-band existing leads.');
    });

  const rescore = () =>
    guard(async () => {
      const r = await api.rescore();
      setNotice(`Recomputed ${r.rescored} lead${r.rescored === 1 ? '' : 's'}, ${r.changed} changed.`);
    });

  if (!meta) {
    return <div className="loading"><span className="spinner" /> Loading rules</div>;
  }

  return (
    <>
      <div className="page-head">
        <div>
          <p className="eyebrow">Scoring</p>
          <h1>Rules</h1>
        </div>
        <div className="spacer" />
        <button className="btn btn-primary" onClick={rescore} disabled={busy}>
          Recompute all scores
        </button>
      </div>

      {error && <div className="banner" role="alert">{error}</div>}
      {notice && !error && <div className="banner ok" role="status">{notice}</div>}

      <div className="panel">
        <div className="panel-head">
          <h2>Rules</h2>
          <span className="small muted">
            Every enabled rule that matches adds its points. The total is clamped to 0-100.
          </span>
        </div>

        <div className="rule-row head">
          <span>On</span><span>Label</span><span>Field</span><span>Test</span><span>Value</span>
          <span style={{ textAlign: 'right' }}>Points</span><span />
        </div>

        {rules.map((rule) => (
          <RuleRow key={rule.id} rule={rule} meta={meta} busy={busy} onSave={saveRule} onDelete={removeRule} />
        ))}

        {!rules.length && <div className="empty"><h3>No rules</h3><p className="small">Every lead will score zero until you add one.</p></div>}
      </div>

      <div className="panel">
        <div className="panel-head"><h2>Add a rule</h2></div>
        <div className="panel-body">
          <RuleFields
            value={draft}
            meta={meta}
            onChange={setDraft}
            labelPlaceholder="e.g. Enterprise budget"
          />
          <button
            className="btn btn-primary"
            style={{ marginTop: 14 }}
            onClick={addRule}
            disabled={busy || !draft.label?.trim()}
          >
            Add rule
          </button>
        </div>
      </div>

      <div className="panel">
        <div className="panel-head">
          <h2>Bands</h2>
          <span className="small muted">Where a score lands on the hot / warm / cold scale.</span>
        </div>
        <div className="panel-body">
          <div className="threshold-grid">
            <div className="field">
              <label htmlFor="hot">Hot at or above</label>
              <input
                id="hot" type="number" min={0} max={100} value={settings.hot_min}
                onChange={(e) => setSettings((s) => ({ ...s, hot_min: Number(e.target.value) }))}
              />
            </div>
            <div className="field">
              <label htmlFor="warm">Warm at or above</label>
              <input
                id="warm" type="number" min={0} max={100} value={settings.warm_min}
                onChange={(e) => setSettings((s) => ({ ...s, warm_min: Number(e.target.value) }))}
              />
            </div>
          </div>
          <div className="legend">
            <span><i className="swatch" style={{ background: 'var(--hot)' }} />Hot: {settings.hot_min} and up</span>
            <span><i className="swatch" style={{ background: 'var(--warm)' }} />Warm: {settings.warm_min} to {Math.max(settings.warm_min, settings.hot_min - 1)}</span>
            <span><i className="swatch" style={{ background: 'var(--cold)' }} />Cold: below {settings.warm_min}</span>
          </div>
          <button className="btn" style={{ marginTop: 16 }} onClick={saveSettings} disabled={busy}>
            Save thresholds
          </button>
        </div>
      </div>
    </>
  );
}

function RuleRow({
  rule, meta, busy, onSave, onDelete,
}: {
  rule: Rule;
  meta: RulesMeta;
  busy: boolean;
  onSave: (id: number, patch: Partial<Rule>) => void;
  onDelete: (id: number) => void;
}) {
  const [local, setLocal] = useState<Partial<Rule>>(rule);
  useEffect(() => { setLocal(rule); }, [rule]);

  const dirty =
    local.label !== rule.label || local.field !== rule.field || local.op !== rule.op ||
    local.value !== rule.value || local.points !== rule.points;

  return (
    <div className={rule.enabled ? 'rule-row' : 'rule-row off'}>
      <input
        type="checkbox"
        checked={rule.enabled}
        disabled={busy}
        aria-label={`Enable ${rule.label}`}
        onChange={(e) => onSave(rule.id, { enabled: e.target.checked })}
      />
      <RuleFields value={local} meta={meta} onChange={setLocal} inline />
      <div style={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
        {dirty ? (
          <button className="btn btn-sm btn-primary" disabled={busy} onClick={() => onSave(rule.id, local)}>
            Save
          </button>
        ) : (
          <button
            className="btn btn-sm btn-ghost btn-danger"
            disabled={busy}
            aria-label={`Delete ${rule.label}`}
            onClick={() => onDelete(rule.id)}
          >
            &#10005;
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * The value control changes shape with the field: a picker for budget, timeline and needs,
 * a free text box only where free text is actually meaningful.
 */
function RuleFields({
  value, meta, onChange, inline, labelPlaceholder,
}: {
  value: Partial<Rule>;
  meta: RulesMeta;
  onChange: (v: Partial<Rule>) => void;
  inline?: boolean;
  labelPlaceholder?: string;
}) {
  const field = value.field ?? 'budget';
  const allowedOps = meta.fieldOps[field] ?? [];

  const setField = (next: string) => {
    const ops = meta.fieldOps[next] ?? [];
    const defaults: Record<string, string> = {
      budget: '3', timeline: '3', needs: meta.needs[0]?.value ?? '', company: '', message: '', email: '',
    };
    onChange({ ...value, field: next, op: ops[0], value: defaults[next] ?? '' });
  };

  const valueControl = () => {
    if (field === 'budget' || field === 'timeline') {
      const options = field === 'budget' ? meta.budget : meta.timeline;
      return (
        <select value={value.value ?? ''} onChange={(e) => onChange({ ...value, value: e.target.value })} aria-label="Value">
          {options.map((o) => <option key={o.value} value={String(o.value)}>{o.label}</option>)}
        </select>
      );
    }
    if (field === 'needs') {
      return (
        <select value={value.value ?? ''} onChange={(e) => onChange({ ...value, value: e.target.value })} aria-label="Value">
          {meta.needs.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      );
    }
    return (
      <input
        type="text" value={value.value ?? ''} placeholder="text to look for"
        onChange={(e) => onChange({ ...value, value: e.target.value })} aria-label="Value"
      />
    );
  };

  const body = (
    <>
      <input
        type="text" value={value.label ?? ''} placeholder={labelPlaceholder ?? 'Label'}
        onChange={(e) => onChange({ ...value, label: e.target.value })} aria-label="Rule label"
      />
      <select value={field} onChange={(e) => setField(e.target.value)} aria-label="Field">
        {meta.fields.map((f) => <option key={f} value={f}>{meta.fieldLabels[f] ?? f}</option>)}
      </select>
      <select value={value.op ?? ''} onChange={(e) => onChange({ ...value, op: e.target.value })} aria-label="Test">
        {allowedOps.map((o) => <option key={o} value={o}>{meta.opLabels[o] ?? o}</option>)}
      </select>
      {valueControl()}
      <input
        className="points-in" type="number" min={-100} max={100} value={value.points ?? 0}
        onChange={(e) => onChange({ ...value, points: Number(e.target.value) })} aria-label="Points"
      />
    </>
  );

  if (inline) return body;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(150px,1.4fr) 1fr 1fr 1.1fr 90px', gap: 8, alignItems: 'center' }}>
      {body}
    </div>
  );
}

import { useEffect, useState } from 'react';

import type { PromptVersion } from '../types.ts';

type Props = {
  versions: PromptVersion[];
  onSave: (systemPrompt: string, label: string) => Promise<void>;
  onActivate: (id: number) => Promise<void>;
};

export function PromptPanel({ versions, onSave, onActivate }: Props) {
  const active = versions.find((version) => version.isActive) ?? versions[0] ?? null;
  const [text, setText] = useState(active?.systemPrompt ?? '');
  const [label, setLabel] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Follow the active version when it changes underneath us (for example after a rollback),
  // but never clobber an in-progress edit.
  const [baseline, setBaseline] = useState(active?.id ?? null);
  useEffect(() => {
    if (active && active.id !== baseline) {
      setBaseline(active.id);
      setText(active.systemPrompt);
    }
  }, [active, baseline]);

  const dirty = active !== null && text.trim() !== active.systemPrompt.trim();

  async function handleSave() {
    if (!dirty || busy) return;
    setBusy(true);
    setError(null);
    try {
      await onSave(text.trim(), label.trim());
      setLabel('');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save that prompt');
    } finally {
      setBusy(false);
    }
  }

  async function handleActivate(id: number) {
    setBusy(true);
    setError(null);
    try {
      await onActivate(id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not switch version');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="prompt-panel">
      <h2 style={{ fontSize: 'var(--t-lg)', margin: '0 0 4px', letterSpacing: '-0.01em' }}>
        The prompt
      </h2>
      <p className="lede" style={{ color: 'var(--ink-2)', fontSize: 13, maxWidth: '68ch', marginTop: 0 }}>
        This is the voice. Saving never overwrites what is here, it creates the next version and
        makes it active, so every rating you have already given stays attached to the exact text
        that earned it. That is what makes the scoreboard mean anything.
      </p>

      <div className="field-group">
        <label htmlFor="prompt-text">
          System prompt {active ? `(currently v${active.version}: ${active.label})` : ''}
        </label>
        <textarea
          id="prompt-text"
          className="prompt-textarea"
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
      </div>

      <div className="field-group">
        <label htmlFor="prompt-label">Name this change (optional)</label>
        <input
          id="prompt-label"
          type="text"
          value={label}
          maxLength={120}
          placeholder="Shorter, always ask about budget"
          onChange={(event) => setLabel(event.target.value)}
        />
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="row">
        <button type="button" className="primary" onClick={handleSave} disabled={!dirty || busy}>
          {busy ? 'Saving...' : `Save as v${(versions[0]?.version ?? 0) + 1}`}
        </button>
        {dirty ? (
          <button
            type="button"
            className="tertiary"
            onClick={() => setText(active?.systemPrompt ?? '')}
            disabled={busy}
          >
            Discard changes
          </button>
        ) : (
          <span style={{ fontSize: 13, color: 'var(--ink-3)' }}>
            No unsaved changes.
          </span>
        )}
      </div>

      <h3 className="section-label" style={{ marginTop: 32 }}>
        Version history
      </h3>
      <ul className="version-list">
        {versions.map((version) => (
          <li key={version.id} className={`version-row${version.isActive ? ' is-active' : ''}`}>
            <div className="grow">
              <div className="name">
                v{version.version} · {version.label}
              </div>
              <div className="when">{new Date(version.createdAt).toLocaleString()}</div>
            </div>
            {version.isActive ? (
              <span className="flag" style={{ color: 'var(--accent)' }}>
                Active
              </span>
            ) : (
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => handleActivate(version.id)}
              >
                Use this one
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

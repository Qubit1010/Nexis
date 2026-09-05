import { useEffect, useState } from 'react';

import type { Draft, Enquiry, Rating } from '../types.ts';

type Props = {
  enquiry: Enquiry;
  drafts: Draft[];
  activeVersion: number | null;
  generating: boolean;
  onGenerate: () => Promise<void>;
  onSaveEdit: (draftId: number, text: string) => Promise<void>;
  onRate: (draftId: number, rating: Rating) => Promise<void>;
};

function formatCost(cost: number | null): string {
  if (cost === null) return 'no cost (stub)';
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

function MetaStrip({ draft }: { draft: Draft }) {
  const items = [
    `prompt v${draft.promptVersion}`,
    draft.provider,
    draft.model,
    draft.inputTokens === null && draft.outputTokens === null
      ? 'tokens n/a'
      : `${draft.inputTokens ?? 0} in / ${draft.outputTokens ?? 0} out`,
    draft.latencyMs === null ? 'timing n/a' : `${draft.latencyMs} ms`,
    formatCost(draft.costUsd),
    draft.editDistance === null
      ? 'unedited'
      : `${draft.editDistance} words changed (${Math.round((draft.keepRatio ?? 0) * 100)}% kept)`,
  ];

  return (
    <div className="metastrip">
      {items.map((item, index) => (
        <span key={item}>
          {index > 0 ? <span className="sep"> · </span> : null}
          {item}
        </span>
      ))}
    </div>
  );
}

export function DraftPane({
  enquiry,
  drafts,
  activeVersion,
  generating,
  onGenerate,
  onSaveEdit,
  onRate,
}: Props) {
  const latest = drafts[0] ?? null;
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Leaving edit mode when the user moves to a different enquiry or generates a new draft
  // avoids the trap of silently carrying one draft's edits onto another.
  useEffect(() => {
    setEditing(false);
    setError(null);
  }, [enquiry.id, latest?.id]);

  async function guard(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'That did not work');
    } finally {
      setBusy(false);
    }
  }

  function startEditing() {
    if (!latest) return;
    setText(latest.editedText ?? latest.generatedText);
    setEditing(true);
  }

  const shown = latest ? (latest.editedText ?? latest.generatedText) : '';

  return (
    <>
      <article className="sheet">
        <div className="received">
          <p className="section-label">Received</p>
          <h2 className="subject">{enquiry.subject}</h2>
          <p className="prose">{enquiry.body}</p>
        </div>

        <div className={`reply${latest ? ' landing' : ''}`} key={latest?.id ?? 'empty'}>
          <p className="section-label">Your reply</p>

          {generating ? (
            <div aria-busy="true" aria-label="Drafting">
              <div className="skeleton" />
              <div className="skeleton" />
              <div className="skeleton short" />
              <div className="skeleton" />
            </div>
          ) : !latest ? (
            <div className="empty">
              <h3>No draft yet</h3>
              <p>
                Drafting uses prompt version {activeVersion ?? '?'}, whichever one is active on
                the Prompt tab. Whatever you do next with this draft, editing it or rating it,
                gets recorded against that version.
              </p>
              <button
                type="button"
                className="primary"
                onClick={() => guard(onGenerate)}
                disabled={busy}
              >
                Draft reply
              </button>
            </div>
          ) : editing ? (
            <>
              <label htmlFor="draft-edit">Edit the reply, then save</label>
              <textarea
                id="draft-edit"
                className="reply-textarea"
                value={text}
                onChange={(event) => setText(event.target.value)}
              />
              <div className="row">
                <button
                  type="button"
                  className="primary"
                  disabled={busy}
                  onClick={() =>
                    guard(async () => {
                      await onSaveEdit(latest.id, text);
                      setEditing(false);
                    })
                  }
                >
                  {busy ? 'Saving...' : 'Save edit'}
                </button>
                <button
                  type="button"
                  className="tertiary"
                  disabled={busy}
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <>
              <p className="prose">{shown}</p>

              <div className="row spread">
                <div className="rating" role="group" aria-label="Rate this draft">
                  <button
                    type="button"
                    className="good"
                    aria-pressed={latest.rating === 'good'}
                    disabled={busy}
                    onClick={() =>
                      guard(() => onRate(latest.id, latest.rating === 'good' ? null : 'good'))
                    }
                  >
                    Good
                  </button>
                  <button
                    type="button"
                    className="bad"
                    aria-pressed={latest.rating === 'bad'}
                    disabled={busy}
                    onClick={() =>
                      guard(() => onRate(latest.id, latest.rating === 'bad' ? null : 'bad'))
                    }
                  >
                    Bad
                  </button>
                </div>

                <div className="row">
                  <button type="button" className="secondary" onClick={startEditing} disabled={busy}>
                    Edit
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy}
                    onClick={() => guard(onGenerate)}
                  >
                    Re-draft with v{activeVersion ?? '?'}
                  </button>
                </div>
              </div>

              <MetaStrip draft={latest} />
            </>
          )}

          {error ? <p className="error">{error}</p> : null}
        </div>
      </article>

      {drafts.length > 1 ? (
        <section className="draft-history">
          <h3 className="section-label">Earlier drafts for this enquiry</h3>
          <div className="table-scroll">
            <table className="ledger">
              <thead>
                <tr>
                  <th>Prompt</th>
                  <th className="num">Words changed</th>
                  <th>Rating</th>
                  <th className="num">When</th>
                </tr>
              </thead>
              <tbody>
                {drafts.slice(1).map((draft) => (
                  <tr key={draft.id}>
                    <td>v{draft.promptVersion}</td>
                    <td className="num">{draft.editDistance ?? '-'}</td>
                    <td>{draft.rating ?? 'unrated'}</td>
                    <td className="num">{new Date(draft.createdAt).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: 13, color: 'var(--ink-3)', marginTop: 12, maxWidth: '66ch' }}>
            Re-drafting the same enquiry under a newer prompt is the cleanest comparison you can
            make by hand: same input, different prompt, two ratings.
          </p>
        </section>
      ) : null}
    </>
  );
}

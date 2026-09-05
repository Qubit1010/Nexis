import { useCallback, useEffect, useState } from 'react';

import { api } from './api.ts';
import { DraftPane } from './components/DraftPane.tsx';
import { EnquiryList } from './components/EnquiryList.tsx';
import { NewEnquiry } from './components/NewEnquiry.tsx';
import { PromptPanel } from './components/PromptPanel.tsx';
import { Scoreboard } from './components/Scoreboard.tsx';
import type {
  Draft,
  Enquiry,
  EnquirySummary,
  Health,
  PromptVersion,
  Rating,
  Scoreboard as ScoreboardData,
} from './types.ts';

type Tab = 'desk' | 'prompt' | 'scoreboard';

export function App() {
  const [tab, setTab] = useState<Tab>('desk');
  const [health, setHealth] = useState<Health | null>(null);
  const [enquiries, setEnquiries] = useState<EnquirySummary[]>([]);
  const [prompts, setPrompts] = useState<PromptVersion[]>([]);
  const [stats, setStats] = useState<ScoreboardData | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selected, setSelected] = useState<{ enquiry: Enquiry; drafts: Draft[] } | null>(null);

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [fatal, setFatal] = useState<string | null>(null);

  const refreshLists = useCallback(async () => {
    const [enquiryList, promptList, scoreboard] = await Promise.all([
      api.listEnquiries(),
      api.listPrompts(),
      api.stats(),
    ]);
    setEnquiries(enquiryList);
    setPrompts(promptList);
    setStats(scoreboard);
    return enquiryList;
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [healthResult, enquiryList] = await Promise.all([api.health(), refreshLists()]);
        if (cancelled) return;
        setHealth(healthResult);
        if (enquiryList.length > 0 && enquiryList[0]) setSelectedId(enquiryList[0].id);
      } catch (cause) {
        if (!cancelled) setFatal(cause instanceof Error ? cause.message : 'Could not start');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshLists]);

  useEffect(() => {
    let cancelled = false;
    if (selectedId === null) {
      setSelected(null);
      return;
    }
    (async () => {
      try {
        const detail = await api.getEnquiry(selectedId);
        if (!cancelled) setSelected(detail);
      } catch (cause) {
        if (!cancelled) setFatal(cause instanceof Error ? cause.message : 'Could not load enquiry');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const reloadSelected = useCallback(async () => {
    if (selectedId === null) return;
    const [detail] = await Promise.all([api.getEnquiry(selectedId), refreshLists()]);
    setSelected(detail);
  }, [selectedId, refreshLists]);

  async function handleCreateEnquiry(subject: string, body: string) {
    const created = await api.createEnquiry(subject, body);
    await refreshLists();
    setSelectedId(created.id);
    setTab('desk');
  }

  async function handleGenerate() {
    if (selectedId === null) return;
    setGenerating(true);
    try {
      await api.generateDraft(selectedId);
      await reloadSelected();
    } finally {
      setGenerating(false);
    }
  }

  async function handleSaveEdit(draftId: number, text: string) {
    await api.saveEdit(draftId, text);
    await reloadSelected();
  }

  async function handleRate(draftId: number, rating: Rating) {
    await api.rate(draftId, rating);
    await reloadSelected();
  }

  async function handleSavePrompt(systemPrompt: string, label: string) {
    await api.createPrompt(systemPrompt, label.length > 0 ? label : undefined);
    await refreshLists();
  }

  async function handleActivatePrompt(id: number) {
    await api.activatePrompt(id);
    await refreshLists();
  }

  const activeVersion = prompts.find((prompt) => prompt.isActive)?.version ?? null;

  return (
    <div className="app">
      {health && !health.hasApiKey ? (
        <div className="stub-banner">
          Stub mode.{' '}
          <span>
            No ANTHROPIC_API_KEY is set, so drafts are canned text and no model is called. Every
            other part of the app is real. Add a key to <code>.env</code> and restart to draft
            with {health.model}.
          </span>
        </div>
      ) : null}

      <header className="masthead">
        <h1>ReplyLab</h1>
        <span className="tagline">Draft replies, rate them, watch the prompt improve</span>
        <nav className="tabs" role="tablist" aria-label="Views">
          {(
            [
              ['desk', 'Desk'],
              ['prompt', `Prompt${activeVersion ? ` v${activeVersion}` : ''}`],
              ['scoreboard', 'Scoreboard'],
            ] as Array<[Tab, string]>
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              className="tab"
              aria-selected={tab === value}
              onClick={() => setTab(value)}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      {fatal ? <p className="error" style={{ margin: 'var(--s-5)' }}>{fatal}</p> : null}

      {tab === 'desk' ? (
        <div className="desk">
          <aside className="rail">
            <NewEnquiry onCreate={handleCreateEnquiry} />
            <div>
              <h2 className="section-label">Enquiries</h2>
              <EnquiryList
                enquiries={enquiries}
                selectedId={selectedId}
                loading={loading}
                onSelect={setSelectedId}
              />
            </div>
          </aside>

          <main className="stage">
            {selected ? (
              <DraftPane
                enquiry={selected.enquiry}
                drafts={selected.drafts}
                activeVersion={activeVersion}
                generating={generating}
                onGenerate={handleGenerate}
                onSaveEdit={handleSaveEdit}
                onRate={handleRate}
              />
            ) : (
              <div className="empty">
                <h3>Pick an enquiry, or paste one in</h3>
                <p>
                  Paste the subject and body of something a client actually sent you. ReplyLab
                  drafts a reply using the active prompt, you edit and rate it, and the Scoreboard
                  tells you whether your prompt changes are helping.
                </p>
              </div>
            )}
          </main>
        </div>
      ) : null}

      {tab === 'prompt' ? (
        <main className="stage">
          <PromptPanel
            versions={prompts}
            onSave={handleSavePrompt}
            onActivate={handleActivatePrompt}
          />
        </main>
      ) : null}

      {tab === 'scoreboard' ? (
        <main className="stage">
          <Scoreboard data={stats} loading={loading} />
        </main>
      ) : null}
    </div>
  );
}

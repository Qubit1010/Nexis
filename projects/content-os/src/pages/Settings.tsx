import { useEffect, useState } from "react";
import { api, FORMAT_LABELS, FORMATS, type Channel, type Format, type Job } from "../lib/api";
import { useAction, useApi } from "../lib/hooks";
import { Button, Card, Field, inputCls, Pill, SectionTitle } from "../components/ui";

interface SettingsT {
  formats: Record<Format, { model: string; maxTurns: number; timeoutMin: number }>;
  leadTimeHours: number;
  atRiskHours: number;
  blogMaxLateMin: number;
  defaultPublishTime: string;
  pauseGeneration: boolean;
  quietHours: { start: string; end: string } | null;
  maxWeeklyUtilization: number;
  cadence: Record<Format, number>;
  mirror: { enabled: boolean; sheetId: string; tab: string; cutoverConfirmed?: boolean };
  sources: { contentIdeasSheetId: string; scheduleSheetId: string };
  git: { name: string; email: string };
  imageHost: { kind: string; bucket: string };
}

interface Health {
  ok: boolean;
  checks: { id: string; label: string; ok: boolean; detail: string }[];
}

export function Settings() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-[22px] font-semibold tracking-tight">Settings</h1>
      </header>
      <HealthPanel />
      <NeedsCheck />
      <ChannelsPanel />
      <SettingsForm />
      <ImportPanel />
    </div>
  );
}

function HealthPanel() {
  const [data, setData] = useState<Health | null>(null);
  const [loading, setLoading] = useState(false);
  const load = async (force = false) => {
    setLoading(true);
    try {
      setData(await api.get<Health>(`/health${force ? "?force=1" : ""}`));
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    void load();
  }, []);
  return (
    <section>
      <SectionTitle
        right={
          <Button variant="quiet" busy={loading} onClick={() => load(true)}>
            Re-check
          </Button>
        }
      >
        Health
      </SectionTitle>
      <Card className="divide-y divide-line">
        {!data && <p className="px-4 py-3 text-[13px] text-dim">Checking...</p>}
        {data?.checks.map((c) => (
          <div key={c.id} className="flex items-start gap-3 px-4 py-2.5 text-[13px]">
            <span className={`mt-1.5 size-2 shrink-0 rounded-full ${c.ok ? "bg-pos" : "bg-neg"}`} aria-label={c.ok ? "ok" : "problem"} />
            <span className="w-56 shrink-0 font-medium">{c.label}</span>
            <span className={`min-w-0 break-words ${c.ok ? "text-muted" : "text-neg"}`}>{c.detail}</span>
          </div>
        ))}
      </Card>
    </section>
  );
}

function NeedsCheck() {
  const { data, reload } = useApi<Job[]>("/jobs?status=needs_check");
  const { run } = useAction();
  if (!data?.length) return null;
  return (
    <section>
      <SectionTitle>Needs a human check</SectionTitle>
      <div className="space-y-2">
        {data.map((j) => (
          <Card key={j.id} className="px-4 py-3 text-[13px]">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span>
                <span className="font-mono">{j.type}</span>
                {j.itemId && (
                  <a className="ml-2 text-accent-bright hover:underline" href={`#/item/${j.itemId}`}>
                    open item
                  </a>
                )}
              </span>
              <div className="flex gap-2">
                <Button onClick={() => run("r", () => api.post(`/jobs/${j.id}/resolve`, { outcome: "done" }), "Marked done").then(reload)}>It went through</Button>
                <Button onClick={() => run("r", () => api.post(`/jobs/${j.id}/resolve`, { outcome: "retry" }), "Retrying").then(reload)}>Retry it</Button>
              </div>
            </div>
            {j.lastError && <p className="mt-1 text-[12px] text-warn">{j.lastError}</p>}
          </Card>
        ))}
      </div>
    </section>
  );
}

function ChannelsPanel() {
  const { data, reload } = useApi<Channel[]>("/channels", { live: false });
  const [buffer, setBuffer] = useState<{ channels?: { id: string; service: string; displayName: string; type: string }[]; error?: string } | null>(null);
  const { busy, run } = useAction();
  const save = (id: string, config: Record<string, unknown>) => run(id, () => api.patch(`/channels/${id}`, { config }), "Channel saved").then(reload);
  return (
    <section>
      <SectionTitle>Channels</SectionTitle>
      <div className="grid gap-3 lg:grid-cols-2">
        {(data ?? []).map((c) => (
          <Card key={c.id} className="space-y-3 px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[14px] font-medium">{c.name}</div>
                <div className="text-[12px] text-dim">
                  {FORMAT_LABELS[c.format]} · {c.kind === "buffer" ? "Buffer" : c.kind === "git_astro" ? "git + deploy" : "manual paste"}
                </div>
              </div>
            </div>
            {c.kind === "buffer" && (
              <div className="space-y-2">
                <Field label="Buffer channel">
                  <div className="flex gap-2">
                    <select className={inputCls} value={c.config.bufferChannelId ?? ""} onChange={(e) => save(c.id, { bufferChannelId: e.target.value || null })}>
                      <option value="">{c.config.bufferChannelId ? c.config.bufferChannelId : "Auto: the single LinkedIn channel"}</option>
                      {buffer?.channels?.map((b) => (
                        <option key={b.id} value={b.id}>
                          {b.service} / {b.displayName} ({b.type})
                        </option>
                      ))}
                    </select>
                    <Button busy={busy === "buf"} onClick={() => run("buf", () => api.get<typeof buffer>("/buffer/channels").catch((e) => ({ error: e.message }))).then((r) => setBuffer(r ?? null))}>
                      Load
                    </Button>
                  </div>
                </Field>
                {buffer?.error && <p className="text-[12px] text-neg">{buffer.error}</p>}
              </div>
            )}
            {c.kind === "git_astro" && (
              <div className="grid grid-cols-2 gap-2 text-[12.5px]">
                <Field label="Repo">
                  <input className={inputCls} defaultValue={c.config.repo} onBlur={(e) => e.target.value !== c.config.repo && save(c.id, { repo: e.target.value })} />
                </Field>
                <Field label="Deploy">
                  <select className={inputCls} value={c.config.deployMode} onChange={(e) => save(c.id, { deployMode: e.target.value })}>
                    <option value="git">git push (Vercel Git integration)</option>
                    <option value="vercel-cli">Vercel CLI deploy + promote</option>
                  </select>
                </Field>
                <Field label="Site URL">
                  <input className={inputCls} defaultValue={c.config.siteUrl} onBlur={(e) => e.target.value !== c.config.siteUrl && save(c.id, { siteUrl: e.target.value })} />
                </Field>
                <Field label="Vercel scope">
                  <input className={inputCls} defaultValue={c.config.vercelScope ?? ""} placeholder="qubit1010s-projects" onBlur={(e) => e.target.value !== (c.config.vercelScope ?? "") && save(c.id, { vercelScope: e.target.value || undefined })} />
                </Field>
              </div>
            )}
            {c.kind === "manual_newsletter" && (
              <div className="grid grid-cols-2 gap-2">
                <Field label="LinkedIn newsletter URL" hint="Opened by the Open LinkedIn button">
                  <input className={inputCls} defaultValue={c.config.linkedinUrl} onBlur={(e) => e.target.value !== c.config.linkedinUrl && save(c.id, { linkedinUrl: e.target.value })} />
                </Field>
                <Field label="Issue log">
                  <input className={inputCls} defaultValue={c.config.issueLog} onBlur={(e) => e.target.value !== c.config.issueLog && save(c.id, { issueLog: e.target.value })} />
                </Field>
              </div>
            )}
          </Card>
        ))}
      </div>
    </section>
  );
}

function SettingsForm() {
  const { data, reload } = useApi<SettingsT>("/settings", { live: false });
  const [s, setS] = useState<SettingsT | null>(null);
  const { busy, run } = useAction();
  useEffect(() => {
    if (data) setS(structuredClone(data));
  }, [data]);
  if (!s) return null;
  const dirty = JSON.stringify(s) !== JSON.stringify(data);
  const set = (patch: Partial<SettingsT>) => setS({ ...s, ...patch });
  const num = (v: string) => (v === "" ? 0 : Number(v));
  return (
    <section className="space-y-4">
      <SectionTitle
        right={
          <Button variant="primary" disabled={!dirty} busy={busy === "save"} onClick={() => run("save", () => api.put("/settings", s), "Settings saved").then(reload)}>
            Save settings
          </Button>
        }
      >
        Generation and scheduling
      </SectionTitle>
      <Card className="grid gap-4 px-4 py-4 md:grid-cols-3">
        <label className="flex items-center gap-2 text-[13px] md:col-span-3">
          <input type="checkbox" checked={s.pauseGeneration} onChange={(e) => set({ pauseGeneration: e.target.checked })} />
          Pause all generation (queued drafts wait; publishing still runs)
        </label>
        <Field label="Quiet hours start (PKT)" hint="No new Claude runs start inside this window">
          <input type="time" className={inputCls} value={s.quietHours?.start ?? ""} onChange={(e) => set({ quietHours: e.target.value ? { start: e.target.value, end: s.quietHours?.end ?? "08:00" } : null })} />
        </Field>
        <Field label="Quiet hours end">
          <input type="time" className={inputCls} value={s.quietHours?.end ?? ""} disabled={!s.quietHours} onChange={(e) => set({ quietHours: { start: s.quietHours!.start, end: e.target.value } })} />
        </Field>
        <Field label="Stop starting runs above this weekly plan usage" hint="0.9 = 90%">
          <input type="number" step="0.05" min="0.1" max="1" className={inputCls} value={s.maxWeeklyUtilization} onChange={(e) => set({ maxWeeklyUtilization: num(e.target.value) })} />
        </Field>
        <Field label="At risk when not approved within (hours)">
          <input type="number" className={inputCls} value={s.atRiskHours} onChange={(e) => set({ atRiskHours: num(e.target.value) })} />
        </Field>
        <Field label="Hold a blog as missed when late by (minutes)" hint="When the PC was off past the slot">
          <input type="number" className={inputCls} value={s.blogMaxLateMin} onChange={(e) => set({ blogMaxLateMin: num(e.target.value) })} />
        </Field>
        <Field label="Default publish time">
          <input className={inputCls} value={s.defaultPublishTime} onChange={(e) => set({ defaultPublishTime: e.target.value })} />
        </Field>
      </Card>

      <Card className="overflow-x-auto px-4 py-4">
        <table className="w-full min-w-[520px] text-[13px]">
          <thead className="text-left text-[11px] uppercase tracking-wider text-dim">
            <tr>
              <th className="pb-2 font-medium">Format</th>
              <th className="pb-2 font-medium">Model</th>
              <th className="pb-2 font-medium">Max turns</th>
              <th className="pb-2 font-medium">Timeout (min)</th>
              <th className="pb-2 font-medium">Weekly target</th>
            </tr>
          </thead>
          <tbody>
            {FORMATS.map((f) => (
              <tr key={f} className="border-t border-line">
                <td className="py-2 pr-3">{FORMAT_LABELS[f]}</td>
                <td className="py-2 pr-3">
                  <select className={inputCls} value={s.formats[f].model} onChange={(e) => set({ formats: { ...s.formats, [f]: { ...s.formats[f], model: e.target.value } } })}>
                    {["opus", "sonnet", "haiku"].map((m) => (
                      <option key={m}>{m}</option>
                    ))}
                  </select>
                </td>
                <td className="py-2 pr-3">
                  <input type="number" className={inputCls} value={s.formats[f].maxTurns} onChange={(e) => set({ formats: { ...s.formats, [f]: { ...s.formats[f], maxTurns: num(e.target.value) } } })} />
                </td>
                <td className="py-2 pr-3">
                  <input type="number" className={inputCls} value={s.formats[f].timeoutMin} onChange={(e) => set({ formats: { ...s.formats, [f]: { ...s.formats[f], timeoutMin: num(e.target.value) } } })} />
                </td>
                <td className="py-2">
                  <input type="number" className={inputCls} value={s.cadence[f]} onChange={(e) => set({ cadence: { ...s.cadence, [f]: num(e.target.value) } })} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="space-y-3 px-4 py-4">
          <SectionTitle>Git identity for site commits</SectionTitle>
          <Field label="Name">
            <input className={inputCls} value={s.git.name} onChange={(e) => set({ git: { ...s.git, name: e.target.value } })} />
          </Field>
          <Field label="Email" hint="Used when a repo has no user.email (nexuspoint-site has none)">
            <input className={inputCls} value={s.git.email} onChange={(e) => set({ git: { ...s.git, email: e.target.value } })} placeholder="you@example.com" />
          </Field>
        </Card>
        <Card className="space-y-3 px-4 py-4">
          <SectionTitle>Google Sheet mirror</SectionTitle>
          <label className="flex items-center gap-2 text-[13px]">
            <input type="checkbox" checked={s.mirror.enabled} onChange={(e) => set({ mirror: { ...s.mirror, enabled: e.target.checked } })} />
            Mirror the schedule to the sheet (one way, Content OS to sheet)
          </label>
          <Field label="Tab" hint='A new tab by default. Writing to "SM Schedule" itself needs the cutover box below.'>
            <input className={inputCls} value={s.mirror.tab} onChange={(e) => set({ mirror: { ...s.mirror, tab: e.target.value } })} />
          </Field>
          {s.mirror.tab.trim().toLowerCase() === "sm schedule" && (
            <label className="flex items-center gap-2 text-[13px] text-warn">
              <input type="checkbox" checked={!!s.mirror.cutoverConfirmed} onChange={(e) => set({ mirror: { ...s.mirror, cutoverConfirmed: e.target.checked } })} />
              Cutover: replace the hand-kept SM Schedule tab (rename it to "SM Schedule (archive)" in Sheets first)
            </label>
          )}
          <Button busy={busy === "mirror"} disabled={!data?.mirror.enabled} onClick={() => run("mirror", () => api.post("/mirror/sync", {}), "Mirror queued")}>
            Sync now
          </Button>
        </Card>
      </div>
    </section>
  );
}

interface ImportReport {
  dryRun: boolean;
  ideas: { tab: string; rows: number; added: number; duplicates: number }[];
  items: { rows: number; created: number; existing: number; skipped: number; byFormat: Record<string, number>; byStatus: Record<string, number> };
  warnings: string[];
}

function ImportPanel() {
  const [report, setReport] = useState<ImportReport | null>(null);
  const { busy, run } = useAction();
  const go = (dryRun: boolean) => run(dryRun ? "dry" : "commit", () => api.post<ImportReport>("/import/sheets", { dryRun }), dryRun ? undefined : "Imported").then((r) => r && setReport(r));
  return (
    <section>
      <SectionTitle>Import from Google Sheets</SectionTitle>
      <Card className="space-y-3 px-4 py-4 text-[13px]">
        <p className="text-muted">
          Reads Daily Brief - Content Ideas (bookmarks), Topics Ideas and SM Schedule into Content OS. Safe to repeat: ideas dedupe by URL or title, schedule rows by row number. Nothing is written to the sheets.
        </p>
        <div className="flex gap-2">
          <Button busy={busy === "dry"} onClick={() => go(true)}>
            Preview (dry run)
          </Button>
          <Button variant="primary" busy={busy === "commit"} disabled={!report} onClick={() => go(false)}>
            Import
          </Button>
        </div>
        {report && (
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <div className="mb-1 text-[11px] uppercase tracking-wider text-dim">Ideas {report.dryRun ? "(preview)" : ""}</div>
              <ul className="space-y-0.5 font-mono text-[12px]">
                {report.ideas.map((i) => (
                  <li key={i.tab}>
                    {i.tab}: {i.rows} rows{!report.dryRun && `, ${i.added} added, ${i.duplicates} already there`}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <div className="mb-1 text-[11px] uppercase tracking-wider text-dim">Schedule items</div>
              <p className="font-mono text-[12px]">
                {report.items.rows} rows ({report.items.existing} already imported, {report.items.skipped} reels or unreadable skipped){!report.dryRun && `, ${report.items.created} created`}
              </p>
              <p className="mt-1 flex flex-wrap gap-1">
                {Object.entries(report.items.byStatus).map(([k, v]) => (
                  <Pill key={k} status={k}>
                    {k} {v}
                  </Pill>
                ))}
              </p>
            </div>
            {report.warnings.map((w) => (
              <p key={w} className="text-warn">
                {w}
              </p>
            ))}
          </div>
        )}
      </Card>
    </section>
  );
}

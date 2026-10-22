import { useState } from "react";
import { api, type Job } from "../lib/api";
import { ago, fmtDateTime } from "../lib/time";
import { useAction, useApi } from "../lib/hooks";
import { Button, Card, Field, inputCls, Modal, Pill } from "../components/ui";

interface Automation {
  id: string;
  name: string;
  jobType: string;
  cron: string;
  tz: string;
  enabled: boolean;
  catchUp: "once" | "skip";
  maxLateMin: number;
  nextRunAt: string | null;
  lastRunAt: string | null;
  builtin: boolean;
  payload: Record<string, unknown>;
  lastJob: Job | null;
}

const DESCRIBE: Record<string, string> = {
  "prepare-week": "Drafts every planned item in the next 7 days that has no draft yet, so reviews are ready ahead of their slots.",
  "buffer-reconcile": "Checks Buffer for posts that went out and marks them published with their LinkedIn URL.",
  "news-brief": "Generates the News and Practical AI briefs (uses OpenAI/Anthropic API credit).",
  "youtube-brief": "Generates the YouTube intelligence brief (uses YouTube + OpenAI API credit).",
  "sheet-mirror": "Rewrites the mirror tab of the Weekly Posting Schedule sheet from Content OS.",
};

const JOB_TYPES = [
  { value: "prepare_week", label: "Draft planned items" },
  { value: "buffer_reconcile", label: "Check Buffer" },
  { value: "sheet_mirror", label: "Mirror to sheet" },
  { value: "shell:daily_brief", label: "Daily brief (News + Practical AI)" },
  { value: "shell:youtube_brief", label: "YouTube brief" },
];

export function Automations() {
  const { data, reload } = useApi<Automation[]>("/automations");
  const [adding, setAdding] = useState(false);
  const { busy, run } = useAction();
  const patch = (id: string, body: Record<string, unknown>, ok?: string) => run(id, () => api.patch(`/automations/${id}`, body), ok).then(reload);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight">Automations</h1>
          <p className="max-w-2xl text-[13px] text-dim">
            Cron schedules in Pakistan time. If the PC was off when one was due, it runs once when Content OS starts again (within its catch-up window), never a backlog.
          </p>
        </div>
        <Button variant="primary" onClick={() => setAdding(true)}>
          New automation
        </Button>
      </header>
      <div className="space-y-2">
        {(data ?? []).map((a) => (
          <Card key={a.id} className="px-4 py-3">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[14px] font-medium">{a.name}</span>
                  {!a.enabled && <Pill status="cancelled">off</Pill>}
                  {a.lastJob && <Pill status={a.lastJob.status} />}
                </div>
                <p className="mt-0.5 text-[12.5px] text-dim">{DESCRIBE[a.id] ?? `${a.jobType} ${JSON.stringify(a.payload)}`}</p>
                <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-[12px] text-muted">
                  <CronEditor value={a.cron} onSave={(cron) => patch(a.id, { cron }, "Schedule updated")} />
                  <span>next: {a.enabled && a.nextRunAt ? `${fmtDateTime(a.nextRunAt)} (${ago(a.nextRunAt)})` : "off"}</span>
                  <span>last: {a.lastRunAt ? ago(a.lastRunAt) : "never"}</span>
                  <label className="flex items-center gap-1.5">
                    catch-up
                    <select className="rounded border border-line-strong bg-s2 px-1 py-0.5 text-[12px]" value={a.catchUp} onChange={(e) => patch(a.id, { catchUp: e.target.value })}>
                      <option value="once">once, within {Math.round(a.maxLateMin / 60)}h</option>
                      <option value="skip">skip missed runs</option>
                    </select>
                  </label>
                </div>
                {a.lastJob?.lastError && a.lastJob.status === "failed" && <p className="mt-1.5 whitespace-pre-wrap text-[12px] text-neg">{a.lastJob.lastError.slice(0, 400)}</p>}
              </div>
              <div className="flex shrink-0 gap-1.5">
                <Button variant="quiet" busy={busy === `run-${a.id}`} onClick={() => run(`run-${a.id}`, () => api.post(`/automations/${a.id}/run-now`, {}), "Queued").then(reload)}>
                  Run now
                </Button>
                <Button onClick={() => patch(a.id, { enabled: !a.enabled }, a.enabled ? "Turned off" : "Turned on")}>{a.enabled ? "Turn off" : "Turn on"}</Button>
                {!a.builtin && (
                  <Button variant="quiet" className="text-neg" onClick={() => run(`del-${a.id}`, () => api.del(`/automations/${a.id}`), "Deleted").then(reload)}>
                    Delete
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
      <NewAutomation open={adding} onClose={() => setAdding(false)} onCreated={reload} />
    </div>
  );
}

function CronEditor({ value, onSave }: { value: string; onSave: (v: string) => void }) {
  const [v, setV] = useState(value);
  const [editing, setEditing] = useState(false);
  if (!editing)
    return (
      <button className="font-mono hover:text-ink" onClick={() => setEditing(true)} title="Edit the cron expression">
        {value}
      </button>
    );
  return (
    <form
      className="flex items-center gap-1"
      onSubmit={(e) => {
        e.preventDefault();
        setEditing(false);
        if (v !== value) onSave(v);
      }}
    >
      <input className="w-32 rounded border border-line-strong bg-s2 px-1.5 py-0.5 font-mono text-[12px]" value={v} onChange={(e) => setV(e.target.value)} autoFocus onBlur={() => setEditing(false)} />
    </form>
  );
}

function NewAutomation({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState("");
  const [type, setType] = useState(JOB_TYPES[0].value);
  const [cron, setCron] = useState("0 9 * * 1");
  const { busy, run } = useAction();
  const create = async () => {
    const [jobType, task] = type.split(":");
    await run("create", () => api.post("/automations", { name: name || JOB_TYPES.find((j) => j.value === type)?.label, jobType, cron, payload: task ? { task } : {} }), "Automation created");
    onCreated();
    onClose();
  };
  return (
    <Modal open={open} onClose={onClose} title="New automation">
      <div className="space-y-3">
        <Field label="What it runs">
          <select className={inputCls} value={type} onChange={(e) => setType(e.target.value)}>
            {JOB_TYPES.map((j) => (
              <option key={j.value} value={j.value}>
                {j.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Name">
          <input className={inputCls} value={name} onChange={(e) => setName(e.target.value)} placeholder="Optional" />
        </Field>
        <Field label="Cron (PKT)" hint="minute hour day-of-month month day-of-week. 0 9 * * 1 = Mondays 9:00 am. */30 * * * * = every 30 minutes.">
          <input className={`${inputCls} font-mono`} value={cron} onChange={(e) => setCron(e.target.value)} />
        </Field>
      </div>
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="quiet" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" busy={busy === "create"} onClick={create}>
          Create
        </Button>
      </div>
    </Modal>
  );
}

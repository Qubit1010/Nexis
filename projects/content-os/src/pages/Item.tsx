import { useEffect, useMemo, useRef, useState } from "react";
import { api, fileUrl, FORMAT_LABELS, type Channel, type ItemDetail, type ItemSummary, type Version } from "../lib/api";
import { ago, fmtDateTime, fromLocalInput, toLocalInput } from "../lib/time";
import { go, toast, useAction, useApi } from "../lib/hooks";
import { Button, Card, Empty, Field, inputCls, Modal, Pill, SectionTitle } from "../components/ui";
import { Markdown, renderMarkdown, splitFrontmatter } from "../components/Markdown";
import { Diff } from "../components/Diff";

type Tab = "draft" | "changes" | "files" | "checks" | "brief" | "history";

export function ItemPage({ id }: { id: string }) {
  const { data, error, reload } = useApi<ItemDetail>(`/items/${id}`);
  const channels = useApi<Channel[]>("/channels", { live: false }).data ?? [];
  const [tab, setTab] = useState<Tab>("draft");
  const [viewN, setViewN] = useState<number | null>(null);
  const [revise, setRevise] = useState(false);
  const [editing, setEditing] = useState(false);
  const [confirm, setConfirm] = useState<null | "approve" | "publish" | "delete">(null);
  const [markOpen, setMarkOpen] = useState(false);
  const { busy, run } = useAction();

  useEffect(() => setViewN(null), [data?.item.currentVersionId]);

  if (error) return <Empty>{error}</Empty>;
  if (!data) return <div className="text-dim">Loading...</div>;
  const { item, versions, channel } = data;
  const current = versions.find((v) => v.id === item.currentVersionId) ?? versions[0];
  const viewing = viewN != null ? versions.find((v) => v.n === viewN) ?? current : current;
  const previous = viewing ? versions.find((v) => v.n === viewing.n - 1) : undefined;
  const liveRun = data.runs.find((r) => r.status === "running");
  const blocked = current?.meta.status === "blocked";
  const fails = current?.checks.filter((c) => c.level === "fail") ?? [];
  const needsForce = blocked || fails.length > 0;
  const act = (key: string, fn: () => Promise<unknown>, ok?: string) => run(key, fn, ok).then((r) => (reload(), r));

  const approve = (force = false) => act("approve", () => api.post(`/items/${id}/approve`, { force }), channel?.kind === "buffer" ? "Approved: sending to Buffer" : channel?.kind === "git_astro" ? `Approved: publishes ${fmtDateTime(item.scheduledFor)}` : "Approved");
  const publishNow = (force = false) => act("publish", () => api.post(`/items/${id}/publish-now`, { force }), "Publishing now");

  return (
    <div className="space-y-5">
      <a href="#/" className="text-[12px] text-dim hover:text-ink">
        Back to the week
      </a>
      <Header data={data} channels={channels} onSaved={reload} />

      {item.error && (
        <div className={`rounded-xl border px-4 py-3 text-[13px] ${item.status === "review" ? "border-warn/40 bg-warn/5 text-warn" : "border-neg/40 bg-neg/5 text-neg"}`}>
          <span className="whitespace-pre-wrap">{item.error}</span>
        </div>
      )}

      {/* Actions follow the item's state */}
      <div className="flex flex-wrap items-center gap-2">
        {!current && !["generating", "published", "skipped"].includes(item.status) && (
          <Button variant="primary" busy={busy === "gen"} onClick={() => act("gen", () => api.post(`/items/${id}/generate`, {}), "Queued: the draft appears here when the run finishes")}>
            Generate draft
          </Button>
        )}
        {item.status === "generating" && (
          <>
            <span className="text-[13px] text-accent-bright">Generating...</span>
            {liveRun && (
              <>
                <Button onClick={() => go(`runs/${liveRun.id}`)}>Watch the run</Button>
                <Button variant="danger" busy={busy === "kill"} onClick={() => act("kill", () => api.post(`/runs/${liveRun.id}/kill`, {}), "Stopping")}>
                  Stop
                </Button>
              </>
            )}
          </>
        )}
        {current && ["review", "failed", "missed", "planned"].includes(item.status) && (
          <>
            <Button variant="primary" busy={busy === "approve"} onClick={() => (needsForce ? setConfirm("approve") : approve())}>
              {needsForce ? "Approve anyway" : channel?.kind === "manual_newsletter" ? "Approve" : `Approve for ${item.scheduledFor ? fmtDateTime(item.scheduledFor) : "..."}`}
            </Button>
            <Button onClick={() => setRevise(true)}>Revise</Button>
            <Button onClick={() => setEditing(true)}>Edit</Button>
          </>
        )}
        {current && ["review", "failed", "missed", "approved", "scheduled"].includes(item.status) && (
          <Button onClick={() => setConfirm("publish")}>Publish now</Button>
        )}
        {["approved", "scheduled"].includes(item.status) && (
          <Button busy={busy === "unapprove"} onClick={() => act("unapprove", () => api.post(`/items/${id}/unapprove`, {}), channel?.kind === "buffer" && item.externalId ? "Pulled back from Buffer" : "Unapproved")}>
            Unapprove
          </Button>
        )}
        {item.status === "ready_to_post" && current && <NewsletterActions version={current} channel={channel} onMark={() => setMarkOpen(true)} />}
        {item.status === "failed" && current && item.approvedAt && (
          <Button busy={busy === "retry"} onClick={() => act("retry", () => api.post(`/items/${id}/retry`, {}), "Retrying")}>
            Retry publish
          </Button>
        )}
        {current && !["generating"].includes(item.status) && (
          <Button variant="quiet" busy={busy === "regen"} onClick={() => act("regen", () => api.post(`/items/${id}/generate`, {}), "Regenerating from scratch")}>
            Regenerate
          </Button>
        )}
        {current && (
          <Button variant="quiet" busy={busy === "doc"} onClick={() => act("doc", () => api.post<{ docUrl: string }>(`/items/${id}/export-doc`, {}).then((r) => window.open(r.docUrl, "_blank")), "Exported to Google Docs")}>
            Export to Doc
          </Button>
        )}
        {item.status !== "published" && (
          <Button variant="quiet" onClick={() => setMarkOpen(true)}>
            Mark published
          </Button>
        )}
        {!["published", "skipped"].includes(item.status) && (
          <Button variant="quiet" busy={busy === "skip"} onClick={() => act("skip", () => api.post(`/items/${id}/skip`, {}), "Skipped")}>
            Skip
          </Button>
        )}
        {["planned", "review", "failed", "skipped", "missed"].includes(item.status) && (
          <Button variant="quiet" className="text-neg" onClick={() => setConfirm("delete")}>
            Delete
          </Button>
        )}
      </div>

      {current && (blocked || current.meta.notes || current.meta.rescue) && (
        <Card className="space-y-2 px-4 py-3 text-[13px]">
          {blocked && (
            <p>
              <span className="font-semibold text-warn">Gate: </span>
              {current.meta.blocked_reason}
            </p>
          )}
          {current.meta.rescue && (
            <p>
              <span className="font-semibold text-accent-bright">{blocked ? "Proposed rescue: " : "Rescue applied: "}</span>
              {current.meta.rescue}
            </p>
          )}
          {current.meta.notes && (
            <details className="text-muted">
              <summary className="cursor-pointer select-none font-semibold text-ink">Notes from the run (decisions it made for you)</summary>
              <p className="mt-1 whitespace-pre-wrap">{current.meta.notes}</p>
            </details>
          )}
        </Card>
      )}

      {versions.length === 0 ? (
        <Empty>{item.status === "generating" ? "The first draft is being written. This usually takes a few minutes." : "No draft yet. Generate one, or it is drafted automatically up to 7 days before its slot."}</Empty>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line">
            <div className="flex gap-1 overflow-x-auto">
              {(["draft", "changes", "files", "checks", "brief", "history"] as Tab[]).map((t) => (
                <button key={t} onClick={() => setTab(t)} className={`-mb-px shrink-0 border-b-2 px-3 py-2 text-[13px] capitalize ${tab === t ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"}`}>
                  {t}
                  {t === "checks" && fails.length > 0 && <span className="ml-1 text-neg">{fails.length}</span>}
                </button>
              ))}
            </div>
            <label className="mb-1.5 flex items-center gap-2 text-[12px] text-dim">
              Version
              <select className="rounded-md border border-line-strong bg-s2 px-2 py-1 text-[12px] text-ink" value={viewing?.n} onChange={(e) => setViewN(Number(e.target.value))}>
                {versions.map((v) => (
                  <option key={v.id} value={v.n}>
                    v{v.n} {v.kind}
                    {v.id === item.currentVersionId ? " (current)" : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {viewing && viewing.id !== item.currentVersionId && (
            <div className="flex items-center justify-between rounded-lg border border-line-strong bg-s2 px-3 py-2 text-[12.5px]">
              <span className="text-muted">Viewing v{viewing.n}, not the current version.</span>
              <Button busy={busy === "restore"} onClick={() => act("restore", () => api.put(`/items/${id}/version`, { bodyMd: viewing.bodyMd }), `Restored v${viewing.n} as a new version`)}>
                Restore this version
              </Button>
            </div>
          )}
          {viewing && tab === "draft" && <DraftView item={item} version={viewing} />}
          {viewing && tab === "changes" && (previous ? <Diff before={previous.bodyMd} after={viewing.bodyMd} /> : <Empty>v{viewing.n} is the first version.</Empty>)}
          {viewing && tab === "files" && <FilesView data={data} version={viewing} onChange={reload} />}
          {viewing && tab === "checks" && <ChecksView version={viewing} />}
          {tab === "brief" && <BriefView data={data} onSaved={reload} />}
          {tab === "history" && <HistoryView data={data} onChange={reload} />}
        </>
      )}
      {versions.length === 0 && <BriefView data={data} onSaved={reload} />}

      <ReviseModal open={revise} onClose={() => setRevise(false)} onSubmit={(feedback, mode) => act("revise", () => api.post(`/items/${id}/generate`, { feedback, mode }), "Revision queued").then(() => setRevise(false))} />
      {current && <EditModal open={editing} onClose={() => setEditing(false)} initial={current.bodyMd} onSave={(bodyMd) => act("edit", () => api.put(`/items/${id}/version`, { bodyMd }), "Saved as a new version").then(() => setEditing(false))} />}
      <MarkPublishedModal open={markOpen} onClose={() => setMarkOpen(false)} onSave={(url) => act("mark", () => api.post(`/items/${id}/mark-published`, { url: url || null }), "Marked published").then(() => setMarkOpen(false))} />
      <Modal open={!!confirm} onClose={() => setConfirm(null)} title={confirm === "delete" ? "Delete this item?" : confirm === "publish" ? "Publish now?" : "Approve with problems?"}>
        <p className="text-[13px] text-muted">
          {confirm === "delete"
            ? "The item and its versions are removed. The idea it came from stays."
            : confirm === "publish"
              ? channel?.kind === "buffer"
                ? "Sends it to Buffer for publishing in about 3 minutes, regardless of the scheduled slot."
                : channel?.kind === "git_astro"
                  ? "Commits it to the site repo, pushes, deploys and checks it is live, right now."
                  : "Marks it ready to post now."
              : blocked
                ? "The gate flagged this draft. Approving overrides that."
                : `${fails.length} check(s) failed. Approving overrides them.`}
        </p>
        {needsForce && confirm !== "delete" && (
          <ul className="mt-2 list-disc pl-5 text-[12.5px] text-warn">
            {blocked && <li>{current?.meta.blocked_reason}</li>}
            {fails.map((f, i) => (
              <li key={i}>{f.message}</li>
            ))}
          </ul>
        )}
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="quiet" onClick={() => setConfirm(null)}>
            Cancel
          </Button>
          <Button
            variant={confirm === "delete" ? "danger" : "primary"}
            onClick={async () => {
              const c = confirm;
              setConfirm(null);
              if (c === "approve") await approve(true);
              else if (c === "publish") await publishNow(needsForce);
              else if (c === "delete") {
                await run("del", () => api.del(`/items/${id}`), "Deleted");
                go("");
              }
            }}
          >
            {confirm === "delete" ? "Delete" : confirm === "publish" ? "Publish now" : "Approve anyway"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}

function Header({ data, channels, onSaved }: { data: ItemDetail; channels: Channel[]; onSaved: () => void }) {
  const { item } = data;
  const [title, setTitle] = useState(item.title);
  const [when, setWhen] = useState(toLocalInput(item.scheduledFor));
  useEffect(() => {
    setTitle(item.title);
    setWhen(toLocalInput(item.scheduledFor));
  }, [item.title, item.scheduledFor]);
  const { run } = useAction();
  const patch = (body: Record<string, unknown>, ok: string) => run("patch", () => api.patch(`/items/${item.id}`, body), ok).then(onSaved);
  const locked = ["publishing", "published"].includes(item.status);
  return (
    <header className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-[12px] text-dim">
        <span className="rounded border border-line-strong px-1.5 py-px">{FORMAT_LABELS[item.format]}</span>
        <Pill status={item.status} />
        {item.publishedUrl && (
          <a className="text-accent-bright hover:underline" href={item.publishedUrl} target="_blank" rel="noreferrer">
            {item.publishedUrl}
          </a>
        )}
        {item.docUrl && (
          <a className="text-accent-bright hover:underline" href={item.docUrl} target="_blank" rel="noreferrer">
            Google Doc
          </a>
        )}
        {data.idea && <span>from: {data.idea.title.slice(0, 60)}</span>}
        {data.dependsOn && (
          <a className="hover:text-ink" href={`#/item/${data.dependsOn.id}`}>
            built from: {data.dependsOn.title.slice(0, 50)} ({data.dependsOn.status})
          </a>
        )}
      </div>
      <input
        className="w-full rounded-lg border border-transparent bg-transparent px-1 text-[22px] font-semibold tracking-tight hover:border-line focus:border-accent focus:outline-none"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onBlur={() => title.trim() && title !== item.title && patch({ title }, "Renamed")}
        disabled={locked}
        aria-label="Title"
      />
      <div className="flex flex-wrap items-end gap-3">
        <Field label="Publish at (PKT)">
          <input
            type="datetime-local"
            className={`${inputCls} w-56`}
            value={when}
            disabled={locked}
            onChange={(e) => setWhen(e.target.value)}
            onBlur={() => {
              const iso = fromLocalInput(when);
              if (iso !== item.scheduledFor) void patch({ scheduledFor: iso }, ["approved", "scheduled"].includes(item.status) ? "Moved: approve again for the new slot" : "Rescheduled");
            }}
          />
        </Field>
        <Field label="Channel">
          <select className={`${inputCls} w-56`} value={item.channelId ?? ""} disabled={locked} onChange={(e) => patch({ channelId: e.target.value || null }, "Channel changed")}>
            {channels
              .filter((c) => c.format === item.format)
              .map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
          </select>
        </Field>
        {item.scheduledFor && <span className="pb-2 text-[12px] text-dim">{ago(item.scheduledFor)}</span>}
      </div>
    </header>
  );
}

function DraftView({ item, version }: { item: ItemSummary; version: Version }) {
  if (item.format === "linkedin_post") return <LinkedInPreview text={version.bodyMd} meta={version.meta.meta} />;
  if (item.format === "li_newsletter") {
    const [issue, notes] = version.bodyMd.split("<!-- end issue -->");
    return (
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
        <Card className="px-6 py-5">
          <Markdown md={issue} />
        </Card>
        <div className="space-y-3 text-[13px]">
          {version.meta.meta?.share_text && (
            <Card className="px-4 py-3">
              <SectionTitle>Share text</SectionTitle>
              <p className="whitespace-pre-wrap">{version.meta.meta.share_text}</p>
            </Card>
          )}
          {notes && (
            <Card className="px-4 py-3">
              <SectionTitle>Publishing notes</SectionTitle>
              <Markdown md={notes} className="text-[12.5px]" />
            </Card>
          )}
        </div>
      </div>
    );
  }
  const { fm, body } = splitFrontmatter(version.bodyMd);
  const fields = (fm ?? "")
    .split(/\r?\n/)
    .map((l) => l.match(/^(\w+):\s*(.*)$/))
    .filter(Boolean) as RegExpMatchArray[];
  const pick = ["title", "seoTitle", "excerpt", "category", "primaryKeyword", "coverImage", "datePublished"];
  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
      <Card className="px-6 py-5">
        <h1 className="mb-2 text-[1.5rem] font-semibold leading-tight">{fields.find((f) => f[1] === "title")?.[2]?.replace(/^["']|["']$/g, "")}</h1>
        <Markdown md={body} />
      </Card>
      <Card className="h-fit px-4 py-3">
        <SectionTitle>Frontmatter</SectionTitle>
        <dl className="space-y-2 text-[12.5px]">
          {fields
            .filter((f) => pick.includes(f[1]))
            .map((f) => (
              <div key={f[1]}>
                <dt className="text-dim">{f[1]}</dt>
                <dd className="break-words">
                  {f[2].replace(/^["']|["']$/g, "")}
                  {f[1] === "excerpt" && <span className="ml-1 font-mono text-[11px] text-dim">({f[2].replace(/^["']|["']$/g, "").length} chars)</span>}
                  {f[1] === "seoTitle" && <span className="ml-1 font-mono text-[11px] text-dim">({f[2].replace(/^["']|["']$/g, "").length} chars)</span>}
                </dd>
              </div>
            ))}
        </dl>
      </Card>
    </div>
  );
}

function LinkedInPreview({ text, meta }: { text: string; meta?: Record<string, any> }) {
  const [expanded, setExpanded] = useState(false);
  const body = text.trim();
  // LinkedIn folds a post after roughly the first 210 characters or 3 lines.
  const lines = body.split("\n");
  let cut = body.length;
  if (body.length > 210) cut = 210;
  const threeLines = lines.slice(0, 3).join("\n").length;
  if (lines.length > 3) cut = Math.min(cut, threeLines);
  const chars = [...body].length;
  const copy = async () => {
    await navigator.clipboard.writeText(body);
    toast("Copied", "ok");
  };
  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,560px)_1fr]">
      <Card className="px-5 py-4">
        <div className="mb-3 flex items-center gap-2.5">
          <div className="size-10 rounded-full bg-s3" />
          <div>
            <div className="text-[13.5px] font-semibold">Aleem Ul Hassan</div>
            <div className="text-[11.5px] text-dim">Preview · folded at "see more"</div>
          </div>
        </div>
        <div className="whitespace-pre-wrap break-words text-[14px] leading-relaxed">
          {expanded || cut >= body.length ? (
            body
          ) : (
            <>
              {body.slice(0, cut)}
              <button className="text-dim hover:text-ink" onClick={() => setExpanded(true)}>
                ...see more
              </button>
            </>
          )}
        </div>
      </Card>
      <div className="space-y-3 text-[13px]">
        <div className="flex flex-wrap gap-2">
          <span className={`rounded-lg border px-3 py-1.5 font-mono text-[12px] ${chars > 3000 ? "border-neg/50 text-neg" : "border-line-strong text-muted"}`}>{chars} / 3000 chars</span>
          <Button onClick={copy}>Copy text</Button>
        </div>
        {meta && (
          <Card className="px-4 py-3">
            <dl className="grid grid-cols-[110px_1fr] gap-y-1.5 text-[12.5px]">
              {["pillar", "content_mode", "ingredients", "hashtags"].map((k) =>
                meta[k] && (Array.isArray(meta[k]) ? meta[k].length : true) ? (
                  <div key={k} className="contents">
                    <dt className="text-dim">{k.replace("_", " ")}</dt>
                    <dd>{Array.isArray(meta[k]) ? meta[k].join(", ") : String(meta[k])}</dd>
                  </div>
                ) : null,
              )}
            </dl>
          </Card>
        )}
      </div>
    </div>
  );
}

function NewsletterActions({ version, channel, onMark }: { version: Version; channel: Channel | null; onMark: () => void }) {
  const issue = version.bodyMd.split("<!-- end issue -->")[0];
  const copyRich = async () => {
    const html = renderMarkdown(issue);
    try {
      await navigator.clipboard.write([new ClipboardItem({ "text/html": new Blob([html], { type: "text/html" }), "text/plain": new Blob([issue], { type: "text/plain" }) })]);
      toast("Copied with formatting: paste into the LinkedIn article editor", "ok");
    } catch {
      await navigator.clipboard.writeText(issue);
      toast("Copied as plain text (this browser blocked rich copy)", "info");
    }
  };
  return (
    <>
      <Button variant="primary" onClick={copyRich}>
        Copy rich text
      </Button>
      <Button onClick={() => window.open(channel?.config.linkedinUrl || "https://www.linkedin.com/article/new/", "_blank")}>Open LinkedIn</Button>
      <Button onClick={onMark}>Mark published</Button>
    </>
  );
}

function FilesView({ data, version, onChange }: { data: ItemDetail; version: Version; onChange: () => void }) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [kind, setKind] = useState<"image" | "cover">(data.item.format === "linkedin_post" ? "image" : "cover");
  const { busy, run } = useAction();
  const upload = async (f: File) => {
    const form = new FormData();
    form.append("file", f);
    form.append("kind", kind);
    await run("up", () => api.upload(`/items/${data.item.id}/assets`, form), "Uploaded");
    onChange();
  };
  const images = version.files.images ?? [];
  return (
    <div className="space-y-5">
      <section>
        <SectionTitle
          right={
            <div className="flex items-center gap-2">
              {data.item.format !== "linkedin_post" && (
                <select className="rounded-md border border-line-strong bg-s2 px-2 py-1 text-[12px]" value={kind} onChange={(e) => setKind(e.target.value as "image" | "cover")}>
                  <option value="cover">Cover</option>
                  <option value="image">Inline image</option>
                </select>
              )}
              <Button busy={busy === "up"} onClick={() => fileInput.current?.click()}>
                Upload image
              </Button>
              <input ref={fileInput} type="file" accept="image/png,image/jpeg,image/webp,image/gif" hidden onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
            </div>
          }
        >
          {data.item.format === "linkedin_post" ? "Post images (attached in Buffer)" : "Images"}
        </SectionTitle>
        {data.assets.length + images.length === 0 ? (
          <Empty>{data.item.format === "linkedin_post" ? "Generate the infographic from the prompt below in Gemini, then upload it here so it posts with the text." : "No images yet."}</Empty>
        ) : (
          <div className="flex flex-wrap gap-3">
            {data.assets.map((a) => (
              <figure key={a.id} className="w-44 overflow-hidden rounded-lg border border-line bg-s2">
                <img src={fileUrl(a.localPath)} alt={a.alt ?? ""} className="aspect-square w-full object-cover" />
                <figcaption className="flex items-center justify-between px-2 py-1 text-[11px] text-dim">
                  {a.kind}
                  <button className="text-neg hover:underline" onClick={() => run("rm", () => api.del(`/items/${data.item.id}/assets/${a.id}`)).then(onChange)}>
                    remove
                  </button>
                </figcaption>
              </figure>
            ))}
            {images.map((p) => (
              <figure key={p} className="w-44 overflow-hidden rounded-lg border border-line bg-s2">
                <img src={fileUrl(p)} alt="" className="aspect-square w-full object-cover" />
                <figcaption className="truncate px-2 py-1 text-[11px] text-dim">{p.split(/[\\/]/).pop()} (generated)</figcaption>
              </figure>
            ))}
          </div>
        )}
      </section>
      {version.extraFiles.map((f) => (
        <section key={f.name}>
          <SectionTitle
            right={
              <Button variant="quiet" onClick={() => navigator.clipboard.writeText(f.content).then(() => toast("Copied", "ok"))}>
                Copy
              </Button>
            }
          >
            {f.name}
          </SectionTitle>
          <Card className="max-h-[420px] overflow-y-auto px-4 py-3">
            {/\.md$/.test(f.name) ? <Markdown md={f.content} className="text-[13px]" /> : <pre className="whitespace-pre-wrap font-mono text-[12px]">{f.content}</pre>}
          </Card>
        </section>
      ))}
      {!!version.meta.sources?.length && (
        <section>
          <SectionTitle>Sources ({version.meta.sources.length})</SectionTitle>
          <ul className="space-y-1 text-[13px]">
            {version.meta.sources.map((s, i) => (
              <li key={i} className="truncate">
                <a href={s.url} target="_blank" rel="noreferrer" className="text-accent-bright hover:underline">
                  {s.title || s.url}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
      {version.files.runDir && <p className="font-mono text-[11px] text-dim">Run folder: {version.files.runDir}</p>}
    </div>
  );
}

function ChecksView({ version }: { version: Version }) {
  if (!version.checks.length) return <Empty>No checks recorded for this version.</Empty>;
  const order = { fail: 0, warn: 1, pass: 2 };
  return (
    <ul className="space-y-1.5">
      {[...version.checks]
        .sort((a, b) => order[a.level] - order[b.level])
        .map((c, i) => (
          <li key={i} className="flex items-start gap-3 rounded-lg border border-line bg-s1 px-3 py-2 text-[13px]">
            <span className={`mt-0.5 w-10 shrink-0 font-mono text-[11px] font-semibold uppercase ${c.level === "fail" ? "text-neg" : c.level === "warn" ? "text-warn" : "text-pos"}`}>{c.level}</span>
            <span>{c.message}</span>
          </li>
        ))}
    </ul>
  );
}

function BriefView({ data, onSaved }: { data: ItemDetail; onSaved: () => void }) {
  const b = data.item.brief ?? {};
  const [form, setForm] = useState({ description: b.description ?? "", reference: b.reference ?? "", contentMode: b.contentMode ?? "", pillar: b.pillar ?? "", notes: b.notes ?? "" });
  const items = useApi<ItemSummary[]>(data.item.format === "li_newsletter" ? "/items" : null, { live: false }).data ?? [];
  const { busy, run } = useAction();
  const dirty = JSON.stringify(form) !== JSON.stringify({ description: b.description ?? "", reference: b.reference ?? "", contentMode: b.contentMode ?? "", pillar: b.pillar ?? "", notes: b.notes ?? "" });
  return (
    <Card className="space-y-3 px-5 py-4">
      <SectionTitle>Brief the skill reads</SectionTitle>
      <Field label="Description">
        <textarea className={`${inputCls} min-h-[90px]`} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
      </Field>
      <div className="grid gap-3 md:grid-cols-2">
        <Field label="Reference">
          <input className={inputCls} value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} />
        </Field>
        <Field label="Content mode">
          <select className={inputCls} value={form.contentMode} onChange={(e) => setForm({ ...form, contentMode: e.target.value })}>
            <option value="">Let the skill decide</option>
            {["News/Analysis", "Opinion/POV", "Personal Story", "Tutorial/How-to"].map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </Field>
        <Field label="Pillar">
          <select className={inputCls} value={form.pillar} onChange={(e) => setForm({ ...form, pillar: e.target.value })}>
            <option value="">Let the skill decide</option>
            {["AI & Automation", "Founder Journey", "Tech Insights", "Young Builder"].map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </Field>
        {data.item.format === "li_newsletter" && (
          <Field label="Built from blog">
            <select
              className={inputCls}
              value={data.item.dependsOnItemId ?? ""}
              onChange={(e) => run("dep", () => api.patch(`/items/${data.item.id}`, { dependsOnItemId: e.target.value || null }), "Saved").then(onSaved)}
            >
              <option value="">None (topic issue)</option>
              {items
                .filter((i) => i.format === "personal_blog" || i.format === "agency_blog")
                .slice(0, 60)
                .map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.title.slice(0, 70)}
                  </option>
                ))}
            </select>
          </Field>
        )}
      </div>
      <Field label="Notes for the writer" hint="First-hand details, numbers, what you want it to say. The run reads these.">
        <textarea className={`${inputCls} min-h-[70px]`} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      </Field>
      <div className="flex justify-end">
        <Button variant="primary" disabled={!dirty} busy={busy === "brief"} onClick={() => run("brief", () => api.patch(`/items/${data.item.id}`, { brief: form }), "Brief saved").then(onSaved)}>
          Save brief
        </Button>
      </div>
    </Card>
  );
}

function HistoryView({ data, onChange }: { data: ItemDetail; onChange: () => void }) {
  const { run } = useAction();
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <section>
        <SectionTitle>Runs</SectionTitle>
        <ul className="space-y-1.5 text-[13px]">
          {data.runs.map((r) => (
            <li key={r.id}>
              <a href={`#/runs/${r.id}`} className="flex items-center justify-between gap-2 rounded-lg border border-line bg-s1 px-3 py-2 hover:border-line-strong">
                <span className="font-mono text-[12px] text-dim">{fmtDateTime(r.startedAt)}</span>
                <span className="font-mono text-[12px] text-dim">
                  {r.numTurns ?? "-"} turns · {r.durationMs ? `${Math.round(r.durationMs / 60000)}m` : "-"}
                </span>
                <Pill status={r.status} />
              </a>
            </li>
          ))}
          {!data.runs.length && <li className="text-dim">No runs yet.</li>}
        </ul>
      </section>
      <section>
        <SectionTitle>Jobs</SectionTitle>
        <ul className="space-y-1.5 text-[13px]">
          {data.jobs.map((j) => (
            <li key={j.id} className="rounded-lg border border-line bg-s1 px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[12px]">{j.type}</span>
                <span className="text-[12px] text-dim">{fmtDateTime(j.dueAt)}</span>
                <Pill status={j.status} />
              </div>
              {j.lastError && <p className="mt-1 whitespace-pre-wrap text-[12px] text-neg">{j.lastError.slice(0, 600)}</p>}
              {j.status === "needs_check" && (
                <div className="mt-2 flex gap-2">
                  <Button onClick={() => run("r", () => api.post(`/jobs/${j.id}/resolve`, { outcome: "done" }), "Marked done").then(onChange)}>It went through</Button>
                  <Button onClick={() => run("r", () => api.post(`/jobs/${j.id}/resolve`, { outcome: "retry" }), "Retrying").then(onChange)}>It did not, retry</Button>
                </div>
              )}
              {["failed", "missed"].includes(j.status) && (
                <Button className="mt-2" onClick={() => run("r", () => api.post(`/jobs/${j.id}/retry`, {}), "Retrying").then(onChange)}>
                  Retry job
                </Button>
              )}
            </li>
          ))}
          {!data.jobs.length && <li className="text-dim">No jobs yet.</li>}
        </ul>
      </section>
      <section className="lg:col-span-2">
        <SectionTitle>Activity</SectionTitle>
        <ul className="space-y-1 font-mono text-[12px] text-muted">
          {data.events.map((e) => (
            <li key={e.id} className="flex gap-3">
              <span className="w-36 shrink-0 text-dim">{fmtDateTime(e.ts)}</span>
              <span className="w-20 shrink-0 text-dim">{e.actor}</span>
              <span>
                {e.type}
                {e.type === "publish.log" && e.data?.message ? `: ${e.data.message}` : ""}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function ReviseModal({ open, onClose, onSubmit }: { open: boolean; onClose: () => void; onSubmit: (feedback: string, mode: "fresh" | "resume") => void }) {
  const [feedback, setFeedback] = useState("");
  const [mode, setMode] = useState<"fresh" | "resume">("fresh");
  useEffect(() => {
    if (open) setFeedback("");
  }, [open]);
  return (
    <Modal open={open} onClose={onClose} title="Revise with feedback">
      <Field label="What should change?" hint="The run revises, it does not rewrite: everything you do not mention is kept.">
        <textarea className={`${inputCls} min-h-[140px]`} value={feedback} onChange={(e) => setFeedback(e.target.value)} autoFocus placeholder="Open with the 3 unusable takes. Cut the second section. Name the actual tool." />
      </Field>
      <label className="mt-3 flex items-center gap-2 text-[12.5px] text-muted">
        <input type="checkbox" checked={mode === "resume"} onChange={(e) => setMode(e.target.checked ? "resume" : "fresh")} />
        Continue the original session (keeps its research in context; uses more of the plan)
      </label>
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="quiet" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" disabled={!feedback.trim()} onClick={() => onSubmit(feedback.trim(), mode)}>
          Queue revision
        </Button>
      </div>
    </Modal>
  );
}

function EditModal({ open, onClose, initial, onSave }: { open: boolean; onClose: () => void; initial: string; onSave: (body: string) => void }) {
  const [body, setBody] = useState(initial);
  useEffect(() => {
    if (open) setBody(initial);
  }, [open, initial]);
  const changed = useMemo(() => body !== initial, [body, initial]);
  return (
    <Modal open={open} onClose={onClose} title="Edit the draft" wide>
      <textarea className={`${inputCls} min-h-[55vh] font-mono text-[12.5px] leading-relaxed`} value={body} onChange={(e) => setBody(e.target.value)} spellCheck />
      <div className="mt-3 flex items-center justify-between">
        <span className="font-mono text-[11px] text-dim">{[...body].length} chars · saved as a new version, checks re-run</span>
        <div className="flex gap-2">
          <Button variant="quiet" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" disabled={!changed} onClick={() => onSave(body)}>
            Save version
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function MarkPublishedModal({ open, onClose, onSave }: { open: boolean; onClose: () => void; onSave: (url: string) => void }) {
  const [url, setUrl] = useState("");
  useEffect(() => {
    if (open) setUrl("");
  }, [open]);
  return (
    <Modal open={open} onClose={onClose} title="Mark as published">
      <Field label="Live URL" hint="Optional, but it links the calendar, the sheet mirror and the newsletter issue log to the real post.">
        <input className={inputCls} value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://www.linkedin.com/pulse/..." autoFocus />
      </Field>
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="quiet" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={() => onSave(url.trim())}>
          Mark published
        </Button>
      </div>
    </Modal>
  );
}

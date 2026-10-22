import { useEffect, useMemo, useState } from "react";
import { api, FORMAT_LABELS, FORMATS, type Channel, type Format, type Idea, type ItemSummary } from "../lib/api";
import { atPkt, dayKey, fmtDateTime, fromLocalInput, toLocalInput } from "../lib/time";
import { go, toast, useApi } from "../lib/hooks";
import { Button, Field, inputCls, Modal } from "./ui";

/**
 * Put an idea (or a fresh title) on the calendar: format, channel, slot, and the
 * brief fields the skills read (description, reference, content mode, pillar).
 */
export function PlanDialog({
  open,
  onClose,
  idea,
  initialFormat,
  initialDay,
}: {
  open: boolean;
  onClose: () => void;
  idea?: Idea | null;
  initialFormat?: Format;
  initialDay?: string;
}) {
  const channels = useApi<Channel[]>(open ? "/channels" : null, { live: false }).data ?? [];
  const items = useApi<ItemSummary[]>(open ? "/items" : null, { live: false }).data ?? [];
  const shortlist = useApi<Idea[]>(open && !idea ? "/ideas?status=shortlisted" : null, { live: false }).data ?? [];
  const [format, setFormat] = useState<Format>(initialFormat ?? "linkedin_post");
  const [pickedIdea, setPickedIdea] = useState<Idea | null>(idea ?? null);
  const [title, setTitle] = useState(idea?.title ?? "");
  const [when, setWhen] = useState("");
  const [channelId, setChannelId] = useState<string>("");
  const [description, setDescription] = useState(idea?.summary ?? "");
  const [reference, setReference] = useState(idea?.url ?? "");
  const [contentMode, setContentMode] = useState("");
  const [pillar, setPillar] = useState("");
  const [dependsOn, setDependsOn] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    setFormat(initialFormat ?? "linkedin_post");
    setPickedIdea(idea ?? null);
    setTitle(idea?.title ?? "");
    setDescription(idea?.summary ?? "");
    setReference(idea?.url ?? "");
    setWhen(toLocalInput(atPkt(initialDay ?? dayKey(new Date(Date.now() + 2 * 86_400_000).toISOString()), "09:00")));
    setContentMode("");
    setPillar("");
    setDependsOn("");
  }, [open, idea, initialFormat, initialDay]);

  const formatChannels = channels.filter((c) => c.format === format && c.enabled);
  useEffect(() => {
    setChannelId(formatChannels[0]?.id ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [format, channels.length]);

  const blogs = useMemo(() => items.filter((i) => (i.format === "personal_blog" || i.format === "agency_blog") && !["skipped"].includes(i.status)).slice(0, 40), [items]);

  const pick = (i: Idea) => {
    setPickedIdea(i);
    setTitle(i.title);
    setDescription(i.summary ?? "");
    setReference(i.url ?? "");
  };

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        format,
        channelId: channelId || null,
        scheduledFor: fromLocalInput(when),
        title: title.trim(),
        brief: { description, reference, contentMode, pillar },
        dependsOnItemId: format === "li_newsletter" && dependsOn ? dependsOn : null,
      };
      const item = pickedIdea
        ? await api.post<ItemSummary>(`/ideas/${pickedIdea.id}/plan`, body)
        : await api.post<ItemSummary>("/items", body);
      toast(`Planned for ${fmtDateTime(item.scheduledFor)}`, "ok");
      onClose();
      go(`item/${item.id}`);
    } catch (e) {
      toast((e as Error).message, "err");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={pickedIdea ? "Plan this idea" : "Plan a piece"} wide>
      <div className="grid gap-4 md:grid-cols-[1fr_220px]">
        <div className="space-y-3">
          {!idea && shortlist.length > 0 && !pickedIdea && (
            <Field label="From the shortlist">
              <div className="max-h-40 space-y-1 overflow-y-auto rounded-lg border border-line bg-s2 p-1">
                {shortlist.slice(0, 30).map((i) => (
                  <button key={i.id} onClick={() => pick(i)} className="block w-full truncate rounded-md px-2 py-1.5 text-left text-[13px] text-muted hover:bg-s3 hover:text-ink">
                    {i.title}
                  </button>
                ))}
              </div>
            </Field>
          )}
          <Field label="Title / topic">
            <input className={inputCls} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="What is this piece about?" autoFocus />
          </Field>
          <Field label="Description" hint="Angle, what to cover, anything the skill should know">
            <textarea className={`${inputCls} min-h-[90px]`} value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <Field label="Reference" hint="A URL, a skill name, or a source note">
            <input className={inputCls} value={reference} onChange={(e) => setReference(e.target.value)} />
          </Field>
        </div>
        <div className="space-y-3">
          <Field label="Format">
            <select className={inputCls} value={format} onChange={(e) => setFormat(e.target.value as Format)}>
              {FORMATS.map((f) => (
                <option key={f} value={f}>
                  {FORMAT_LABELS[f]}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Channel">
            <select className={inputCls} value={channelId} onChange={(e) => setChannelId(e.target.value)}>
              {formatChannels.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Publish at (PKT)">
            <input type="datetime-local" className={inputCls} value={when} onChange={(e) => setWhen(e.target.value)} />
          </Field>
          <Field label="Content mode">
            <select className={inputCls} value={contentMode} onChange={(e) => setContentMode(e.target.value)}>
              <option value="">Let the skill decide</option>
              {["News/Analysis", "Opinion/POV", "Personal Story", "Tutorial/How-to"].map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </Field>
          <Field label="Pillar">
            <select className={inputCls} value={pillar} onChange={(e) => setPillar(e.target.value)}>
              <option value="">Let the skill decide</option>
              {["AI & Automation", "Founder Journey", "Tech Insights", "Young Builder"].map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </Field>
          {format === "li_newsletter" && (
            <Field label="Built from blog" hint="Waits for that blog to go live, then links to it">
              <select className={inputCls} value={dependsOn} onChange={(e) => setDependsOn(e.target.value)}>
                <option value="">None (topic issue)</option>
                {blogs.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.title.slice(0, 60)}
                  </option>
                ))}
              </select>
            </Field>
          )}
        </div>
      </div>
      <div className="mt-5 flex justify-end gap-2 border-t border-line pt-4">
        <Button variant="quiet" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" busy={busy} disabled={!title.trim()} onClick={submit}>
          Put on calendar
        </Button>
      </div>
    </Modal>
  );
}

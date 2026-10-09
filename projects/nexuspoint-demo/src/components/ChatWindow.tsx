"use client";
import { useEffect, useRef, useState } from "react";
import { T, type Lang } from "@/lib/i18n";
import type { Choice } from "@/lib/healthcare-types";

type Msg = {
  role: "customer" | "business";
  content: string;
  at: string;
  meta?: string;
  source?: string;
  cards?: Choice[];
};

export function visitorId(slug: string): string {
  const k = `np-visitor-${slug}`;
  try {
    const v = localStorage.getItem(k);
    if (v) return v;
    const id = crypto.randomUUID();
    localStorage.setItem(k, id);
    return id;
  } catch {
    return `anon-${Math.random().toString(36).slice(2)}`;
  }
}

const time = (d = new Date()) =>
  d
    .toLocaleTimeString("en-US", {
      timeZone: "Asia/Karachi",
      hour: "numeric",
      minute: "2-digit",
    })
    .toLowerCase();

export default function ChatWindow({
  slug,
  token,
  name,
  lang,
  prompts,
  snapshot,
  onSent,
  healthcare = false,
  restaurant = false,
  school = false,
}: {
  slug: string;
  token: string;
  name: string;
  lang: Lang;
  prompts: string[];
  snapshot?: { role: "customer" | "business"; content: string }[] | null;
  onSent?: () => void;
  healthcare?: boolean;
  restaurant?: boolean;
  school?: boolean;
}) {
  const t = T[lang];
  const [msgs, setMsgs] = useState<Msg[]>(() =>
    (snapshot ?? []).map((m) => ({ ...m, at: "9:41 pm" })),
  );
  const [busy, setBusy] = useState(false);
  const [text, setText] = useState("");
  const [staffMode, setStaffMode] = useState(false),
    [error, setError] = useState("");
  const busyRef = useRef(false);
  const box = useRef<HTMLDivElement>(null);
  const visitor = useRef<string>("");

  useEffect(() => {
    if (snapshot) return;
    visitor.current = visitorId(slug);
    let live = true;
    const restore = async () => {
      if (busyRef.current || document.visibilityState !== "visible") return;
      try {
        const r = await fetch(
          `/api/chat?slug=${slug}&t=${token}&visitor=${visitor.current}`,
          { cache: "no-store" },
        );
        const d = await r.json();
        if (!r.ok) throw new Error(d.error ?? "Chat unavailable");
        if (live && !busyRef.current) {
          setStaffMode(d.staffMode ?? false);
          if (Array.isArray(d.messages))
            setMsgs(
              d.messages.map((m: Msg) => ({ ...m, at: time(new Date(m.at)) })),
            );
          setError("");
        }
      } catch {
        if (live)
          setError(
            lang === "ur"
              ? "گفتگو لوڈ نہیں ہو سکی۔ دوبارہ کوشش کریں۔"
              : "Chat could not load. Please try again.",
          );
      }
    };
    restore();
    const id = setInterval(restore, 2000);
    return () => {
      live = false;
      clearInterval(id);
    };
  }, [slug, token, snapshot]);

  useEffect(() => {
    box.current?.scrollTo({
      top: box.current.scrollHeight,
      behavior: "smooth",
    });
  }, [msgs, busy]);

  async function send(raw: string, choice?: Choice) {
    const body = raw.trim();
    if (!body || busy || snapshot) return;
    setText("");
    setMsgs((m) => [...m, { role: "customer", content: body, at: time() }]);
    setBusy(true);
    busyRef.current = true;
    setError("");
    const started = performance.now();
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          slug,
          t: token,
          visitor: visitor.current,
          text: body,
          choice,
        }),
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error ?? "Could not send");
      const secs = ((performance.now() - started) / 1000).toFixed(1);
      if (d.reply)
        setMsgs((m) => [
          ...m,
          {
            role: "business",
            content: d.reply,
            at: time(),
            meta: `${secs}s`,
            source: d.source,
            cards: d.cards ?? [],
          },
        ]);
      if (d.source === "staff") setStaffMode(true);
      onSent?.();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : lang === "ur"
            ? "کنکشن کا مسئلہ، دوبارہ بھیجیں۔"
            : "Connection problem, please send again.",
      );
      setText(body);
    } finally {
      setBusy(false);
      busyRef.current = false;
    }
  }

  return (
    <>
      <div className="chat-bar">
        <span className="av" aria-hidden="true">
          {name.slice(0, 1)}
        </span>
        <span>
          <span className="chat-name" style={{ display: "block" }}>
            {name}
          </span>
          <span className="chat-status">
            {staffMode
              ? lang === "ur"
                ? "عملہ جواب دے رہا ہے"
                : "Staff is replying"
              : t.online}
          </span>
        </span>
        {healthcare && (
          <a
            className="chat-portal-link"
            href={`/d/${slug}/patient?t=${encodeURIComponent(token)}${lang === "ur" ? "&lang=ur" : ""}`}
          >
            {lang === "ur" ? "مریض پورٹل" : "Patient portal"}
          </a>
        )}
        {restaurant && <a className="chat-portal-link" href={`/d/${slug}/customer?t=${encodeURIComponent(token)}${lang==='ur'?'&lang=ur':''}`}>{lang==='ur'?'کسٹمر پورٹل':'Customer portal'}</a>}
        {school && <a className="chat-portal-link" href={`/d/${slug}/parent?t=${encodeURIComponent(token)}${lang==='ur'?'&lang=ur':''}`}>{lang==='ur'?'والدین پورٹل':'Parent portal'}</a>}
      </div>
      <div className="msgs" ref={box} aria-live="polite">
        {msgs.length === 0 && (
          <div className="prompts" style={{ marginTop: "auto" }}>
            {prompts.map((p) => (
              <button key={p} type="button" onClick={() => send(p)}>
                {p}
              </button>
            ))}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={`bub ${m.role}`}>
            <p dir="auto">{m.content}</p>
            {!!m.cards?.length && i === msgs.length - 1 && (
              <div className="chat-choices">
                {m.cards.map((c, j) => (
                  <button
                    key={`${c.kind}-${c.value}-${j}`}
                    type="button"
                    disabled={busy || !!snapshot}
                    onClick={() => send(c.label, c)}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            )}
            <span className="tm">
              {m.source === "staff"
                ? lang === "ur"
                  ? "عملہ · "
                  : "Staff · "
                : ""}
              {m.meta ? `${m.at} · ${m.meta}` : m.at}
            </span>
          </div>
        ))}
        {busy && (
          <span className="typing" aria-label="typing">
            <i />
            <i />
            <i />
          </span>
        )}
      </div>
      {error && (
        <p className="chat-error" role="alert">
          {error}
        </p>
      )}
      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          send(text);
        }}
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t.typeHere}
          aria-label={t.typeHere}
          dir="auto"
          disabled={!!snapshot}
        />
        <button type="submit" aria-label={t.send} disabled={busy || !!snapshot}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M4 12 20 4l-6 16-3-7-7-1Z" />
          </svg>
        </button>
      </form>
    </>
  );
}

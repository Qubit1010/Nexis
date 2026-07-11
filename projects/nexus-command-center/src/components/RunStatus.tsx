import { useEffect, useState } from "react";
import { api } from "../api";
import { useStore } from "../store";

function fmtElapsed(startedIso: string, now: number): string {
  const s = Math.max(0, Math.floor((now - Date.parse(startedIso)) / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

const EXIT_COLOR: Record<string, string> = {
  ok: "var(--np-ok)",
  timeout: "var(--np-warn)",
  error: "var(--np-err)",
  killed: "var(--np-err)",
};

/**
 * The live run cluster (running / ceiling lock / last run), shared by the
 * Deck tab and the Console footer on other tabs. Reads deck state from the
 * store (Console owns the poll); handles the ceiling acknowledge itself.
 */
export default function RunStatus({ err }: { err?: string | null }) {
  const deck = useStore((s) => s.deck);
  const setDeck = useStore((s) => s.setDeck);
  const [now, setNow] = useState(Date.now());
  const [ackErr, setAckErr] = useState<string | null>(null);
  const running = !!deck?.running;

  useEffect(() => {
    if (!running) return;
    const iv = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(iv);
  }, [running]);

  const ack = async () => {
    try {
      await api.ack();
      setDeck(await api.status());
    } catch {
      setAckErr("Acknowledge failed.");
    }
  };

  const shownErr = err ?? ackErr;

  return (
    <div className="ml-auto flex items-center gap-4">
      {shownErr && (
        <span className="text-[13px]" style={{ color: "var(--np-err)" }}>
          {shownErr}
        </span>
      )}

      {running && deck?.current && (
        <span className="flex items-center gap-2">
          <span
            className="np-pulse inline-block h-2.5 w-2.5 rounded-full"
            style={{ background: "var(--np-blue)" }}
          />
          <span className="text-[13px]">{deck.current.label}</span>
          <span className="np-mono" style={{ color: "var(--np-fog)" }}>
            {fmtElapsed(deck.current.started, now)}
          </span>
        </span>
      )}

      {deck?.locked && (
        <span className="flex items-center gap-3">
          <span className="text-[13px]" style={{ color: "var(--np-warn)" }}>
            Last run cost ${(deck.last?.cost_usd ?? 0).toFixed(2)} — over its ceiling, console locked
          </span>
          <button className="np-btn-ghost" onClick={ack}>
            Acknowledge
          </button>
        </span>
      )}

      {!running && deck?.last && !deck.locked && (
        <span className="flex items-center gap-2" title={deck.last.result_file ?? undefined}>
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ background: EXIT_COLOR[deck.last.exit] ?? "var(--np-fog)" }}
          />
          <span className="np-mono" style={{ color: "var(--np-fog)" }}>
            {deck.last.label} · ${deck.last.cost_usd.toFixed(4)} ·{" "}
            {Math.round(deck.last.duration_ms / 1000)}s · {deck.last.exit}
          </span>
        </span>
      )}
    </div>
  );
}

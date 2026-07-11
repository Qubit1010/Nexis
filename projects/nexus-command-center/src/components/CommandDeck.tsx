import { useState } from "react";
import { api, ApiError, type CommandInfo } from "../api";
import { useStore } from "../store";
import ConfirmModal from "./ConfirmModal.tsx";
import RunStatus from "./RunStatus.tsx";

/**
 * Deck tab content: read-profile preset buttons + the live run cluster.
 * The footer chrome and the status poll live in Console.
 */
export default function CommandDeck() {
  const commands = useStore((s) => s.commands);
  const deck = useStore((s) => s.deck);
  const setDeck = useStore((s) => s.setDeck);
  const [pending, setPending] = useState<CommandInfo | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const running = !!deck?.running;

  const run = async (cmd: CommandInfo) => {
    setPending(null);
    setErr(null);
    try {
      await api.run(cmd.id);
      setDeck(await api.status());
    } catch (e) {
      if (e instanceof ApiError) {
        const msg: Record<string, string> = {
          RUN_IN_PROGRESS: "A run is already in progress.",
          CEILING_LOCKED: "Deck is locked — acknowledge the over-ceiling run first.",
          UNKNOWN_COMMAND: "Unknown command preset.",
        };
        setErr(msg[e.code] ?? e.message);
      } else {
        setErr("Command failed to start.");
      }
    }
  };

  const ceiling = deck?.ceilings.read ?? 0.5;

  return (
    <>
      {commands.map((c) => (
        <button
          key={c.id}
          className="np-btn-ghost"
          disabled={running || !!deck?.locked}
          title={c.description}
          onClick={() => setPending(c)}
        >
          {c.label}
        </button>
      ))}
      {commands.length === 0 && (
        <span className="np-mono opacity-50">no presets — check commands.json</span>
      )}

      <RunStatus err={err} />

      {pending && (
        <ConfirmModal
          title={pending.label}
          description={pending.description}
          note={`read-only run · max $${ceiling.toFixed(2)} · killed past 5:00 · output → vault/raw/command-center/`}
          onCancel={() => setPending(null)}
          onConfirm={() => run(pending)}
        />
      )}
    </>
  );
}

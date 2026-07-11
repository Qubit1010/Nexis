import { useEffect, useState } from "react";
import { api, ApiError, type SkillActionInfo } from "../api";
import { useStore } from "../store";
import ConfirmModal from "./ConfirmModal.tsx";

const fieldStyle = {
  background: "rgba(11,11,11,0.7)",
  border: "1px solid var(--np-hairline)",
} as const;

/**
 * Skills tab: curated quick-actions (act profile — these runs can write files
 * and create Docs). Pick an action, fill its inputs, confirm, run. Same
 * mutex/ceiling as the deck, so one run at a time across the whole console.
 */
export default function SkillsPanel() {
  const actions = useStore((s) => s.skillActions);
  const deck = useStore((s) => s.deck);
  const setDeck = useStore((s) => s.setDeck);
  const [active, setActive] = useState<SkillActionInfo | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [confirming, setConfirming] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const running = !!deck?.running;
  const locked = !!deck?.locked;

  const pick = (a: SkillActionInfo) => {
    setActive(a);
    setValues({});
    setErr(null);
  };

  // Graph -> cockpit: SidePanel's "Run this skill" preselects the action.
  const focusActionId = useStore((s) => s.focusActionId);
  const setFocusAction = useStore((s) => s.setFocusAction);
  useEffect(() => {
    if (!focusActionId) return;
    const a = actions.find((x) => x.id === focusActionId);
    if (a) pick(a);
    setFocusAction(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusActionId, actions]);

  const canRun =
    !!active && !running && !locked && active.inputs.every((i) => (values[i.name] ?? "").trim());

  const run = async () => {
    if (!active) return;
    setConfirming(false);
    setErr(null);
    try {
      await api.runSkillAction(active.id, values);
      setDeck(await api.status());
    } catch (e) {
      if (e instanceof ApiError) {
        const msg: Record<string, string> = {
          RUN_IN_PROGRESS: "A run is already in progress.",
          CEILING_LOCKED: "Console is locked — acknowledge the over-ceiling run first.",
          MISSING_INPUT: "Fill every field before running.",
          INPUT_TOO_LONG: "An input is too long (6000 chars max).",
          UNKNOWN_ACTION: "Unknown skill action.",
        };
        setErr(msg[e.code] ?? e.message);
      } else {
        setErr("Action failed to start.");
      }
    }
  };

  const lastForActive = active && deck?.last?.run_id.endsWith(active.id) ? deck.last : null;

  return (
    <div className="flex h-full">
      <aside
        className="w-80 shrink-0 space-y-2 overflow-y-auto p-4"
        style={{ borderRight: "1px solid var(--np-hairline)" }}
      >
        <span
          className="block px-1 pb-1 text-[11px] uppercase"
          style={{ color: "var(--np-fog)", letterSpacing: "0.22em" }}
        >
          Skill actions
        </span>
        {actions.map((a) => (
          <button
            key={a.id}
            className="np-panel block w-full p-3 text-left"
            style={active?.id === a.id ? { borderColor: "var(--np-blue)" } : undefined}
            onClick={() => pick(a)}
          >
            <div className="text-[14px]">{a.label}</div>
            <div className="mt-0.5 text-xs" style={{ color: "var(--np-fog)" }}>
              {a.description}
            </div>
          </button>
        ))}
        {actions.length === 0 && (
          <span className="np-mono opacity-50">no actions — check skill-actions.json</span>
        )}
      </aside>

      <div className="min-w-0 flex-1 overflow-y-auto p-5">
        {!active ? (
          <div className="flex h-full items-center justify-center">
            <span className="np-mono" style={{ color: "var(--np-fog)" }}>
              pick an action to run
            </span>
          </div>
        ) : (
          <div className="max-w-2xl">
            <h3 className="np-display text-xl">{active.label}</h3>
            <p className="mt-1 mb-4 text-sm" style={{ color: "var(--np-fog)" }}>
              {active.description}
            </p>

            {active.inputs.map((input) => (
              <label key={input.name} className="mb-4 block">
                <span className="mb-1 block text-[13px]" style={{ color: "var(--np-fog)" }}>
                  {input.label}
                </span>
                {input.multiline ? (
                  <textarea
                    className="w-full rounded-md p-3 text-sm"
                    style={fieldStyle}
                    rows={8}
                    placeholder={input.placeholder}
                    value={values[input.name] ?? ""}
                    onChange={(e) => setValues((v) => ({ ...v, [input.name]: e.target.value }))}
                  />
                ) : (
                  <input
                    className="w-full rounded-md p-3 text-sm"
                    style={fieldStyle}
                    placeholder={input.placeholder}
                    value={values[input.name] ?? ""}
                    onChange={(e) => setValues((v) => ({ ...v, [input.name]: e.target.value }))}
                  />
                )}
              </label>
            ))}

            <div className="flex items-center gap-4">
              <button className="np-btn-primary" disabled={!canRun} onClick={() => setConfirming(true)}>
                Run
              </button>
              <span className="np-mono text-xs" style={{ color: "var(--np-fog)" }}>
                headless with write access · max ${(deck?.ceilings.act ?? 1).toFixed(2)} · 10:00 cap ·
                record → vault/raw/command-center/
              </span>
            </div>

            {err && (
              <p className="mt-3 text-[13px]" style={{ color: "var(--np-err)" }}>
                {err}
              </p>
            )}
            {running && deck?.current && (
              <p className="np-mono mt-3 text-xs" style={{ color: "var(--np-fog)" }}>
                running: {deck.current.label}…
              </p>
            )}
            {lastForActive && !running && (
              <p
                className="np-mono mt-3 text-xs"
                style={{ color: "var(--np-fog)" }}
                title={lastForActive.result_file ?? undefined}
              >
                last: ${lastForActive.cost_usd.toFixed(4)} ·{" "}
                {Math.round(lastForActive.duration_ms / 1000)}s · {lastForActive.exit}
                {lastForActive.result_file ? ` · saved ${lastForActive.result_file}` : ""}
              </p>
            )}
          </div>
        )}
      </div>

      {confirming && active && (
        <ConfirmModal
          title={active.label}
          description={active.description}
          note={`this run can write files and create Docs · max $${(deck?.ceilings.act ?? 1).toFixed(2)} · killed past 10:00`}
          onCancel={() => setConfirming(false)}
          onConfirm={run}
        />
      )}
    </div>
  );
}

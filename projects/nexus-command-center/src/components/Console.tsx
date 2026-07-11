import { useEffect } from "react";
import { api } from "../api";
import { useStore, type ConsoleTab } from "../store";
import BrainPanel from "./BrainPanel.tsx";
import ChatPanel from "./ChatPanel.tsx";
import CommandDeck from "./CommandDeck.tsx";
import ProjectsPanel from "./ProjectsPanel.tsx";
import RunStatus from "./RunStatus.tsx";
import SkillsPanel from "./SkillsPanel.tsx";

const TABS: { id: ConsoleTab; label: string }[] = [
  { id: "deck", label: "Deck" },
  { id: "projects", label: "Projects" },
  { id: "skills", label: "Skills" },
  { id: "chat", label: "Chat" },
  { id: "brain", label: "Brain" },
];

/**
 * The bottom console dock: tab strip in a slim footer; Projects/Skills expand
 * an overlay sheet above it. Owns the deck status poll so every tab sees the
 * live run state (architecture.md §6: 2s while running, relaxed when idle).
 */
export default function Console() {
  const tab = useStore((s) => s.consoleTab);
  const setTab = useStore((s) => s.setConsoleTab);
  const setDeck = useStore((s) => s.setDeck);
  const running = useStore((s) => !!s.deck?.running);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const st = await api.status();
        if (alive) setDeck(st);
      } catch {
        /* server briefly away — next tick retries */
      }
    };
    tick();
    const iv = setInterval(tick, running ? 2000 : 15000);
    return () => {
      alive = false;
      clearInterval(iv);
    };
  }, [running, setDeck]);

  return (
    <>
      {tab !== "deck" && (
        <section
          className="min-h-0 shrink-0 overflow-y-auto"
          style={{
            // Chat + brain need real vertical room; the grids don't.
            height: tab === "chat" || tab === "brain" ? "62vh" : "42vh",
            borderTop: "1px solid var(--np-hairline)",
            background: "var(--np-panel-grad)",
          }}
        >
          {tab === "projects" ? (
            <ProjectsPanel />
          ) : tab === "skills" ? (
            <SkillsPanel />
          ) : tab === "brain" ? (
            <BrainPanel />
          ) : (
            <ChatPanel />
          )}
        </section>
      )}

      <footer
        className="flex h-16 shrink-0 items-center gap-3 px-5"
        style={{
          borderTop: "1px solid var(--np-hairline)",
          background: "var(--np-panel-grad)",
        }}
      >
        <span
          className="text-[11px] uppercase"
          style={{ color: "var(--np-fog)", letterSpacing: "0.22em" }}
        >
          Console
        </span>
        <nav className="flex items-center gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              className="np-btn-ghost"
              onClick={() => setTab(t.id)}
              style={
                tab === t.id
                  ? { borderColor: "var(--np-blue)", color: "var(--np-white)" }
                  : undefined
              }
            >
              {t.label}
            </button>
          ))}
        </nav>
        <span className="h-4 w-px" style={{ background: "var(--np-hairline)" }} />

        {tab === "deck" ? <CommandDeck /> : <RunStatus />}
      </footer>
    </>
  );
}

import { useStore } from "../store";

function ago(iso: string | null | undefined): string {
  if (!iso) return "—";
  const ms = Date.now() - Date.parse(iso);
  if (Number.isNaN(ms)) return "—";
  const m = Math.floor(ms / 60000);
  if (m < 1) return "now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

function Item({ label, value }: { label: string; value: string }) {
  return (
    <span className="np-mono whitespace-nowrap" style={{ color: "var(--np-fog)" }}>
      {label} <span style={{ color: "var(--np-white)" }}>{value}</span>
    </span>
  );
}

/** Top-bar vitals — mono numbers with fog labels (design-system.md §6). */
export default function VitalsBar() {
  const vitals = useStore((s) => s.vitals);
  const c = vitals?.counts ?? {};
  const fmt = (k: string) => (c[k] != null ? String(c[k]) : "—");

  return (
    <div className="hidden items-center gap-4 lg:flex" aria-label="System vitals">
      <Item label="SKILLS" value={fmt("skills")} />
      <Item label="PROJECTS" value={fmt("projects")} />
      <Item label="WIKI" value={fmt("wiki")} />
      <Item label="DECISIONS" value={fmt("decisions")} />
      <Item label="NODES" value={c.nodes != null ? `${c.nodes}/${c.edges ?? 0}` : "—"} />
      <span className="h-4 w-px" style={{ background: "var(--np-hairline)" }} />
      <Item label="SYNC" value={ago(vitals?.last_sync?.ts)} />
      <Item label="VAULT" value={ago(vitals?.last_vault_commit?.ts)} />
      <Item
        label="SPEND"
        value={vitals ? `$${vitals.command_spend.total_usd.toFixed(2)}` : "—"}
      />
    </div>
  );
}

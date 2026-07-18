/* Small shared formatters. Kept in one place so every view renders numbers the same way. */

/** Week-over-week delta, rounded to kill float noise (69.2 - 132.8 = -63.6, not -63.600001). */
export function delta(cur?: number, prev?: number): number | null {
  if (typeof cur !== "number" || typeof prev !== "number") return null;
  return Math.round((cur - prev) * 10) / 10;
}

/** Compact integer-ish display: 1_001 -> "1,001", 16.86 -> "16.86". */
export function num(n: number | undefined | null): string {
  if (typeof n !== "number" || Number.isNaN(n)) return "0";
  return Number.isInteger(n) ? n.toLocaleString("en-US") : String(Math.round(n * 100) / 100);
}

/** "2026-07-17T14:16:46.52" -> "Jul 17". */
export function shortDate(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso.length <= 10 ? `${iso}T00:00:00` : iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/** "2026-07-17T..." -> "Fri" (weekday, for day grouping). */
export function weekday(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso.length <= 10 ? `${iso}T00:00:00` : iso);
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString("en-US", { weekday: "short" });
}

/** Minutes -> "2h 05m" / "45m". */
export function hoursMins(min?: number | null): string {
  if (!min) return "";
  const h = Math.floor(min / 60);
  const m = min % 60;
  return h ? `${h}h${m ? ` ${String(m).padStart(2, "0")}m` : ""}` : `${m}m`;
}

export const PLATFORM_LABEL: Record<string, string> = {
  linkedin: "LinkedIn",
  instagram: "Instagram",
  facebook: "Facebook",
};

export function titleCase(s: string): string {
  return s ? s[0].toUpperCase() + s.slice(1) : s;
}

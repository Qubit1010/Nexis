// Display and input are in Pakistan time (UTC+5, no DST); storage is ISO UTC.
const OFFSET = 5 * 60 * 60_000;
const TZ = "Asia/Karachi";

export function pkt(iso: string): Date {
  return new Date(Date.parse(iso) + OFFSET); // read with getUTC* only
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return "unscheduled";
  return new Intl.DateTimeFormat("en-GB", { timeZone: TZ, weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit", hour12: true }).format(new Date(iso));
}

export function fmtTime(iso: string): string {
  return new Intl.DateTimeFormat("en-US", { timeZone: TZ, hour: "numeric", minute: "2-digit" }).format(new Date(iso));
}

export function fmtDay(iso: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: TZ, weekday: "short", day: "numeric", month: "short" }).format(new Date(iso));
}

export function ago(iso: string | null | undefined): string {
  if (!iso) return "";
  const s = Math.round((Date.now() - Date.parse(iso)) / 1000);
  const abs = Math.abs(s);
  const unit = abs < 60 ? `${abs}s` : abs < 3600 ? `${Math.round(abs / 60)}m` : abs < 86400 ? `${Math.round(abs / 3600)}h` : `${Math.round(abs / 86400)}d`;
  return s >= 0 ? `${unit} ago` : `in ${unit}`;
}

/** Monday 00:00 PKT of the week containing `iso`, as ISO UTC. */
export function weekStart(iso: string): string {
  const d = pkt(iso);
  const dow = (d.getUTCDay() + 6) % 7;
  const monday = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - dow);
  return new Date(monday - OFFSET).toISOString();
}

export const addDays = (iso: string, n: number) => new Date(Date.parse(iso) + n * 86_400_000).toISOString();

/** PKT day key (YYYY-MM-DD) for grouping. */
export function dayKey(iso: string): string {
  return pkt(iso).toISOString().slice(0, 10);
}

/** <input type="datetime-local"> value in PKT. */
export function toLocalInput(iso: string | null | undefined): string {
  if (!iso) return "";
  return pkt(iso).toISOString().slice(0, 16);
}

export function fromLocalInput(v: string): string | null {
  if (!v) return null;
  const [d, t] = v.split("T");
  const [y, m, day] = d.split("-").map(Number);
  const [h, min] = (t || "09:00").split(":").map(Number);
  return new Date(Date.UTC(y, m - 1, day, h, min) - OFFSET).toISOString();
}

/** A PKT day (YYYY-MM-DD) at a PKT clock time -> ISO UTC. */
export function atPkt(day: string, hhmm = "09:00"): string {
  return fromLocalInput(`${day}T${hhmm}`)!;
}

export function pktClock(iso: string): string {
  return pkt(iso).toISOString().slice(11, 16);
}

// Pakistan Standard Time is a fixed UTC+5 with no DST, so conversions are
// arithmetic. Everything is stored as ISO UTC; PKT exists only at the edges
// (sheet import/mirror, UI display, cron evaluation via croner's timezone).
const PKT_OFFSET_MIN = 5 * 60;
const MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export const nowIso = (): string => new Date().toISOString();

export function addMinutes(iso: string, minutes: number): string {
  return new Date(Date.parse(iso) + minutes * 60_000).toISOString();
}

/** Wall-clock PKT components -> ISO UTC. */
export function pktToIso(y: number, month1: number, d: number, h = 9, min = 0): string {
  return new Date(Date.UTC(y, month1 - 1, d, h, min) - PKT_OFFSET_MIN * 60_000).toISOString();
}

/** ISO UTC -> PKT wall-clock parts. */
export function pktParts(iso: string) {
  const d = new Date(Date.parse(iso) + PKT_OFFSET_MIN * 60_000);
  return {
    y: d.getUTCFullYear(),
    m: d.getUTCMonth() + 1,
    d: d.getUTCDate(),
    h: d.getUTCHours(),
    min: d.getUTCMinutes(),
    dow: d.getUTCDay(),
  };
}

/** "Oct 19" -> {month, day}; also accepts "2026-10-19", "19/10/2026" and "October 19". */
export function parseMonthDay(raw: string): { y?: number; m: number; d: number } | null {
  const s = raw.trim();
  let m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (m) return { y: Number(m[1]), m: Number(m[2]), d: Number(m[3]) };
  m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (m) return { y: Number(m[3]), m: Number(m[2]), d: Number(m[1]) };
  m = s.match(/^([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:,?\s+(\d{4}))?/);
  if (m) {
    const mi = MONTHS.indexOf(m[1].slice(0, 3).toLowerCase());
    if (mi < 0) return null;
    return { y: m[3] ? Number(m[3]) : undefined, m: mi + 1, d: Number(m[2]) };
  }
  return null;
}

/** "3:00 pm" / "15:00" / "9am" -> {h, min}. */
export function parseClock(raw: string | undefined | null): { h: number; min: number } | null {
  if (!raw) return null;
  const m = raw.trim().toLowerCase().match(/^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/);
  if (!m) return null;
  let h = Number(m[1]);
  const min = m[2] ? Number(m[2]) : 0;
  if (m[3] === "pm" && h < 12) h += 12;
  if (m[3] === "am" && h === 12) h = 0;
  if (h > 23 || min > 59) return null;
  return { h, min };
}

export function fmtSheetDate(iso: string): string {
  const p = pktParts(iso);
  return `${MONTH_LABELS[p.m - 1]} ${p.d}`;
}

export function fmtSheetDay(iso: string): string {
  return DAYS[pktParts(iso).dow];
}

export function fmtClock(iso: string): string {
  const p = pktParts(iso);
  const ampm = p.h >= 12 ? "pm" : "am";
  const h12 = p.h % 12 === 0 ? 12 : p.h % 12;
  return `${h12}:${String(p.min).padStart(2, "0")} ${ampm}`;
}

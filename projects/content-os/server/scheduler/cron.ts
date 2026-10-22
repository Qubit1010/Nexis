import { Cron } from "croner";

/** Next occurrence strictly after `from`, as ISO UTC (null if the pattern never fires again). */
export function nextRunAfter(pattern: string, tz: string, from: Date): string | null {
  const next = new Cron(pattern, { timezone: tz, paused: true }).nextRun(from);
  return next ? next.toISOString() : null;
}

export function validCron(pattern: string): boolean {
  try {
    new Cron(pattern, { paused: true });
    return true;
  } catch {
    return false;
  }
}

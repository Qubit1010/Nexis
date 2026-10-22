/** Poll a URL until it serves 200 and contains the expected title (deploys take a few minutes). */
export async function waitForLive(
  url: string,
  title: string,
  timeoutMs = Number(process.env.CONTENT_OS_LIVE_TIMEOUT_MS || 10 * 60_000),
  intervalMs = Number(process.env.CONTENT_OS_LIVE_POLL_MS || 20_000),
): Promise<{ ok: boolean; status: number; detail: string }> {
  const deadline = Date.now() + timeoutMs;
  const needle = title.toLowerCase().replace(/&/g, "&amp;").slice(0, 60);
  let last = { ok: false, status: 0, detail: "not checked" };
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(20_000), headers: { "Cache-Control": "no-cache" } });
      const html = res.ok ? (await res.text()).toLowerCase() : "";
      if (res.ok && (html.includes(needle) || html.includes(title.toLowerCase().slice(0, 60)))) return { ok: true, status: res.status, detail: "live" };
      last = { ok: false, status: res.status, detail: res.ok ? "200 but the title is not on the page yet" : `HTTP ${res.status}` };
    } catch (e) {
      last = { ok: false, status: 0, detail: (e as Error).message };
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return last;
}

// End-to-end tests against a throwaway data dir and a fake `claude`. Env must be
// set before any server module is imported (config reads it at import time).
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "content-os-test-"));
process.env.CONTENT_OS_DATA_DIR = path.join(TMP, "data");
process.env.CONTENT_OS_ENV_FILE = path.join(TMP, "empty.env");
fs.writeFileSync(process.env.CONTENT_OS_ENV_FILE, "");
process.env.CLAUDE_BIN = process.execPath;
process.env.CLAUDE_BIN_ARGS = JSON.stringify([path.join(HERE, "fake-claude.mjs")]);
process.env.CONTENT_OS_LIVE_POLL_MS = "200";
process.env.CONTENT_OS_LIVE_TIMEOUT_MS = "8000";

const { db, schema } = await import("../server/db/index.ts");
const { seed } = await import("../server/db/seed.ts");
const { eq } = await import("drizzle-orm");
const { ingestIdea } = await import("../server/ideas.ts");
const items = await import("../server/items.ts");
const { tick, runAutomations, recover } = await import("../server/scheduler/tick.ts");
const { enqueue } = await import("../server/scheduler/queue.ts");
const { putSettings } = await import("../server/settings.ts");
const { normalizeUrl, dedupeKey } = await import("../server/lib/dedupe.ts");
const { parseSchedule } = await import("../server/integrations/sheets-import.ts");
const { runChecks } = await import("../server/engine/checks.ts");
const { buildApp } = await import("../server/index.ts");
const { nowIso, addMinutes } = await import("../server/lib/time.ts");

before(async () => {
  await seed();
});
after(() => {
  try {
    fs.rmSync(TMP, { recursive: true, force: true });
  } catch {
    /* Windows may hold the sqlite file; temp dir cleanup is best effort */
  }
});

async function job(id: string) {
  return (await db.select().from(schema.jobs).where(eq(schema.jobs.id, id)).get())!;
}

/** Drive the scheduler until the job leaves queued/running. */
async function settle(jobId: string, timeoutMs = 20_000) {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    await tick();
    const j = await job(jobId);
    if (!["queued", "running"].includes(j.status) || (j.status === "queued" && Date.parse(j.dueAt) > Date.now() + 1000)) return j;
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error(`job ${jobId} did not settle`);
}

const inDays = (d: number) => addMinutes(nowIso(), d * 24 * 60);

test("urls normalize so the same article dedupes", () => {
  assert.equal(normalizeUrl("https://www.youtube.com/watch?v=abc&utm_source=x&t=10"), "youtube.com/watch?v=abc");
  assert.equal(normalizeUrl("https://youtu.be/abc"), "youtube.com/watch?v=abc");
  assert.equal(normalizeUrl("https://Example.com/post/?utm_medium=a&id=2"), "example.com/post?id=2");
  assert.equal(dedupeKey({ title: "Hello, World!" }), dedupeKey({ title: "hello world" }));
});

test("ingest bumps seen_count instead of duplicating", async () => {
  const a = await ingestIdea({ title: "Gemini 4 Argon", url: "https://news.example.com/a?utm_source=x", source: "news_article" });
  const b = await ingestIdea({ title: "Gemini 4 Argon (again)", url: "https://news.example.com/a", source: "news_article" });
  assert.equal(a.duplicate, false);
  assert.equal(b.duplicate, true);
  assert.equal(b.id, a.id);
  assert.equal(b.seenCount, 2);
});

test("schedule import infers years across a year boundary and maps sections", () => {
  const values = [
    ["Date", "Day", "Platform", "Post Type", "Media Type", "Content Theme", "Topic / Idea", "Post Description", "Reference", "Format", "Content Mode", "Pillars", "Design Template", "x", "x", "x", "x", "x", "x", "x", "Final Video/Post", "x", "Publish Time", "Status"],
    ["Dec 8", "Monday", "All", "Reel", "", "", "A reel", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Published"],
    ["Dec 20", "Saturday", "LinkedIn", "Text", "", "", "December post", "", "", "Text Post", "", "", "", "", "", "", "", "", "", "", "https://linkedin.com/p/1", "", "", "Published"],
    ["Jan 5", "Monday", "LinkedIn", "Text", "", "", "January post", "", "", "Text Post", "", "", "", "", "", "", "", "", "", "", "", "", "", "Cancelled"],
    ["Blog Posts"],
    ["Oct 26", "Monday", "Blog", "Blog", "", "", "Future blog", "desc", "ref", "Blog Post", "News/Analysis", "", "", "", "", "", "", "", "", "", "", "", "3:00 pm", "Planned"],
    ["Agency Blog Posts"],
    ["Oct 27", "Tuesday", "Blog", "Blog", "", "", "Agency piece", "", "", "Blog Post", "", "", "", "", "", "", "", "", "", "", "", "", "", "Planned"],
  ];
  const { rows, skipped } = parseSchedule(values, new Date("2026-10-22T03:00:00Z"));
  assert.equal(skipped, 1, "the reel row is skipped");
  const by = Object.fromEntries(rows.map((r) => [r.title, r]));
  assert.equal(by["December post"].scheduledFor.slice(0, 4), "2025");
  assert.equal(by["January post"].scheduledFor.slice(0, 4), "2026");
  assert.equal(by["December post"].publishedUrl, "https://linkedin.com/p/1");
  assert.equal(by["January post"].status, "skipped");
  assert.equal(by["Future blog"].format, "personal_blog");
  assert.equal(by["Future blog"].scheduledFor, "2026-10-26T10:00:00.000Z", "3:00 pm PKT = 10:00 UTC");
  assert.equal(by["Agency piece"].format, "agency_blog");
});

test("hard checks catch dashes, agency names and LinkedIn length", () => {
  const c = runChecks("linkedin_post", "I built it \u2014 at NexusPoint.\n" + "x".repeat(3100));
  const ids = c.filter((x) => x.level === "fail").map((x) => x.id);
  assert.ok(ids.includes("no_dashes"));
  assert.ok(ids.includes("personal_brand_terms"));
  assert.ok(ids.includes("li_length"));
  const agency = runChecks("agency_blog", "---\ntitle: T\nexcerpt: E\ndatePublished: 2026-10-01\ndateModified: 2026-10-01\ncategory: nope\n---\n\nNexusPoint builds things.", { categories: ["systems"] });
  assert.ok(!agency.some((x) => x.id === "personal_brand_terms"), "the agency blog may name the agency");
  assert.ok(agency.some((x) => x.id === "fm_category" && x.level === "fail"));
});

function guard(input: object, runDir: string) {
  return spawnSync(process.execPath, [path.join(HERE, "..", "server", "engine", "hook-guard.mjs"), "generate", runDir], { input: JSON.stringify(input), encoding: "utf8" });
}

test("guard fences writes to the run folder and blocks side effects", () => {
  const runDir = path.join(TMP, "run-guard");
  fs.mkdirSync(runDir, { recursive: true });
  assert.equal(guard({ tool_name: "Write", tool_input: { file_path: path.join(runDir, "post.md") } }, runDir).status, 0);
  assert.equal(guard({ tool_name: "Write", tool_input: { file_path: "D:/aleem-portfolio/src/content/blog/x.md" } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Edit", tool_input: { file_path: path.join(runDir, "..", "escape.md") } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Bash", tool_input: { command: "git push origin master" } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Bash", tool_input: { command: "python tools/gdocs/save_content.py" } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Bash", tool_input: { command: "curl -X POST https://api.buffer.com/graphql" } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Read", tool_input: { file_path: "D:/Nexis/.env" } }, runDir).status, 2);
  assert.equal(guard({ tool_name: "Bash", tool_input: { command: 'python .claude/skills/post-creator/scripts/research.py --topic "x" -o out.json' } }, runDir).status, 0);
  assert.equal(guard({ tool_name: "Bash", tool_input: { command: "git log --oneline -5" } }, runDir).status, 0);
});

test("generate -> review -> revise produces versions; buffer push without a key fails loudly", async () => {
  const idea = await ingestIdea({ title: "Claude 5.5 in production", source: "youtube_topic", summary: "what changed" });
  const item = await items.planItem({ ideaId: idea.id, format: "linkedin_post", scheduledFor: inDays(3) });
  assert.equal(item.channelId, "li-personal");
  const idea2 = (await db.select().from(schema.ideas).where(eq(schema.ideas.id, idea.id)).get())!;
  assert.equal(idea2.status, "used");

  const g = (await items.requestGeneration(item.id)) as { id: string };
  const gj = await settle(g.id);
  assert.equal(gj.status, "done", gj.lastError ?? "");
  let it = await items.getItem(item.id);
  assert.equal(it.status, "review");
  const v1 = (await items.currentVersion(it))!;
  assert.equal(v1.n, 1);
  assert.match(v1.bodyMd, /I shipped the thing/);
  const run = (await db.select().from(schema.runs).where(eq(schema.runs.itemId, item.id)).get())!;
  assert.equal(run.apiKeySource, "none");
  assert.equal(run.status, "ok");
  const input = JSON.parse(fs.readFileSync(path.join(process.env.CONTENT_OS_DATA_DIR!, "runs", run.id, "input.json"), "utf8"));
  assert.equal(input.topic, "Claude 5.5 in production");

  const r = (await items.requestGeneration(item.id, { feedback: "shorter" })) as { id: string };
  assert.equal((await settle(r.id)).status, "done");
  it = await items.getItem(item.id);
  const v2 = (await items.currentVersion(it))!;
  assert.equal(v2.n, 2);
  assert.equal(v2.kind, "revised");
  assert.match(v2.bodyMd, /Revised/);

  await items.approveItem(item.id);
  const push = (await db.select().from(schema.jobs).where(eq(schema.jobs.itemId, item.id)).all()).find((j) => j.type === "buffer_push")!;
  const pj = await settle(push.id);
  assert.equal(pj.status, "failed");
  assert.match(pj.lastError ?? "", /BUFFER_API_KEY/);
  assert.equal((await items.getItem(item.id)).status, "failed");
});

test("a failing check gets one automatic fix-up turn on the same session", async () => {
  process.env.FAKE_MODE = "dash";
  try {
    const item = await items.planItem({ format: "linkedin_post", title: "Dash test", scheduledFor: inDays(2) });
    const g = (await items.requestGeneration(item.id)) as { id: string };
    assert.equal((await settle(g.id)).status, "done");
    const v = (await items.currentVersion(await items.getItem(item.id)))!;
    const checks = JSON.parse(v.checksJson) as { id: string; level: string }[];
    assert.ok(!checks.some((c) => c.level === "fail"), "the fix-up turn removed the dash");
    assert.ok(!v.bodyMd.includes("\u2014"));
  } finally {
    delete process.env.FAKE_MODE;
  }
});

test("blocked gate still yields a reviewable draft, and approval needs force", async () => {
  process.env.FAKE_MODE = "blocked";
  try {
    const item = await items.planItem({ format: "linkedin_post", title: "Neutral tool relay", scheduledFor: inDays(2) });
    const g = (await items.requestGeneration(item.id)) as { id: string };
    await settle(g.id);
    const it = await items.getItem(item.id);
    assert.equal(it.status, "review");
    assert.match(it.error ?? "", /Blocked by the gate/);
    await assert.rejects(items.approveItem(item.id), /blocked/);
  } finally {
    delete process.env.FAKE_MODE;
  }
});

test("usage limit requeues for the reset without spending an attempt", async () => {
  process.env.FAKE_MODE = "ratelimit";
  try {
    const item = await items.planItem({ format: "linkedin_post", title: "Rate limited", scheduledFor: inDays(2) });
    const g = (await items.requestGeneration(item.id)) as { id: string };
    const j = await settle(g.id);
    assert.equal(j.status, "queued");
    assert.equal(j.attempts, 0);
    assert.ok(Date.parse(j.dueAt) > Date.now() + 30 * 60_000, "requeued for the reset time");
    assert.equal((await items.getItem(item.id)).status, "planned");
    await db.update(schema.jobs).set({ status: "cancelled" }).where(eq(schema.jobs.id, j.id));
  } finally {
    delete process.env.FAKE_MODE;
  }
  // The remembered "rejected" window would block the next tests' runs; an allowed run replaces it.
  const { startEngineRun } = await import("../server/engine/claude-cli.ts");
  const dir = path.join(TMP, "reset-run");
  fs.mkdirSync(dir, { recursive: true });
  await startEngineRun({ runId: "reset", runDir: dir, prompt: "x", model: "fake", maxTurns: 1, timeoutMs: 10_000 }).done;
});

test("a run that would bill an API key is refused", async () => {
  process.env.FAKE_MODE = "apikey";
  try {
    const item = await items.planItem({ format: "linkedin_post", title: "API key leak", scheduledFor: inDays(2) });
    const g = (await items.requestGeneration(item.id)) as { id: string };
    const j = await settle(g.id);
    assert.equal(j.status, "failed");
    assert.match(j.lastError ?? "", /apiKeySource/);
    const run = (await db.select().from(schema.runs).where(eq(schema.runs.itemId, item.id)).get())!;
    assert.equal(run.status, "auth_refused");
  } finally {
    delete process.env.FAKE_MODE;
  }
});

test("a signed-out CLI fails fast with the fix, without burning retries", async () => {
  process.env.FAKE_MODE = "authfail";
  try {
    const item = await items.planItem({ format: "linkedin_post", title: "Signed out", scheduledFor: inDays(2) });
    const g = (await items.requestGeneration(item.id)) as { id: string };
    const j = await settle(g.id);
    assert.equal(j.status, "failed");
    assert.equal(j.attempts, 1, "no retry");
    assert.match(j.lastError ?? "", /\/login/);
    const run = (await db.select().from(schema.runs).where(eq(schema.runs.itemId, item.id)).get())!;
    assert.equal(run.status, "auth_failed");
  } finally {
    delete process.env.FAKE_MODE;
  }
});

test("missed automations catch up exactly once, never a backlog", async () => {
  const id = "test-auto";
  await db.insert(schema.automations).values({
    id,
    name: "hourly",
    jobType: "prepare_week",
    cron: "0 * * * *",
    tz: "Asia/Karachi",
    enabled: true,
    catchUp: "once",
    maxLateMin: 720,
    nextRunAt: addMinutes(nowIso(), -180), // three hourly occurrences missed
    createdAt: nowIso(),
  });
  assert.equal(await runAutomations(), 1);
  const a = (await db.select().from(schema.automations).where(eq(schema.automations.id, id)).get())!;
  assert.ok(Date.parse(a.nextRunAt!) > Date.now(), "next run moved past now");
  assert.equal(await runAutomations(), 0, "no second catch-up");

  await db.update(schema.automations).set({ catchUp: "skip", nextRunAt: addMinutes(nowIso(), -180) }).where(eq(schema.automations.id, id));
  assert.equal(await runAutomations(), 0, "skip policy enqueues nothing");
  await db.delete(schema.automations).where(eq(schema.automations.id, id));
});

test("recovery requeues interrupted jobs but never retries a buffer push blind", async () => {
  const gen = await enqueue({ type: "prepare_week", idempotencyKey: "rec-gen" });
  const push = await enqueue({ type: "buffer_push", idempotencyKey: "rec-push", dueAt: inDays(5) });
  await db.update(schema.jobs).set({ status: "running" }).where(eq(schema.jobs.id, gen.id));
  await db.update(schema.jobs).set({ status: "running" }).where(eq(schema.jobs.id, push.id));
  await recover();
  assert.equal((await job(gen.id)).status, "queued");
  assert.equal((await job(push.id)).status, "needs_check");
});

test("API rejects cross-origin and non-JSON writes", async () => {
  const app = buildApp();
  const bad = await app.request("/api/ideas", { method: "POST", headers: { origin: "https://evil.example", "content-type": "application/json" }, body: JSON.stringify({ title: "x", source: "manual" }) });
  assert.equal(bad.status, 403);
  const form = await app.request("/api/ideas", { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body: "title=x" });
  assert.equal(form.status, 415);
  const ok = await app.request("/api/ideas", { method: "POST", headers: { origin: "http://127.0.0.1:3000", "content-type": "application/json" }, body: JSON.stringify({ title: "From the brief", source: "news_article", url: "https://x.example/1" }) });
  assert.equal(ok.status, 200);
  const invalid = await app.request("/api/ideas", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ title: "", source: "nope" }) });
  assert.equal(invalid.status, 400);
});

test("git publish: build gate, commit only our paths, push, verify live, release the newsletter", async () => {
  // A local "site": bare remote + clone, a build that rejects posts without a title, and an HTTP server as the live site.
  const remote = path.join(TMP, "remote.git");
  const site = path.join(TMP, "site");
  const git = (cwd: string, ...args: string[]) => execFileSync("git", args, { cwd, encoding: "utf8" });
  execFileSync("git", ["init", "--bare", "-b", "master", remote]);
  execFileSync("git", ["clone", remote, site]);
  git(site, "checkout", "-B", "master");
  fs.mkdirSync(path.join(site, "src", "content", "blog"), { recursive: true });
  fs.mkdirSync(path.join(site, "node_modules"));
  fs.writeFileSync(path.join(site, ".gitignore"), "node_modules/\n");
  fs.writeFileSync(path.join(site, "package.json"), JSON.stringify({ name: "site", private: true, scripts: { build: "node build.mjs" } }));
  fs.writeFileSync(
    path.join(site, "build.mjs"),
    "import fs from 'node:fs';for (const f of fs.readdirSync('src/content/blog').filter((n) => n.endsWith('.md'))) { const t = fs.readFileSync('src/content/blog/'+f,'utf8'); if (!/^title:/m.test(t)) { console.error('missing title in '+f); process.exit(1); } }",
  );
  fs.writeFileSync(path.join(site, "src", "content", "blog", ".keep"), "");
  fs.writeFileSync(path.join(site, "src", "content", "blog", "existing.md"), "---\ntitle: Existing\n---\n");
  git(site, "add", ".");
  git(site, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-m", "init");
  git(site, "push", "-u", "origin", "master");

  const server = http.createServer((req, res) => {
    const slug = (req.url || "").replace(/^\/blog\//, "");
    const file = path.join(site, "src", "content", "blog", `${slug}.md`);
    if (fs.existsSync(file)) {
      res.writeHead(200, { "content-type": "text/html" });
      res.end("<html><title>Test post</title><h1>Test post</h1></html>");
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", () => r()));
  const port = (server.address() as { port: number }).port;

  try {
    await putSettings({ git: { name: "Content OS Test", email: "test@example.com" } });
    await db
      .update(schema.channels)
      .set({ configJson: JSON.stringify({ repo: site, branch: "master", contentDir: "src/content/blog", assetsDir: "src/assets/blog", siteUrl: `http://127.0.0.1:${port}`, blogPath: "/blog/", deployMode: "git", categories: ["ai-automation"] }) })
      .where(eq(schema.channels.id, "blog-personal"));

    const blog = await items.planItem({ format: "personal_blog", title: "Test post", scheduledFor: inDays(1) });
    const nl = await items.planItem({ format: "li_newsletter", title: "Issue from test post", scheduledFor: inDays(1), dependsOnItemId: blog.id });
    const g = (await items.requestGeneration(blog.id)) as { id: string };
    assert.equal((await settle(g.id)).status, "done");

    // The newsletter waits on the blog.
    const gn = (await items.requestGeneration(nl.id)) as { id: string };
    assert.equal((await settle(gn.id)).status, "done");
    await items.approveItem(nl.id, { publishNow: true });
    const nlJob = (await db.select().from(schema.jobs).where(eq(schema.jobs.itemId, nl.id)).all()).find((j) => j.type === "newsletter_ready")!;
    const waiting = await settle(nlJob.id);
    assert.equal(waiting.status, "queued", "requeued while the blog is unpublished");

    await items.approveItem(blog.id, { publishNow: true });
    const pub = (await db.select().from(schema.jobs).where(eq(schema.jobs.itemId, blog.id)).all()).find((j) => j.type === "publish_git")!;
    const pj = await settle(pub.id, 60_000);
    assert.equal(pj.status, "done", pj.lastError ?? "");
    const it = await items.getItem(blog.id);
    assert.equal(it.status, "published");
    assert.equal(it.publishedUrl, `http://127.0.0.1:${port}/blog/test-post`);
    const remoteLog = execFileSync("git", ["--git-dir", remote, "log", "--format=%s|%ae", "-1"], { encoding: "utf8" }).trim();
    assert.equal(remoteLog, "Publish Test post|test@example.com");
    const published = fs.readFileSync(path.join(site, "src", "content", "blog", "test-post.md"), "utf8");
    assert.match(published, /^datePublished: \d{4}-\d{2}-\d{2}$/m);
    assert.equal(git(site, "status", "--porcelain").trim(), "", "nothing else touched in the site");

    // Publishing released the newsletter.
    const ready = await settle(nlJob.id);
    assert.equal(ready.status, "done", ready.lastError ?? "");
    assert.equal((await items.getItem(nl.id)).status, "ready_to_post");
  } finally {
    server.close();
  }
});

test("a broken build rolls back and commits nothing", async () => {
  const blog = await items.planItem({ format: "personal_blog", title: "Broken post", scheduledFor: inDays(1) });
  const g = (await items.requestGeneration(blog.id)) as { id: string };
  await settle(g.id);
  const v = (await items.currentVersion(await items.getItem(blog.id)))!;
  // Strip the title so the fake site's build fails, and give it a fresh slug.
  await db
    .update(schema.versions)
    .set({ bodyMd: v.bodyMd.replace(/^title:.*$/m, "subtitle: none"), metaJson: JSON.stringify({ ...JSON.parse(v.metaJson), meta: { slug: "broken-post" } }) })
    .where(eq(schema.versions.id, v.id));
  await items.approveItem(blog.id, { publishNow: true, force: true });
  const pub = (await db.select().from(schema.jobs).where(eq(schema.jobs.itemId, blog.id)).all()).find((j) => j.type === "publish_git")!;
  const pj = await settle(pub.id, 60_000);
  assert.equal(pj.status, "failed");
  assert.match(pj.lastError ?? "", /build failed/);
  const site = path.join(TMP, "site");
  assert.ok(!fs.existsSync(path.join(site, "src", "content", "blog", "broken-post.md")), "rolled back");
  assert.equal((await items.getItem(blog.id)).status, "failed");
});

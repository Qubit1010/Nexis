// Test stand-in for `claude -p --output-format stream-json`. It behaves like a
// Content OS generation run: reads the prompt on stdin, writes the files the
// contract asks for into $CONTENT_OS_RUN_DIR, then output.json, then a result.
// FAKE_MODE: ok | blocked | noout | ratelimit | apikey | dash | hang
import fs from "node:fs";
import path from "node:path";

const argv = process.argv.slice(2);
const mode = process.env.FAKE_MODE || "ok";
const runDir = process.env.CONTENT_OS_RUN_DIR;
const w = (o) => process.stdout.write(JSON.stringify(o) + "\n");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let prompt = "";
for await (const chunk of process.stdin) prompt += chunk;

const resume = argv.includes("--resume") ? argv[argv.indexOf("--resume") + 1] : null;
const sid = resume || (argv.includes("--session-id") ? argv[argv.indexOf("--session-id") + 1] : `sess-${Math.random().toString(36).slice(2, 10)}`);

w({ type: "system", subtype: "init", session_id: sid, apiKeySource: mode === "apikey" ? "ANTHROPIC_API_KEY" : "none", model: "fake" });
if (mode === "apikey") {
  await sleep(5000); // the engine must kill us before we "spend" anything
  process.exit(0);
}
w({ type: "rate_limit_event", rate_limit_info: { status: mode === "ratelimit" ? "rejected" : "allowed", resetsAt: Math.floor(Date.now() / 1000) + 3600, rateLimitType: "five_hour", unifiedWindows: { seven_day: { utilization: 0.2 } } } });
if (mode === "ratelimit") {
  w({ type: "result", subtype: "error", is_error: true, result: "usage limit reached", total_cost_usd: 0, num_turns: 0, session_id: sid });
  process.exit(1);
}
if (mode === "authfail") {
  w({ type: "result", subtype: "success", is_error: true, result: "Failed to authenticate: OAuth session expired and could not be refreshed", total_cost_usd: 0, num_turns: 1, session_id: sid });
  process.exit(1);
}
if (mode === "hang") await sleep(60_000);

w({ type: "assistant", message: { content: [{ type: "tool_use", name: "Bash", input: { command: "python research.py" } }] } });

const format = /linkedin-newsletter/.test(prompt) ? "li_newsletter" : /blog-writer/.test(prompt) ? "blog" : "linkedin_post";
const isRevision = /This is a revision/.test(prompt);
const fixed = !!resume; // a resumed session is the fix-up turn
const dash = mode === "dash" && !fixed ? " — " : ", ";

if (mode !== "noout" && runDir) {
  let main;
  let meta;
  if (format === "linkedin_post") {
    main = "post.md";
    fs.writeFileSync(path.join(runDir, main), `I shipped the thing last week${dash}and the first run broke.\n\n${isRevision ? "Revised: tighter." : "Here is what I changed."}\n`);
    fs.writeFileSync(path.join(runDir, "infographic-prompt.md"), "Infographic prompt");
    meta = { hook: "I shipped the thing", char_count: 80, pillar: "AI & Automation", content_mode: "Personal Story", ingredients: ["lived_experience"], hashtags: [] };
  } else if (format === "blog") {
    main = "test-post.md";
    fs.writeFileSync(
      path.join(runDir, main),
      `---\ntitle: "Test post"\nseoTitle: "Test post about testing things properly here"\nexcerpt: "A test excerpt that is long enough to sit inside the meta description range, describing what the post covers for readers."\ncategory: "ai-automation"\ndraft: false\ndatePublished: 2026-10-22\ndateModified: 2026-10-22\n---\n\nAnswer first${dash}body.\n\n## A section\n\nText.\n`,
    );
    meta = { slug: "test-post", primary_keyword: "test", word_count: 700, category: "ai-automation", seo_title: "Test post", excerpt: "x" };
  } else {
    main = "issue.md";
    fs.writeFileSync(path.join(runDir, main), "# Issue title\n\nBody text https://aleemuh.com/newsletter\n\n<!-- end issue -->\nnotes");
    meta = { issue_title: "Issue title", word_count: 400, share_text: "share", cover_note: "cover", check_passed: true };
  }
  fs.writeFileSync(
    path.join(runDir, "output.json"),
    JSON.stringify({
      status: mode === "blocked" ? "blocked" : "ok",
      blocked_reason: mode === "blocked" ? "needs a first-hand result" : null,
      rescue: mode === "blocked" ? "tell what broke when you ran it" : null,
      gate: { ladder: "pass" },
      title: "Fake title",
      files: { main, extra: format === "linkedin_post" ? ["infographic-prompt.md"] : [] },
      meta,
      sources: [{ url: "https://example.com", title: "Example" }],
      notes_for_reviewer: "fake run",
    }),
  );
}

w({ type: "assistant", message: { content: [{ type: "text", text: "output.json written" }] } });
w({ type: "result", subtype: "success", is_error: false, result: "done", total_cost_usd: 0.01, num_turns: 3, session_id: sid, usage: { input_tokens: 10 } });

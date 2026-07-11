// Test stand-in for the claude CLI. Two modes, keyed off argv like the real
// binary: default emits one headless-format result JSON (deck/skill runs);
// `--output-format stream-json` emits NDJSON stream events (chat turns).
const argv = process.argv.slice(2);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let raw = "";
for await (const chunk of process.stdin) raw += chunk;

if (argv.includes("stream-json")) {
  // Session contract mirrors the CLI: --resume keeps the id (so a test can
  // prove resume was passed), otherwise a fresh unique id is minted.
  const rIdx = argv.indexOf("--resume");
  const sid = rIdx >= 0 ? argv[rIdx + 1] : `sess-${Math.random().toString(36).slice(2, 10)}`;
  const w = (o) => process.stdout.write(JSON.stringify(o) + "\n");

  w({ type: "system", subtype: "init", session_id: sid });
  await sleep(100);
  w({ type: "stream_event", event: { type: "content_block_delta", delta: { type: "text_delta", text: "Hello " } } });
  w({ type: "stream_event", event: { type: "content_block_delta", delta: { type: "text_delta", text: "from fake." } } });
  w({
    type: "assistant",
    message: {
      content: [
        { type: "tool_use", name: "Read", input: { file_path: "x.md" } },
        { type: "text", text: "Hello from fake." },
      ],
    },
  });
  // FAKE_STREAM_HANG lets the stop test kill this mid-run.
  await sleep(Number(process.env.FAKE_STREAM_HANG ?? "100"));
  w({
    type: "result",
    subtype: "success",
    is_error: false,
    result: "Hello from fake.",
    total_cost_usd: Number(process.env.FAKE_COST ?? "0.01"),
    session_id: sid,
  });
} else {
  await sleep(250);
  process.stdout.write(
    JSON.stringify({
      type: "result",
      is_error: false,
      result: `# Fake report\n\nPrompt bytes: ${raw.length}`,
      total_cost_usd: Number(process.env.FAKE_COST ?? "0.01"),
    }),
  );
}

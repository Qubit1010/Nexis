// PreToolUse guard for command-deck headless runs (architecture.md §6.4).
// Second layer behind the settings allow/deny lists: blocks credential/secret
// paths and destructive commands, no matter how the allowlist evolves.
// Profiles (argv[2]): "read" (default) additionally blocks ALL Bash;
// "act" allows Bash for curated skill actions but keeps every other block.
// Contract: read hook JSON on stdin; exit 2 blocks the tool call, 0 allows.

const profile = process.argv[2] === "act" ? "act" : "read";

let raw = "";
for await (const chunk of process.stdin) raw += chunk;

let input = {};
try {
  input = JSON.parse(raw);
} catch {
  // Unparseable hook payload: fail closed.
  console.error("hook-guard: unparseable input");
  process.exit(2);
}

const tool = input.tool_name ?? "";
const ti = input.tool_input ?? {};
const haystack = [ti.file_path, ti.path, ti.notebook_path, ti.pattern, ti.command]
  .filter(Boolean)
  .join(" ");

const SENSITIVE = [
  /\.env(\.|$|[\\/\s])/i,
  /\.(pem|key|p12|pfx)($|[\s"'])/i,
  /id_rsa/i,
  /[\\/]\.ssh([\\/]|$)/i,
  /credential/i,
  /client-projects/i, // confidential client workspaces never enter deck runs
  /settings\.local\.json/i,
  /[\\/]\.aws([\\/]|$)/i,
];

const DESTRUCTIVE = [
  /\brm\s+(-\w*\s+)*-\w*[rf]/i,
  /\bdel\s+\/[sq]/i,
  /\brmdir\b/i,
  /\bformat\s+[a-z]:/i,
  /remove-item/i,
  /\bgit\s+push\s+--force/i,
  /\btaskkill\b/i,
  /\bshutdown\b/i,
];

function block(msg) {
  console.error(`hook-guard: ${msg}`);
  process.exit(2);
}

if (tool === "Bash" && profile !== "act") block("Bash is not allowed in read-profile runs");
if (SENSITIVE.some((r) => r.test(haystack))) block(`sensitive path blocked (${tool})`);
if (DESTRUCTIVE.some((r) => r.test(haystack))) block(`destructive pattern blocked (${tool})`);

process.exit(0);

// PreToolUse guard for Content OS generation runs. Second layer behind the
// settings allow/deny lists (ported from nexus-command-center/server/hook-guard.mjs).
//
// Profile "generate" (argv[2]) with the run folder as argv[3]:
//   - Write/Edit may only touch files inside the run folder. Content OS, not the
//     model, owns every side effect: publishing, git, Docs, sheets, Buffer.
//   - Bash may run research and check scripts but never a side-effecting command.
//   - Secrets and destructive commands are blocked as in NCC.
// Contract: hook JSON on stdin; exit 2 blocks the tool call, 0 allows.
import path from "node:path";

const profile = process.argv[2] || "generate";
const runDir = process.argv[3] ? path.resolve(process.argv[3]) : null;

let raw = "";
for await (const chunk of process.stdin) raw += chunk;

let input = {};
try {
  input = JSON.parse(raw);
} catch {
  console.error("hook-guard: unparseable input");
  process.exit(2); // fail closed
}

const tool = input.tool_name ?? "";
const ti = input.tool_input ?? {};
const haystack = [ti.file_path, ti.path, ti.notebook_path, ti.pattern, ti.command].filter(Boolean).join(" ");

function block(msg) {
  console.error(`hook-guard: ${msg}`);
  process.exit(2);
}

const SENSITIVE = [
  /\.env(\.|$|[\\/\s"'])/i,
  /\.(pem|key|p12|pfx)($|[\s"'])/i,
  /id_rsa/i,
  /[\\/]\.ssh([\\/]|$)/i,
  /credential/i,
  /settings\.local\.json/i,
  /[\\/]\.aws([\\/]|$)/i,
  /[\\/]\.config[\\/]gws/i,
];

const DESTRUCTIVE = [
  /\brm\s+(-\w*\s+)*-\w*[rf]/i,
  /\bdel\s+\/[sq]/i,
  /\brmdir\b/i,
  /\bformat\s+[a-z]:/i,
  /remove-item/i,
  /\btaskkill\b/i,
  /\bshutdown\b/i,
];

// Side effects that belong to Content OS's publishers, never to a generation run.
const SIDE_EFFECTS = [
  /\bgit\s+(commit|push|reset|checkout|clean|rebase|merge|tag|stash|restore|switch|am|apply)\b/i,
  /\bvercel\b/i,
  /\bgws(\.cmd|\.exe)?\b/i,
  /@googleworkspace[\\/]cli/i,
  /schedule\.py\s+write/i,
  /save_content\.py/i,
  /blog-writer[\\/]scripts[\\/]publish\.py/i,
  /kit-draft/i,
  /api\.buffer\.com/i,
  /api\.kit\.com|api\.convertkit\.com/i,
  /\bcurl\b[^|;&]*\s-(X|-request)\s*(POST|PUT|PATCH|DELETE)/i,
  /\bcurl\b[^|;&]*\s(-d|--data|--data-raw|--data-binary|-F|--form)\b/i,
  /invoke-(restmethod|webrequest)[^|;&]*-method\s+(post|put|patch|delete)/i,
  /\bnpm\s+(publish|i|install|ci|uninstall)\b/i,
  /\bnpx\s+vercel\b/i,
  /\bschtasks\b/i,
  /\breg\s+(add|delete)\b/i,
];

if (SENSITIVE.some((r) => r.test(haystack))) block(`sensitive path blocked (${tool})`);
if (DESTRUCTIVE.some((r) => r.test(haystack))) block(`destructive pattern blocked (${tool})`);

if (profile === "generate") {
  if (tool === "Bash" && SIDE_EFFECTS.some((r) => r.test(ti.command ?? ""))) {
    block("side-effecting command blocked: Content OS publishes, the generation run only writes files to its run folder");
  }
  if (["Write", "Edit", "MultiEdit", "NotebookEdit"].includes(tool)) {
    const target = ti.file_path || ti.notebook_path || "";
    if (!runDir || !target) block(`${tool} without a run folder`);
    const abs = path.resolve(target);
    const inside = (a, b) => {
      const rel = path.relative(b.toLowerCase(), a.toLowerCase());
      return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
    };
    if (!inside(abs, runDir)) block(`${tool} outside the run folder is blocked (${abs}); write to ${runDir}`);
  }
}

process.exit(0);

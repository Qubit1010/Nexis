import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url)); // server/
export const PROJECT_ROOT = path.resolve(HERE, "..");
export const NEXIS_ROOT = path.resolve(PROJECT_ROOT, "..", ".."); // projects/<name> -> repo root

export const VAULT =
  process.env.OBSIDIAN_VAULT_PATH || "C:\\Users\\qubit\\OneDrive\\Documents\\agency-brain";
export const PORT = Number(process.env.PORT || 4400);
// Per-profile ceilings: a live proposal run measured $0.58 on sonnet, so a
// single $0.50 ceiling would lock the console after every normal act run.
export const CEILING_USD = {
  read: Number(process.env.COMMAND_COST_CEILING_USD || 0.5),
  act: Number(process.env.COMMAND_COST_CEILING_ACT_USD || 1.0),
  chat: Number(process.env.COMMAND_COST_CEILING_CHAT_USD || 0.5),
} as const;
export const CLAUDE_BIN = process.env.CLAUDE_BIN || "claude";
// Headless runs default to the CLI's configured model (Opus) — a digest run
// measured $1.81. Sonnet is plenty for presets and skill actions.
export const RUN_MODEL = process.env.NCC_RUN_MODEL || "sonnet";
/** Test seam: JSON array of args injected before the standard ones (lets tests run `node fake-claude.mjs`). */
export const CLAUDE_BIN_ARGS: string[] = process.env.CLAUDE_BIN_ARGS
  ? JSON.parse(process.env.CLAUDE_BIN_ARGS)
  : [];

// NCC_RUNS_DIR: test seam so the suite never pollutes the real audit log.
export const RUNS_DIR = process.env.NCC_RUNS_DIR || path.join(PROJECT_ROOT, "runs");
export const WORKSPACE = path.join(RUNS_DIR, "workspace");
export const LOG_FILE = path.join(RUNS_DIR, "log.jsonl");
export const SETTINGS_FILES = {
  read: path.join(RUNS_DIR, "claude-settings-read.json"),
  act: path.join(RUNS_DIR, "claude-settings-act.json"),
  chat: path.join(RUNS_DIR, "claude-settings-chat.json"),
} as const;
export const DATA_FILE = path.join(PROJECT_ROOT, "data", "system-graph.json");
export const COMMANDS_FILE = path.join(PROJECT_ROOT, "commands.json");
// Registries are env-overridable so tests can point at fixtures.
export const PROJECTS_FILE = process.env.NCC_PROJECTS_FILE || path.join(PROJECT_ROOT, "projects.json");
export const SKILL_ACTIONS_FILE =
  process.env.NCC_SKILL_ACTIONS_FILE || path.join(PROJECT_ROOT, "skill-actions.json");
// act runs execute a whole skill end-to-end (research, scripts, Doc export) —
// they get double the wall clock. Ceiling + mutex are identical for both.
export const TIMEOUT_MS = { read: 5 * 60 * 1000, act: 10 * 60 * 1000, chat: 5 * 60 * 1000 } as const;

// Chat threads persist here (env seam for tests); message length is bounded
// because chat is the one freeform-prompt surface in the whole console.
export const CHAT_FILE = process.env.NCC_CHAT_FILE || path.join(RUNS_DIR, "chat-threads.json");
export const MAX_CHAT_CHARS = 8000;

// Brain panel: the brain-sync script is the single source of truth for
// freshness/drift — the server shells it rather than re-implementing.
export const PYTHON_BIN = process.env.NCC_PYTHON || "python";
export const SYNC_SCRIPT = path.join(NEXIS_ROOT, ".claude", "skills", "brain-sync", "scripts", "sync_vault.py");
/** Graph rescan command as argv (test seam: NCC_SCAN_CMD is a JSON array). */
export const SCAN_CMD: string[] = process.env.NCC_SCAN_CMD
  ? JSON.parse(process.env.NCC_SCAN_CMD)
  : [PYTHON_BIN, path.join(PROJECT_ROOT, "scripts", "build_system_graph.py")];

// Both profiles: the model can never read secrets or client-confidential paths.
const SENSITIVE_READS = [
  "Read(**/.env)",
  "Read(**/.env.*)",
  "Read(**/*.pem)",
  "Read(**/*.key)",
  "Read(**/id_rsa*)",
  "Read(**/.ssh/**)",
  "Read(**/credentials*)",
  "Read(**/client-projects/**)",
  "Read(**/settings.local.json)",
];

function settingsFor(profile: "read" | "act" | "chat", guard: string) {
  const base = {
    hooks: {
      PreToolUse: [
        {
          matcher: ".*",
          hooks: [{ type: "command", command: `node "${guard}" ${profile}` }],
        },
      ],
    },
  };
  if (profile === "chat") {
    // Chat advises, never acts (the "curated acts, chat advises" decision):
    // pure read tools, no Write at all — the freeform prompt surface gets the
    // tightest profile in the console.
    return {
      permissions: {
        allow: ["Read", "Glob", "Grep"],
        deny: [
          "Bash",
          "Write",
          "Edit",
          "Task",
          "WebFetch",
          "WebSearch",
          "NotebookEdit",
          ...SENSITIVE_READS,
        ],
        additionalDirectories: [NEXIS_ROOT, VAULT],
      },
      ...base,
    };
  }
  if (profile === "read") {
    return {
      permissions: {
        // Only these four ever get auto-approved; headless runs cannot prompt,
        // so everything else is implicitly denied.
        allow: ["Read", "Glob", "Grep", "Write(./**)"],
        deny: [
          "Bash",
          "WebFetch",
          "WebSearch",
          "Task",
          "Edit",
          "NotebookEdit",
          ...SENSITIVE_READS,
        ],
        additionalDirectories: [NEXIS_ROOT, VAULT],
      },
      ...base,
    };
  }
  // act: curated skill actions may run their scripts (python/gws) and edit
  // files — the hook-guard still blocks sensitive paths and destructive
  // commands, and the ceiling/timeout/mutex apply unchanged.
  return {
    permissions: {
      allow: ["Read", "Glob", "Grep", "Write", "Edit", "Bash", "Task", "WebSearch"],
      deny: ["WebFetch", "NotebookEdit", ...SENSITIVE_READS],
      additionalDirectories: [NEXIS_ROOT, VAULT],
    },
    ...base,
  };
}

/**
 * runs/ is gitignored and fully regenerable: workspace dir + the per-profile
 * settings files for spawned `claude -p` runs are (re)written here on every
 * boot so absolute paths are always correct for this machine.
 */
export function ensureRunFiles(): void {
  fs.mkdirSync(WORKSPACE, { recursive: true });
  const guard = path.join(PROJECT_ROOT, "server", "hook-guard.mjs");
  for (const profile of ["read", "act", "chat"] as const) {
    fs.writeFileSync(SETTINGS_FILES[profile], JSON.stringify(settingsFor(profile, guard), null, 2));
  }
}

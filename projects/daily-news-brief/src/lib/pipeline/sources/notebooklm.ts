import { spawn } from "child_process";
import { resolve } from "path";
import type { RawArticle } from "./types";

/**
 * Thin wrapper around the `notebooklm-py` CLI for live, grounded tool lookups.
 *
 * Flow per lookup: create a throwaway notebook -> fast web research (imports
 * real docs/blogs/videos as sources) -> grounded ask for a synthesis -> delete
 * the notebook. Returns the grounded answer + the imported sources (with URLs)
 * so the caller can format them into the dashboard's JSON shape.
 *
 * Sessions expire periodically; every function fails soft (returns null/[]) so
 * the caller can fall back to the deterministic web/GitHub sources.
 */

function nlmExe(): string {
  return (
    process.env.NOTEBOOKLM_EXE ||
    "C:/Users/qubit/AppData/Local/Programs/Python/Python312/Scripts/notebooklm.exe"
  );
}

const CMD_TIMEOUT_MS = 120_000;

interface NlmCreateResult {
  notebook?: { id?: string };
}

interface NlmResearchSource {
  url?: string;
  title?: string;
}
interface NlmImportedSource {
  id?: string;
  title?: string;
}
interface NlmResearchResult {
  status?: string;
  sources_found?: number;
  sources?: NlmResearchSource[];
  imported?: number;
  imported_sources?: NlmImportedSource[];
}

interface NlmReference {
  source_id?: string;
  citation_number?: number;
}
interface NlmAskResult {
  answer?: string;
  references?: NlmReference[];
}

export interface NotebookLmLookup {
  /** Grounded prose synthesis with inline [n] citations. */
  synthesis: string;
  /** Imported research sources (real URLs: docs, blogs, videos, threads). */
  sources: RawArticle[];
  /** Source IDs that the synthesis actually cited (most relevant subset). */
  citedSourceIds: string[];
  /** Public NotebookLM link to the notebook, so the lookup is verifiable. */
  notebookUrl: string;
}

/**
 * Exact source URLs to drop from every lookup. These are low-signal landing
 * pages that NotebookLM keeps surfacing but add nothing over better sources.
 */
const IGNORED_URLS = new Set<string>([
  "https://code.claude.com/docs/en/plugins",
  "https://code.claude.com/docs/en/overview",
]);

/** Entire hostnames to drop (any path under them). www. is stripped first. */
const IGNORED_DOMAINS = new Set<string>([
  "code.claude.com",
]);

export function isIgnoredUrl(url: string): boolean {
  const stripped = url.replace(/[#?].*$/, "").replace(/\/$/, "");
  if (IGNORED_URLS.has(url) || IGNORED_URLS.has(stripped)) return true;
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (IGNORED_DOMAINS.has(host)) return true;
  } catch {
    /* malformed url - keep it */
  }
  return false;
}

function notebookUrlFor(id: string): string {
  return `https://notebooklm.google.com/notebook/${id}`;
}

// --- low-level spawn -------------------------------------------------------

function runNlm(args: string[]): Promise<unknown | null> {
  const exe = nlmExe();
  return new Promise((resolvePromise) => {
    const child = spawn(exe, args, {
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      timeout: CMD_TIMEOUT_MS,
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString("utf-8")));
    child.stderr.on("data", (d) => (stderr += d.toString("utf-8")));

    child.on("error", (err) => {
      console.warn(`[NotebookLM] spawn error (${args[0]}):`, err.message);
      resolvePromise(null);
    });

    child.on("close", (code) => {
      // Extract the JSON object even if log lines precede it.
      const start = stdout.indexOf("{");
      const end = stdout.lastIndexOf("}");
      if (start === -1 || end === -1 || end < start) {
        if (code !== 0) {
          console.warn(
            `[NotebookLM] "${args[0]}" exited ${code}: ${stderr.trim().split("\n").slice(-2).join(" | ")}`
          );
        }
        resolvePromise(null);
        return;
      }
      try {
        const parsed = JSON.parse(stdout.slice(start, end + 1));
        // CLI signals auth/errors with {error:true,...}
        if (parsed && typeof parsed === "object" && (parsed as { error?: boolean }).error) {
          console.warn(
            `[NotebookLM] "${args[0]}" error:`,
            (parsed as { message?: string }).message || "unknown"
          );
          resolvePromise(null);
          return;
        }
        resolvePromise(parsed);
      } catch {
        console.warn(`[NotebookLM] "${args[0]}" returned non-JSON`);
        resolvePromise(null);
      }
    });
  });
}

// --- operations ------------------------------------------------------------

async function createNotebook(title: string): Promise<string | null> {
  const res = (await runNlm(["create", title, "--json"])) as NlmCreateResult | null;
  return res?.notebook?.id ?? null;
}

async function addResearch(
  notebookId: string,
  query: string
): Promise<NlmResearchResult | null> {
  return (await runNlm([
    "source",
    "add-research",
    query,
    "--from",
    "web",
    "--mode",
    "fast",
    "--import-all",
    "--json",
    "-n",
    notebookId,
  ])) as NlmResearchResult | null;
}

async function ask(
  notebookId: string,
  question: string
): Promise<NlmAskResult | null> {
  return (await runNlm([
    "ask",
    question,
    "--json",
    "-n",
    notebookId,
  ])) as NlmAskResult | null;
}

async function deleteNotebook(notebookId: string): Promise<void> {
  await runNlm(["delete", "-n", notebookId, "--yes", "--json"]);
}

async function deleteSource(notebookId: string, sourceId: string): Promise<void> {
  await runNlm(["source", "delete", sourceId, "-n", notebookId, "--yes", "--json"]);
}

/**
 * Delete any imported source whose URL is in IGNORED_URLS from the notebook.
 * Maps research result URLs -> imported source IDs by matching titles.
 */
async function removeIgnoredSources(
  notebookId: string,
  research: NlmResearchResult | null
): Promise<void> {
  if (!research) return;
  const ignoredTitles = new Set(
    (research.sources || [])
      .filter((s) => s.url && s.title && isIgnoredUrl(s.url))
      .map((s) => s.title!)
  );
  if (ignoredTitles.size === 0) return;
  const ids = (research.imported_sources || [])
    .filter((s) => s.id && s.title && ignoredTitles.has(s.title))
    .map((s) => s.id!);
  for (const id of ids) {
    await deleteSource(notebookId, id);
    console.log(`[NotebookLM] removed ignored source ${id} from notebook`);
  }
}

// --- high-level lookup -----------------------------------------------------

/**
 * Run a grounded NotebookLM lookup for a tool. Returns null on any failure
 * (auth expired, timeout, no sources) so the caller can fall back.
 */
export async function notebookLmLookup(
  tool: string,
  days: number
): Promise<NotebookLmLookup | null> {
  const title = `Tool Lookup: ${tool} (${new Date().toISOString().slice(0, 10)})`;
  const notebookId = await createNotebook(title);
  if (!notebookId) {
    console.warn("[NotebookLM] Could not create notebook (auth/expired?) - falling back");
    return null;
  }

  try {
    const researchQuery = `"${tool}" - focus strictly and only on "${tool}". Find the best and most notable specific "${tool}" (named examples), recent updates from the last ${days} days, official documentation, tutorials, and real-world usage of "${tool}". Exclude adjacent or tangential topics that are not directly about "${tool}".`;
    const research = await addResearch(notebookId, researchQuery);

    // Hard-remove ignored URLs from the notebook itself so they never appear
    // in the sources tab, never get cited, and never reach the dashboard.
    await removeIgnoredSources(notebookId, research);

    const sources: RawArticle[] = (research?.sources || [])
      .filter((s) => s.url && s.title && !isIgnoredUrl(s.url))
      .map((s) => ({
        title: s.title!,
        url: s.url!,
        source: hostLabel(s.url!),
        sourceOrigin: "notebooklm" as const,
        publishedAt: new Date().toISOString(),
        description: "",
        topic: tool,
      }));

    if (sources.length === 0) {
      console.warn("[NotebookLM] No sources imported - falling back");
      return null;
    }

    const question = `Based strictly on the sources, answer for "${tool}": (1) what it is right now and what's notable in the last ${days} days, (2) the best/most notable options, plugins, or extensions available now with specifics, and (3) how people actually use it to solve real business problems, with concrete steps. Be specific and practical, cite sources.`;
    const answer = await ask(notebookId, question);

    if (!answer?.answer) {
      console.warn("[NotebookLM] No grounded answer - falling back");
      return null;
    }

    // Map cited source_ids -> their URLs via imported_sources titles.
    const idToTitle = new Map<string, string>();
    for (const s of research?.imported_sources || []) {
      if (s.id && s.title) idToTitle.set(s.id, s.title);
    }
    const titleToUrl = new Map<string, string>();
    for (const s of research?.sources || []) {
      if (s.title && s.url) titleToUrl.set(s.title, s.url);
    }
    const citedSourceIds = Array.from(
      new Set((answer.references || []).map((r) => r.source_id).filter((id): id is string => !!id))
    );

    // Reorder sources so cited ones come first (more relevant).
    const citedUrls = new Set(
      citedSourceIds
        .map((id) => idToTitle.get(id))
        .map((t) => (t ? titleToUrl.get(t) : undefined))
        .filter((u): u is string => !!u)
    );
    sources.sort((a, b) => Number(citedUrls.has(b.url)) - Number(citedUrls.has(a.url)));

    console.log(
      `[NotebookLM] "${tool}" -> ${sources.length} sources, ${citedSourceIds.length} cited`
    );

    return {
      synthesis: answer.answer,
      sources,
      citedSourceIds,
      notebookUrl: notebookUrlFor(notebookId),
    };
  } catch (err) {
    // On failure, clean up the throwaway notebook so it doesn't linger.
    deleteNotebook(notebookId).catch(() => {});
    console.warn("[NotebookLM] lookup failed:", (err as Error)?.message);
    return null;
  }
}

function hostLabel(url: string): string {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (host.includes("reddit.com")) return "Reddit";
    if (host.includes("youtube.com") || host.includes("youtu.be")) return "YouTube";
    if (host.includes("github.com")) return "GitHub";
    return host;
  } catch {
    return "Web";
  }
}

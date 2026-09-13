import fs from "node:fs";
import path from "node:path";
import type { PriceBook, Rubric, SourceRegistry } from "./types";

/**
 * The rubric is data, not a prompt string, so it can be versioned, cited and
 * diffed. rubric/ is tracked in git because it is the product; data/ is not,
 * because it holds client revenue figures.
 */

const RUBRIC_DIR = path.join(process.cwd(), "rubric");

function load<T>(file: string): T {
  const full = path.join(RUBRIC_DIR, file);
  try {
    return JSON.parse(fs.readFileSync(full, "utf-8")) as T;
  } catch (err) {
    throw new Error(
      `Could not load ${file} from ${RUBRIC_DIR}. The rubric is required; the app cannot score without it. Original error: ${
        err instanceof Error ? err.message : String(err)
      }`
    );
  }
}

let _rubric: Rubric | null = null;
let _pricebook: PriceBook | null = null;
let _sources: SourceRegistry | null = null;

export function getRubric(): Rubric {
  if (!_rubric) _rubric = load<Rubric>("rubric.v1.json");
  return _rubric;
}

export function getPriceBook(): PriceBook {
  if (!_pricebook) _pricebook = load<PriceBook>("pricebook.v1.json");
  return _pricebook;
}

export function getSources(): SourceRegistry {
  if (!_sources) _sources = load<SourceRegistry>("sources.json");
  return _sources;
}

/** Everything the client needs to render scores with their citations. */
export function getRubricBundle() {
  return {
    rubric: getRubric(),
    pricebook: getPriceBook(),
    sources: getSources().sources,
  };
}

/** Resolves source ids to full citations. An unknown id is surfaced, never dropped. */
export function resolveSources(ids: string[]) {
  const registry = getSources().sources;
  return ids.map((id) => {
    const s = registry[id];
    if (!s) {
      return {
        id,
        title: `UNKNOWN SOURCE (${id})`,
        publisher: "",
        url: "",
        kind: "missing",
        caveat: "This citation does not resolve. Treat the claim as unsourced.",
      };
    }
    return { id, ...s };
  });
}

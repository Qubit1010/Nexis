// Content OS re-runs the hard checks itself instead of trusting the model's
// claim that it ran them. A fail blocks approval only through the reviewer's
// eyes: checks inform the Review screen, they never silently rewrite content.
import { spawnSync } from "node:child_process";
import path from "node:path";
import { NEXIS_ROOT, PYTHON_BIN } from "../config.ts";

export interface Check {
  id: string;
  level: "pass" | "warn" | "fail";
  message: string;
}

const EMOJI = /\p{Extended_Pictographic}/u;
const PERSONAL_BANNED = [/nexus\s*-?\s*point/i, /\bbsai\b/i, /\biqra\b/i, /\buniversity\b/i, /\bsemester\b/i];

export function splitFrontmatter(md: string): { fm: string | null; body: string } {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { fm: null, body: md };
  return { fm: m[1], body: md.slice(m[0].length) };
}

/** Top-level scalar value of a frontmatter key (enough for checks; the site build is the real schema gate). */
export function fmValue(fm: string, key: string): string | null {
  const m = fm.match(new RegExp(`^${key}:\\s*(.*)$`, "m"));
  if (!m) return null;
  return m[1].trim().replace(/^["']|["']$/g, "");
}

function stripCode(s: string): string {
  return s.replace(/```[\s\S]*?```/g, "").replace(/`[^`]*`/g, "");
}

export function runChecks(
  format: string,
  text: string,
  opts: { edition?: string; voice?: string; categories?: string[]; mainFile?: string; sourceUrl?: string | null } = {},
): Check[] {
  const out: Check[] = [];
  const add = (id: string, level: Check["level"], message: string) => out.push({ id, level, message });
  const { fm, body } = splitFrontmatter(text);
  const prose = stripCode(format === "li_newsletter" ? text.split("<!-- end issue -->")[0] : body);

  if (/[—–]/.test(prose)) add("no_dashes", "fail", "Em or en dash in the body. Use commas or periods.");
  else add("no_dashes", "pass", "No em or en dashes.");
  if (EMOJI.test(prose)) add("no_emoji", "fail", "Emoji in the body.");
  if (/[‘’“”]/.test(prose)) add("no_smart_quotes", "warn", "Smart quotes in the body (Docs and LinkedIn can mangle them).");
  const todo = prose.match(/\[(?:[^\]]*\b(?:TODO|TBD)\b[^\]]*)\]/i);
  if (todo) add("placeholders", "fail", `Unfilled placeholder: ${todo[0]}`);

  const personal = format === "linkedin_post" || format === "personal_blog" || (format === "li_newsletter" && opts.edition !== "agency");
  if (personal) {
    const hit = PERSONAL_BANNED.map((r) => prose.match(r)).find(Boolean);
    if (hit) add("personal_brand_terms", "fail", `Personal-brand content names "${hit[0]}". The agency, university and degree stay out.`);
    else add("personal_brand_terms", "pass", "No agency or university mentions.");
  }

  if (format === "linkedin_post") {
    const n = [...body.trim()].length;
    if (n > 3000) add("li_length", "fail", `${n} characters. LinkedIn caps posts at 3,000.`);
    else add("li_length", "pass", `${n} characters.`);
    if (/^#{1,6}\s/m.test(body) || /\*\*[^*]+\*\*/.test(body)) {
      add("li_markdown", "warn", "Markdown headings or bold: LinkedIn shows them as literal symbols.");
    }
  }

  if (format === "personal_blog" || format === "agency_blog") {
    if (!fm) add("frontmatter", "fail", "No YAML frontmatter. The site build needs it.");
    else {
      for (const key of ["title", "excerpt", "datePublished", "dateModified"]) {
        if (!fmValue(fm, key)) add(`fm_${key}`, "fail", `Frontmatter is missing ${key}.`);
      }
      const cat = fmValue(fm, "category");
      if (cat && opts.categories?.length && !opts.categories.includes(cat)) {
        add("fm_category", "fail", `Category "${cat}" is not one of: ${opts.categories.join(", ")}.`);
      }
      const excerpt = fmValue(fm, "excerpt") || "";
      if (excerpt && (excerpt.length < 105 || excerpt.length > 160)) add("fm_excerpt_len", "warn", `Excerpt is ${excerpt.length} chars; the meta range is 105-155.`);
      const seoTitle = fmValue(fm, "seoTitle") || "";
      if (seoTitle && (seoTitle.length < 40 || seoTitle.length > 62)) add("fm_seo_title_len", "warn", `seoTitle is ${seoTitle.length} chars; aim for 50-60.`);
    }
    if (/^#\s/m.test(body)) add("no_h1", "fail", "The body has an H1. The layout renders the title; use H2s.");
    if (/^##\s+SEO Metadata/m.test(body)) add("no_meta_block", "fail", "The SEO Metadata block belongs in seo-metadata.md, not the post.");
    const words = (body.match(/[A-Za-z0-9']+/g) || []).length;
    add("word_count", words < 600 ? "warn" : "pass", `${words} words.`);
  }

  if (format === "li_newsletter" && opts.mainFile) {
    const args = [path.join(NEXIS_ROOT, ".claude/skills/linkedin-newsletter/scripts/check_issue.py"), opts.mainFile, "--edition", opts.edition === "agency" ? "agency" : "personal"];
    if (opts.sourceUrl) args.push("--source-url", opts.sourceUrl);
    const r = spawnSync(PYTHON_BIN, args, { encoding: "utf8", env: { ...process.env, PYTHONIOENCODING: "utf-8" }, timeout: 60_000 });
    const lines = `${r.stdout || ""}`.split(/\r?\n/).filter(Boolean);
    if (!lines.some((l) => l.startsWith("checked:"))) add("check_issue", "fail", `check_issue.py did not run: ${(r.stderr || r.error?.message || "").slice(0, 200)}`);
    else {
      for (const l of lines) {
        if (l.startsWith("FAIL:")) add("check_issue", "fail", l.slice(5).trim());
        else if (l.startsWith("WARN:")) add("check_issue", "warn", l.slice(5).trim());
      }
      if (r.status === 0) add("check_issue", "pass", lines[0]);
    }
  }
  return out;
}

export const hasFails = (checks: Check[]) => checks.some((c) => c.level === "fail");

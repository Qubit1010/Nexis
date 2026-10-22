import fs from "node:fs";
import path from "node:path";
import { z } from "zod";
import { PROMPTS_DIR } from "../config.ts";
import { fmtClock, fmtSheetDate, pktParts } from "../lib/time.ts";
import type { Format } from "../settings.ts";
import { FORMAT_LABELS } from "../settings.ts";

export const OutputSchema = z.object({
  status: z.enum(["ok", "blocked"]),
  blocked_reason: z.string().nullish(),
  rescue: z.string().nullish(),
  gate: z.record(z.string(), z.unknown()).nullish(),
  title: z.string().min(1),
  files: z.object({ main: z.string().min(1), extra: z.array(z.string()).default([]) }),
  meta: z.record(z.string(), z.unknown()).default({}),
  sources: z.array(z.object({ url: z.string(), title: z.string().nullish() })).default([]),
  notes_for_reviewer: z.string().nullish(),
});
export type EngineOutput = z.infer<typeof OutputSchema>;

export interface ItemContext {
  item: { id: string; format: string; title: string; briefJson: string; scheduledFor: string | null };
  idea: { title: string; summary: string | null; url: string | null; source: string; payloadJson: string | null } | null;
  channel: { name: string; configJson: string } | null;
  dependsOn: { title: string; publishedUrl: string | null; localFile: string | null } | null;
  revision: { previousFile: string; feedback: string } | null;
}

export function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 70)
    .replace(/-+$/g, "");
}

export function buildInput(ctx: ItemContext, runDir: string): Record<string, unknown> {
  const brief = safeParse(ctx.item.briefJson);
  const channelCfg = ctx.channel ? safeParse(ctx.channel.configJson) : {};
  const when = ctx.item.scheduledFor;
  return {
    source: "content-os",
    itemId: ctx.item.id,
    format: ctx.item.format,
    formatLabel: FORMAT_LABELS[ctx.item.format as Format] ?? ctx.item.format,
    channel: ctx.channel ? { name: ctx.channel.name, ...pick(channelCfg, ["siteUrl", "categories", "edition", "voice"]) } : null,
    topic: brief.topic || ctx.item.title,
    description: brief.description || ctx.idea?.summary || "",
    reference: brief.reference || ctx.idea?.url || "",
    contentMode: brief.contentMode || "",
    pillar: brief.pillar || "",
    designTemplate: brief.designTemplate || "",
    notes: brief.notes || "",
    scheduledFor: when ? `${fmtSheetDate(when)} ${pktParts(when).y}, ${fmtClock(when)} PKT` : "unscheduled",
    idea: ctx.idea
      ? { title: ctx.idea.title, summary: ctx.idea.summary, url: ctx.idea.url, source: ctx.idea.source, details: safeParse(ctx.idea.payloadJson) }
      : null,
    dependsOn: ctx.dependsOn,
    revision: ctx.revision ? { previousVersionFile: ctx.revision.previousFile, feedback: ctx.revision.feedback } : null,
    runDir,
  };
}

function fill(template: string, vars: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? "");
}

export function buildPrompt(ctx: ItemContext, runDir: string, input: Record<string, unknown>): string {
  const format = ctx.item.format as Format;
  const template = fs.readFileSync(path.join(PROMPTS_DIR, `${format}.md`), "utf8");
  const cfg = ctx.channel ? safeParse(ctx.channel.configJson) : {};
  const when = ctx.item.scheduledFor ?? new Date().toISOString();
  const p = pktParts(when);
  const publishDate = `${p.y}-${String(p.m).padStart(2, "0")}-${String(p.d).padStart(2, "0")}`;
  const edition = String(cfg.edition || "personal");
  const sourceUrl = ctx.dependsOn?.publishedUrl || "";
  const vars: Record<string, string> = {
    RUN_DIR: runDir.replace(/\\/g, "/"),
    INPUT_JSON: JSON.stringify(input, null, 2),
    SLUG_HINT: slugify(String(input.topic || ctx.item.title)) || "post",
    CATEGORIES: Array.isArray(cfg.categories) ? cfg.categories.map((c: string) => `\`${c}\``).join(", ") : "the site's categories",
    PUBLISH_DATE: publishDate,
    EDITION: edition,
    CHANNEL_NAME: ctx.channel?.name ?? "",
    EDITION_RULES:
      edition === "agency"
        ? "Agency edition: NexusPoint voice from `agency/14-brand-voice.md`, the agency name is allowed, the one CTA is \"Subscribe to this newsletter\"."
        : "Personal edition (Notes from the Workbench): Aleem's personal-brand voice, never name the agency, one aleemuh.com CTA.",
    SOURCE_LINE: ctx.dependsOn
      ? `the published blog post "${ctx.dependsOn.title}" at ${sourceUrl}${ctx.dependsOn.localFile ? ` (local file: ${ctx.dependsOn.localFile.replace(/\\/g, "/")})` : ""}. Write a condensed edition with a backlink to that URL.`
      : "a bare topic (the brief). Run the gate first and get sources from the research skill.",
    SOURCE_URL_ARG: sourceUrl ? ` --source-url ${sourceUrl}` : "",
  };
  let prompt = fill(template, vars);
  if (ctx.revision) {
    prompt += `\n\n## This is a revision\n\nThe previous version is \`${ctx.revision.previousFile.replace(/\\/g, "/")}\`. The reviewer's feedback:\n\n> ${ctx.revision.feedback.replace(/\n/g, "\n> ")}\n\nRevise, don't rewrite: keep everything the feedback does not touch, especially first-hand details and real numbers. Re-run only the research the feedback needs. Write the full revised files and a fresh output.json.`;
  }
  return prompt;
}

export function readOutput(runDir: string): { output: EngineOutput; main: string } {
  const file = path.join(runDir, "output.json");
  if (!fs.existsSync(file)) throw new Error("the run finished without writing output.json");
  const parsed = OutputSchema.safeParse(JSON.parse(fs.readFileSync(file, "utf8")));
  if (!parsed.success) throw new Error(`output.json is invalid: ${parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ")}`);
  const output = parsed.data;
  const mainPath = resolveInside(runDir, output.files.main);
  if (!fs.existsSync(mainPath)) throw new Error(`output.json names ${output.files.main}, which does not exist`);
  return { output, main: fs.readFileSync(mainPath, "utf8") };
}

/** Run-relative path -> absolute, refusing anything that escapes the run folder. */
export function resolveInside(runDir: string, rel: string): string {
  const abs = path.resolve(runDir, rel);
  const r = path.relative(runDir, abs);
  if (r.startsWith("..") || path.isAbsolute(r)) throw new Error(`path escapes the run folder: ${rel}`);
  return abs;
}

export function safeParse(raw: string | null | undefined): Record<string, any> {
  if (!raw) return {};
  try {
    const v = JSON.parse(raw);
    return v && typeof v === "object" ? v : {};
  } catch {
    return {};
  }
}

function pick(o: Record<string, unknown>, keys: string[]): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const k of keys) if (o[k] !== undefined) out[k] = o[k];
  return out;
}

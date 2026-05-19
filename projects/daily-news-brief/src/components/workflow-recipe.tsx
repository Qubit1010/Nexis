"use client";

import { useState } from "react";
import { Terminal, Clock, Gauge, Copy, Check } from "lucide-react";
import { CardActions, mdFilename } from "./card-actions";

export interface WorkflowRecipeStep {
  step: string;
  commandOrPrompt: string;
  expectedOutcome: string;
}

export interface WorkflowRecipeData {
  id: number;
  title: string;
  subtitle: string;
  scenario: string;
  agent: string;
  toolsUsed: string[];
  steps: WorkflowRecipeStep[];
  timeSaved: string | null;
  difficulty: string | null;
  audienceHook: string;
}

const DIFFICULTY_STYLES: Record<string, string> = {
  beginner: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  intermediate: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  advanced: "bg-rose-500/15 text-rose-400 border-rose-500/25",
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      // ignore
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="text-[10px] font-medium text-muted-foreground/60 hover:text-foreground inline-flex items-center gap-1 px-2 py-0.5 rounded border border-border/40 hover:border-border transition-all duration-200"
      title="Copy to clipboard"
    >
      {copied ? (
        <>
          <Check className="w-3 h-3" /> Copied
        </>
      ) : (
        <>
          <Copy className="w-3 h-3" /> Copy
        </>
      )}
    </button>
  );
}

export function WorkflowRecipe({
  recipe,
  briefDate,
}: {
  recipe: WorkflowRecipeData;
  briefDate: string;
}) {
  const diffClass = recipe.difficulty
    ? DIFFICULTY_STYLES[recipe.difficulty] || DIFFICULTY_STYLES.beginner
    : DIFFICULTY_STYLES.beginner;

  const recipeMarkdown = () =>
    [
      `# ${recipe.title}`,
      "",
      recipe.subtitle ? `_${recipe.subtitle}_` : "",
      "",
      `**Agent:** ${recipe.agent}`,
      recipe.timeSaved ? `**Time saved:** ${recipe.timeSaved}` : "",
      recipe.difficulty ? `**Difficulty:** ${recipe.difficulty}` : "",
      "",
      `## Scenario`,
      recipe.scenario,
      "",
      ...(recipe.toolsUsed.length > 0
        ? [`## Tools used`, ...recipe.toolsUsed.map((t) => `- ${t}`), ""]
        : []),
      `## Steps`,
      ...recipe.steps.flatMap((s, i) => [
        `### ${i + 1}. ${s.step}`,
        "",
        s.commandOrPrompt ? "```" : "",
        s.commandOrPrompt || "",
        s.commandOrPrompt ? "```" : "",
        "",
        s.expectedOutcome ? `_Expected: ${s.expectedOutcome}_` : "",
        "",
      ]),
      recipe.audienceHook ? `## Audience hook\n> ${recipe.audienceHook}` : "",
      "",
    ]
      .filter((l) => l !== "")
      .join("\n") + "\n";

  return (
    <div className="rounded-2xl border border-violet-500/30 bg-gradient-to-br from-violet-500/[0.08] via-transparent to-transparent p-6 sm:p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center shrink-0">
          <Terminal className="w-5 h-5 text-violet-400" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-violet-400/90 mb-1">
              Workflow Recipe of the Day
            </p>
            <CardActions
              id={`recipe-${recipe.id}`}
              storageKey="tools-brief-used-recipes"
              markdownFilename={mdFilename(recipe.title, "recipe")}
              buildMarkdown={recipeMarkdown}
              buildSheetPayload={() => ({
                briefDate,
                title: recipe.title,
                format: "tutorial",
                timeliness: "evergreen",
                angle: recipe.scenario,
                hook: recipe.audienceHook || recipe.subtitle,
                keyPoints: recipe.steps.map(
                  (s) => `${s.step}${s.expectedOutcome ? ` -> ${s.expectedOutcome}` : ""}`
                ),
                relatedTrends: recipe.toolsUsed,
              })}
            />
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight leading-tight">
            {recipe.title}
          </h2>
          {recipe.subtitle && (
            <p className="text-sm text-muted-foreground mt-1">
              {recipe.subtitle}
            </p>
          )}
        </div>
      </div>

      {/* Meta strip */}
      <div className="flex flex-wrap items-center gap-2 mb-5">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-violet-300 bg-violet-500/15 border border-violet-500/25 px-2.5 py-1 rounded-full inline-flex items-center gap-1">
          <Terminal className="w-3 h-3" />
          {recipe.agent}
        </span>
        {recipe.timeSaved && (
          <span className="text-[11px] font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded-full inline-flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Saves {recipe.timeSaved}
          </span>
        )}
        {recipe.difficulty && (
          <span
            className={`text-[11px] font-medium px-2.5 py-1 rounded-full border inline-flex items-center gap-1 ${diffClass}`}
          >
            <Gauge className="w-3 h-3" />
            {recipe.difficulty}
          </span>
        )}
      </div>

      {/* Scenario */}
      <div className="mb-5">
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/60 mb-1.5">
          Scenario
        </p>
        <p className="text-sm leading-relaxed">{recipe.scenario}</p>
      </div>

      {/* Tools used */}
      {recipe.toolsUsed.length > 0 && (
        <div className="mb-5 flex items-center gap-2 flex-wrap">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/60">
            Tools:
          </p>
          {recipe.toolsUsed.map((t) => (
            <span
              key={t}
              className="text-[11px] font-medium text-muted-foreground bg-muted/40 px-2 py-0.5 rounded"
            >
              {t}
            </span>
          ))}
        </div>
      )}

      {/* Steps */}
      <div className="space-y-3">
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/60">
          Steps ({recipe.steps.length})
        </p>
        {recipe.steps.map((s, i) => (
          <div
            key={i}
            className="rounded-lg border border-border/50 bg-card/40 p-4"
          >
            <div className="flex items-start gap-3 mb-2">
              <span className="shrink-0 w-6 h-6 rounded-full bg-violet-500/15 text-violet-400 text-[12px] font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </span>
              <p className="text-sm font-medium leading-snug min-w-0">
                {s.step}
              </p>
            </div>

            {s.commandOrPrompt && (
              <div className="ml-9 mb-2 relative group/code">
                <pre className="rounded-md bg-zinc-950 border border-white/[0.05] text-zinc-300 text-[12px] font-mono px-3 py-2.5 overflow-x-auto whitespace-pre-wrap break-words leading-relaxed">
                  {s.commandOrPrompt}
                </pre>
                <div className="absolute top-1.5 right-1.5 opacity-0 group-hover/code:opacity-100 transition-opacity">
                  <CopyButton text={s.commandOrPrompt} />
                </div>
              </div>
            )}

            {s.expectedOutcome && (
              <p className="ml-9 text-xs text-muted-foreground italic leading-relaxed">
                → {s.expectedOutcome}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Audience hook */}
      {recipe.audienceHook && (
        <div className="mt-5 rounded-lg border border-amber-500/20 bg-amber-500/[0.04] px-4 py-3">
          <p className="text-[10px] font-semibold text-amber-500/80 uppercase tracking-[0.15em] mb-1">
            Audience Hook
          </p>
          <p className="text-sm font-medium italic leading-snug">
            "{recipe.audienceHook}"
          </p>
        </div>
      )}
    </div>
  );
}

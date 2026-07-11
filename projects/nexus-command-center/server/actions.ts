import fs from "node:fs";
import * as cfg from "./config.ts";
import { HttpError, type RunSpec } from "./spawn.ts";

/**
 * Skill quick-actions: curated prompt templates with one or more bounded
 * input slots. The template and skill routing stay server-side; the browser
 * only ever sends an action id + the input values (validated + length-capped
 * here). Runs go through the same startRun engine as deck presets, on the
 * "act" profile.
 */

export interface ActionInput {
  name: string;
  label: string;
  placeholder?: string;
  multiline?: boolean;
}

export interface SkillAction {
  id: string;
  label: string;
  description: string;
  skill: string;
  inputs: ActionInput[];
  prompt_template: string;
  profile: "act";
}

const MAX_INPUT_CHARS = 6000;

export function loadActions(): SkillAction[] {
  return JSON.parse(fs.readFileSync(cfg.SKILL_ACTIONS_FILE, "utf8")) as SkillAction[];
}

export function buildActionRun(id: unknown, inputs: Record<string, unknown>): RunSpec {
  const action = loadActions().find((a) => a.id === id);
  if (!action) throw new HttpError(400, "UNKNOWN_ACTION", `unknown skill action: ${String(id)}`);

  let prompt = action.prompt_template;
  for (const def of action.inputs) {
    const v = inputs?.[def.name];
    if (typeof v !== "string" || !v.trim()) {
      throw new HttpError(400, "MISSING_INPUT", `missing input: ${def.name}`);
    }
    if (v.length > MAX_INPUT_CHARS) {
      throw new HttpError(400, "INPUT_TOO_LONG", `${def.name} exceeds ${MAX_INPUT_CHARS} chars`);
    }
    prompt = prompt.split(`{${def.name}}`).join(v.trim());
  }
  return { id: action.id, label: action.label, prompt, profile: "act" };
}

/** Data contract shared between content.json, the prepare script, and the composition. */

export type SceneType =
  | "intro"
  | "problem"
  | "solution"
  | "stats"
  | "punch"
  | "outro";

export interface StatItem {
  value: number; // numeric target for the count-up animation
  suffix?: string; // e.g. "%"
  prefix?: string; // e.g. "$"
  label: string; // caption under the number
}

/** One stage of a native animated funnel (the motion rebuild of a funnel infographic). */
export interface FunnelStage {
  name: string; // e.g. "Awareness"
  goal?: string; // short one-liner, e.g. "Get discovered"
}

/** A floating callout pill that points at an element in a scene (cinematic annotation). */
export interface CalloutSpec {
  text: string; // e.g. "60% avg fill"
  /** 0-based index of the stage / node / stat the callout points at. */
  at?: number;
}

export interface Scene {
  id: string;
  type: SceneType;
  /** The portion of the voiceover spoken during this scene. Concatenated in
   *  order, scenes[].voiceText must equal content.voiceScript exactly. */
  voiceText: string;
  headline?: string;
  sub?: string;
  /** Optional keyword/command chips for the Problem scene (e.g. ["grep","glob","read"]).
   *  Leave empty/omit for non-technical posts — the scene then shows just headline + sub.
   *  Also used as the line items for the "crossout" problem variant. */
  chips?: string[];
  /** Problem-scene treatment, picked per post so the pain beat varies across reels:
   *  "chips" (default) | "crossout" (struck list) | "glitch" (glitching headline). */
  problemVariant?: "chips" | "crossout" | "glitch";
  /** Punch-scene treatment, picked per post so the payoff beat varies across reels:
   *  "rule" (default) | "quote" (mantra) | "spotlight" (radial glow emphasis). */
  punchVariant?: "rule" | "quote" | "spotlight";
  /** Filename inside the reel's public folder (e.g. "infographic.png"). */
  asset?: string;
  /** Solution scene visual: "infographic" pans the raw image (default);
   *  "funnel" | "roadmap" | "layers" render native motion rebuilds instead. */
  visual?: "infographic" | "funnel" | "roadmap" | "layers";
  /** Stages for the native funnel when visual === "funnel". */
  funnel?: FunnelStage[];
  /** Phases for the native roadmap when visual === "roadmap". */
  roadmap?: FunnelStage[];
  /** Layers for the native stack when visual === "layers". */
  layers?: FunnelStage[];
  stats?: StatItem[];
  cta?: string;
  /** Cinematic options (all optional; absent = the prior, simpler look). */
  /** Giant word that wipes through on this scene's entry; defaults to the headline's *accent* word. */
  transitionWord?: string;
  /** Background intensity for this scene: "hero" (full particle wave) or "calm" (subtle). */
  bg?: "hero" | "calm";
  /** Floating callout pills annotating this scene. */
  callouts?: CalloutSpec[];
  /** 0-based index of the stage/node the animated cursor lands on (solution scene). */
  cursorTarget?: number;
}

export interface ReelContent {
  slug: string;
  platform: "instagram" | "linkedin" | string;
  title: string;
  /** Exact text the user pastes into ElevenLabs. */
  voiceScript: string;
  scenes: Scene[];
  source?: string;
  /** Optional override of the handle shown in the outro. */
  handle?: string;
}

export interface TimelineEntry {
  sceneId: string;
  startFrame: number;
  endFrame: number;
}

export interface Timeline {
  fps: number;
  durationInFrames: number;
  durationMs: number;
  /** True once audio has been transcribed and aligned. */
  aligned: boolean;
  scenes: TimelineEntry[];
}

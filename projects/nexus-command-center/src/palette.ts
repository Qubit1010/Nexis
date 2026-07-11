/** Node/community colors (design-system.md §2) — all readable on #0B0B0B. */
export const PALETTE = [
  "#208EC7", // c0 brand blue
  "#7A5AF8", // c1 violet
  "#34C388", // c2 green
  "#E5A83B", // c3 amber
  "#E25A5A", // c4 red
  "#2FB6BC", // c5 teal
  "#C25AC2", // c6 magenta
  "#8AA84B", // c7 olive
  "#D97C4A", // c8 orange
  "#5A78E2", // c9 indigo
] as const;

/**
 * ponytail: nodes are colored by TYPE, not by raw community id — 38 vault
 * communities would need 38 chip filters and an illegible legend. Communities
 * still shape the layout (links cluster them) and show in the side panel.
 */
export const TYPE_COLOR: Record<string, number> = {
  skill: 0,
  project: 1,
  context: 2,
  rule: 3,
  "decision-cluster": 4,
  wiki: 5,
  raw: 6,
  asset: 8,
  community: 9,
};

export const TYPE_LABEL: Record<string, string> = {
  skill: "Skills",
  project: "Projects",
  context: "Context",
  rule: "Rules",
  "decision-cluster": "Decisions",
  wiki: "Wiki",
  raw: "Raw",
  asset: "Assets",
  community: "Communities",
};

export const GLOW = "rgba(32,142,199,0.55)";

export function colorFor(index: number | undefined): string {
  return PALETTE[(index ?? 9) % PALETTE.length];
}

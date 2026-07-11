import { create } from "zustand";
import {
  api,
  type CommandInfo,
  type DeckStatus,
  type GraphData,
  type ProjectView,
  type SkillActionInfo,
  type Vitals,
} from "./api";
import { TYPE_COLOR, TYPE_LABEL } from "./palette";

export type ConsoleTab = "deck" | "projects" | "skills" | "chat" | "brain";

export interface GroupChip {
  type: string;
  label: string;
  colorIndex: number;
  count: number;
}

interface State {
  graph: GraphData | null;
  graphError: "missing" | string | null;
  chips: GroupChip[];
  hidden: Record<string, boolean>;
  selectedId: string | null;
  focusId: string | null;
  catalogOpen: boolean;
  vitals: Vitals | null;
  commands: CommandInfo[];
  deck: DeckStatus | null;
  consoleTab: ConsoleTab;
  projects: ProjectView[];
  skillActions: SkillActionInfo[];
  // Graph -> launcher handoff: SidePanel sets these, the target tab consumes.
  focusProjectId: string | null;
  focusActionId: string | null;

  select: (id: string | null) => void;
  setFocus: (id: string | null) => void;
  toggleType: (t: string) => void;
  setCatalog: (open: boolean) => void;
  setDeck: (d: DeckStatus) => void;
  setConsoleTab: (t: ConsoleTab) => void;
  setFocusProject: (id: string | null) => void;
  setFocusAction: (id: string | null) => void;
  loadGraph: () => Promise<void>;
  loadVitals: () => Promise<void>;
  loadCommands: () => Promise<void>;
  loadProjects: () => Promise<void>;
  loadSkillActions: () => Promise<void>;
}

export const useStore = create<State>((set) => ({
  graph: null,
  graphError: null,
  chips: [],
  hidden: {},
  selectedId: null,
  focusId: null,
  catalogOpen: false,
  vitals: null,
  commands: [],
  deck: null,
  consoleTab: "deck",
  projects: [],
  skillActions: [],
  focusProjectId: null,
  focusActionId: null,

  select: (id) => set({ selectedId: id }),
  setFocus: (id) => set({ focusId: id }),
  toggleType: (t) => set((s) => ({ hidden: { ...s.hidden, [t]: !s.hidden[t] } })),
  setCatalog: (open) => set({ catalogOpen: open }),
  setDeck: (d) => set({ deck: d }),
  setConsoleTab: (t) => set({ consoleTab: t }),
  setFocusProject: (id) => set({ focusProjectId: id }),
  setFocusAction: (id) => set({ focusActionId: id }),

  loadGraph: async () => {
    try {
      const g = await api.graph();
      // Enrich once: type color + bloom seed (nodes start near the origin and
      // settle outward — the "system coming online" open, design-system.md §7).
      const n = g.nodes.length || 1;
      g.nodes.forEach((node, i) => {
        node.colorIndex = TYPE_COLOR[node.type] ?? 9;
        const a = (i / n) * Math.PI * 2;
        const r = 6 + (i % 9) * 3;
        node.x = Math.cos(a) * r;
        node.y = Math.sin(a) * r;
      });
      const counts = new Map<string, number>();
      g.nodes.forEach((node) => counts.set(node.type, (counts.get(node.type) ?? 0) + 1));
      const chips = [...counts.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([type, count]) => ({
          type,
          label: TYPE_LABEL[type] ?? type,
          colorIndex: TYPE_COLOR[type] ?? 9,
          count,
        }));
      set({ graph: g, chips, graphError: null });
    } catch (e) {
      const err = e as { code?: string; message?: string };
      set({ graphError: err.code === "GRAPH_MISSING" ? "missing" : (err.message ?? "failed") });
    }
  },

  loadVitals: async () => {
    try {
      set({ vitals: await api.vitals() });
    } catch {
      /* vitals are decorative; dashes render when null */
    }
  },

  loadCommands: async () => {
    try {
      const r = await api.commands();
      set({ commands: r.commands });
    } catch {
      set({ commands: [] });
    }
  },

  loadProjects: async () => {
    try {
      const r = await api.projects();
      set({ projects: r.projects });
    } catch {
      /* keep the last known state; next poll retries */
    }
  },

  loadSkillActions: async () => {
    try {
      const r = await api.skillActions();
      set({ skillActions: r.actions });
    } catch {
      set({ skillActions: [] });
    }
  },
}));

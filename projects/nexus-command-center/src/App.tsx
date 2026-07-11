import { useEffect } from "react";
import { useStore } from "./store";
import AuroraBackground from "./components/AuroraBackground.tsx";
import HudShell from "./components/HudShell.tsx";

export default function App() {
  const loadGraph = useStore((s) => s.loadGraph);
  const loadVitals = useStore((s) => s.loadVitals);
  const loadCommands = useStore((s) => s.loadCommands);
  const loadProjects = useStore((s) => s.loadProjects);
  const loadSkillActions = useStore((s) => s.loadSkillActions);

  useEffect(() => {
    loadGraph();
    loadCommands();
    loadSkillActions();
    loadProjects();
    loadVitals();
    const iv = setInterval(loadVitals, 30_000);
    return () => clearInterval(iv);
  }, [loadGraph, loadVitals, loadCommands, loadProjects, loadSkillActions]);

  return (
    <>
      <AuroraBackground />
      <HudShell />
    </>
  );
}

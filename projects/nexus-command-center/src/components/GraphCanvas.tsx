import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { endpointId, type GraphLink, type GraphNode } from "../api";
import { useStore } from "../store";
import { colorFor, GLOW } from "../palette";

/** The living system graph — canvas 2D per the blueprint (§3). */
export default function GraphCanvas() {
  const graph = useStore((s) => s.graph)!;
  const hidden = useStore((s) => s.hidden);
  const selectedId = useStore((s) => s.selectedId);
  const focusId = useStore((s) => s.focusId);
  const select = useStore((s) => s.select);
  const setFocus = useStore((s) => s.setFocus);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [hoverId, setHoverId] = useState<string | null>(null);
  const fitDone = useRef(false);

  useLayoutEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    setSize({ w: el.clientWidth, h: el.clientHeight });
    return () => ro.disconnect();
  }, []);

  const nodeById = useMemo(() => {
    const m = new Map<string, GraphNode>();
    graph.nodes.forEach((n) => m.set(n.id, n));
    return m;
  }, [graph]);

  // Filtered view — same node objects, so positions survive filter toggles.
  const data = useMemo(() => {
    const anyHidden = Object.values(hidden).some(Boolean);
    if (!anyHidden) return { nodes: graph.nodes, links: graph.links };
    const visible = (id: string) => {
      const n = nodeById.get(id);
      return !!n && !hidden[n.type];
    };
    return {
      nodes: graph.nodes.filter((n) => !hidden[n.type]),
      links: graph.links.filter((l) => visible(endpointId(l.source)) && visible(endpointId(l.target))),
    };
  }, [graph, hidden, nodeById]);

  // Adjacency of the current selection (nodes + links highlighting).
  const neighborIds = useMemo(() => {
    const set = new Set<string>();
    if (!selectedId) return set;
    set.add(selectedId);
    for (const l of graph.links) {
      const s = endpointId(l.source);
      const t = endpointId(l.target);
      if (s === selectedId) set.add(t);
      if (t === selectedId) set.add(s);
    }
    return set;
  }, [graph, selectedId]);

  // Catalog → focus a node: fly to it.
  useEffect(() => {
    if (!focusId || !fgRef.current) return;
    const n = nodeById.get(focusId);
    if (n && n.x != null && n.y != null) {
      fgRef.current.centerAt(n.x, n.y, 600);
      fgRef.current.zoom(2.4, 600);
    }
    setFocus(null);
  }, [focusId, nodeById, setFocus]);

  return (
    <div ref={wrapRef} className="absolute inset-0" style={{ cursor: hoverId ? "pointer" : "grab" }}>
      {size.w > 0 && (
        <ForceGraph2D
          ref={fgRef}
          width={size.w}
          height={size.h}
          graphData={data}
          backgroundColor="rgba(0,0,0,0)"
          nodeLabel={() => ""}
          cooldownTime={5000}
          d3AlphaDecay={0.025}
          d3VelocityDecay={0.35}
          onEngineStop={() => {
            if (!fitDone.current && fgRef.current) {
              fitDone.current = true;
              fgRef.current.zoomToFit(700, 70);
            }
          }}
          onNodeClick={(n: GraphNode) => select(n.id)}
          onNodeHover={(n: GraphNode | null) => setHoverId(n ? n.id : null)}
          onBackgroundClick={() => select(null)}
          linkColor={(l: GraphLink) => {
            if (
              selectedId &&
              (endpointId(l.source) === selectedId || endpointId(l.target) === selectedId)
            ) {
              return "rgba(32,142,199,0.45)";
            }
            return "rgba(255,255,255,0.12)";
          }}
          linkWidth={(l: GraphLink) =>
            selectedId && (endpointId(l.source) === selectedId || endpointId(l.target) === selectedId)
              ? 1.4
              : 0.6
          }
          nodePointerAreaPaint={(node: GraphNode, color: string, ctx: CanvasRenderingContext2D) => {
            const r = 2.2 + Math.sqrt(node.size || 1) * 1.4 + 3;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x!, node.y!, r, 0, 2 * Math.PI);
            ctx.fill();
          }}
          nodeCanvasObject={(node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const x = node.x!;
            const y = node.y!;
            const r = 2.2 + Math.sqrt(node.size || 1) * 1.4;
            const isSel = node.id === selectedId;
            const isHover = node.id === hoverId;
            const inFocusSet = !selectedId || neighborIds.has(node.id);
            const alpha = inFocusSet ? 0.95 : 0.22;
            const color = colorFor(node.colorIndex);

            ctx.save();
            ctx.globalAlpha = alpha;
            if (isSel || isHover) {
              ctx.shadowColor = GLOW;
              ctx.shadowBlur = 12;
            }
            ctx.beginPath();
            ctx.arc(x, y, r, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.shadowBlur = 0;

            if (isSel) {
              ctx.beginPath();
              ctx.arc(x, y, r + 1.6 / globalScale, 0, 2 * Math.PI);
              ctx.strokeStyle = "#F5F7FA";
              ctx.lineWidth = 1.5 / globalScale;
              ctx.stroke();
            }

            // Labels fade in above zoom 1.4; always on for selected/hovered.
            if (globalScale >= 1.4 || isSel || isHover) {
              const fs = 11 / globalScale;
              ctx.font = `${fs}px Urbanist, sans-serif`;
              ctx.textAlign = "center";
              ctx.textBaseline = "top";
              ctx.fillStyle = isSel ? "rgba(245,247,250,0.95)" : "rgba(255,255,255,0.62)";
              ctx.fillText(node.label, x, y + r + 2 / globalScale);
            }
            ctx.restore();
          }}
        />
      )}
    </div>
  );
}

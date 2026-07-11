import { useStore } from "../store";
import { colorFor } from "../palette";

/** Bottom-left legend — color key and type filters in one (design-system.md §6). */
export default function LegendFilters() {
  const chips = useStore((s) => s.chips);
  const hidden = useStore((s) => s.hidden);
  const toggleType = useStore((s) => s.toggleType);

  if (chips.length === 0) return null;

  return (
    <div className="absolute bottom-4 left-4 flex max-w-[60vw] flex-wrap gap-2">
      {chips.map((c) => (
        <button
          key={c.type}
          className="np-chip"
          data-off={!!hidden[c.type]}
          aria-pressed={!hidden[c.type]}
          onClick={() => toggleType(c.type)}
          title={`${hidden[c.type] ? "Show" : "Hide"} ${c.label}`}
        >
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ background: colorFor(c.colorIndex) }}
          />
          {c.label}
          <span className="np-mono opacity-60">{c.count}</span>
        </button>
      ))}
    </div>
  );
}

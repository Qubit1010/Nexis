import { useMemo } from "react";
import { diffWordsWithSpace } from "diff";

export function Diff({ before, after }: { before: string; after: string }) {
  const parts = useMemo(() => diffWordsWithSpace(before, after), [before, after]);
  const added = parts.filter((p) => p.added).reduce((n, p) => n + p.value.split(/\s+/).filter(Boolean).length, 0);
  const removed = parts.filter((p) => p.removed).reduce((n, p) => n + p.value.split(/\s+/).filter(Boolean).length, 0);
  return (
    <div>
      <div className="mb-3 font-mono text-[12px] text-dim">
        <span className="text-pos">+{added}</span> / <span className="text-neg">-{removed}</span> words
      </div>
      <pre className="whitespace-pre-wrap break-words rounded-lg border border-line bg-s2 p-4 font-sans text-[13.5px] leading-relaxed">
        {parts.map((p, i) => (
          <span key={i} className={p.added ? "diff-add" : p.removed ? "diff-del" : ""}>
            {p.value}
          </span>
        ))}
      </pre>
    </div>
  );
}

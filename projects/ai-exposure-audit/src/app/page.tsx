import Link from "next/link";
import { listAudits } from "@/lib/db";
import { getRubric } from "@/lib/rubric";
import NewAuditButton from "@/components/NewAuditButton";

export const dynamic = "force-dynamic";

export default function Home() {
  const audits = listAudits();
  const rubric = getRubric();

  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <header className="mb-14">
        <p className="tabular mb-3 text-[11px] uppercase tracking-[0.2em] text-bone-600">
          Diagnostic instrument
        </p>
        <h1 className="mb-4 text-4xl font-semibold tracking-tight text-bone-100">
          AI Exposure Audit
        </h1>
        <p className="max-w-xl text-[15px] leading-relaxed text-bone-300">
          Which of a service business&apos;s revenue lines AI is about to take, what share of the
          book that represents, and what to move them to.
        </p>
        <p className="tabular mt-5 text-[11px] text-bone-600">
          Rubric v{rubric.version} &middot; {rubric.dimensions.length} dimensions &middot; published{" "}
          {rubric.published}
        </p>
      </header>

      <div className="mb-6 flex items-baseline justify-between border-b border-ink-700 pb-3">
        <h2 className="tabular text-[11px] uppercase tracking-[0.16em] text-bone-500">
          Audits ({audits.length})
        </h2>
        <NewAuditButton />
      </div>

      {audits.length === 0 ? (
        <div className="rounded border border-dashed border-ink-600 px-6 py-14 text-center">
          <p className="mb-2 text-sm text-bone-300">No audits yet.</p>
          <p className="text-[13px] text-bone-600">
            Start with your own book before selling this to anyone else.
          </p>
        </div>
      ) : (
        <ul className="divide-y divide-ink-700">
          {audits.map((a) => (
            <li key={a.id}>
              <Link
                href={`/audit/${a.id}`}
                className="group flex items-center justify-between py-4 transition-colors hover:bg-ink-850"
              >
                <div className="min-w-0">
                  <p className="truncate text-[15px] font-medium text-bone-100 group-hover:text-ember-300">
                    {a.business_name}
                  </p>
                  <p className="tabular mt-1 text-[11px] text-bone-600">
                    {a.line_count} service line{a.line_count === 1 ? "" : "s"}
                  </p>
                </div>
                <span className="tabular shrink-0 pl-6 text-[11px] text-bone-600">
                  {a.updated_at.slice(0, 10)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <footer className="mt-20 border-t border-ink-700 pt-6">
        <p className="text-[12px] leading-relaxed text-bone-600">
          Scores are structured judgment against a sourced rubric, not measurements. No source
          gives a numeric AI-substitution risk for a named service line, and this tool says so on
          the face of every report it produces.
        </p>
      </footer>
    </main>
  );
}

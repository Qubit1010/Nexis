# Detailed proposal and delivery

## Content

Aim for approximately 700–1,100 useful words, then inspect actual pagination. This is a working range, not a quota. Simple tasks can be one page. Do not shrink typography to squeeze an oversized proposal into three pages.

Choose and combine sections according to the brief:
- Objective and understanding of the work, including concrete constraints.
- Proposed approach and meaningful technical or design choices.
- Deliverables and observable acceptance criteria.
- Milestones with conditional duration estimates and review points.
- Closely relevant experience when substantiated.
- Dependencies, scope assumptions, and material exclusions.
- Pricing when supplied or explicitly requested, followed by a practical next step.

Do not force every section into every document. Avoid a cover page, generic agency biography, invented ROI, fabricated urgency, guarantees, free bonuses, or a contract-length statement of work. Client budget alone is not authorization to quote that amount. Distinguish estimated working time from elapsed time and name dependencies such as access, approved content, or feedback. Unknown prices can simply be omitted.

## Layout defaults

- Use a clear title and descriptive section headings, with whitespace between sections. Keep the main summary to a short paragraph.
- Use real bullets for parallel deliverables, assumptions, exclusions, and next actions. Keep paragraphs to a few sentences; split dense prose by meaning.
- Use native tables where readers compare information: deliverable and included scope; phase, timing, and output; or fee and coverage. Usually one or two focused tables suffice, with a third only when it adds clarity.
- Tables have two or three columns, bold shaded headers, cell padding, and readable 11-point type. Keep cells short; explanatory paragraphs belong outside the table. Avoid repeating the same information in prose and a table.
- Preserve scope and pricing when reformatting an existing proposal. Keep the 2–3-page target. Review row breaks and wrapping in the exported PDF; simplify an overcrowded table rather than shrinking the font.

## Google Doc helper usage

Run from the repository root. Use a unique local working directory outside tracked client content, preferably under the OS temporary directory. Preserve this directory through retries. JSON and Markdown may contain private client information; do not add them to git.

Input is UTF-8 JSON:
```json
{"title":"Project name | Proposal","sections":[{"heading":"Objective","body":"Client-facing prose."},{"heading":"Deliverables","bullets":["A concrete deliverable and how it will be accepted."]}]}
```

Only `title` and a nonempty `sections` array are required. Each section accepts `heading`, `body`, `body_runs`, `bullets`, `bullet_runs`, and `table`. Content appears in that order. Existing paragraph/bullet payloads remain supported. The helper renders real headings, lists, inline bold text, and native tables with 11-point Arial, A4 pages, and 54-point margins.

For inline emphasis, use runs instead of Markdown asterisks:
```json
{"heading":"Investment","body_runs":[{"text":"Proposed fee: "},{"text":"USD 1,500/month","bold":true},{"text":" after scope confirmation."}]}
```

Use bold selectively, generally one or two short phrases per paragraph or bullet. Bold the decision-relevant value, deliverable, date, tool, acceptance condition, or constraint. Do not bold whole paragraphs, every keyword, or the document title's entire text. `bullet_runs` is an array of run arrays, one array per bullet.

Example table section:
```json
{"heading":"Investment","table":{"headers":["Fee","Coverage"],"rows":[["USD 1,500 / month","Agreed ongoing content and management scope"],["USD 750 once","Initial setup"]]}}
```

Use only supplied or requested estimated prices. Table rows must match the two or three header columns, and all cell values must be strings. Markdown fallback drafts include readable Markdown tables. Tables are inserted and read back cell by cell; a partial insertion is a delivery failure, not success. Retry with the same state path to replace the body and rebuild its tables.

```text
python .claude/skills/upwork-proposal-studio/scripts/create_doc.py --input <proposal.json> --state <delivery.json> --dry-run
python .claude/skills/upwork-proposal-studio/scripts/create_doc.py --input <proposal.json> --state <delivery.json>
```

Dry run validates and returns a preview without writing files or calling Google. Real delivery preserves a Markdown draft and recovery state alongside the state file. The helper creates the Doc in `NexusPoint Proposals`, reads back text and formatting, exports a PDF beside the state file, and returns structured status and artifact paths. It never changes permissions.

Inspect the exported PDF visually and count pages using an available PDF library. Check clipped text, heading breaks, list spacing, and whether the content fits 2–3 pages. Shorten genuinely excessive content and rerun with the **same state path**; the helper updates only its recorded document. Do not claim pagination was verified if export or inspection failed. Body/API verification is distinct from visual verification.

Success requires `status: ok` plus visual review. Report a returned `partial` status accurately. If authentication or network access fails, give the readable draft and explain that Google Doc delivery is incomplete. Do not present raw JSON as the user's only fallback.

Never restart with a new state file after an uncertain create. The helper searches its unique Drive app property marker on recovery. If creation or content replacement has an ambiguous response, rerun the same command: it reconciles the document and rewrites its body rather than appending duplicate text. State is tied to this proposal; use a new state path for an unrelated job. Do not manually edit the Doc during automatic recovery.

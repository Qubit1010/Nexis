# Argon evaluation evidence audit, 22 October 2026

Primary evaluator snapshot, not original model testing. Facts were read from public Artificial Analysis (AA) model and agent data. Current model pages were independently opened and their titles match these configurations. Values are from the shared public model catalog on the Argon page. JSON audit preserves exact values.

## Model configurations and cost

Closest current practical comparators: Claude Sonnet 5.5 (Max, Default Fallback) and GPT-6.1 Sol (Max), which match Argon's current input/output token prices. Add Claude Opus 5.5 (Max, Default Fallback) and GPT-6 Astra (Max) for capability ceilings. Fable 5.1 is an older premium baseline. All six list 1 M context tokens.

| Exact AA configuration | Release | II v4.3.2 | Input/output $/1 M | Weighted II $/task | Output tokens/II task |
|---|---|---:|---:|---:|---:|
| [Gemini 4 Argon (High)](https://artificialanalysis.ai/models/gemini-4-argon) | 2026-09-30 | 52.56 | 2/10 | 1.99 | 61, 558 |
| [Claude Opus 5.5 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-opus-5-5) | 2026-09-22 | 57.62 | 4/20 | 5.98 | 119, 166 |
| [Claude Sonnet 5.5 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-sonnet-5-5) | 2026-09-28 | 56.00 | 2/10 | 5.46 | 197, 430 |
| [Claude Fable 5.1 (Max, Default Fallback)](https://artificialanalysis.ai/models/claude-fable-5-1) | 2026-09-01 | 53.35 | 10/50 | 7.63 | 78, 111 |
| [GPT-6 Astra (Max)](https://artificialanalysis.ai/models/gpt-6-astra) | 2026-09-03 | 52.67 | 10/50 | 3.26 | 27, 206 |
| [GPT-6.1 Sol (Max)](https://artificialanalysis.ai/models/gpt-6-1-sol) | 2026-09-29 | 51.83 | 2/10 | 0.72 | 38, 128 |

## Fixed-harness task results

| Model | Terminal-Bench 4 | FrontierCode 1.1 | Briefcase 1.1 Elo | GDPval-AA 2.1 Elo | AutomationBench-AA | AnalystAgent pass^5 |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 4 Argon (High) | 57.07% | 43.45% | 1485.76 | 1623.11 | 77.51% | 48.75% |
| Claude Opus 5.5 (Max, Default Fallback) | 59.60% | 52.17% | 1802.36 | 1866.27 | 69.54% | 56.25% |
| Claude Sonnet 5.5 (Max, Default Fallback) | 63.64% | 45.83% | 1816.92 | 1837.82 | 71.77% | 57.50% |
| Claude Fable 5.1 (Max, Default Fallback) | 52.02% | 48.97% | 1671.77 | 1752.91 | 59.38% | 57.50% |
| GPT-6 Astra (Max) | 59.09% | 46.98% | 1568.49 | 1571.76 | 68.49% | 51.25% |
| GPT-6.1 Sol (Max) | 56.06% | 49.12% | 1556.34 | 1592.10 | 64.87% | 50.00% |

## Knowledge and abstention

| Model | Omniscience accuracy | Conditional hallucination | Omniscience Index | AA-LCR 1.1 | GDP.pdf all-pass |
|---|---:|---:|---:|---:|---:|
| Gemini 4 Argon (High) | 49.90% | 15.07% | 42.35 | 79.67% | 21.80% |
| Claude Opus 5.5 (Max, Default Fallback) | 66.22% | 58.61% | 46.42 | 84.67% | 26.20% |
| Claude Sonnet 5.5 (Max, Default Fallback) | 53.95% | 47.01% | 32.30 | 82.67% | 25.80% |
| Claude Fable 5.1 (Max, Default Fallback) | 67.23% | 72.58% | 43.45 | 85.33% | 26.20% |
| GPT-6 Astra (Max) | 62.60% | 51.34% | 43.40 | 80.67% | 31.00% |
| GPT-6.1 Sol (Max) | 62.10% | 54.27% | 41.53 | 83.00% | 31.00% |

## Inference latency

| Model | Output t/s | First answer seconds | Synthetic 500-token end-to-end seconds |
|---|---:|---:|---:|
| Gemini 4 Argon (High) | 81.62 | 48.55 | 54.68 |
| Claude Opus 5.5 (Max, Default Fallback) | 95.13 | 650.86 | 656.12 |
| Claude Sonnet 5.5 (Max, Default Fallback) | 133.82 | 417.93 | 421.66 |
| Claude Fable 5.1 (Max, Default Fallback) | 68.85 | 249.47 | 256.73 |
| GPT-6 Astra (Max) | 56.74 | 287.37 | 296.18 |
| GPT-6.1 Sol (Max) | 54.13 | 281.39 | 290.62 |

## Actual coding-agent products, separate from model evaluations

[AA Coding Agent Index v1.5](https://artificialanalysis.ai/agents/coding-agents) measures complete agent variants.

| Actual tested variant | Index/100 | DeepSWE | Terminal-Bench 4 | SWE-Atlas-QnA | API $/task | Active min/task | CLI version |
|---|---:|---:|---:|---:|---:|---:|---|
| Antigravity CLI - Gemini 4 Argon (high) | 63.76 | 78.76% | 56.06% | 56.45% | 5.84 | 34.5 | 1.2.10 |
| Claude Code - Sonnet 5.5 (max) | 68.36 | 71.98% | 66.16% | 66.94% | 14.19 | 87.4 | 2.1.280 |
| Codex - GPT-6.1 Sol (max) | 60.15 | 69.62% | 53.03% | 57.80% | 1.55 | 24.4 | 0.154.0 |
| Codex - GPT-6 Astra (max) | 61.65 | 67.55% | 55.56% | 61.83% | 7.50 | 29.4 | 0.151.0, 0.153.4 |
| Claude Code - Fable 5.1 (max) (with fallback) | 62.22 | 64.31% | 57.58% | 64.78% | 12.39 | 34.8 | 2.1.259, 2.1.263 |
| Claude Code - Opus 5.5 (max) | 65.99 | 68.44% | 63.13% | 66.40% | 13.04 | 64.5 | 2.1.280 |
The JSON audit also preserves the Devin Fusion router row, which combines Opus 5.5 Max and GPT-6 Luna High. It should not be attributed to either model alone.

## Methodology, dates and limitations

- [Argon launch analysis, 30 September 2026](https://artificialanalysis.ai/articles/gemini-4-argon-google-top-three-labs): standard prices are $4/$20, temporarily discounted to $2/$10, with the end date unconfirmed at publication. The [current official pricing page](https://ai.google.dev/gemini-api/docs/pricing) now confirms $2/$10 through 30 November 2026 and $4/$20 from 1 December 2026, cached input $0.10 then $0.20; explicit caching is unsupported. The discounted weighted II cost is $1.99/task, rising to $3.98 at standard prices. Current model data still uses the discount. The article reports selected-user access at launch, not general availability. It tested High, described as the highest available reasoning setting, using Long Decode Continuation across follow-up calls up to 1 M output tokens. No Argon Medium result appeared in the examined AA model catalog or coding-agent rows. That is absence of measured evidence, not proof Medium cannot be selected in a product.
- [AA Intelligence methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking): II v4.3.2 aggregates ten evaluations, with Agents 30%, Coding 20%, Scientific Reasoning 20% and General 30%. It is primarily text-based and English. Temperature is generally 0.6 for reasoning models unless the lab recommends otherwise; maximum output is the model's disclosed limit. API errors can be retried up to 30 times. Provider token counts and representative measured caching determine costs. These settings do not guarantee identical inference compute across models.
- [Terminal-Bench 4](https://artificialanalysis.ai/evaluations/terminalbench-4-0): 66 tasks, three repeats, mini-swe-agent, pass@1, every verifier test must pass. AA caps at 500 steps, uses upstream task time/resources, native bash and a full transcript without compaction. These fixed-harness model rows are distinct from Claude Code, Codex and Antigravity scores.
- [FrontierCode 1.1](https://artificialanalysis.ai/evaluations/frontiercode): private Main set of 100 tasks; three attempts with Stirrup, 250 turns and a four-hour wall limit. It combines tests and blocking/nonblocking review criteria; any blocking failure or detected solution lookup gives zero. GPT-6 Luna medium judges review criteria. It is outside II. Opus 5.5 Medium reaches 57.1%, versus 52.17% at Max, showing maximum effort is not universally best.
- [AA-Briefcase 1.1](https://artificialanalysis.ai/evaluations/aa-briefcase):91 deliverable tasks across four knowledge-work projects, Stirrup, 500 turns and offline access to provided files. Each task runs independently, including later weeks. Elo combines rubric compliance, analytical quality and presentation. The public Lite scenario is demonstrative and excluded from official results. Argon's overall 95% Elo interval is 1475.63-1495.84; Sol 1546.38-1566.61; Astra 1560.26-1577.46; Fable 1663.25-1681.75; Opus 1791.17-1814.12; Sonnet 1806.17-1829.25.
- [AutomationBench-AA](https://artificialanalysis.ai/evaluations/automationbench-aa):657 private tasks in simulated SaaS applications, one attempt, 50-turn cap. Its headline is the average share of objectives completed with zero credit for any guardrail violation. It is not the proportion of tasks fully completed, and is not directly comparable to Zapier's hosted headline metric. Final-state checks are programmatic, without a separate LLM judge.
- [AA-AnalystAgent](https://artificialanalysis.ai/evaluations/aa-analyst-agent):80 tasks and five attempts. Its pass^5 result measures consistency across five runs, not general production reliability.
- [AA-Omniscience](https://artificialanalysis.ai/evaluations/omniscience):6, 000 questions. Accuracy is correct/all. Hallucination rate is incorrect/(incorrect + partial + not attempted). Thus Argon's 15.07% is a conditional failure metric associated with abstention, not a blanket production hallucination rate. Its 49.9% factual accuracy is also lower than Astra 62.6% and Sol 62.1%.
- [API performance methodology](https://artificialanalysis.ai/methodology/performance-benchmarking): default workload is approximately 10 k input tokens and at least 1, 500 answer tokens, single request, median over the previous 72 hours. These models use first-party endpoints. Speed uses standardized o200k_base tokens; first-answer latency includes thinking. The 500-token response metric is synthetic. It is not the time to complete a coding task. II task-time fields are calculated decode times excluding TTFT/overhead, and should not substitute for agent wall time.
- [Coding Agent Index methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking): v1.5 equally weights DeepSWE v1.1 (113 tasks), Terminal-Bench 4 (66) and SWE-Atlas-QnA (124), three attempts per task. API costs include caching but exclude subscriptions, infrastructure, engineering and supervision. Active agent runtime excludes environment startup and verifier/judge time. DeepSWE blocks internet except necessary API access. Terminal-Bench reward-hacking detections are zeroed after trajectory review. SWE-Atlas uses Claude Opus 4.5 as judge. A row represents an agent variant, not a model in isolation.
- Default fallback matters: the Fable coding-agent row explicitly includes fallback, and Opus/Sonnet trials also recorded fallbacks. The primary model label does not imply every token came from it. The JSON audit retains the evaluator's refusal/fallback data. The [Sonnet launch article, 28 September](https://artificialanalysis.ai/articles/claude-sonnet-5-5) also discloses a prerelease structured-output bug and default fallback in its II runs, roughly 0.1% of tasks falling to Sonnet 5. Do not silently erase those qualifiers.
- Snapshot versus launch: the 30 September Argon article gives Briefcase 1494 Elo, rubric 65%, analytical 1576 and presentation 1308. The current v1.1 page gives 1485.76, 64.63%, 1559.81 and 1303.33. Elo refits or additional comparisons can change values. Do not infer model regression, or combine release-day scores and current scores without labels. Live pages do not expose exact internal benchmark run timestamps/commits in the extracted fields.
- [Sol launch analysis, 29 September](https://artificialanalysis.ai/articles/gpt-6-1-sol-replaces-gpt-6-sol-after-just-7-days-with-near-astra-intelligence) says 6.1 replaced 6 Sol after seven days. Prefer 6.1 for a current practical comparison. It reports Sol xhigh exceeding max in the coding-agent index, so effort setting must remain visible.
- Reproducibility resources: [Stirrup](https://github.com/ArtificialAnalysis/Stirrup), [Terminal-Bench repository](https://github.com/harbor-framework/terminal-bench), [AA-Briefcase Lite](https://huggingface.co/datasets/ArtificialAnalysis/AA-Briefcase-Lite). These permit inspection/reproduction of public components, not reproduction of private benchmark tasks.
- Cross-check: the [upstream Terminal-Bench 4 leaderboard](https://www.tbench.ai/?version=4) fetched with Claude/GPT submissions but no Argon entry. Its scores come from different submitted runs and differ from AA; do not mix them. [Cognition's FrontierCode 1.1 announcement](https://cognition.com/blog/frontier-code-1.1), dated 7 July 2026, documents private task construction and fair-internet checks, not an October independent Argon comparison.

## Interpretation for the writer

Inference from these results: Argon is competitive with Astra/Sol on aggregate II and leads the measured simulated SaaS workflow score, with strong abstention when it lacks knowledge. Opus/Sonnet are stronger on knowledge-work deliverable Elo. Sonnet wins the fixed-harness terminal comparison; Opus wins FrontierCode among these Max variants. Antigravity+Argon leads the measured Codex configurations on aggregate coding-agent quality, while Codex+Sol is much cheaper and faster. These are workload-specific observations, not a universal winner or first-person usage claim.

For article readability, keep a model capability table separate from an actual coding-agent table. Aim for four main rows and four or five metrics per table, with Fable and full run details in an appendix. Treat a rounded II tie as a rounded tie, not statistical equivalence.

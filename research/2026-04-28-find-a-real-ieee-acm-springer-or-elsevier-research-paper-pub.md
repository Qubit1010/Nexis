# Find a real IEEE, ACM, Springer, or Elsevier research paper (published 2019-2024) that proposes a specific algorithm with pseudocode or clear steps, for a Design and Analysis of Algorithms undergraduate assignment. Paper should be in AI, data mining, networking, image processing, cryptography, or software engineering. Need: exact title, authors, journal name, year, DOI, algorithm main steps or pseudocode, time complexity (best/average/worst case), space complexity, and what 2 existing algorithms it compares against. Prefer a well-known paper with freely accessible details.

*Research mode: deep | Date: 2026-04-28*

---

## Executive Summary
- We identified a strong, well-cited Elsevier paper that squarely fits your 2019–2024 window and includes clear algorithmic steps and complexity: “Harris hawks optimization: Algorithm and applications” (Heidari et al., Future Generation Computer Systems, 2019; DOI: 10.1016/j.future.2019.02.028). It presents the Harris Hawks Optimization (HHO) metaheuristic with explicit pseudocode and complexity analysis.
- HHO’s total time complexity is O(N × (T + T·D + 1)) ≈ O(T·N·D), space is O(N·D). The paper benchmarks HHO against standard algorithms including GA and PSO and reports superior results on widely used test suites. Sources and cross-references are provided below.

## Key Findings
1. Paper selected: Elsevier FGCS (2019) “Harris hawks optimization: Algorithm and applications,” by Heidari, Mirjalili, Faris, Aljarah, Mafarja, Chen; DOI: 10.1016/j.future.2019.02.028. Freely accessible accepted-manuscript PDF with Algorithm 1 (pseudocode) and complexity section is available from the author’s page. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530))
2. Algorithm overview: HHO alternates between exploration and exploitation using prey “energy” and randomization, with four chase modes (soft/hard besiege, with/without progressive rapid dives via Lévy flights). The paper includes a labeled “Algorithm 1: Pseudo-code of HHO algorithm.” ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
3. Complexity (from the paper): initialization O(N); per-iteration update O(T·N) + O(T·N·D); overall O(N × (T + T·D + 1)) ≈ O(T·N·D). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
4. Space complexity (by inspection): O(N·D) to store the population (N hawks × D dimensions) plus O(D) for the current best (“rabbit”) and a few scalars.
5. Benchmarks and baselines: HHO is compared against GA, PSO, DE, GWO, FA, BAT, CS, MFO, TLBO, BBO, FPA; it outperforms competitors on 84.6% of 30-D and 92.3% of 100-D test cases (F1–F13). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
6. For the comparative table, standard complexities for PSO and GA are O(T·N·D) time and O(N·D) space (GA adds O(N log N) or O(N²) for selection/sorting in some implementations), supported by recent Scientific Reports analyses. ([nature.com](https://www.nature.com/articles/s41598-025-27390-2.pdf))

## Detailed Analysis
A) Bibliographic details (meets all assignment constraints)
- Exact title: Harris hawks optimization: Algorithm and applications
- Authors: Ali Asghar Heidari; Seyedali Mirjalili; Hossam Faris; Ibrahim Aljarah; Majdi Mafarja; Huiling Chen
- Journal: Future Generation Computer Systems (Elsevier), Volume 97, August 2019, pp. 849–872
- Year: 2019
- DOI: 10.1016/j.future.2019.02.028
- Access: ScienceDirect record; accepted-manuscript PDF (author’s site) contains Algorithm 1 pseudocode and the complexity section. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530))

B) Problem setting and proposed algorithm
- Domain fit: AI/metaheuristic optimization; frequently applied in data mining, image processing, control, and engineering design. HHO models the cooperative “surprise pounce” behavior of Harris’ hawks and codifies four pursuit strategies depending on prey energy and random thresholds. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530?utm_source=openai))

C) Algorithm main steps (pseudocode in own words)
Let N = number of hawks (population), D = dimension, T = max iterations, f(·) = fitness.

Inputs: N, T, bounds [LB, UB], objective f.
Output: Best solution Xrabbit and f(Xrabbit).

1) Initialize positions Xi ∈ [LB, UB] for i = 1..N.
2) Evaluate f(Xi) for all hawks; set Xrabbit = argmin f(Xi) (best).
3) For t = 1..T:
   3.1) For each hawk i:
        - Sample initial energy E0 ∈ (−1, 1) and jump strength J ∈ (0, 2) as in the paper; update prey energy E = 2E0(1 − t/T).
        - Draw r ∼ U(0,1).
        - If |E| ≥ 1 (exploration):
            • Perch/position update via either random perching around group mean or near random hawk, per paper’s exploration equations.
          Else (|E| < 1, exploitation):
            • Choose chase mode based on r and |E|:
              - Soft besiege,
              - Hard besiege,
              - Soft besiege with progressive rapid dives (Lévy flight),
              - Hard besiege with progressive rapid dives (Lévy flight).
            • Compute candidate Y (deterministic step) and Z = Y + S·LF(D) (stochastic dive), accept the better of {Y, Z} if it improves fitness.
        - Apply bound-handling if needed; update Xi.
   3.2) Re-evaluate f(Xi); if better than f(Xrabbit), update Xrabbit.
4) Return Xrabbit and f(Xrabbit).

Notes:
- The actual step formulas for exploration/exploitation and the definitions of ΔX, Xm (population mean), Lévy flight operator LF(·), etc., are given in the paper’s equations (1)–(13) and Algorithm 1. The accepted-manuscript PDF contains the labeled pseudocode and all update equations. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))

D) Time and space complexity (best/average/worst)
- From the paper: “computational complexity … mainly depends on initialization O(N) and updating O(T·N) + O(T·N·D). Therefore, computational complexity of HHO is O(N × (T + T·D + 1)).” For practical D > 1, this is Θ(T·N·D). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
- Best case: O(Tbest·N·D) if early stopping/rapid convergence occurs (Tbest ≪ T).
- Average case: O(Tavg·N·D), where Tavg is the typical iteration count to convergence.
- Worst case: O(T·N·D) when all T iterations run and each update scans all dimensions.
- Space complexity (by inspection of Algorithm 1): Θ(N·D) to store all hawk positions, plus O(D) for Xrabbit and O(1) scalars (E, J, r). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))

E) Baselines used in the paper and performance summary
- Reported baselines: GA, PSO, DE, BBO, FA, BAT, CS, GWO, MFO, TLBO, FPA (among others). The paper’s tables cover 29–30 benchmark functions (UM/MM/CM) across multiple dimensions. HHO attains the best results on 84.6% of 30-D cases, 92.3% of 100-D cases, and remains competitive at 500–1000 D; the text explicitly states HHO “performs faster than BBO, PSO, GA, CS, GWO, and FA,” consistent with its linear-in-D per-iteration updates. Results include statistical tests (Wilcoxon, Friedman). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))

F) Comparison against two existing algorithms (requested table)
Assumptions: N = population size; D = problem dimension; T = iterations. For GA/PSO complexities, we cite recent Scientific Reports analyses that summarize Big-O costs for standard forms.

| Algorithm | Core approach | Time complexity (per run) | Space complexity | Accuracy/performance vs HHO (per Heidari et al.) |
| - | - | - | - | - |
| HHO (Heidari et al., 2019) | Population-based prey–predator metaphor; exploration/exploitation via prey energy E; four besiege strategies; occasional Lévy dives | O(N × (T + T·D + 1)) ≈ O(T·N·D) | O(N·D) | Outperformed competitors (incl. GA, PSO) on 84.6% of 30-D and 92.3% of 100-D test cases; statistically significant on most functions. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf)) |
| PSO (canonical) | Velocity–position updates guided by personal/global bests | O(T·N·D) | O(N·D) | HHO often faster/more accurate on the paper’s CEC-style functions; PSO included among compared methods. ([nature.com](https://www.nature.com/articles/s41598-025-27390-2.pdf)) |
| GA (real-coded, elitist) | Selection, crossover, mutation over a population of chromosomes | O(T·N·D + N·log N) (selection/sorting overhead; sometimes reported as O(T·N·D) + O(N²) depending on selection) | O(N·D) | HHO significantly better on most reported cases (30-D, 100-D) per the FGCS paper’s tables and tests. ([nature.com](https://www.nature.com/articles/s41598-025-27390-2.pdf)) |

G) Why this paper fits your DAA course brief
- Publication window 2019–2024: 2019 Elsevier FGCS issue. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530))
- Contains explicit pseudocode (Algorithm 1) and equations with clarity for step-by-step explanation. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
- Provides its own complexity analysis (rare and valuable in metaheuristic papers). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
- Benchmarks against multiple widely known algorithms, enabling a rich comparison section in your assignment. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
- Freely accessible accepted-manuscript PDF ensures you can quote equations and reproduce pseudocode with attribution. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))

## Recommendations
For NexusPoint (and the student’s assignment deliverables):
1. Reproduce HHO in a clean, documented reference implementation (Python/NumPy):
   - Modules: initialization, energy update, exploration/exploitation modes, Lévy flight operator, bound-handling policies. Unit-test each mode with synthetic functions (Sphere, Rastrigin, Rosenbrock). Then validate against results in the paper. ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
2. Demonstrate practical value on client-relevant tasks:
   - Hyperparameter tuning for tabular ML models; compare HHO vs PSO vs GA under identical evaluation budgets. Use the same Big-O framing when presenting results to stakeholders. ([nature.com](https://www.nature.com/articles/s41598-025-27390-2.pdf))
   - Feature selection or image thresholding/segmentation where metaheuristics often excel (include a run-time/accuracy dashboard). 
3. Prepare the DAA assignment package:
   - A 2–3 page algorithm explanation (with your own pseudocode above), a formal complexity section stating best/avg/worst cases, and the comparison table provided here. Include direct citations to the FGCS article and accepted-manuscript PDF where Algorithm 1 and complexity are shown. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530))
4. Add a short “limitations and tuning” note:
   - Metaheuristics depend on T, N, and parameterization; always report evaluation budgets and random seeds. When fitness evaluations are expensive, cache results or use surrogate models to reduce total runtime. 
5. Optional extension (for extra credit/portfolio):
   - Implement an HHO variant that adaptively tunes N or switches besiege strategies based on online diversity metrics; compare against canonical HHO on a small suite to show measurable gains.

## Sources
- Heidari, A.A., Mirjalili, S., Faris, H., Aljarah, I., Mafarja, M., Chen, H. Harris hawks optimization: Algorithm and applications. Future Generation Computer Systems, 97, 849–872 (2019). DOI: 10.1016/j.future.2019.02.028. ScienceDirect record (bibliographic details). ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0167739X18313530))
- Accepted-manuscript PDF with Algorithm 1 pseudocode and complexity section (author’s site). Contains “Algorithm 1: Pseudo-code of HHO algorithm” and computational complexity derivation O(N × (T + T·D + 1)). ([aliasgharheidari.com](https://aliasgharheidari.com/HarrisHawksOptimizationHHOAlgorithmandapplications-aliasgharheidaricom.pdf))
- Scientific Reports (2025). Complexity summary table for metaheuristics (PSO O(T·N·D); GA O(T·N·D)+O(N log N)), used to ground the GA/PSO entries in our comparison. ([nature.com](https://www.nature.com/articles/s41598-025-27390-2.pdf))
- Survey/context on HHO’s use and variants: “Harris Hawk Optimization: A Survey on Variants and Applications,” Symmetry (open-access review, contextualizes HHO adoption). ([mdpi.com](https://www.mdpi.com/2073-8994/13/12/2364?utm_source=openai))
- Additional context on PSO practice and algorithmic structure: “A quarter century of particle swarm optimization,” Complex & Intelligent Systems (Springer, open access). ([link.springer.com](https://link.springer.com/article/10.1007/s40747-018-0071-2?utm_source=openai))

If you want, I can export a polished assignment document (with figures/equations referenced) and a small, runnable Python notebook that reproduces HHO on a few benchmark functions and logs per-iteration complexity metrics.
<!--
HOW TO USE IN GAMMA:
1. In Gamma, choose Create new > "Paste in text".
2. Copy everything BELOW the dividing line and paste it in.
3. Each "##" heading becomes one card (10 cards total).
4. The italic "Visual:" line is your image/diagram prompt for that card.
Delete everything above the line before pasting for the cleanest import.
-->

----------------------------- PASTE BELOW THIS LINE -----------------------------

## How to Be a Responsible Data Scientist

- Data shapes real decisions: who gets hired, a loan, or medical care
- A technically correct dataset can still be turned into a misleading chart
- Responsibility runs the whole chain: collect it fairly, model it honestly, show it truthfully
- This talk: the principles, the visualization sins to avoid, and a practical checklist

*Visual: a single clean line chart on a dark background, with a small human silhouette at the end of the line, symbolizing decisions made from data. Minimal, editorial.*

---

## What "Responsible" Actually Means

- Build data and AI systems that are trustworthy, fair, and aligned with human well-being
- It is more than math: it is owning the social impact of your data and models
- Guided by professional codes (ACM, IEEE, ASA) and the idea that data is never bent to fit a desired story
- The rest of this deck breaks it into pillars you can act on

*Visual: a simple hub-and-spoke diagram, center node "Responsible Data Scientist" with spokes to the six pillars in the next slides.*

---

## The Six Pillars

- **Integrity:** never misrepresent data for a narrative
- **Privacy & consent:** protect people, follow GDPR / CCPA, collect only what you need
- **Bias & fairness:** stop models from amplifying historical discrimination
- **Honest visualization:** charts that do not exaggerate or hide
- **Accessibility:** charts everyone can read
- **Transparency & accountability:** show your work, own the impact

*Visual: six clean icon tiles in a 3x2 grid, one per pillar, consistent line-icon style, brand accent color.*

---

## Pillar 1: Data Integrity & Provenance

- Garbage in, garbage out: the chart is only as honest as the data behind it
- Know where data came from, how it was collected, and whether it represents the real population
- Vet for errors and sampling problems before any analysis
- Document the source so others can trust and trace it

*Visual: a pipeline graphic, "raw source > cleaning > dataset," with a magnifying glass checking quality at each stage.*

---

## Pillar 2: Privacy & Consent

- Protect personal data and comply with laws like GDPR and CCPA
- Get informed consent, and give people a way to revoke it later
- Data minimization: collect only what the task actually needs
- Use privacy tech when data is sensitive: differential privacy, federated learning

*Visual: a shield icon over a table of anonymized rows, some cells masked with asterisks. Calm, trustworthy tone.*

---

## Pillar 3: Bias & Fairness

- Models inherit bias from historical data and can discriminate in hiring, credit, and justice
- Watch for proxy variables, for example a zip code standing in for race
- Test with fairness metrics: Disparate Impact, Equalized Odds
- Mitigate by curating representative data and techniques like reweighing or adversarial debiasing

*Visual: an unbalanced scale tipping to one side, with data points as the weights, then a second balanced scale beside it showing the corrected version.*

---

## Honest Visualization, Part 1: The Cardinal Sins

- **Truncated axis:** not starting bars at zero turns a tiny gap into a dramatic one
- **Dual axes:** two different scales can fake a correlation that is not real
- **Cherry-picked range:** showing only the good months hides the real trend
- **Chartjunk & 3D:** decoration and perspective distort what the data says

*Visual: side-by-side bar charts. Left: a truncated y-axis exaggerating a small difference, labeled "Misleading." Right: same data with a zero baseline, labeled "Honest." Red vs green framing.*

---

## Honest Visualization, Part 2: Doing It Right

- Start bar charts at zero and use uniform intervals
- Keep the context: do not crop out the benchmark period
- Show uncertainty with confidence intervals or ranges instead of faking precision
- Cut chartjunk (Tufte's data-ink ratio) and label directly, with clear units

*Visual: a clean line chart with a shaded confidence band around the line, direct labels at the end of each series, no gridline clutter. The "good example."*

---

## Accessibility & Inclusive Design

- Use color-blind safe palettes: blue is safest, pair blue with orange or yellow, avoid red-green
- Meet contrast standards (WCAG: 3:1 for chart elements, 4.5:1 for text); if it reads in grayscale, it works
- Never rely on color alone: add shapes, patterns, or direct labels
- Add alt text for screen readers: "[chart type] of [data] where [reason]," plus a longer description

*Visual: the same chart shown twice, once in full color and once in grayscale, both still readable, with a small color-blind simulation swatch in the corner.*

---

## Takeaways: The Responsible DS Checklist

- Collect with consent, check quality and representativeness
- Test fairness, protect privacy, make it reproducible (version data, fix seeds)
- Explain it (SHAP / LIME) and document it (Datasheet, Model Card)
- Visualize honestly and accessibly, then monitor after launch with human oversight
- **One line to remember:** a chart is a promise. It must not say more, or less, than the data honestly supports.

*Visual: a clean checklist graphic with ticked boxes, and the closing quote in large type underneath. Strong, memorable end slide.*

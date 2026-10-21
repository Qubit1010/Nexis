# Islamabad Local Market

Local outreach for NexusPoint in Islamabad, modelled on `projects/quetta-local-market`. Started
2026-10-21. Launch sectors: healthcare (aesthetic, dental and specialist clinics first), restaurants
and cafes, and real estate (developers, society sales offices, agencies). Prices approved by Aleem
on 2026-10-21, about 40% above Quetta (see `decisions/log.md`).

| Folder | What | Tracked |
|---|---|---|
| `research/` | `islamabad-market-brief.md`: sector ranking, scan findings, sources | No |
| `data/` | `kit.json` (approved prices, copy, proof), Maps scan (`maps_raw/`), `maps_summary.json`, scored `prospects.csv`, `competitor_scan.json` | No |
| `templates/` | Print system on the Soft Fold v2.0 brand (`brand.css`) and document templates | Yes |
| `scripts/` | Scan, analysis, prospect workbook and PDF rendering | Yes |
| `assets/fonts/` | Mokoto, Conthrax, Inter copied from the website source (licensed for NexusPoint use only) | No |
| `deliverables/` | Finished PDFs and the prospect workbook | No, regenerate |

Prospect data and the display fonts stay out of git: the Nexis repo is public.

## Rebuild

Run unsandboxed, from this folder:

```bash
python scripts/scrape_maps.py                # core scan (24 categories), Apify credits
python scripts/scrape_maps.py --second-pass  # DHA, Bahria, Gulberg, B-17 + deeper core, 3 sectors
python scripts/analyze_maps.py               # stats + scoring -> data/maps_summary.json, prospects.csv
python scripts/build_prospects.py            # deliverables/Islamabad-Prospects.xlsx
python scripts/render.py                     # all PDFs (onepager, report, deck, healthcheck-sample)
```

`render.py` prints `[overflow]` if any page or slide content spills past its edge. A per-prospect
Digital Health Check is rendered by `make_demo.py`, which calls `render.py` with the same API as Quetta.

## What is in the kit

- `Islamabad-Prospects.xlsx`: a summary sheet plus one ranked sheet per sector, with an opportunity line, door-opener, pitch and an outreach Status dropdown.
- `OnePager-<sector>-<en|ur>.pdf`: one-page offer per sector, in English and Urdu.
- `Health-Check-SAMPLE-<lang>.pdf`: layout sample of the free Digital Health Check (illustrative data, never send it).
- `Islamabad-Market-Intelligence-Report.pdf`: internal report covering the market, the scan, the three sectors, the competition and the outreach plan.
- `NexusPoint-Islamabad-Company-Profile.pdf`: a 9-slide deck to show in meetings.

Landing site: `projects/nexuspoint-islamabad-landing`. Demos: `projects/nexuspoint-demo` (city-aware, plus a real-estate sector).

## Prices

Change prices only in `data/kit.json`, and only with founder approval. Then re-render, rebuild the landing site, and run
`python projects/nexuspoint-demo/scripts/sync_bundles.py`.

## Placeholders before outreach

`kit.json` `meta.whatsapp`, `meta.whatsapp_link` and `meta.office` are still placeholders. Every QR code and WhatsApp link reads from them.

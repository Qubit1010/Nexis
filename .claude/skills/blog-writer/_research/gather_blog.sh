#!/usr/bin/env bash
# Deep research passes for the blog-writer skill corpus.
set -u
PY="C:/Users/qubit/AppData/Local/Programs/Python/Python312/python.exe"
RS="c:/Users/qubit/OneDrive/Documents/Automations/Nexis/.claude/skills/research/scripts/research.py"
OUT="c:/Users/qubit/OneDrive/Documents/Automations/Nexis/.claude/skills/blog-writer/_research"
LOG="$OUT/gather.log"
echo "START $(date)" > "$LOG"

run() {
  local id="$1"; shift
  local q="$1"; shift
  echo "[$id] START $(date)" >> "$LOG"
  "$PY" "$RS" --query "$q" --depth deep --json > "$OUT/$id.json" 2> "$OUT/$id.err"
  echo "[$id] EXIT $? bytes=$(wc -c < "$OUT/$id.json")" >> "$LOG"
}

run q1_blog_seo "blog SEO best practices 2026: on-page structure, E-E-A-T experience expertise authority trust, keyword strategy and search intent, title tags and meta descriptions, internal linking, heading hierarchy, article and BlogPosting schema, content freshness and updating"
run q2_aeo_geo "answer engine optimization AEO and generative engine optimization GEO in 2026: how to get blog content cited by ChatGPT Perplexity Claude and Gemini, extractable 40-60 word answer blocks, FAQ and definition blocks, adding statistics and citations and quotations, the Princeton GEO study ranking of optimization methods and any 2026 updates"
run q3_aio_overviews "Google AI Overviews and AI Mode optimization 2026: how to appear and get cited in AI Overviews, query fan-out and topical clusters, E-E-A-T and helpful people-first content, semantic HTML, what content wins, Google official stance on optimizing for generative AI search"
run q4_human_tone "how to write long-form blog content that reads human and not AI-generated in 2026: common AI writing tells and phrases to avoid, sentence cadence and burstiness, first-person voice and specificity, storytelling, how AI content detectors work and how legitimate original human-edited writing avoids false positives"
run q5_blog_formats "which blog content formats rank in Google and get cited most by AI search engines in 2026: comparison articles, definitive guides, original research and data studies, how-to guides, listicles, opinion analysis, ideal blog word count, heading structure, and readability"

echo "DONE $(date)" >> "$LOG"

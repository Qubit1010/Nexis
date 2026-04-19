# Decision Log

Append-only. When a meaningful decision is made, log it here.

Format: [YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...

---

[2026-04-17] DECISION: Extended South Asia exclusion filter to also check LinkedIn URL subdomain (pk/in/bd/lk/np.linkedin.com) | REASONING: Profiles without a location field set were bypassing the filter despite being South Asian - URL subdomain is a reliable secondary signal | CONTEXT: lead-gen/linkedin_push.py

[2026-04-17] DECISION: Added Unicode normalization step to GPT connection note output before returning from transformer | REASONING: GPT-4o-mini occasionally returns smart quotes and em dashes that cause encoding errors in downstream CSV/terminal output | CONTEXT: lead-gen/transformers/linkedin_transformer.py

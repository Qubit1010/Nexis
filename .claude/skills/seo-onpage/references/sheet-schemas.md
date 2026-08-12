# Sheet Schemas

The payload `push_sheet.py` consumes, and the six tabs it produces. Column order is owned
by the `TABS` dict in the script - do not reorder or rename here without changing it there.

```bash
python scripts/push_sheet.py --payload payload.json --validate-only    # no title needed
python scripts/push_sheet.py --payload payload.json --title "On-Page Audit - Acme"
```

---

## The payload

```jsonc
{
  "page_audit": [                      // one row per check per page, straight from onpage.py
    {
      "url": "https://acme.com/services/landscaping",
      "area": "Titles and metas",      // the check's area
      "check": "title.length",         // check_id
      "observed": "78 chars",
      "threshold": "50-60 chars",
      "verdict": "fail",               // pass | fail | review | unknown
      "source": "course/11 [s296]",
      "evidence": "Garden Landscaping Services..."
    }
  ],

  "findings": [                        // the prioritized diagnosis - this is the deliverable
    {
      "priority": "this week",         // this week | this month | structural | backlog
      "area": "Internal linking",
      "finding": "Nine commercial pages have no inbound body links",
      "evidence": "links.py: 9 of 14 priority pages, 0 inbound",  // REQUIRED, blocks the write
      "fix": "Add contextual links from the six highest-traffic blog posts",
      "expected_effect": "Modest. These pages already rank; this removes a cap rather than "
                         "creating demand.",
      "effort": "3 hours",
      "owner": "client"
    }
  ],

  "metadata": [                        // current vs proposed, paste-ready
    {
      "url": "https://acme.com/services/landscaping",
      "primary_query": "garden landscaping small yards",
      "current_title": "Services | Acme",
      "proposed_title": "Garden Landscaping for Small Urban Yards | Acme",   // 50-60, ENFORCED
      "title_chars": 49,
      "current_meta": "",
      "proposed_meta": "Garden landscaping for small urban yards...",        // 105-155, ENFORCED
      "meta_chars": 131,
      "current_h1": "Our Services",
      "proposed_h1": "Garden Landscaping for Small Urban Yards",
      "notes": "Title, H1 and opening now agree, which is the defence against a Google rewrite."
    }
  ],

  "inventory": [                       // course/19's schema; every row needs a track
    {
      "url": "https://acme.com/blog/old-post",
      "clicks_6mo": null,              // null renders as blank; see not_connected in the report
      "impressions_6mo": null,
      "internal_links_in": 0,
      "external_backlinks": null,
      "cluster": "drainage",
      "last_meaningful_update": null,
      "track": "remove",               // keep | update | merge | remove - NEVER blank
      "reason": "Orphaned and thin (180 words). Confirm backlinks before deleting.",
      "merge_into": ""                 // required when track is merge
    }
  ],

  "internal_links": [
    {
      "type": "opportunity",           // orphan | opportunity | bad anchor | too deep | broken | redirect | unreachable
      "from_url": "https://acme.com/blog/clay-soil",
      "to_url": "https://acme.com/services/drainage",
      "anchor": "",
      "detail": "Mentions 'drainage' 4 times, links to it 0 times",
      "action": "Add a contextual link on the second mention"
    }
  ],

  "media": [
    {
      "page_url": "https://acme.com/",
      "image": "hero-garden.jpg",
      "bytes": 412000,
      "format": "JPEG",
      "natural_size": "2400x1600",
      "has_alt": true,
      "explicit_size": false,
      "measured_webp_saving": "341 KB",
      "action": "Convert to WebP and add width/height. This is the LCP element."
    }
  ]
}
```

Any tab with no rows is skipped - the sheet only carries tabs that have something in them.

---

## The six tabs

### 1. Page Audit
`URL | Area | Check | Observed | Threshold | Verdict | Source | Evidence`

The raw record. Nobody reads it front to back; it exists so any finding can be traced to
the measurement behind it.

### 2. Findings
`Priority | Area | Finding | Evidence | Fix | Expected Effect | Effort | Owner`

The deliverable. Sorted by priority. **More than five rows at "this week" blocks the
write** - a prioritized diagnosis is the product, and forty findings is what an automated
tool produces.

### 3. Metadata
`URL | Primary Query | Current Title | Proposed Title | Title Chars | Current Meta |
Proposed Meta | Meta Chars | Current H1 | Proposed H1 | Notes`

The tab a client actually uses. Current beside proposed, paste-ready. Writing the
replacement rather than flagging the failure is most of the value on this tab.

### 4. Content Inventory
`URL | Clicks 6mo | Impressions 6mo | Internal Links In | External Backlinks | Cluster |
Last Meaningful Update | Track | Reason`

`course/19`'s eight columns plus Reason. Clicks, impressions and backlinks are blank
without a GSC export - that is disclosed in the report, not silently zeroed.

### 5. Internal Links
`Type | From URL | To URL | Anchor | Detail | Action`

Opportunities first; they are the largest single gain and each is a one-line fix.

### 6. Media
`Page URL | Image | Bytes | Format | Natural Size | Has Alt | Explicit Size |
Measured WebP Saving | Action`

Every saving here was measured by re-encoding the real file, not estimated.

---

## What validation blocks

`push_sheet.py` refuses to write rather than shipping a sheet that contradicts itself.
`--force` overrides, and should be rare enough to need a sentence of justification.

| Problem | Why it blocks |
|---|---|
| A proposed title outside 50-60 chars | An audit that ships a replacement breaking its own threshold has failed at its own job |
| A proposed meta outside 105-155 chars | Same |
| A blank track | The decision was avoided |
| `merge` with no reason | Unexecutable - it does not say what it merges into |
| Merging into a page marked `remove` | Consolidation into something about to disappear loses the equity |
| A finding with no evidence | An opinion the client cannot check |
| More than five "this week" findings | Padding; rank them |
| An invalid verdict, priority, track or link type | Typos silently break every filter on the sheet |

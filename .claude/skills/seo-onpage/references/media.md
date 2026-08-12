# Media

Where content quality and page speed collide. `course/17`.

The whole point of this area is that every finding is a measured byte count with a measured
saving. "Optimize your images" is advice the client has already been given and already
ignored. "Your hero is 412KB, and re-encoded to WebP at the same visual quality it is 71KB"
is a different conversation.

```bash
python scripts/media.py --url URL --max-images 30 --out media.json
```

The saving is computed locally with Pillow by actually re-encoding the file. Nothing is
uploaded and nothing on the client's site is changed.

---

## Priority order

Work top-down. The first three are where nearly all the value is.

| # | Check | Threshold | Why it is here |
|---|---|---|---|
| 1 | Hero image weight | **under 150KB** `[s295, s292]` | It is usually the LCP element, so it is the one image that affects a measured threshold |
| 2 | Hero not lazy-loaded, `fetchpriority="high"` | - | Lazy-loading the hero delays the LCP directly. One attribute. |
| 3 | `width` and `height` on every image | present | Removes an entire category of layout shift for one line of HTML each |
| 4 | Format | **WebP or AVIF** `[s295]` | WebP is typically 25-35% smaller than equivalent JPEG and universally supported |
| 5 | Sized to display | natural width under 2x displayed | Bytes the browser discards |
| 6 | Alt text | present on every image | Accessibility first, and it is what the image is indexed on |
| 7 | Filenames | descriptive | **Going forward only** |
| 8 | LCP | **2.5s at p75** `[confirmed]` | A floor. Passing means stop. |

**AVIF:** smaller than WebP with narrower support. `pillow_avif` is not installed here, so
`media.py` measures the WebP saving and cites AVIF directionally. WebP with a JPEG fallback
is the safe default recommendation.

**Do not bulk-rename existing images.** A filename is a URL, and renaming carries the same
inbound-link cost as changing a page slug, for a much smaller return. Name new ones well.

**Alt text test:** how would you describe this to someone over the phone? `alt=""` on a
genuinely decorative image is correct and passes. Omitting the attribute entirely is the
failure. Never stuff it.

**Captions** are read at roughly headline rate and, unlike alt text, are indexable page
content. Under-used.

---

## LCP is a floor, not a lever

The single most common way to waste a client's money in this area is optimizing past good.
LCP at 2.4 seconds passes. Getting it to 1.1 seconds is real engineering effort with no
ranking return.

So: if `lighthouse.py` reports the vital as met, the finding is "this passes, no further
work here is worth buying", and that belongs in the report's "What is fine" section.

---

## Video

Two things matter and one of them is almost always missing.

- **Host on YouTube**, not on the client's server. YouTube is the most-cited domain in
  Google AI Overviews `[practitioner]`, and self-hosting a large video file is a page-weight
  problem with no compensating benefit.
- **Publish the transcript on the page.** This is the highest-value and most-skipped action
  in the whole area, because models train on transcripts and a video with no transcript is
  invisible to every text-based retrieval system.
- No autoplay with sound. Use a facade or lazy embed so the player does not load until
  someone wants it.

---

## Media that earns citations

Worth saying to a client directly, because it changes what they commission:

- Original diagrams and charts built from their own data
- Screenshots of real interfaces showing real numbers
- Comparison tables

Stock photography does none of this. `media.py` flags likely stock by CDN host and filename
so the point can be made with a count attached.

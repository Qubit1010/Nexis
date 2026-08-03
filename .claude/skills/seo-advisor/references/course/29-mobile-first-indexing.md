# Technical SEO - Section 29: Mobile-First Indexing

*Google indexes the mobile version. If your mobile page has less content, that is your page.*

**Bottom line:** Mobile-first indexing means the mobile rendering of your page is the version
Google evaluates for indexing and ranking, for every site. The failure mode is content parity:
anything hidden, trimmed, or omitted on mobile effectively does not exist.

---

## What mobile-first actually means

Google crawls, indexes and ranks using the **mobile version** of your page. Not the desktop
version with a mobile check applied. The mobile version *is* the page as far as Google is
concerned. `[confirmed]`

This is now universal, not a rollout.

Two things it does **not** mean:

- It is not a separate mobile ranking. There is one index, built from mobile crawling.
- It is not "mobile-friendliness as a ranking factor" in the old sense. That is part of page
  experience and behaves as a floor, per Section 3.

## The parity problem

The dominant failure, and it is almost always accidental.

**If your mobile page has less content than desktop, the missing content is not indexed.**
Common causes:

- Content collapsed and loaded on tap rather than present in the DOM
- Sections hidden with `display: none` and never rendered on mobile
- Shortened copy "for mobile readability"
- Sidebars, related content and internal link modules dropped on small screens
- Images and their alt text omitted
- Structured data present only in the desktop template

**Content hidden behind an accordion but present in the DOM is fine.** Google indexes it and
has said so. The problem is content that is *not there*, not content that is not *visible*.

The distinction matters: `display: none` on markup that exists is fine. Conditionally rendering
a component only above a breakpoint is not.

## Parity checklist

Everything below should match between mobile and desktop:

| Element | Requirement |
|---|---|
| **Body content** | Identical. Not a shortened version |
| **Headings** | Same H1 and heading structure |
| **Internal links** | Same links present, even if the nav is collapsed |
| **Structured data** | Present in the mobile template |
| **Metadata** | Same title, meta description, canonical |
| **Images** | Same images with the same alt text |
| **Hreflang** | Present on mobile if used |

A collapsed hamburger menu is fine as long as the links exist in the markup.

## Mobile usability

Separate from parity, and part of page experience:

- **Tap targets** large enough and not crowded together
- **Text readable without zooming**
- **No horizontal scrolling**
- **No intrusive interstitials.** A popup covering the content immediately on arrival from
  search is a specific, documented problem. Cookie banners required by law are fine; a
  full-screen newsletter modal on first paint is not
- **Forms usable on a small screen**, with correct input types so the right keyboard appears

## Responsive versus separate URLs

**Responsive design**, one URL serving all devices, is the recommended configuration and what
almost everyone should use. One URL, one page, no parity risk by construction.

**Separate mobile URLs** (`m.example.com`) are legacy and carry real cost: duplicate content
management, hreflang-style annotations linking the versions, doubled maintenance, and constant
parity risk. If you have this setup, migrating to responsive is usually worth it.

**Dynamic serving**, same URL with different HTML by user agent, is workable but fragile and
easy to get wrong.

## Testing

**Search Console URL Inspection, Test live URL.** Shows what Googlebot smartphone rendered.
This is the authoritative check.

**Chrome DevTools device emulation** with a mid-range device profile. Not just a narrow window,
which does not emulate touch, device pixel ratio, or CPU.

**The parity test**, which takes two minutes and finds most problems:

1. Load the page on desktop, view source, copy the body text.
2. Load it in mobile emulation, view the rendered DOM, copy the body text.
3. Compare. Anything present on desktop and missing on mobile is not indexed.

**Test on a real device** occasionally. Emulators miss touch behaviour, real network latency and
actual CPU throttling.

## The overlap with Section 27

Mobile is also where Core Web Vitals are judged. From Section 27, use the **mobile** report in
Search Console, and remember the 75th percentile is a mid-range phone on a mobile network. The
two sections reinforce each other: mobile parity gets your content indexed, mobile performance
gets it over the floor.

> **Why this matters:** teams design and review on desktop, then check that the mobile version
> "looks okay". Looking okay and containing the same content are different tests. A site can
> look perfect on a phone while quietly having half its content unindexed.

## Do this now

1. **Run URL Inspection, Test live URL on your most important page.** Read the rendered HTML
   Googlebot smartphone received.
2. **Run the parity test.** Desktop body text against mobile rendered DOM. Note anything
   missing.
3. **Check internal links are present** in the mobile markup, including anything inside a
   collapsed menu.
4. **Confirm structured data is in the mobile template**, not just desktop.
5. **Check metadata parity:** title, description, canonical.
6. **Test on a real mid-range phone** if you can borrow one. Note anything awkward.
7. **Check for intrusive interstitials** on arrival from a search result.
8. **Test one form on mobile.** Correct keyboard types, usable tap targets.
9. **Fix any parity gaps you found.** These are indexing problems, not cosmetic ones.

## Capstone step

Your key templates have verified content parity between mobile and desktop, structured data and
metadata present on mobile, internal links intact in collapsed navigation, and no intrusive
interstitials on entry.

## Key takeaways

- Google indexes the mobile version. Content missing on mobile is content that does not exist.
- Hidden behind an accordion but present in the DOM is fine. Conditionally not rendered on small
  screens is not.
- Parity covers content, headings, internal links, structured data, metadata and images. Check
  all of them, not just how the page looks.
- Responsive design removes this entire class of risk by construction. Separate mobile URLs are
  legacy and worth migrating away from.

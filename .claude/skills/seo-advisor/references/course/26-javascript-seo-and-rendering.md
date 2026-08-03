# Technical SEO - Section 26: JavaScript SEO and Rendering

*Google will eventually see your JavaScript. Several AI engines never will.*

**Bottom line:** Google indexes in two waves: raw HTML first, then JavaScript execution 24 to
72 hours later. That delay is survivable. What is not survivable is that AI crawlers frequently
skip JavaScript entirely, so a client-rendered site can be perfectly visible in Google and
structurally invisible to ChatGPT and Perplexity.

---

## The two-wave model

**Wave one.** Googlebot fetches the raw HTML and indexes what is in it, immediately.

**Wave two.** The URL is queued for the Web Rendering Service, which runs JavaScript and
indexes what appears. This happens **24 to 72 hours later**, sometimes longer under load.
`[practitioner]`

Consequences:

- Content only present after JavaScript execution is invisible for days
- Links only present after execution are not followed until wave two, delaying discovery of
  everything behind them
- Time-sensitive content can be stale before it is indexed
- Any wave-two failure means that content is never indexed at all

## The part that changed

**AI crawlers often do not execute JavaScript at all.**

GPTBot, OAI-SearchBot, ClaudeBot and PerplexityBot crawl independently of Googlebot, and
several of them fetch raw HTML and stop. There is no wave two. `[practitioner]`

This is the single most consequential technical fact in the course for 2026. A React or Vue
site with client-side rendering can rank normally in Google, because Google eventually renders,
and be **completely absent from AI answers**, because the AI crawler saw an empty shell.

You would never detect this by checking your Google rankings.

## The rendering options

**Client-side rendering (CSR).** The browser receives a near-empty HTML shell plus JavaScript
that builds the page. Worst case for SEO and effectively fatal for AI visibility.

**Server-side rendering (SSR).** The server renders complete HTML per request. Bots receive
real content immediately. Best for both Google and AI crawlers.

**Static site generation (SSG).** Pages pre-rendered at build time and served as static HTML.
Fastest and excellent for SEO. Ideal for content that does not change per request.

**Incremental static regeneration (ISR).** SSG that revalidates on a schedule. A good middle
ground for content sites.

**Dynamic rendering.** Serve pre-rendered HTML to bots and the JS app to users. Google
previously described this as a workaround rather than a recommendation, and it adds complexity
and a maintenance burden. Prefer SSR or SSG.

**The default recommendation:** if content needs to be found, render it server-side or
statically. Modern frameworks make this the default path rather than an exotic one, which was
not true a few years ago.

## What breaks in practice

**Content behind interaction.** Tabs, accordions and "load more" that fetch content on click.
If it requires a click, bots do not see it. Content in a tab already present in the DOM and
hidden with CSS is fine.

**Infinite scroll** with no paginated fallback. Items past the initial load are unreachable.

**JavaScript-only links.** `<span onclick="navigate()">` is not a link. Bots follow `<a href>`.
This is the most common cause of whole sections going undiscovered.

**Content loaded from an API after page load** with no server-rendered fallback.

**Blocked JavaScript files.** From Section 21, blocking your JS in robots.txt means the render
fails.

**Slow or failing JS.** If a script times out during rendering, that content is not indexed.
Bots do not retry patiently.

## How to test

**Google's URL Inspection, Test live URL, View tested page.** This is the ground truth for what
Google renders. Check both the screenshot and the HTML tab.

**Compare raw against rendered.** View source shows raw HTML that a non-rendering crawler sees.
Inspect element shows the rendered DOM. **The gap between them is what AI crawlers miss.**

**Disable JavaScript in your browser** and load the page. Chrome DevTools, Command Palette,
"Disable JavaScript". What remains is roughly what a non-rendering bot receives. This is the
fastest and most sobering test available.

**Fetch the raw HTML directly** with `curl` or any HTTP client and search it for your main
heading and body text. If they are absent, so is your AI visibility.

## The pragmatic fix path

You rarely need to rebuild.

1. **Server-render or statically generate the content that must be found.** Usually main copy,
   headings, links and metadata. Interactive components can stay client-side.
2. **Make navigation real `<a href>` links.** Cheap and high-impact.
3. **Provide paginated fallbacks** behind infinite scroll.
4. **Move content out of click-gated interactions**, or ensure it is in the DOM and hidden with
   CSS rather than fetched on demand.
5. **Ensure metadata is server-rendered.** Title, meta description and canonical injected by
   JavaScript are unreliable and frequently missed.

That last one catches people constantly. A client-side SEO plugin setting titles after load
often means bots see the default template title.

> **Why this matters:** this is the failure mode most likely to be silently costing you AI
> visibility right now while your Google rankings look fine. The diagnostic takes two minutes,
> disable JavaScript and reload, and almost nobody runs it.

## Do this now

1. **Open your most important page and disable JavaScript.** Reload. What is still there?
2. **View source and search for your H1 text.** Present in the raw HTML, or not?
3. **Do the same for your main body copy, your title tag, and your canonical tag.**
4. **Run URL Inspection, Test live URL, View tested page** on the same URL. Compare Google's
   rendered version against raw source.
5. **Check your navigation links** in raw HTML. Are they real `<a href>` elements?
6. **Fetch the page with curl** and grep for a distinctive sentence from your content. This is
   exactly what a non-rendering AI crawler sees.
7. **Write down what is missing from the raw HTML.** That list is your AI visibility gap.
8. **If content is missing, identify what your site would need** to server-render it, and note
   it as a development task with a clear justification.

## Capstone step

You know precisely what your site looks like without JavaScript, which is what several AI
crawlers see. Any gap between raw and rendered HTML is documented as a specific development
task rather than a vague concern.

## Key takeaways

- Google renders JavaScript in a second wave 24 to 72 hours later. Survivable, but it delays
  everything.
- AI crawlers frequently do not execute JavaScript at all. A client-rendered site can rank fine
  in Google and be entirely absent from AI answers.
- Disable JavaScript and reload. What remains is roughly what a non-rendering bot sees, and it
  is the fastest diagnostic in this tier.
- Server-render the things that must be found: content, headings, real `<a href>` links, and
  especially metadata.

# On-Page & Content - Section 17: Images, Video, and Media

*Media is where content quality and Core Web Vitals collide, and where most sites quietly fail both.*

**Bottom line:** Images are usually the largest thing on a page and the most common cause of a
failing Largest Contentful Paint. Getting them right serves accessibility, search visibility,
and performance at the same time. There are about six rules and they are all cheap.

---

## The weight problem

Your hero image is very often your LCP element, which means it directly determines whether the
page passes the threshold you will meet properly in Section 27.

**Targets:**

| Guideline | Value | Tier |
|---|---|---|
| Hero image weight | under **150KB** | `[practitioner]` |
| Format | **WebP or AVIF** | `[practitioner]` |
| LCP threshold the image must not break | **2.5 seconds** at p75 | `[confirmed]` |

**WebP** is universally supported now and typically 25 to 35% smaller than an equivalent JPEG.
**AVIF** is smaller still with slightly less support. Serving WebP with a JPEG fallback is the
safe default.

**Size the image to its display size.** A 4000px image displayed at 800px wastes most of the
bytes. Responsive `srcset` lets the browser pick.

**Never lazy-load the hero image.** Lazy loading below-the-fold images is good. Lazy loading
the LCP element delays the exact thing being measured. Mark it `fetchpriority="high"` and load
it eagerly.

**Always set width and height attributes.** Without them the browser does not know how much
space to reserve, the layout jumps when the image arrives, and that is Cumulative Layout Shift.
This one attribute pair prevents an entire category of CLS failure.

## Alt text

**Every non-decorative image needs descriptive alt text.** It is an accessibility requirement
first, a search signal second, and the two want the same thing.

**Describe the image, in context.** What would you say to someone who cannot see it and needs
to understand why it is here?

- Bad: `alt="image"`, `alt="seo audit seo checklist seo tools"`, or empty on a meaningful image
- Good: `alt="Search Console coverage report showing 340 pages indexed and 82 excluded"`

**Purely decorative images take an empty alt** (`alt=""`), which tells screen readers to skip
them. Omitting the attribute entirely is not the same thing.

**Do not keyword-stuff.** Alt text stuffed with terms is a recognizable spam pattern and it
actively degrades the accessibility function it exists for.

## File names

`search-console-coverage-report.webp` beats `IMG_4471.webp`. It costs nothing at upload time
and is annoying to fix later.

## Captions

Captions are read at roughly the same rate as headlines, far more than body text. If an image
is carrying real information, caption it. Captions are also genuine content that search engines
index, unlike alt text which is a fallback.

## Video

**Host on YouTube unless you have a reason not to.** YouTube is the most-cited domain in Google
AI Overviews and correlates strongly with ChatGPT visibility, because models are trained on
transcripts. Self-hosting gets you control and costs you that entire discovery surface.
`[practitioner]`

**Publish the transcript on the page.** This is the highest-value and most-skipped video SEO
action. The transcript is indexable text, it is what AI systems can actually retrieve, and it
makes the content accessible. A video with no transcript is invisible to text retrieval.

**Do not autoplay with sound.** It is a page experience problem and people leave.

**Embed lazily.** A YouTube embed pulls a significant amount of JavaScript. Use a facade,
meaning a thumbnail that loads the real player on click, unless the video is the point of the
page.

## Media that earns citations

From Section 5, the content types that still get clicked and cited overlap heavily with
original media:

- **Original diagrams and charts** built from your own data
- **Screenshots of real interfaces** with real numbers in them
- **Comparison tables**, which extract cleanly into AI answers and featured snippets

Stock photography does none of this. A generic photo of people around a laptop adds page
weight and nothing else. If an image is not carrying information, consider whether it should
exist.

> **Why this matters:** media is the most common single cause of a failing Core Web Vitals
> assessment, and images are usually the easiest large win available. Meanwhile alt text and
> transcripts are the cheapest accessibility work you can do, and they happen to be exactly
> what makes media legible to retrieval systems.

## Do this now

1. **Run PageSpeed Insights on your Section 9 page.** Note the LCP element. It is probably an
   image.
2. **Check your hero image weight.** Over 150KB, compress it and convert to WebP. Squoosh is
   free and browser-based.
3. **Confirm the hero is not lazy-loaded** and has `fetchpriority="high"`.
4. **Add width and height attributes** to every image on the page.
5. **Audit alt text** on that page. Every meaningful image described, decorative ones empty,
   nothing stuffed.
6. **Rename any `IMG_1234`-style files** going forward. Do not bulk-rename existing ones, that
   is a URL change with the costs from Section 13.
7. **If the page has a video, publish the transcript** underneath it.
8. **Delete one stock image** that carries no information. Note the weight saved.
9. **Re-run PageSpeed Insights** and compare LCP.

## Capstone step

Your priority page now has compressed modern-format images sized to display, a hero that loads
eagerly with high priority, dimension attributes preventing layout shift, real alt text, and a
transcript if there is video. You have a before-and-after LCP number.

## Key takeaways

- The hero image is usually the LCP element. Under 150KB, WebP or AVIF, sized to display, never
  lazy-loaded, `fetchpriority="high"`.
- Width and height attributes on every image prevent an entire category of Cumulative Layout
  Shift failure.
- Alt text is accessibility first and search second, and both want the same thing: describe the
  image in context. Empty alt for decorative images, never stuffed.
- Publish video transcripts. Untranscribed video is invisible to text retrieval, and YouTube is
  the most-cited domain in AI Overviews.

# Navigation & selectors (how post → profile resolution works)

This is the maintenance map for the resolver in `scripts/facebook-lead-nav.mjs`. Facebook's
markup is deliberately hostile to scraping (randomized class names, scrambled text, link
obfuscation), so the resolver leans on **stable structural/behavioral signals** rather than
classes. If Facebook changes something and resolution breaks, this explains what each step
relies on so you can re-discover the new signal with `playwright-cli` quickly.

## The browser session

All browser steps run through `playwright-cli` attached over CDP to a dedicated, logged-in
Chrome (`playwright-cli attach --cdp=http://localhost:9222`). The resolver is one
`async page => {…}` function executed via `playwright-cli --raw run-code --filename=<tmp>`,
which both navigates and returns JSON in a single call. Note: `setTimeout` is **not**
available in that context — use `page.waitForTimeout(ms)`.

## Step 1 — open the post, let it settle

`page.goto(postUrl)` then wait ~5s, then `scrollTo(0,0)`. The 5s matters: on a slow render
the author header isn't in the DOM yet (an early test failed at 3.5s, succeeded at 5s).

## Step 2 — find the post author

Two strategies, tried in order.

### Strategy A — clean group-scoped user link (most posts)

The author shows up as an anchor `href="/groups/{gid}/user/{uid}/?__cft__…"`. **Commenters
use the same link shape**, so the disambiguator is: take the **first such link that is NOT
inside a comment subtree**. Comments are wrapped in an element with
`aria-label="Comment by …"`, so walk ancestors and reject if any has an `aria-label`
starting with "Comment".

```js
function inComment(el){ while(el){ const al=el.getAttribute&&el.getAttribute('aria-label');
  if (al && /^Comment/i.test(al)) return true; el=el.parentElement; } return false; }
```

First non-comment `/groups/{gid}/user/{uid}/` link with non-empty text → `{gid, uid, name}`.

### Strategy B — hovercard fallback (obfuscated posts)

Some posts (often older ones) obfuscate the header: the author name is rendered with
**scrambled DOM character order** (e.g. `"d r n s S o p e t o"` for "Spotson dr…") and the
author link's href is just `?__cft__[0]=…` (no profile path). Strategy A finds nothing.

The fix mirrors the video: **hover the author actor to spawn the profile hovercard**, which
asynchronously injects the author's *canonical* link.

- **Find the actor:** an `<a>` whose href contains `__cft__`, is **not** the group link
  (`/groups/\d+/?(\?|$)`), not `l.facebook.com`, not in a comment, located in the header band
  (`getBoundingClientRect().top` ≈ 70–240) of the **center column** (`left > 360`).
- **Hover it**, wait ~4s.
- **Read the new canonical link:** diff the set of canonical profile links present *before*
  the hover; the **new** `profile.php?id=…` or vanity link the hovercard injects is the
  author. (The hovercard injects at document body level, not inside a `[role="dialog"]` —
  scoping to dialog/tooltip misses it. That was a real bug during development.)

## Step 3 — resolve the canonical profile URL

- **Strategy A:** navigate to `https://www.facebook.com/groups/{gid}/user/{uid}/` (the
  author's group-member page). There, the **"View profile"** anchor gives
  `profile.php?id={uid}`, and a header name anchor gives the **vanity**
  (`facebook.com/{username}` with `__cft__` tracking). Prefer vanity; strip everything after `?`.
- **Strategy B:** the hovercard already yielded the canonical link directly.

## Normalization & identity

- **Preference:** vanity `https://www.facebook.com/{username}` first, else
  `https://www.facebook.com/profile.php?id={uid}`.
- **Strip tracking:** drop `__cft__`, `__tn__`, `mibextid`, `eav`, `sk`, `fbclid`, etc.
  (keep only `?id=` for profile.php).
- **Why vanity-first:** it matches the existing rows' style in the sheet. But the numeric
  `uid` is the most *stable* dedup key (vanity can change), so `leads-to-crm`'s future
  Facebook channel should key on `uid` / the slug consistently.

## System-path exclusion

When scanning for a "canonical profile" anchor, exclude Facebook system paths so you don't
grab a nav/utility link by mistake:

```
groups | friends | photo | watch | reel | marketplace | notifications | saved | events |
gaming | bookmarks | me | pages | profile.php | afad | story.php | permalink | sharer |
policies | help | settings | business
```

## Re-discovery recipe (when FB changes markup)

1. `playwright-cli attach --cdp=http://localhost:9222`
2. `playwright-cli goto <a known post url>` ; wait.
3. `playwright-cli --raw eval "<js>"` to dump candidate anchors (href + text + bounding box),
   exactly how these selectors were originally found. Prefer roles / hrefs / aria over classes.
4. For the obfuscated case, hover the actor and dump what new links appear.
5. Update the two `page.evaluate(...)` blocks in the resolver template inside
   `scripts/facebook-lead-nav.mjs`.

# Next.js 16 + Tailwind v4 — Gotchas

These specific issues tripped up the reference run. Bake them into the build from the start.

---

## 1. CSS @import order

**Symptom:** Fonts work in dev but fall back to system sans in production build.

**Cause:** Next 16's CSS optimizer (built on Turbopack) requires `@import` rules to come BEFORE everything else. When you write:

```css
@import "tailwindcss";   /* this expands inline to a bunch of CSS rules */
@import url('https://fonts.googleapis.com/...');  /* dropped silently! */
```

…the optimizer sees rules before the second @import and drops it.

**Fix:** Always put font imports above the Tailwind import:

```css
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@300,600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&display=swap');
@import "tailwindcss";

/* rules below this point are fine */
```

`verify_build.py` detects this error and prints the fix.

---

## 2. `"use client"` on interactive components

**Symptom:** Build fails with:
> Error: Event handlers cannot be passed to Client Component props.

**Cause:** Server Components (the default) can't have `onClick`, `onChange`, `onSubmit`, `useState`, `useEffect`, or any browser API (`window`, `localStorage`, etc.). The most common offenders are:
- Navbar with mobile-menu toggle (`useState`)
- Footer with "to top" button (`onClick`)
- Process/FAQ accordions (`useState`)
- Any image carousel or marquee with state

**Fix:** Add `"use client";` as the very first line of any such component file (before imports).

```tsx
"use client";
import Link from "next/link";

export default function Footer() {
  return <button onClick={() => window.scrollTo(0, 0)}>Top</button>;
}
```

Components that are purely presentational stay as Server Components — only mark client-side what truly needs it. This is faster.

---

## 3. `<Image fill />` needs `sizes`

**Symptom:** Build passes but logs warnings:
> Image with src "/images/hero.png" has "fill" but is missing "sizes" prop.

**Cause:** Next can't tell the browser what size to download without `sizes`. Not a fatal error, but it tanks performance and clutters logs.

**Fix:** Always pass `sizes` when using `fill`:

```tsx
<Image src="/images/hero.png" alt="Hero" fill sizes="(max-width: 768px) 100vw, 50vw" className="object-cover" />
```

Rough heuristic for `sizes`:
- Full-bleed image: `100vw`
- 2-column grid: `(max-width: 768px) 100vw, 50vw`
- 3-column grid: `(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw`
- Small avatar (~32-64px): `64px`

---

## 4. `--use-npm` flag on `create-next-app`

**Symptom:** `create-next-app` fails on Windows with `pnpm is not recognized`.

**Cause:** Recent `create-next-app` defaults to pnpm if available, and on a clean Windows install pnpm usually isn't there.

**Fix:** Always pass `--use-npm`:

```bash
npx create-next-app@latest faithful \
  --typescript --tailwind --app --src-dir \
  --import-alias "@/*" --use-npm --no-git --yes
```

---

## 5. The scaffold's AGENTS.md / CLAUDE.md

**What you'll see:** `create-next-app` drops an `AGENTS.md` and `CLAUDE.md` in the new project. They say things like _"This is NOT the Next.js you know"_ and instruct the agent to read `node_modules/next/dist/docs/` first.

**What to do:** Ignore these instructions for our purposes. The Next.js 16 patterns we use here are stable and documented in this file. Reading the entire next docs every build would be a massive context tax with no payoff.

You can leave the files in place — they don't break anything — but don't follow their boilerplate guidance.

---

## 6. Tailwind v4 token system

**What's different from v3:**
- `tailwind.config.ts` is OPTIONAL in v4 — you can define tokens directly in `globals.css` using `@theme`:

```css
@import "tailwindcss";

@theme {
  --color-bg: rgb(29, 30, 31);
  --color-surface: rgb(31, 31, 31);
  --font-satoshi: 'Satoshi', sans-serif;
  --radius-card: 16px;
}
```

- However, a `tailwind.config.ts` still works and is sometimes clearer for complex themes. Either is fine — pick one and stay consistent.
- Arbitrary value syntax in classNames works fine: `text-[rgb(242,236,228)]`, `rounded-[16px]`, `font-[Satoshi]`.

For most rebuilds, inline arbitrary values + a small @theme block is the fastest path.

---

## 7. `next/font` vs CSS @import

Both work. Rough heuristic:
- **Google Font + you need it system-wide:** use `next/font/google` — better perf, Next handles preload + subsetting
- **Fontshare or any non-Google font:** use CSS @import (no native next/font support)
- **One-off accent font used in a single section:** CSS @import is fine

`next/font` example (`layout.tsx`):

```tsx
import { Inter, Playfair_Display } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", weight: ["300", "400", "600"] });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair", style: "italic" });

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="font-[var(--font-inter)]">{children}</body>
    </html>
  );
}
```

---

## 8. `next.config.ts` for remote images

If you keep any images served from a CDN (rather than downloading them locally), add:

```ts
import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "framerusercontent.com" },
    ],
  },
};
export default nextConfig;
```

We default to downloading assets locally (via `download_assets.py`) so this is rarely needed. But include it as a fallback when an asset fails to download.

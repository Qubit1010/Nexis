# Faithful Rebuild — Patterns

How to translate SPEC.md into a working Next.js app. Read this before writing any code in `faithful/`. The reference implementation that exemplifies these patterns is [projects/nexuspoint-landing/faithful/](projects/nexuspoint-landing/faithful/) — open any of its section components for a worked example.

## File layout

```
faithful/
├── next.config.ts          # may need images.remotePatterns
├── tailwind.config.ts      # optional in Tailwind v4 — small theme block is enough
├── src/
│   ├── app/
│   │   ├── globals.css     # font @import + tokens + Tailwind import
│   │   ├── layout.tsx      # root layout, metadata
│   │   └── page.tsx        # composes section components in order
│   ├── components/
│   │   └── sections/       # one file per section in SPEC inventory
│   │       ├── Navbar.tsx
│   │       ├── Hero.tsx
│   │       ├── Services.tsx
│   │       ├── Work.tsx
│   │       └── ...
│   └── lib/
│       └── content.ts      # all copy, one typed object per section
└── public/
    └── images/             # copied from extraction/public-images/
```

## content.ts

The single source of mutable content. Use `assets/content-template.ts` as the starter. Shape it so each section consumes one named export:

```ts
export const HERO = {
  headline: "Automate the Work. Scale the Revenue.",
  subheadline: "I build custom AI workflows...",
  cta: { label: "My Services", href: "#services" },
};

export const SERVICES = [
  { number: "01", title: "...", body: "...", cta: "...", href: "..." },
  { number: "02", ... },
];
```

Use TypeScript readonly arrays + `as const` if the data is fully static. The aim: every word the user might want to change in 6 months lives in this file, NOT in component JSX.

## globals.css

```css
/* Fonts FIRST — see nextjs-gotchas.md */
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@300,600&display=swap');
@import "tailwindcss";

:root {
  --font-display: 'Satoshi', sans-serif;
  --color-bg: rgb(29, 30, 31);
  --color-surface: rgb(31, 31, 31);
  --color-text: rgb(242, 236, 228);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-display);
  font-weight: 300;
  -webkit-font-smoothing: antialiased;
}

/* Marquee — used by ticker / logo strips */
@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.marquee-track { display: flex; width: max-content; animation: marquee 25s linear infinite; }
```

## tailwind.config.ts (optional but useful for tokens)

```ts
import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "rgb(29, 30, 31)",
        surface: "rgb(31, 31, 31)",
        border: "rgb(52, 51, 48)",
        "text-primary": "rgb(242, 236, 228)",
        "text-muted": "rgba(242, 236, 228, 0.55)",
        accent: "rgba(0, 183, 255, 0.6)",
      },
      borderRadius: { pill: "500px", card: "16px" },
    },
  },
};
export default config;
```

## layout.tsx

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "<Title from SPEC>",
  description: "<og:description from metadata.json>",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head><link rel="icon" href="/images/favicon.png" /></head>
      <body className="min-h-full antialiased">{children}</body>
    </html>
  );
}
```

## page.tsx

```tsx
import Navbar from "@/components/sections/Navbar";
import Hero from "@/components/sections/Hero";
import Services from "@/components/sections/Services";
// ...one per section

export default function Home() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main id="main">
        <Hero />
        <Services />
        {/* …in the order SPEC inventory lists */}
      </main>
      <Footer />
    </div>
  );
}
```

## Section component recipes

### Navbar (centered pill with CTA, sticky)
```tsx
"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { NAV_LINKS } from "@/lib/content";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return <header className="fixed top-0 inset-x-0 z-50 flex justify-center pt-4"> ... </header>;
}
```
Use `useState` only if you need the scroll-state effect — otherwise this can be a Server Component.

### Hero (full viewport, centered, image+text)
Server Component is fine. Use `next/image` with `priority` on the hero image, `sizes` set to cover the viewport.

### Services / Work / Testimonials (grid of cards)
Loop `SERVICES.map(...)` in JSX. Each card is a `<article>` (semantic HTML) with surface bg + 1px border. Use the `rounded-card`/`rounded-[16px]` token.

### Process (numbered list, often expandable)
If interactive (accordion), needs `"use client"` + `useState`. Otherwise render all sections expanded.

### Ticker / Logo marquee (continuous scroll)
Server Component is fine. Duplicate the items 2–3× inside a `marquee-track` div so the CSS animation creates a seamless loop.

### Footer (often has scroll-to-top button)
`"use client"` IF it has `onClick`. Otherwise Server Component.

## Animation policy

For section reveals, two reasonable choices:
1. **Pure CSS (`fade-up.visible` toggled by IntersectionObserver in a small client wrapper)** — minimal JS
2. **Framer Motion** — install `framer-motion`, use `<motion.div initial={{opacity:0, y:24}} whileInView={{opacity:1, y:0}} viewport={{once:true}} transition={{duration:0.7, ease:[0.22,1,0.36,1]}}>` — works great and is what Framer's own sites use

Pick one and stay consistent. Default to Framer Motion if you'd otherwise be writing 50+ lines of CSS+JS for IntersectionObserver scaffolding.

## What NOT to do

- Don't put copy inline in component JSX. It must live in `content.ts`.
- Don't add Storybook, testing setup, ESLint plugins, or any tooling beyond what `create-next-app` ships.
- Don't write CSS modules. Tailwind utility classes + occasional inline styles in JSX are sufficient.
- Don't pre-optimize. Get the page rendering correctly first, then look at Lighthouse if needed.

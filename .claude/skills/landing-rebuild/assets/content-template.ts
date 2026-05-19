// src/lib/content.ts
//
// All site copy lives here. Section components import named exports
// from this file — never put copy inline in JSX. Future edits should
// touch this file only.
//
// Shape:
//   - one named export per section
//   - arrays for repeating items (services, work, testimonials, etc.)
//   - readonly via `as const` where the structure is fully static
//
// Replace placeholders during Phase 4. Keep verbatim copy from the
// source site — do NOT paraphrase.

export const SITE = {
  brand: "<BRAND_NAME>",
  tagline: "<short tagline shown in <title> or footer>",
  url: "<https://example.com>",
} as const;

export const NAV_LINKS = [
  { label: "Services", href: "#services" },
  { label: "Work", href: "#work" },
  { label: "Process", href: "#process" },
  { label: "About", href: "#about" },
  { label: "Contact", href: "#contact" },
] as const;

export const HERO = {
  eyebrow: "<optional small label above headline, or empty string>",
  headline: "<verbatim hero headline from source>",
  subheadline: "<verbatim hero subheadline>",
  cta: { label: "<CTA label>", href: "<href or #anchor>" },
  secondaryCta: { label: "<optional, or null>", href: "<or null>" },
  image: { src: "/images/hero.png", alt: "<descriptive alt>" },
};

export const LOGOS = [
  // logo strip / ticker — empty array hides the section
  // { src: "/images/logo-1.svg", alt: "Client 1" },
];

export const SERVICES = [
  {
    number: "01",
    title: "<service title>",
    body: "<service description, verbatim>",
    cta: { label: "Learn more", href: "#" },
  },
  // duplicate per service in source
] as const;

export const WORK = [
  {
    title: "<project title>",
    client: "<client name>",
    image: { src: "/images/work-1.png", alt: "<alt>" },
    href: "<case study url or # if none>",
    tags: ["<tag>", "<tag>"],
  },
] as const;

export const PROCESS = [
  {
    number: "01",
    title: "<step title>",
    body: "<step description>",
  },
] as const;

export const TESTIMONIALS = [
  {
    quote: "<verbatim testimonial>",
    name: "<author>",
    role: "<role / company>",
    avatar: { src: "/images/avatar-1.png", alt: "<name>" },
  },
] as const;

export const ABOUT = {
  headline: "<about section headline>",
  body: "<about body, verbatim — may be multi-paragraph, split on \\n\\n if needed>",
  image: { src: "/images/about.png", alt: "<alt>" },
  stats: [
    // optional — { label: "Years", value: "5+" }
  ],
};

export const CTA = {
  headline: "<closing CTA headline>",
  body: "<optional supporting line>",
  primary: { label: "<label>", href: "<href>" },
};

export const FOOTER = {
  blurb: "<short footer blurb / colophon>",
  columns: [
    {
      heading: "Company",
      links: [
        { label: "About", href: "#about" },
        { label: "Contact", href: "#contact" },
      ],
    },
  ],
  socials: [
    // { label: "LinkedIn", href: "https://..." }
  ],
  copyright: "© <YEAR> <BRAND>. All rights reserved.",
};

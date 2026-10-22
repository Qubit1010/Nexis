import { useMemo } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";

/** Strip YAML frontmatter for display; return it separately. */
export function splitFrontmatter(md: string): { fm: string | null; body: string } {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  return m ? { fm: m[1], body: md.slice(m[0].length) } : { fm: null, body: md };
}

export function renderMarkdown(md: string): string {
  const html = marked.parse(md, { async: false, gfm: true, breaks: false }) as string;
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
}

export function Markdown({ md, className = "" }: { md: string; className?: string }) {
  const html = useMemo(() => renderMarkdown(md), [md]);
  return <div className={`prose-draft ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}

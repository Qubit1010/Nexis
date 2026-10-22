// Publish an approved blog version into an Astro site repo: pre-flight, write the
// content file + images, build (the schema gate), commit only those paths, push,
// deploy, then confirm the live URL. Content OS owns this; generation runs never
// touch the site repos.
import fs from "node:fs";
import path from "node:path";
import { rootEnv } from "../config.ts";
import { run, tail } from "../lib/proc.ts";
import { pktParts } from "../lib/time.ts";
import { splitFrontmatter, fmValue } from "../engine/checks.ts";
import { waitForLive } from "./verify-live.ts";

export interface SiteConfig {
  repo: string;
  branch: string;
  contentDir: string;
  assetsDir: string;
  siteUrl: string;
  blogPath: string;
  deployMode: "git" | "vercel-cli";
  vercelScope?: string;
  categories?: string[];
}

export class PublishError extends Error {
  /** retry may help (network); false = needs a human or a fix first */
  retryable: boolean;
  constructor(message: string, retryable = false) {
    super(message);
    this.retryable = retryable;
  }
}

const git = (repo: string, args: string[], timeoutMs = 120_000) => run("git", args, { cwd: repo, timeoutMs });

function pktDate(iso: string): string {
  const p = pktParts(iso);
  return `${p.y}-${String(p.m).padStart(2, "0")}-${String(p.d).padStart(2, "0")}`;
}

/** Set datePublished (first publish only) and dateModified in the frontmatter. */
export function stampDates(md: string, publishedOn: string, modifiedOn: string, keepPublished: boolean): string {
  const { fm, body } = splitFrontmatter(md);
  if (!fm) return md;
  let next = fm;
  const set = (key: string, value: string) => {
    const re = new RegExp(`^${key}:.*$`, "m");
    next = re.test(next) ? next.replace(re, `${key}: ${value}`) : `${next}\n${key}: ${value}`;
  };
  if (!keepPublished || !fmValue(fm, "datePublished")) set("datePublished", publishedOn);
  set("dateModified", modifiedOn);
  return `---\n${next}\n---\n${body.startsWith("\n") ? body : `\n${body}`}`;
}

export function slugFromVersion(main: string, metaSlug: unknown, mainFile: string): string {
  const s = typeof metaSlug === "string" && metaSlug ? metaSlug : path.basename(mainFile, path.extname(mainFile));
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s)) throw new PublishError(`slug "${s}" is not a clean kebab-case slug`);
  void main;
  return s;
}

export async function publishToAstro(input: {
  site: SiteConfig;
  slug: string;
  title: string;
  markdown: string;
  images: string[];
  previousSha: string | null;
  gitIdentity: { name: string; email: string };
  onCommitted: (sha: string) => Promise<void>;
  log: (msg: string) => void;
}): Promise<{ sha: string; url: string }> {
  const { site, slug, log } = input;
  const repo = site.repo;
  if (!fs.existsSync(path.join(repo, ".git"))) throw new PublishError(`${repo} is not a git repo`);
  const relMd = `${site.contentDir}/${slug}.md`.replace(/\\/g, "/");
  const relAssets = `${site.assetsDir}/${slug}`.replace(/\\/g, "/");
  const absMd = path.join(repo, relMd);
  const absAssets = path.join(repo, relAssets);

  // 1. Pre-flight
  const branch = (await git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])).out.trim();
  if (branch !== site.branch) throw new PublishError(`${repo} is on "${branch}", expected "${site.branch}". Switch branches first.`);
  const dirty = (await git(repo, ["status", "--porcelain", "--", relMd, relAssets])).out.trim();
  if (dirty) throw new PublishError(`uncommitted changes already sit at the target paths:\n${dirty}`);
  const pull = await git(repo, ["pull", "--ff-only", "origin", site.branch], 180_000);
  if (pull.code !== 0) {
    const msg = pull.err || pull.out;
    throw new PublishError(`git pull --ff-only failed: ${tail(msg, 400)}`, /could not resolve|timed out|unable to access|network/i.test(msg));
  }
  const existed = fs.existsSync(absMd);
  if (existed && !input.previousSha) throw new PublishError(`${relMd} already exists in the site and was not published by this item. Change the slug.`);
  log(`pre-flight ok on ${repo} (${branch})`);

  // 2. Write content + images
  const today = pktDate(new Date().toISOString());
  const md = stampDates(input.markdown, today, today, existed);
  const createdAssetsDir = !fs.existsSync(absAssets);
  fs.mkdirSync(path.dirname(absMd), { recursive: true });
  fs.writeFileSync(absMd, md.replace(/\r\n/g, "\n"));
  if (input.images.length) {
    fs.mkdirSync(absAssets, { recursive: true });
    for (const img of input.images) fs.copyFileSync(img, path.join(absAssets, path.basename(img)));
  }
  const rollback = async () => {
    if (existed) await git(repo, ["checkout", "--", relMd]);
    else fs.rmSync(absMd, { force: true });
    if (createdAssetsDir) fs.rmSync(absAssets, { recursive: true, force: true });
    else if (fs.existsSync(absAssets)) await git(repo, ["checkout", "--", relAssets]);
  };

  // 3. Build: the content-collection schema is the real validator
  if (!fs.existsSync(path.join(repo, "node_modules"))) {
    log("installing site dependencies (npm ci)");
    const ci = await run("npm", ["ci", "--no-audit", "--no-fund"], { cwd: repo, timeoutMs: 15 * 60_000, shell: true });
    if (ci.code !== 0) {
      await rollback();
      throw new PublishError(`npm ci failed in ${repo}: ${tail(ci.err || ci.out, 600)}`);
    }
  }
  log("building the site");
  const build = await run("npm", ["run", "build"], { cwd: repo, timeoutMs: 15 * 60_000, shell: true });
  if (build.code !== 0) {
    await rollback();
    throw new PublishError(`site build failed, nothing was committed:\n${tail((build.out + "\n" + build.err).trim(), 1500)}`);
  }

  // 4. Commit only our paths
  const addPaths = [relMd, ...(fs.existsSync(absAssets) ? [relAssets] : [])];
  await git(repo, ["add", "--", ...addPaths]);
  const staged = (await git(repo, ["diff", "--cached", "--name-only", "--", ...addPaths])).out.trim();
  let sha = input.previousSha ?? "";
  if (staged) {
    const ident = input.gitIdentity.email ? ["-c", `user.name=${input.gitIdentity.name}`, "-c", `user.email=${input.gitIdentity.email}`] : [];
    const commit = await git(repo, [...ident, "commit", "-m", `Publish ${input.title.replace(/[\r\n]+/g, " ").slice(0, 120)}`, "--", ...addPaths]);
    if (commit.code !== 0) {
      await git(repo, ["reset", "-q", "--", ...addPaths]);
      await rollback();
      const msg = commit.err || commit.out;
      throw new PublishError(/identity|user\.email|user\.name/i.test(msg) ? `git has no identity in ${repo}. Set name and email in Content OS Settings > Git.` : `git commit failed: ${tail(msg, 400)}`);
    }
    sha = (await git(repo, ["rev-parse", "HEAD"])).out.trim();
    await input.onCommitted(sha); // recorded before the push, so a retry treats this as an update
    log(`committed ${sha.slice(0, 7)}`);
  } else log("nothing changed since the last publish; skipping the commit");

  // 5. Push
  const push = await git(repo, ["push", "origin", site.branch], 180_000);
  if (push.code !== 0) throw new PublishError(`git push failed (the commit is safe locally; retry): ${tail(push.err || push.out, 400)}`, true);
  log("pushed");

  // 6. Deploy
  if (site.deployMode === "vercel-cli") await vercelDeploy(repo, site.vercelScope, log);

  // 7. Verify live
  const url = `${site.siteUrl.replace(/\/+$/, "")}${site.blogPath.endsWith("/") ? site.blogPath : `${site.blogPath}/`}${slug}`;
  log(`waiting for ${url}`);
  const live = await waitForLive(url, input.title);
  if (!live.ok) throw new PublishError(`pushed ${sha.slice(0, 7)} but ${url} is not live yet (${live.detail}). If the site deploys on push, check Vercel; otherwise set this site's deploy mode to vercel-cli.`, true);
  return { sha, url };
}

async function vercelDeploy(repo: string, scope: string | undefined, log: (m: string) => void): Promise<void> {
  const token = rootEnv().VERCEL_TOKEN;
  const common = [...(scope ? ["--scope", scope] : []), ...(token ? ["--token", token] : [])];
  log("deploying with the Vercel CLI (production candidate, then promote)");
  const dep = await run("npx", ["--yes", "vercel", "deploy", "--prod", "--skip-domain", "--yes", ...common], { cwd: repo, timeoutMs: 20 * 60_000, shell: true });
  if (dep.code !== 0) {
    const msg = dep.err || dep.out;
    throw new PublishError(
      /not logged in|no existing credentials|token/i.test(msg) ? "the Vercel CLI is not logged in on this machine. Run `npx vercel login` or set VERCEL_TOKEN in D:/Nexis/.env." : `vercel deploy failed: ${tail(msg, 600)}`,
      false,
    );
  }
  const url = (dep.out.match(/https:\/\/[^\s]+\.vercel\.app/g) || []).pop();
  if (!url) throw new PublishError(`vercel deploy succeeded but printed no deployment URL: ${tail(dep.out, 300)}`);
  const promote = await run("npx", ["--yes", "vercel", "promote", url, "--yes", ...common], { cwd: repo, timeoutMs: 10 * 60_000, shell: true });
  if (promote.code !== 0) throw new PublishError(`vercel promote failed for ${url}: ${tail(promote.err || promote.out, 400)}`, true);
  log(`promoted ${url}`);
}

#!/usr/bin/env node
/**
 * preflight.mjs — get the environment ready for facebook-lead-nav, then report status.
 *
 * Three things have to be true before the enrichment can run, and all three were
 * fiddly to set up by hand. This makes them one command:
 *   1. gws (Google Workspace CLI) has a valid token   -> needed to read/write the sheet
 *   2. a dedicated Chrome is running with CDP on :9222 -> needed for playwright-cli to attach
 *   3. that Chrome is logged into Facebook             -> needed to see group posts
 *
 * It will LAUNCH the dedicated Chrome if it's not up, but it never tries to silently
 * re-auth Google or log into Facebook for you (both are interactive + security-sensitive)
 * — it surfaces the exact next action instead.
 *
 * Usage:
 *   node preflight.mjs
 *   node preflight.mjs --cdp http://localhost:9222 --profile "C:\\Users\\Aleem\\fb-automation-profile"
 */

import { execSync } from 'node:child_process';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';

const args = process.argv.slice(2);
const flag = (name, def) => { const i = args.indexOf(`--${name}`); if (i === -1) return def; const v = args[i + 1]; return v && !v.startsWith('--') ? v : true; };

const CDP = flag('cdp', 'http://localhost:9222');
const PORT = (CDP.match(/:(\d+)/) || [])[1] || '9222';
const PROFILE = flag('profile', process.env.FB_AUTOMATION_PROFILE || 'C:\\Users\\Aleem\\fb-automation-profile');
const CHROME_CANDIDATES = [
  `${process.env['ProgramFiles'] || 'C:\\Program Files'}\\Google\\Chrome\\Application\\chrome.exe`,
  `${process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)'}\\Google\\Chrome\\Application\\chrome.exe`,
  `${process.env['LOCALAPPDATA'] || ''}\\Google\\Chrome\\Application\\chrome.exe`,
];

const sh = (cmd) => execSync(cmd, { shell: 'bash', encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], maxBuffer: 32 * 1024 * 1024 });
const attempt = (fn) => { try { return fn(); } catch (e) { return null; } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function cdpUp() {
  const out = attempt(() => sh(`curl -s --max-time 4 http://localhost:${PORT}/json/version`));
  if (out && out.includes('Browser')) { try { return JSON.parse(out).Browser; } catch { return 'up'; } }
  return null;
}

async function main() {
  const report = [];
  let ready = true;

  // ---- 1. gws auth ----------------------------------------------------------
  const status = attempt(() => sh('gws auth status 2>/dev/null'));
  let gwsOk = false;
  if (status) { try { gwsOk = JSON.parse(status.slice(status.indexOf('{'))).token_valid === true; } catch { gwsOk = /"token_valid":\s*true/.test(status); } }
  if (gwsOk) report.push('  [OK]  gws token valid');
  else { ready = false; report.push('  [!!]  gws token invalid/expired  ->  run:  gws auth login   (then open the printed URL, sign in as hassanaleem86@gmail.com)'); }

  // ---- 2. CDP Chrome --------------------------------------------------------
  let browser = await cdpUp();
  if (!browser) {
    const chrome = CHROME_CANDIDATES.find((p) => existsSync(p));
    if (!chrome) { ready = false; report.push('  [!!]  CDP down and chrome.exe not found  ->  launch Chrome manually with --remote-debugging-port=' + PORT); }
    else {
      report.push(`  [..]  CDP down — launching dedicated Chrome (${PROFILE}) ...`);
      const child = spawn(chrome, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check', 'https://www.facebook.com'], { detached: true, stdio: 'ignore' });
      child.unref();
      for (let i = 0; i < 12 && !browser; i++) { await sleep(1500); browser = await cdpUp(); }
      if (browser) report.push(`  [OK]  CDP up (${browser})`);
      else { ready = false; report.push('  [!!]  Chrome launched but CDP did not come up on :' + PORT); }
    }
  } else { report.push(`  [OK]  CDP up (${browser})`); }

  // ---- 3. attach + Facebook login ------------------------------------------
  if (browser) {
    attempt(() => sh(`playwright-cli attach --cdp=${CDP} 2>&1`)); // idempotent-ish; ignores "already attached"
    const probe = attempt(() => sh(`playwright-cli --raw eval "(() => { const li = !!document.querySelector('[aria-label=\\"Your profile\\"i], div[role=\\"navigation\\"], a[href*=\\"/me/\\"]'); const lf = !!document.querySelector('input[name=\\"pass\\"]'); return JSON.stringify({ host: location.host, li, lf }); })()" 2>/dev/null`));
    let fb = null; if (probe) { try { fb = JSON.parse(probe.slice(probe.indexOf('{'))); } catch {} }
    if (fb && fb.host && fb.host.includes('facebook') && fb.li && !fb.lf) report.push('  [OK]  playwright-cli attached + Facebook logged in');
    else if (fb && fb.host && fb.host.includes('facebook')) { ready = false; report.push('  [!!]  Attached, but NOT logged into Facebook  ->  log in once in the launched Chrome window'); }
    else { report.push('  [..]  Attached; open a facebook.com tab in the launched Chrome to confirm login'); }
  }

  // ---- summary --------------------------------------------------------------
  console.log('\n=== facebook-lead-nav preflight ===');
  console.log(report.join('\n'));
  if (ready) {
    console.log('\nREADY ✓   next:  node ' + 'scripts/facebook-lead-nav.mjs --dry-run --limit 3');
    process.exit(0);
  } else {
    console.log('\nNOT READY ✗  — resolve the [!!] item(s) above, then re-run preflight.');
    process.exit(1);
  }
}

main().catch((e) => { console.error('preflight error:', e); process.exit(1); });

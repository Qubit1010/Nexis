#!/usr/bin/env node
/**
 * facebook-lead-nav.mjs
 *
 * Enriches the "Instant Facebook Leads" Google Sheet. Column A ("Link") holds
 * Facebook group POST urls (facebook.com/groups/{id}/posts/{id}/). For each post
 * row that has not been enriched yet, this script:
 *   1. opens the post,
 *   2. finds the post author (first non-comment /groups/{gid}/user/{uid}/ link),
 *   3. opens that author's group-member page and resolves their canonical profile
 *      URL (vanity preferred, profile.php?id= fallback) -- the video's "View profile",
 *   4. writes Lead Name + Profile URL + Date Added back to the same row in new columns.
 *
 * Browser steps run through the `playwright-cli` skill, attached over CDP to a
 * dedicated, already-logged-in Chrome (run scripts/preflight.mjs first; see SKILL.md).
 * Sheet I/O runs through the `gws` Google Workspace CLI. Sub-commands are invoked via
 * bash so single-quoted JSON payloads pass through cleanly on Windows/git-bash.
 *
 * Usage:
 *   node facebook-lead-nav.mjs --dry-run            # resolve + print, write nothing
 *   node facebook-lead-nav.mjs --limit 3            # enrich up to 3 new rows
 *   node facebook-lead-nav.mjs --start-row 272      # only consider rows >= 272
 *
 * Flags:
 *   --limit N         max rows to enrich this run (default 15)
 *   --dry-run         resolve and print the table, do not write to the sheet
 *   --start-row N     skip sheet rows below N (1-based, includes header offset)
 *   --spreadsheet ID  target spreadsheet id (default Instant Facebook Leads / env FB_LEADS_SHEET_ID)
 *   --tab NAME        target tab name (default Sheet1 / env FB_LEADS_TAB)
 *   --cdp URL         CDP endpoint of the attached Chrome (default http://localhost:9222)
 *   --delay-min MS    min delay between posts (default 3000)
 *   --delay-max MS    max delay between posts (default 8000)
 */

import { execSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// ---- Args -------------------------------------------------------------------
const args = process.argv.slice(2);
const flag = (name, def) => {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  const v = args[i + 1];
  return v && !v.startsWith('--') ? v : true;
};

// ---- Config (overridable, defaults to the Instant Facebook Leads sheet) ------
const SPREADSHEET_ID = flag('spreadsheet', process.env.FB_LEADS_SHEET_ID || '1ao7_Aam6bsI6D4xk-Mfc-EM54WZYivN9petcZU2P68U');
const TAB = flag('tab', process.env.FB_LEADS_TAB || 'Sheet1');
const POST_RE = /facebook\.com\/groups\/[^/]+\/(posts|permalink)\//i;
const NEW_HEADERS = ['Lead Name', 'Profile URL', 'Date Added'];
const RESOLVER_PATH = join(tmpdir(), 'fb-lead-resolver.js').replace(/\\/g, '/');

const LIMIT = parseInt(flag('limit', '15'), 10);
const DRY_RUN = args.includes('--dry-run');
const START_ROW = parseInt(flag('start-row', '2'), 10);
const CDP = flag('cdp', 'http://localhost:9222');
const DELAY_MIN = parseInt(flag('delay-min', '3000'), 10);
const DELAY_MAX = parseInt(flag('delay-max', '8000'), 10);

// ---- Helpers ----------------------------------------------------------------
const sh = (cmd) => execSync(cmd, { shell: 'bash', encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], maxBuffer: 64 * 1024 * 1024 });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const jitter = () => DELAY_MIN + Math.floor(Math.random() * Math.max(1, DELAY_MAX - DELAY_MIN));
const parseJsonLoose = (out) => { const i = out.indexOf('{'); const j = out.lastIndexOf('}'); if (i === -1 || j === -1) throw new Error('no JSON in output: ' + out.slice(0, 200)); return JSON.parse(out.slice(i, j + 1)); };

// 0-based column index -> A1 column letter
function colLetter(idx) {
  let s = '';
  idx += 1;
  while (idx > 0) { const m = (idx - 1) % 26; s = String.fromCharCode(65 + m) + s; idx = Math.floor((idx - 1) / 26); }
  return s;
}

// ---- gws sheet I/O ----------------------------------------------------------
function readRange(range) {
  const out = sh(`gws sheets +read --spreadsheet ${SPREADSHEET_ID} --range "${TAB}!${range}" --format json`);
  return parseJsonLoose(out).values || [];
}
function batchUpdate(data) {
  if (!data.length) return;
  const body = JSON.stringify({ valueInputOption: 'RAW', data });
  // single-quoted JSON is safe in bash because JSON contains no single quotes
  sh(`gws sheets spreadsheets values batchUpdate --params '${JSON.stringify({ spreadsheetId: SPREADSHEET_ID })}' --json '${body}'`);
}

// ---- playwright-cli ---------------------------------------------------------
function ensureAttached() {
  try {
    const out = sh(`playwright-cli --raw eval "location.host" 2>/dev/null`);
    if (out && out.toLowerCase().includes('facebook')) return;
  } catch { /* not attached yet */ }
  try { sh(`playwright-cli attach --cdp=${CDP} 2>&1`); } catch (e) { /* may already be attached */ }
}

const RESOLVER_TEMPLATE = (postUrl) => `async page => {
  const POST_URL = ${JSON.stringify(postUrl)};
  const sleep = ms => page.waitForTimeout(ms);
  const SYS = /\\/(groups|friends|photo|watch|reel|marketplace|notifications|saved|events|gaming|bookmarks|me|pages|profile\\.php|afad|story\\.php|permalink|sharer|policies|help|settings|business)\\b/;
  const isCanonical = h => /^https?:\\/\\/www\\.facebook\\.com\\/[A-Za-z0-9.]+\\/?(\\?|$)/.test(h) && !SYS.test(h);
  try { await page.goto(POST_URL, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  catch (e) { return { ok:false, stage:'goto-post', error:String(e).slice(0,120) }; }
  await sleep(5000);
  await page.evaluate(() => window.scrollTo(0, 0));
  await sleep(800);

  // ---- Strategy A: clean group-scoped author link (/groups/{gid}/user/{uid}/) ----
  const author = await page.evaluate(() => {
    function inComment(el){ while(el){ const al = el.getAttribute && el.getAttribute('aria-label'); if (al && /^Comment/i.test(al)) return true; el = el.parentElement; } return false; }
    for (const a of document.querySelectorAll('a[href*="/user/"]')) {
      if (inComment(a)) continue;
      const m = (a.getAttribute('href') || '').match(/\\/groups\\/(\\d+)\\/user\\/(\\d+)/);
      const txt = (a.innerText || '').trim().replace(/\\s+/g, ' ');
      if (m && txt) return { gid: m[1], uid: m[2], name: txt.slice(0, 80) };
    }
    return null;
  });

  if (author) {
    const guURL = 'https://www.facebook.com/groups/' + author.gid + '/user/' + author.uid + '/';
    try { await page.goto(guURL, { waitUntil:'domcontentloaded', timeout:45000 }); }
    catch (e) { return { ok:false, stage:'goto-user', error:String(e).slice(0,120), author }; }
    await sleep(2500);
    const prof = await page.evaluate((SYS_SRC) => {
      const SYS2 = new RegExp(SYS_SRC);
      let idUrl = '', vanity = '';
      for (const a of document.querySelectorAll('a[href]')) {
        const t = (a.innerText || '').trim();
        if (/^view profile$/i.test(t)) { idUrl = (a.getAttribute('href') || '').split('&')[0]; break; }
      }
      for (const a of document.querySelectorAll('a[href]')) {
        let h = a.getAttribute('href') || '';
        if (!/^https?:\\/\\/www\\.facebook\\.com\\/[A-Za-z0-9.]+\\/?(\\?|$)/.test(h)) continue;
        if (SYS2.test(h)) continue;
        vanity = h.split('?')[0]; break;
      }
      return { idUrl, vanity };
    }, SYS.source);
    let idUrl = prof.idUrl || '';
    if (idUrl.startsWith('/')) idUrl = 'https://www.facebook.com' + idUrl;
    const idFallback = 'https://www.facebook.com/profile.php?id=' + author.uid;
    const profileUrl = prof.vanity || idUrl || idFallback;
    return { ok:true, method:'clean', postUrl:POST_URL, uid:author.uid, name:author.name, profileUrl, vanity:prof.vanity||'', idUrl:idUrl||idFallback };
  }

  // ---- Strategy B: obfuscated post -> hover author actor, read hovercard ----
  // record canonical profile links present BEFORE hover, so we can isolate the new one
  const before = await page.evaluate((SYS_SRC) => {
    const SYS2 = new RegExp(SYS_SRC); const set = [];
    for (const a of document.querySelectorAll('a[href]')) { const h=a.getAttribute('href')||''; if ((/profile\\.php\\?id=\\d+/.test(h)) || (/^https?:\\/\\/www\\.facebook\\.com\\/[A-Za-z0-9.]+\\/?(\\?|$)/.test(h) && !SYS2.test(h))) set.push(h.split('&')[0].split('?')[0] + (/(profile\\.php\\?id=\\d+)/.exec(h)?('?'+RegExp.$1):'')); }
    return set;
  }, SYS.source);

  const handle = await page.evaluateHandle(() => {
    function inComment(el){ while(el){ const al=el.getAttribute&&el.getAttribute('aria-label'); if(al&&/^Comment/i.test(al)) return true; el=el.parentElement; } return false; }
    for (const a of document.querySelectorAll('a[href]')){
      const h = a.getAttribute('href')||'';
      if (!h.includes('__cft__')) continue;
      if (/\\/groups\\/\\d+\\/?(\\?|$)/.test(h)) continue;
      if (/l\\.facebook\\.com/.test(h)) continue;
      if (inComment(a)) continue;
      const r = a.getBoundingClientRect();
      if (r.top < 70 || r.top > 240) continue;
      if (r.left < 360) continue;
      return a;
    }
    return null;
  });
  const el = handle.asElement();
  if (!el) return { ok:false, stage:'author', error:'no author link or actor found' };
  try { await el.hover(); } catch(e){ return { ok:false, stage:'hover', error:String(e).slice(0,120) }; }
  await sleep(4000);

  const card = await page.evaluate((args) => {
    const [beforeSet, SYS_SRC] = args;
    const SYS2 = new RegExp(SYS_SRC);
    const seen = new Set(beforeSet);
    let vanity='', idUrl='', name='';
    for (const a of document.querySelectorAll('a[href]')){
      const h = a.getAttribute('href')||'';
      const t = (a.innerText||'').trim();
      const idm = h.match(/profile\\.php\\?id=(\\d+)/);
      const key = idm ? ('https://www.facebook.com/profile.php?id='+idm[1]) : (/^https?:\\/\\/www\\.facebook\\.com\\/[A-Za-z0-9.]+\\/?(\\?|$)/.test(h) && !SYS2.test(h) ? h.split('?')[0] : '');
      if (!key) continue;
      if (seen.has(key)) continue;            // skip links present before hover
      // new canonical link injected by the hovercard = the author
      if (idm) { if (!idUrl) idUrl = key; if (t && !name) name = t; }
      else { if (!vanity) vanity = key; if (t && !name) name = t; }
      if ((vanity || idUrl) && name) break;
    }
    return { vanity, idUrl, name };
  }, [before, SYS.source]);

  const profileUrl = card.vanity || card.idUrl || '';
  if (!profileUrl) return { ok:false, stage:'hovercard', error:'hovercard yielded no profile link' };
  return { ok:true, method:'hovercard', postUrl:POST_URL, uid:(card.idUrl.match(/id=(\\d+)/)||[])[1]||'', name:card.name||'', profileUrl, vanity:card.vanity||'', idUrl:card.idUrl||'' };
}`;

function resolvePost(postUrl) {
  writeFileSync(RESOLVER_PATH, RESOLVER_TEMPLATE(postUrl), 'utf8');
  const out = sh(`playwright-cli --raw run-code --filename="${RESOLVER_PATH}"`);
  if (out.includes('### Error')) return { ok: false, stage: 'run-code', error: out.split('\n').slice(0, 3).join(' ').slice(0, 160) };
  return parseJsonLoose(out);
}

// ---- Main -------------------------------------------------------------------
async function main() {
  console.log(`\n=== facebook-lead-nav ${DRY_RUN ? '(DRY RUN)' : '(LIVE)'} | limit=${LIMIT} start-row=${START_ROW} | ${SPREADSHEET_ID.slice(0, 8)}…/${TAB} ===\n`);

  // 1) Headers — find or place the 3 new columns (by header name, never position).
  const header = (readRange('1:1')[0] || []).map((h) => (h || '').trim());
  const colOf = {};
  const headerWrites = [];
  let nextCol = header.length;
  for (const name of NEW_HEADERS) {
    let idx = header.findIndex((h) => h.toLowerCase() === name.toLowerCase());
    if (idx === -1) { idx = nextCol++; headerWrites.push({ range: `${TAB}!${colLetter(idx)}1`, values: [[name]] }); }
    colOf[name] = idx;
  }

  // 2) Read all data (post col + the resolved-profile col for resume).
  const profCol = colOf['Profile URL'];
  const lastCol = colLetter(Math.max(profCol, header.length) + 1);
  const rows = readRange(`A2:${lastCol}`); // row 0 here == sheet row 2

  // 3) Build the worklist: post rows not yet enriched.
  const work = [];
  for (let i = 0; i < rows.length; i++) {
    const sheetRow = i + 2;
    if (sheetRow < START_ROW) continue;
    const postUrl = (rows[i]?.[0] || '').trim();
    if (!POST_RE.test(postUrl)) continue;                 // only group post links
    const already = (rows[i]?.[profCol] || '').trim();
    if (already) continue;                                 // resume-safe: skip done
    work.push({ sheetRow, postUrl });
    if (work.length >= LIMIT) break;
  }

  console.log(`Found ${work.length} post row(s) to enrich (cap ${LIMIT}).`);
  if (!work.length) { console.log('Nothing to do.'); return; }

  if (headerWrites.length && !DRY_RUN) { batchUpdate(headerWrites); console.log(`Added new headers: ${NEW_HEADERS.join(', ')}`); }

  ensureAttached();

  // 4) Resolve each post.
  const today = new Date().toISOString().slice(0, 10);
  const results = [];
  for (let k = 0; k < work.length; k++) {
    const { sheetRow, postUrl } = work[k];
    process.stdout.write(`[${k + 1}/${work.length}] row ${sheetRow}  ... `);
    let r;
    try { r = resolvePost(postUrl); } catch (e) { r = { ok: false, stage: 'exception', error: String(e).slice(0, 160) }; }
    if (r.ok) { console.log(`${r.name}  ->  ${r.profileUrl}`); results.push({ sheetRow, ...r }); }
    else { console.log(`NEEDS REVIEW (${r.stage}: ${r.error})`); results.push({ sheetRow, ...r }); }
    if (k < work.length - 1) await sleep(jitter());
  }

  // 5) Write back (skip needs-review rows).
  const ok = results.filter((r) => r.ok);
  console.log(`\nResolved ${ok.length}/${results.length}.`);
  if (DRY_RUN) { console.log('\n(DRY RUN — no sheet writes.)'); return; }

  const data = [];
  for (const r of ok) {
    data.push({ range: `${TAB}!${colLetter(colOf['Lead Name'])}${r.sheetRow}`, values: [[r.name]] });
    data.push({ range: `${TAB}!${colLetter(colOf['Profile URL'])}${r.sheetRow}`, values: [[r.profileUrl]] });
    data.push({ range: `${TAB}!${colLetter(colOf['Date Added'])}${r.sheetRow}`, values: [[today]] });
  }
  batchUpdate(data);
  console.log(`Wrote ${ok.length} row(s) to the sheet (cols ${colLetter(colOf['Lead Name'])}-${colLetter(colOf['Date Added'])}).`);

  const review = results.filter((r) => !r.ok);
  if (review.length) console.log(`\n${review.length} row(s) need manual review: ${review.map((r) => r.sheetRow).join(', ')}`);
}

main().catch((e) => { console.error('FATAL:', e); process.exit(1); });

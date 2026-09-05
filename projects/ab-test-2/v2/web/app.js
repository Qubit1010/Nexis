/* Reply Drafter — client.
 *
 * No framework, no build. Every piece of user or enquiry text reaches the DOM through
 * textContent, never innerHTML: enquiry bodies arrive from email and are hostile input.
 */

// ---------------------------------------------------------------------------------------
// Tiny DOM helper
// ---------------------------------------------------------------------------------------

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k === 'text') node.textContent = v;
    else if (k === 'html') throw new Error('innerHTML is not allowed here');
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else if (k === 'value') node.value = v;
    else node.setAttribute(k, v === true ? '' : String(v));
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(typeof child === 'string' || typeof child === 'number' ? String(child) : child);
  }
  return node;
}

const $ = (sel) => document.querySelector(sel);

// ---------------------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------------------

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: options.body ? { 'content-type': 'application/json' } : undefined,
  });
  const text = await res.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    throw new Error(`server returned non-JSON (${res.status})`);
  }
  if (!res.ok) throw new Error(payload?.error ?? `request failed (${res.status})`);
  return payload;
}

const post = (path, body) => api(path, { method: 'POST', body: JSON.stringify(body) });

let toastTimer = null;
function toast(message, isError = false) {
  document.querySelector('.toast')?.remove();
  const node = el('div', { class: `toast${isError ? ' err' : ''}`, text: message });
  document.body.append(node);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.remove(), isError ? 6500 : 2600);
}

async function guard(fn) {
  try {
    await fn();
  } catch (err) {
    toast(err.message, true);
  }
}

// ---------------------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------------------

const pct = (n) => (n === null || n === undefined ? '--' : `${Math.round(n * 100)}%`);
const ratio2 = (n) => (n === null || n === undefined ? '--' : n.toFixed(2));

function relDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

/** Horizontal 95% interval bar. The point estimate alone would overstate what n supports. */
function intervalBar(approval, interval, n) {
  if (n === 0) return el('span', { class: 'dim', text: 'no reviews' });
  const width = Math.max(1, (interval.high - interval.low) * 100);
  return el(
    'div',
    { class: 'ci' },
    el(
      'div',
      { class: 'ci-track', title: `95% interval ${pct(interval.low)} to ${pct(interval.high)}` },
      el('div', {
        class: 'ci-range',
        style: `left:${interval.low * 100}%; width:${width}%`,
      }),
      el('div', { class: 'ci-point', style: `left:calc(${approval * 100}% - 1px)` }),
    ),
    el('span', { class: 'ci-label', text: pct(approval) }),
    el('span', { class: 'ci-range-text', text: `${pct(interval.low)}-${pct(interval.high)}` }),
  );
}

// ---------------------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------------------

const state = { health: null };

// ---------------------------------------------------------------------------------------
// View: Inbox
// ---------------------------------------------------------------------------------------

async function viewInbox(view) {
  const enquiries = await api('/enquiries');

  const form = el(
    'form',
    {
      class: 'hidden',
      onsubmit: (e) => {
        e.preventDefault();
        const data = new FormData(e.target);
        guard(async () => {
          const created = await post('/enquiries', {
            subject: String(data.get('subject') ?? ''),
            body: String(data.get('body') ?? ''),
            sender: String(data.get('sender') ?? '') || null,
            in_bench: data.get('in_bench') === 'on',
          });
          location.hash = `#/enquiry/${created.id}`;
        });
      },
    },
    el('div', { class: 'field' }, el('label', { text: 'From' }), el('input', { type: 'text', name: 'sender', placeholder: 'Dana Whitfield' })),
    el('div', { class: 'field' }, el('label', { text: 'Subject' }), el('input', { type: 'text', name: 'subject', required: true, maxlength: '500' })),
    el('div', { class: 'field' }, el('label', { text: 'Body' }), el('textarea', { name: 'body', rows: '10', required: true, maxlength: '50000' })),
    el(
      'div',
      { class: 'row' },
      el('label', { style: 'display:flex;align-items:center;gap:7px;margin:0' }, el('input', { type: 'checkbox', name: 'in_bench', style: 'width:auto' }), 'Add to the bench'),
      el('div', { class: 'spacer' }),
      el('button', { class: 'primary', type: 'submit', text: 'Save enquiry' }),
    ),
  );

  view.append(
    el('h1', { text: 'Inbox' }),
    el('p', { class: 'lede', text: 'Paste an inbound enquiry, draft a reply to it, then say whether the draft was any good.' }),
    el(
      'div',
      { class: 'row', style: 'margin-bottom:22px' },
      el('button', {
        text: 'New enquiry',
        onclick: (e) => {
          form.classList.toggle('hidden');
          e.target.textContent = form.classList.contains('hidden') ? 'New enquiry' : 'Cancel';
          if (!form.classList.contains('hidden')) form.querySelector('input')?.focus();
        },
      }),
    ),
    form,
    enquiries.length === 0
      ? el('p', { class: 'empty', text: 'Nothing here yet. Add an enquiry to get started.' })
      : el(
          'div',
          { class: 'list' },
          enquiries.map((e) =>
            el(
              'button',
              { class: 'item', onclick: () => { location.hash = `#/enquiry/${e.id}`; } },
              el(
                'div',
                { class: 'item-top' },
                el('span', { class: 'item-subject', text: e.subject }),
                e.sender ? el('span', { class: 'item-sender', text: e.sender }) : null,
                el('div', { class: 'spacer' }),
                e.in_bench ? el('span', { class: 'tag accent', text: 'bench' }) : null,
                el('span', { class: 'tag', text: `${e.reviewed_count}/${e.draft_count} rated` }),
              ),
              el('div', { class: 'item-preview', text: e.body.replace(/\s+/g, ' ').slice(0, 160) }),
            ),
          ),
        ),
  );
}

// ---------------------------------------------------------------------------------------
// View: one enquiry (draft + review)
// ---------------------------------------------------------------------------------------

async function viewEnquiry(view, id) {
  const [{ enquiry, drafts }, prompts] = await Promise.all([
    api(`/enquiries/${id}`),
    api('/prompts'),
  ]);

  const latest = drafts[0] ?? null;
  const older = drafts.slice(1);

  const left = el(
    'div',
    {},
    el('p', { class: 'eyebrow', text: enquiry.sender ?? 'unknown sender' }),
    el('h2', { text: enquiry.subject }),
    el('div', { class: 'enquiry-body', text: enquiry.body }),
    el(
      'div',
      { class: 'row', style: 'margin-top:16px' },
      el('button', {
        class: 'ghost',
        text: enquiry.in_bench ? 'Remove from bench' : 'Add to bench',
        onclick: () =>
          guard(async () => {
            await post(`/enquiries/${enquiry.id}/bench`, { in_bench: !enquiry.in_bench });
            render();
          }),
      }),
    ),
  );

  const right = el('div', {});
  right.append(
    el(
      'div',
      { class: 'row', style: 'margin-bottom:16px' },
      el('h2', { text: 'Draft', style: 'margin:0' }),
      el('div', { class: 'spacer' }),
      el(
        'select',
        { id: 'draft-version', style: 'width:auto;max-width:230px' },
        prompts
          .slice()
          .reverse()
          .map((p) =>
            el('option', { value: String(p.id), selected: p.is_active === 1 }, `${p.label}${p.is_active ? ' (active)' : ''}`),
          ),
      ),
      el('button', {
        class: 'primary',
        text: latest ? 'Draft again' : 'Draft a reply',
        onclick: (e) =>
          guard(async () => {
            e.target.disabled = true;
            e.target.textContent = 'Drafting...';
            try {
              await post('/drafts', {
                enquiry_id: enquiry.id,
                prompt_version_id: Number($('#draft-version').value),
              });
              render();
            } finally {
              e.target.disabled = false;
            }
          }),
      }),
    ),
  );

  if (!latest) {
    right.append(el('p', { class: 'empty', text: 'No draft yet. Pick a prompt version and draft a reply.' }));
  } else {
    right.append(reviewPanel(latest, render));
  }

  if (older.length > 0) {
    right.append(
      el(
        'div',
        { class: 'history' },
        el('p', { class: 'eyebrow', style: 'margin-top:28px', text: 'Earlier drafts' }),
        older.map((d) =>
          el(
            'div',
            { class: 'history-row' },
            el('span', { class: 'tag', text: d.prompt_label }),
            el('span', { class: 'dim', text: relDate(d.created_at) }),
            el('div', { class: 'spacer' }),
            d.edit_ratio !== null ? el('span', { class: 'dim', text: `edited ${ratio2(d.edit_ratio)}` }) : null,
            d.verdict ? el('span', { class: `tag ${d.verdict}`, text: d.verdict }) : el('span', { class: 'tag', text: 'unrated' }),
          ),
        ),
      ),
    );
  }

  view.append(
    el('a', { href: '#/inbox', class: 'dim', style: 'font-size:13px;text-decoration:none', text: '← Inbox' }),
    el('div', { class: 'split', style: 'margin-top:18px' }, left, right),
  );
}

/**
 * The editable draft plus its verdict.
 *
 * The textarea is the measurement instrument as much as it is a convenience: the server
 * compares what it served against what comes back, so ordinary editing produces the edit
 * ratio for free.
 */
function reviewPanel(draft, onSaved, options = {}) {
  const box = el('textarea', { class: 'draft', rows: '16', value: draft.final_text ?? draft.text });
  const note = el('input', { type: 'text', placeholder: 'Why? (optional)', value: draft.note ?? '' });
  let chosen = draft.verdict ?? null;

  const save = (verdict) =>
    guard(async () => {
      await post('/reviews', {
        draft_id: draft.id,
        verdict,
        final_text: box.value,
        note: note.value || null,
      });
      chosen = verdict;
      toast(verdict === 'good' ? 'Marked good' : 'Marked bad');
      if (onSaved) onSaved();
    });

  const goodBtn = el('button', { class: `good${chosen === 'good' ? ' on' : ''}`, text: 'Good', onclick: () => save('good') });
  const badBtn = el('button', { class: `bad${chosen === 'bad' ? ' on' : ''}`, text: 'Bad', onclick: () => save('bad') });

  const meta = el(
    'div',
    { class: 'meta' },
    options.blind ? null : el('span', { text: draft.prompt_label }),
    el('span', { text: draft.provider === 'mock' ? 'offline mock' : draft.model }),
    el('span', { text: `${draft.latency_ms} ms` }),
    draft.cost_usd !== null ? el('span', { text: `$${draft.cost_usd.toFixed(5)}` }) : null,
    draft.edit_ratio !== null ? el('span', { text: `edited ${ratio2(draft.edit_ratio)}` }) : null,
  );

  return el(
    'div',
    {},
    box,
    meta,
    el(
      'div',
      { class: 'row', style: 'margin-top:14px' },
      note,
    ),
    el(
      'div',
      { class: 'row', style: 'margin-top:12px' },
      el('span', { class: 'dim', style: 'font-size:12.5px', text: 'Edit it into the shape you would actually send, then judge it.' }),
      el('div', { class: 'spacer' }),
      el('button', {
        class: 'ghost',
        text: 'Copy',
        onclick: () => {
          navigator.clipboard?.writeText(box.value).then(
            () => toast('Copied'),
            () => toast('Clipboard blocked by the browser', true),
          );
        },
      }),
      badBtn,
      goodBtn,
    ),
  );
}

// ---------------------------------------------------------------------------------------
// View: Prompt
// ---------------------------------------------------------------------------------------

async function viewPrompt(view) {
  const prompts = await api('/prompts');
  const active = prompts.find((p) => p.is_active === 1) ?? prompts[prompts.length - 1];

  const editor = el('textarea', { class: 'prompt', rows: '20', value: active?.system_prompt ?? '' });
  const label = el('input', { type: 'text', placeholder: `v${prompts.length + 1} shorter, asks a question`, maxlength: '120' });

  view.append(
    el('h1', { text: 'Prompt' }),
    el('p', { class: 'lede', text: 'Saving never overwrites a version. Each save creates a new one, so every draft stays attributed to the exact text that produced it, and the scoreboard can compare them honestly.' }),
    el('div', { class: 'field' }, el('label', { text: 'System prompt' }), editor),
    el(
      'div',
      { class: 'row' },
      el('div', { style: 'flex:1;min-width:260px' }, el('label', { text: 'Name this version' }), label),
      el('button', {
        class: 'primary',
        style: 'align-self:flex-end',
        text: 'Save as new version',
        onclick: () =>
          guard(async () => {
            if (!label.value.trim()) throw new Error('give the version a name so you can tell it apart later');
            await post('/prompts', { label: label.value.trim(), system_prompt: editor.value, activate: true });
            toast('New version saved and activated');
            render();
          }),
      }),
    ),
    el(
      'div',
      { class: 'section' },
      el('h2', { text: 'Versions' }),
      el(
        'table',
        {},
        el('thead', {}, el('tr', {}, el('th', { text: 'Version' }), el('th', { text: 'Created' }), el('th', {}))),
        el(
          'tbody',
          {},
          prompts
            .slice()
            .reverse()
            .map((p) =>
              el(
                'tr',
                { class: p.is_active ? 'active' : '' },
                el('td', {}, el('strong', { text: p.label }), p.is_active ? el('span', { class: 'tag accent', style: 'margin-left:9px', text: 'active' }) : null),
                el('td', { class: 'dim', text: relDate(p.created_at) }),
                el(
                  'td',
                  { style: 'text-align:right' },
                  el('button', {
                    class: 'ghost',
                    text: 'Load into editor',
                    onclick: () => {
                      editor.value = p.system_prompt;
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    },
                  }),
                  p.is_active
                    ? null
                    : el('button', {
                        class: 'ghost',
                        text: 'Activate',
                        onclick: () => guard(async () => { await post(`/prompts/${p.id}/activate`, {}); render(); }),
                      }),
                ),
              ),
            ),
        ),
      ),
    ),
  );
}

// ---------------------------------------------------------------------------------------
// View: Scoreboard
// ---------------------------------------------------------------------------------------

const scopeState = { scope: 'bench' };

async function viewScoreboard(view) {
  const board = await api(`/scoreboard?scope=${scopeState.scope}`);
  const versions = board.versions;
  const rated = versions.filter((v) => v.reviewed > 0);

  const scopePicker = el(
    'select',
    {
      style: 'width:auto',
      onchange: (e) => {
        scopeState.scope = e.target.value;
        render();
      },
    },
    el('option', { value: 'bench', selected: scopeState.scope === 'bench' }, 'Bench runs only (comparable)'),
    el('option', { value: 'live', selected: scopeState.scope === 'live' }, 'Real inbox only (confounded)'),
    el('option', { value: 'all', selected: scopeState.scope === 'all' }, 'Everything'),
  );

  view.append(
    el('h1', { text: 'Scoreboard' }),
    el('p', {
      class: 'lede',
      text: 'Approval rate per prompt version, with a 95% interval. The interval is the point: at these sample sizes the gap between two versions is usually noise, and the width tells you when.',
    }),
    el('div', { class: 'row', style: 'margin-bottom:24px' }, el('span', { class: 'eyebrow', style: 'margin:0', text: 'Counting' }), scopePicker),
  );

  if (scopeState.scope === 'live') {
    view.append(
      el('p', {
        class: 'note',
        text: 'Real-inbox numbers are confounded. Each version saw whichever enquiries happened to arrive while it was active, so an easier week reads as a better prompt. Use the bench scope to compare versions on identical inputs.',
      }),
    );
  }

  if (rated.length === 0) {
    view.append(el('p', { class: 'empty', text: 'No rated drafts in this scope yet. Rate some drafts, or run the bench.' }));
    return;
  }

  if (rated.some((v) => v.mixed_providers)) {
    view.append(el('div', { class: 'banner', text: 'At least one version below mixes offline-mock drafts with live Claude drafts. Those are not comparable to each other.' }));
  }

  view.append(trendChart(rated));

  view.append(
    el(
      'table',
      { style: 'margin-top:28px' },
      el(
        'thead',
        {},
        el(
          'tr',
          {},
          el('th', { text: 'Version' }),
          el('th', { class: 'num', text: 'Rated' }),
          el('th', { text: 'Approval (95% interval)' }),
          el('th', { class: 'num', text: 'Median edit' }),
          el('th', { class: 'num', text: 'Kept as-is' }),
          el('th', { class: 'num', text: 'Cost' }),
        ),
      ),
      el(
        'tbody',
        {},
        versions.map((v) =>
          el(
            'tr',
            { class: v.is_active ? 'active' : '' },
            el(
              'td',
              {},
              el('strong', { text: v.label }),
              v.mixed_providers ? el('span', { class: 'tag bad', style: 'margin-left:8px', text: 'mixed' }) : null,
            ),
            el('td', { class: 'num', text: String(v.reviewed) }),
            el('td', {}, intervalBar(v.approval, v.interval, v.reviewed)),
            el('td', { class: 'num', text: ratio2(v.median_edit_ratio) }),
            el('td', { class: 'num', text: v.reviewed ? `${v.kept_verbatim}/${v.reviewed}` : '--' }),
            el('td', { class: 'num dim', text: v.cost_usd === null ? '--' : `$${v.cost_usd.toFixed(4)}` }),
          ),
        ),
      ),
    ),
    el('p', {
      class: 'note',
      text: 'Median edit is how much of the draft you rewrote, 0 to 1. It is the more honest of the two signals: a thumbs-up records what you said, the edit ratio records what you actually did.',
    }),
  );

  view.append(await compareSection(versions));
}

/** Approval over version order, with 95% whiskers. The visual answer to "better or worse". */
function trendChart(versions) {
  const W = 720;
  const H = 210;
  const padL = 42;
  const padR = 16;
  const padT = 16;
  const padB = 38;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;

  // Inset the first and last points so their labels have room and do not clip.
  const inset = versions.length > 1 ? Math.min(56, innerW / (versions.length * 2)) : 0;
  const spanW = innerW - inset * 2;
  const x = (i) =>
    padL + inset + (versions.length === 1 ? spanW / 2 : (i / (versions.length - 1)) * spanW);
  const y = (v) => padT + (1 - v) * innerH;

  const svgNs = 'http://www.w3.org/2000/svg';
  const make = (tag, attrs) => {
    const n = document.createElementNS(svgNs, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, String(v));
    return n;
  };

  const svg = make('svg', { class: 'chart', viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMid meet' });

  for (const gv of [0, 0.25, 0.5, 0.75, 1]) {
    svg.append(make('line', { class: gv === 0 ? 'axis' : 'grid', x1: padL, x2: W - padR, y1: y(gv), y2: y(gv) }));
    const t = make('text', { class: 'tick', x: padL - 8, y: y(gv) + 3.5, 'text-anchor': 'end' });
    t.textContent = `${gv * 100}%`;
    svg.append(t);
  }

  const line = make('polyline', {
    class: 'connector',
    points: versions.map((v, i) => `${x(i)},${y(v.approval)}`).join(' '),
  });
  svg.append(line);

  versions.forEach((v, i) => {
    svg.append(make('line', { class: 'whisker', x1: x(i), x2: x(i), y1: y(v.interval.high), y2: y(v.interval.low) }));
    svg.append(make('line', { class: 'whisker', x1: x(i) - 4, x2: x(i) + 4, y1: y(v.interval.high), y2: y(v.interval.high) }));
    svg.append(make('line', { class: 'whisker', x1: x(i) - 4, x2: x(i) + 4, y1: y(v.interval.low), y2: y(v.interval.low) }));
    svg.append(make('circle', { class: 'dot', cx: x(i), cy: y(v.approval), r: 3.5 }));

    const label = make('text', { class: 'tick', x: x(i), y: H - 18, 'text-anchor': 'middle' });
    label.textContent = v.label.length > 16 ? `${v.label.slice(0, 15)}…` : v.label;
    svg.append(label);

    const n = make('text', { class: 'tick', x: x(i), y: H - 5, 'text-anchor': 'middle' });
    n.textContent = `n=${v.reviewed}`;
    svg.append(n);
  });

  return el('div', {}, el('p', { class: 'eyebrow', text: 'Approval over versions' }), svg);
}

async function compareSection(versions) {
  const wrap = el('div', { class: 'section' });
  if (versions.length < 2) {
    wrap.append(el('h2', { text: 'Head to head' }), el('p', { class: 'empty', text: 'Save a second prompt version to compare.' }));
    return wrap;
  }

  const ids = versions.map((v) => v.prompt_version_id);
  const sel = (id, defaultId) =>
    el(
      'select',
      { id, style: 'width:auto;max-width:240px', onchange: refresh },
      versions.map((v) => el('option', { value: String(v.prompt_version_id), selected: v.prompt_version_id === defaultId }, v.label)),
    );

  const result = el('div', { style: 'margin-top:20px' });

  async function refresh() {
    const a = Number(wrap.querySelector('#cmp-a').value);
    const b = Number(wrap.querySelector('#cmp-b').value);
    result.replaceChildren(el('p', { class: 'dim', text: 'Comparing...' }));
    try {
      const c = await api(`/compare?a=${a}&b=${b}&scope=${scopeState.scope}`);
      const tone = c.verdict === 'better' ? 'better' : c.verdict === 'worse' ? 'worse' : 'unknown';
      result.replaceChildren(
        el(
          'div',
          { class: `verdict ${tone}` },
          el('div', { class: 'verdict-head', text: c.verdict }),
          el('div', { class: 'verdict-why', text: c.reason }),
          el(
            'div',
            { class: 'meta', style: 'margin-top:16px' },
            el('span', { text: `baseline ${pct(c.a.approval)} (n=${c.a.n}, edit ${ratio2(c.a.median_edit_ratio)})` }),
            el('span', { text: `candidate ${pct(c.b.approval)} (n=${c.b.n}, edit ${ratio2(c.b.median_edit_ratio)})` }),
          ),
        ),
      );
    } catch (err) {
      result.replaceChildren(el('p', { class: 'empty', text: err.message }));
    }
  }

  wrap.append(
    el('h2', { text: 'Head to head' }),
    el(
      'div',
      { class: 'row' },
      el('span', { class: 'dim', style: 'font-size:13px', text: 'Baseline' }),
      sel('cmp-a', ids[Math.max(0, ids.length - 2)]),
      el('span', { class: 'dim', style: 'font-size:13px', text: 'against candidate' }),
      sel('cmp-b', ids[ids.length - 1]),
    ),
    result,
  );

  queueMicrotask(refresh);
  return wrap;
}

// ---------------------------------------------------------------------------------------
// View: Bench
// ---------------------------------------------------------------------------------------

async function viewBench(view) {
  const [prompts, runs, enquiries] = await Promise.all([api('/prompts'), api('/bench/runs'), api('/enquiries')]);
  const benchSize = enquiries.filter((e) => e.in_bench).length;

  const picker = el(
    'select',
    { id: 'bench-version', style: 'width:auto;max-width:260px' },
    prompts.slice().reverse().map((p) => el('option', { value: String(p.id), selected: p.is_active === 1 }, p.label)),
  );

  view.append(
    el('h1', { text: 'Bench' }),
    el('p', {
      class: 'lede',
      text: 'A fixed set of enquiries, drafted again by every prompt version. Because the inputs are identical, a difference between two versions is the prompt and not the week you had. This is the comparison worth trusting.',
    }),
    el(
      'div',
      { class: 'row', style: 'margin-bottom:8px' },
      picker,
      el('button', {
        class: 'primary',
        text: `Run the bench (${benchSize} enquiries)`,
        disabled: benchSize === 0,
        onclick: (e) =>
          guard(async () => {
            e.target.disabled = true;
            e.target.textContent = 'Running...';
            try {
              const out = await post('/bench/run', { prompt_version_id: Number(picker.value) });
              location.hash = `#/bench/${out.run.id}`;
            } finally {
              e.target.disabled = false;
            }
          }),
      }),
    ),
    benchSize === 0
      ? el('p', { class: 'note', text: 'The bench is empty. Open an enquiry and add it to the bench first.' })
      : el('p', { class: 'note', text: 'Rate every draft in a run, then compare versions on the Scoreboard with the scope set to bench runs.' }),
  );

  view.append(
    el(
      'div',
      { class: 'section' },
      el('h2', { text: 'Runs' }),
      runs.length === 0
        ? el('p', { class: 'empty', text: 'No runs yet.' })
        : el(
            'table',
            {},
            el('thead', {}, el('tr', {}, el('th', { text: 'Run' }), el('th', { text: 'Version' }), el('th', { text: 'When' }), el('th', { class: 'num', text: 'Drafts' }))),
            el(
              'tbody',
              {},
              runs.map((r) =>
                el(
                  'tr',
                  { style: 'cursor:pointer', onclick: () => { location.hash = `#/bench/${r.id}`; } },
                  el('td', {}, el('strong', { text: `#${r.id}` })),
                  el('td', { text: r.label }),
                  el('td', { class: 'dim', text: relDate(r.created_at) }),
                  el('td', { class: 'num', text: String(r.drafts) }),
                ),
              ),
            ),
          ),
    ),
  );
}

const blindState = { on: true };

async function viewBenchRun(view, runId) {
  const drafts = await api(`/bench/runs/${runId}`);
  if (drafts.length === 0) {
    view.append(el('p', { class: 'empty', text: 'That run has no drafts.' }));
    return;
  }

  const done = drafts.filter((d) => d.verdict).length;

  view.append(
    el('a', { href: '#/bench', class: 'dim', style: 'font-size:13px;text-decoration:none', text: '← Bench' }),
    el('h1', { style: 'margin-top:14px', text: `Bench run #${runId}` }),
    el(
      'div',
      { class: 'row', style: 'margin-bottom:8px' },
      el('span', { class: 'dim', style: 'font-size:13px', text: `${done} of ${drafts.length} rated` }),
      el('div', { class: 'spacer' }),
      el(
        'label',
        { style: 'display:flex;align-items:center;gap:7px;margin:0;font-size:13px' },
        el('input', {
          type: 'checkbox',
          checked: blindState.on,
          style: 'width:auto',
          onchange: (e) => {
            blindState.on = e.target.checked;
            render();
          },
        }),
        'Blind (hide which version wrote it)',
      ),
    ),
    el('p', {
      class: 'note',
      text: 'Blind is on by default. Knowing which prompt produced a draft while you judge it is exactly how you talk yourself into believing your latest edit helped.',
    }),
  );

  for (const d of drafts) {
    view.append(
      el(
        'div',
        { class: 'section' },
        el('p', { class: 'eyebrow', text: d.subject }),
        reviewPanel(d, () => render(), { blind: blindState.on }),
      ),
    );
  }
}

// ---------------------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------------------

const view = $('#view');

async function render() {
  const hash = location.hash || '#/inbox';
  const parts = hash.replace(/^#\//, '').split('/');
  const [route, arg] = parts;

  document.querySelectorAll('.nav a').forEach((a) => {
    const target = a.dataset.nav;
    a.classList.toggle('on', target === route || (route === 'enquiry' && target === 'inbox'));
  });

  view.replaceChildren(el('p', { class: 'dim', text: 'Loading...' }));

  try {
    const next = el('div', {});
    if (route === 'enquiry' && arg) await viewEnquiry(next, arg);
    else if (route === 'prompt') await viewPrompt(next);
    else if (route === 'scoreboard') await viewScoreboard(next);
    else if (route === 'bench' && arg) await viewBenchRun(next, arg);
    else if (route === 'bench') await viewBench(next);
    else await viewInbox(next);
    view.replaceChildren(...next.childNodes);
  } catch (err) {
    view.replaceChildren(el('p', { class: 'empty', text: `Could not load: ${err.message}` }));
  }
}

async function boot() {
  try {
    state.health = await api('/health');
    $('#provider-badge').textContent = state.health.live_api_key ? 'live claude' : 'offline mock';
    $('#rail-foot').replaceChildren(
      el('div', { text: state.health.live_api_key ? state.health.model : 'No API key set.' }),
      el('div', {
        style: 'margin-top:6px',
        text: state.health.live_api_key
          ? 'Drafting against the live API.'
          : 'Every feature works offline. Set ANTHROPIC_API_KEY to draft with Claude.',
      }),
    );
  } catch {
    $('#provider-badge').textContent = 'api unreachable';
  }
  window.addEventListener('hashchange', render);
  await render();
}

boot();

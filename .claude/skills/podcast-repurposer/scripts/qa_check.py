#!/usr/bin/env python3
"""Mechanical QA for a generated 05-hybrid.md, run at Step 7 before writing the file.

Only checks rules that are objectively measurable AND have actually failed in
production. Everything judgement-based stays a human check in the template.
Self-attested checkboxes for these items shipped false passes twice (hooks
opening with "I", hooks over the word ceiling), which is why they live here now.

    python scripts/qa_check.py <path-to-05-hybrid.md>

Exit 0 = clean, 1 = violations found.
"""
import re
import sys

IMPERATIVE_STARTS = {
    'stop', 'start', 'never', 'always', 'quit', 'avoid', 'forget', 'try', 'do',
}
# tokens that look proper-noun-ish but are fine mid-hook
CAP_ALLOW = {
    'I', "I'm", "I've", "I'd", "I'll", 'AI', 'CEO', 'CFO', 'COO', 'LinkedIn',
    'Instagram', 'Facebook', 'Monday', 'Friday', 'God',
}


def hooks(md):
    """(segment, hook_number, text) for every numbered hook under a Text hooks heading."""
    out, in_hooks, seg = [], False, '?'
    for line in md.splitlines():
        s = line.strip()
        if s.startswith('## Segment'):
            seg = s.split('—')[0].replace('#', '').strip() or s[:14]
        if s.startswith('###'):
            in_hooks = 'text hook' in s.lower()
            continue
        m = re.match(r'^([1-5])\.\s+(.*)$', s)
        if in_hooks and m:
            out.append((seg, int(m.group(1)), m.group(2)))
    return out


def main(path):
    md = open(path, encoding='utf-8').read()
    fails, warns = [], []

    for seg, n, raw in hooks(md):
        text = re.sub(r'\((recommended|2nd option)\)\s*$', '', raw).strip()
        words = text.split()
        if not words:
            continue
        if words[0].strip('"“').rstrip(',') == 'I':
            fails.append('%s hook %d opens with "I": %s' % (seg, n, text))
        if not 6 <= len(words) <= 12:
            fails.append('%s hook %d is %d words (want 6-12): %s' % (seg, n, len(words), text))
        if words[0].lower().strip('"“') in IMPERATIVE_STARTS:
            warns.append('%s hook %d is imperative: %s' % (seg, n, text))
        for w in words[1:]:
            bare = w.strip('".,?!“”’()')
            prev = words[words.index(w) - 1] if w in words else ''
            if (bare and bare[0].isupper() and bare not in CAP_ALLOW
                    and not prev.endswith(('.', '?', '!'))):
                warns.append('%s hook %d has a proper noun "%s" (brand names are barred): %s'
                             % (seg, n, bare, text))
                break

    # defects that show up when a reviewer's paragraph merges are accepted
    for pat, label in [
        (r'[a-zA-Z0-9\)\?\!][.!?:](?=[A-Za-z])', 'run-together sentences (missing space)'),
        (r'\S  +\S', 'double space'),
        (r'[]', 'vertical tab (Shift+Enter artifact)'),
    ]:
        for m in re.finditer(pat, md):
            snippet = ' '.join(md[max(0, m.start() - 40):m.end() + 26].split())
            if '·' in snippet or 'http' in snippet or '](' in snippet:
                continue
            fails.append('%s: ...%s...' % (label, snippet))

    for para in md.split('\n\n'):
        if para.count('“') != para.count('”'):
            fails.append('unbalanced smart quotes: %s' % ' '.join(para.split())[:80])

    for label, items in (('FAIL', fails), ('WARN', warns)):
        for i in items:
            print('%s  %s' % (label, i))
    print('\n%d failures, %d warnings' % (len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

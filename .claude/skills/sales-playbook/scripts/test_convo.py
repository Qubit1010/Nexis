"""Runnable check for convo.py. Offline normalizer tests always run; DB
integration tests run only when Supabase creds are available (test- prefix
rows, cleaned up after). Run: python test_convo.py"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import convo

# --- offline: normalizers + exchange counting --------------------------------

assert convo.normalize_identity("linkedin", "https://www.linkedin.com/in/Sarah-Lin-123/?utm=x") == "sarah-lin-123"
assert convo.normalize_identity("linkedin", "@sarah-lin-123") == "sarah-lin-123"
assert convo.normalize_identity("instagram", "https://www.instagram.com/some.founder/") == "some.founder"
assert convo.normalize_identity("instagram", "@Some.Founder") == "some.founder"
assert convo.normalize_identity("instagram", "https://www.instagram.com/p/Cxyz123/") == ""  # post, not a person
assert convo.normalize_identity("facebook", "https://www.facebook.com/profile.php?id=100012345") == "id:100012345"
assert convo.normalize_identity("facebook", "https://www.facebook.com/john.doe.35") == "john.doe.35"
assert convo.normalize_identity("facebook", "https://www.facebook.com/profile.php") == ""

THREAD = """[Me]: saw your post on manual onboarding
[Them]: yeah it's a mess honestly
[Me]: how does it run today?
[Them]: spreadsheets and prayers
[Prospect]: also a VA copies it all over weekly
"""
assert convo.count_exchanges(THREAD) == 3
assert convo.count_exchanges("") == 0
assert convo.count_exchanges("[Me]: hello") == 0

RAW_PASTE_THREAD = """Alistair Horscroft
No I've done groups for 15 years as well more ability to leverage Knowledge
And you Aleem?

Aleem
Hm, fair enough, sounds like the leverage piece has been there for a long time too.

Alistair Horscroft
Yeah pretty much, what do you do exactly?
"""
assert convo.count_exchanges(RAW_PASTE_THREAD) == 2
assert convo.count_exchanges("Aleem\nhey there\n") == 0

# Regression: a multi-paragraph self-message (blank line inside one turn) or a
# timestamp/read-receipt line must NOT be miscounted as extra prospect turns.
MULTI_PARA_THREAD = """Alistair Horscroft
Thanks for the follow.
05:38

Alistair Horscroft
They are always both as one leads to the other
Seen 23 m ago

Aleem
Fair point.

I build AI workflows for coaches and consultants, mainly the ops side.

Alistair Horscroft
I have someone for that thanks mate
"""
assert convo.count_exchanges(MULTI_PARA_THREAD) == 3

# Regression: lowercase IG handles as speaker lines (e.g. "hupru") need the
# contact_hint to be recognized - the Title-Case check alone would miss them.
HANDLE_THREAD = """Aleem
Hey Hupru, loved that post.

hupru
Thanks for reaching out, appreciate it a lot
"""
assert convo.count_exchanges(HANDLE_THREAD) == 0  # no hint: "hupru" not recognized
assert convo.count_exchanges(HANDLE_THREAD, contact_hint="hupru") == 1

# Regression: LinkedIn-style exports put the timestamp on the same line as
# the name ("Anna Sandholm   10:38 PM") - must still be recognized as a name.
TIMESTAMP_THREAD = """Aleem Ul Hassan   10:33 PM
Noticed your focus on clarity.

Anna Sandholm   10:38 PM
Yes, that's a big part of it.

Aleem Ul Hassan 2:23 AM
Makes sense.

Anna Sandholm   2:25 AM
Could be either one.
"""
assert convo.count_exchanges(TIMESTAMP_THREAD) == 2

print("offline checks passed")

# --- integration: only when creds exist --------------------------------------

try:
    convo._load_env()
    have_creds = True
except SystemExit:
    have_creds = False

if not have_creds:
    print("SUPABASE creds not set; skipped DB integration checks")
    sys.exit(0)


def run(*args, stdin=None):
    out = subprocess.run([sys.executable, str(Path(__file__).parent / "convo.py"), *args],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    return json.loads(out.stdout)


IDENT = "test-convo-selfcheck"
try:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(THREAD)
        tf = f.name

    rec = run("upsert", "linkedin", IDENT, "--name", "Test Row", "--thread-file", tf)
    assert rec["identity"] == IDENT and rec["exchange_count"] == 3, rec

    got = run("get", "linkedin", IDENT)
    assert got["name"] == "Test Row" and got["thread"].startswith("[Me]:"), got

    rec2 = run("upsert", "linkedin", IDENT, "--stage", "ask", "--meeting", "asked")
    assert rec2["id"] == rec["id"], "second upsert must update, not duplicate"
    assert rec2["stage"] == "ask" and rec2["name"] == "Test Row", "partial update must keep old fields"

    print("db integration checks passed")
finally:
    os.unlink(tf)
    run("delete", "linkedin", IDENT)

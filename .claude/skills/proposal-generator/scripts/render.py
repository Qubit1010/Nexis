"""Validate, lint and render a proposal JSON into a deployable HTML page.

Usage:
  python render.py <proposal.json> [--client-slug SLUG] [--check]

A draft JSON without an "id" gets one (slug + random token) and is moved to
client-projects/<slug>/proposals/<id>/proposal.json, which becomes its home.
Re-running on that file re-renders in place. --check validates without writing.

Prints a JSON summary: id, paths, hash, errors, warnings. Exit 1 on any error.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

SKILL = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
# PROPOSALS_ROOT overrides client-projects/ (used by evals so test runs never touch real client folders)
CLIENTS = Path(os.environ.get("PROPOSALS_ROOT") or ROOT / "client-projects")
AGENCY = json.loads((SKILL / "assets" / "agency.json").read_text(encoding="utf-8"))

PRICE_FLOOR = 500  # agency/pricing-and-packages.md: $500 fixed-price minimum
SYMBOLS = {"USD": "$", "GBP": "£", "EUR": "€", "CAD": "CA$", "AUD": "A$"}
PAY_METHODS = {"USD": "card, US bank transfer (ACH) or wire", "GBP": "card or UK bank transfer",
               "EUR": "card or SEPA bank transfer", "CAD": "card or bank transfer", "AUD": "card or bank transfer"}
PAY_HOSTS = ("payoneer.com", "buy.stripe.com", "checkout.stripe.com")
PAY_JUNK = ("xxx", "example", "placeholder", "your-", "<", "todo")

KILL_WORDS = [
    "leverage", "robust", "seamless", "streamline", "elevate", "unlock", "empower",
    "cutting-edge", "cutting edge", "comprehensive solution", "pain points", "synergy",
    "game-changer", "game changer", "revolutionize", "revolutionise", "delve", "world-class",
    "best-in-class", "next-level", "supercharge", "harness the power", "tailored solution",
    "in today's fast-paced", "no-brainer", "irresistible", "act now", "limited spots",
]
PLACEHOLDER = re.compile(r"\[[^\]]{0,40}\]|\{\{|\}\}|\bTBD\b|\bTODO\b|\bXXX\b|lorem ipsum|"
                         r"\bplaceholder\b|Client Name|Company Name", re.I)
VALUE_STACK = re.compile(r"\$\s?[\d,]+(\.\d+)?\s*(in\s+)?value\b|\(\s*\$[\d,]+\s*value\s*\)", re.I)
HASH_EXCLUDE_OPTION_KEYS = {"pay_url"}  # payment links are not contract content


def money(amount, currency):
    sym = SYMBOLS.get(currency, currency + " ")
    return f"{sym}{amount:,.0f}" if float(amount).is_integer() else f"{sym}{amount:,.2f}"


def longdate(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:32] or "client"


def content_hash(p):
    """sha256 of the contract content. Excludes pay links and nothing else."""
    clean = json.loads(json.dumps(p))
    for o in clean.get("options", []):
        for k in HASH_EXCLUDE_OPTION_KEYS:
            o.pop(k, None)
    canon = json.dumps(clean, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def derive_options(p):
    """Price labels and amount due to start. Arithmetic lives here, never in prose."""
    cur = p.get("currency", "USD")
    out = []
    for o in p.get("options", []):
        price = o["price"]
        billing = o.get("billing", "one_time")
        if billing == "monthly":
            pct = o.get("deposit_pct", 100)
            due = price
            price_label = money(price, cur) + "/month"
            due_note = "First month, billed monthly after that"
        else:
            pct = o.get("deposit_pct", 50)
            due = round(price * pct / 100)
            price_label = money(price, cur)
            if pct >= 100:
                due_note = "Paid in full to start"
            else:
                rest = price - due
                due_note = f"{pct}% deposit, the remaining {money(rest, cur)} {o.get('balance_due', 'is due on delivery')}"
        out.append({**o, "billing": billing, "deposit_pct": pct, "due_amount": due, "currency": cur,
                    "price_label": price_label, "due_label": money(due, cur), "due_note": due_note})
    return out


def walk_text(node, path=""):
    """Yield (path, string) for every client-facing string."""
    skip = {"id", "pay_url", "link", "contact_email", "email", "issued", "valid_until", "currency", "billing"}
    if isinstance(node, dict):
        for k, v in node.items():
            if k in skip:
                continue
            yield from walk_text(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_text(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def need(p, dotted):
    cur = p
    for part in dotted.split("."):
        if not isinstance(cur, dict) or not cur.get(part):
            return False
        cur = cur[part]
    return True


def validate(p):
    errors, warnings = [], []
    for f in ["client.company", "client.contact_name", "issued", "valid_until", "hero.headline",
              "hero.subhead", "diagnosis.heading", "diagnosis.lead", "investment.heading",
              "investment.recommendation", "prepared_by.name", "prepared_by.email"]:
        if not need(p, f):
            errors.append(f"missing required field: {f}")
    if not (p.get("program") or (p.get("timeline") or {}).get("rows")):
        errors.append("needs at least one of: program, timeline.rows")
    if p.get("currency", "USD") not in SYMBOLS:
        warnings.append(f"currency {p.get('currency')} has no symbol, will print the code")

    # dates
    try:
        issued = dt.date.fromisoformat(p.get("issued", ""))
        valid = dt.date.fromisoformat(p.get("valid_until", ""))
        if valid <= issued:
            errors.append("valid_until must be after issued")
        if valid < dt.date.today():
            errors.append(f"valid_until {valid} is already in the past")
        if (valid - issued).days > 30:
            warnings.append("validity window over 30 days weakens the decision date")
    except ValueError:
        errors.append("issued and valid_until must be ISO dates (YYYY-MM-DD)")

    # options
    opts = p.get("options") or []
    if not 1 <= len(opts) <= 3:
        errors.append(f"need 1-3 options, found {len(opts)}")
    ids = [o.get("id") for o in opts]
    if len(set(ids)) != len(ids):
        errors.append("option ids must be unique")
    recs = [o for o in opts if o.get("recommended")]
    if len(opts) > 1 and len(recs) != 1:
        errors.append(f"exactly one option must be recommended, found {len(recs)}")
    for o in opts:
        tag = f"option {o.get('id')!r}"
        if not re.fullmatch(r"[a-z0-9-]{2,40}", str(o.get("id", ""))):
            errors.append(f"{tag}: id must be lowercase letters, digits, hyphens")
        if not o.get("name"):
            errors.append(f"{tag}: missing name")
        price = o.get("price")
        if not isinstance(price, (int, float)) or price <= 0:
            errors.append(f"{tag}: price must be a positive number (Aleem sets it, never invent one)")
        elif price < PRICE_FLOOR:
            errors.append(f"{tag}: price {price} is under the ${PRICE_FLOOR} floor")
        if o.get("billing", "one_time") not in ("one_time", "monthly"):
            errors.append(f"{tag}: billing must be one_time or monthly")
        pct = o.get("deposit_pct")
        if pct is not None and not (isinstance(pct, (int, float)) and 0 < pct <= 100):
            errors.append(f"{tag}: deposit_pct must be between 1 and 100")
        url = o.get("pay_url") or ""
        if url:
            u = urlparse(url)
            host = (u.hostname or "").lower()
            if u.scheme != "https" or not any(host == h or host.endswith("." + h) for h in PAY_HOSTS):
                errors.append(f"{tag}: pay_url must be an https Payoneer or Stripe link, got {url!r}")
            if any(j in url.lower() for j in PAY_JUNK):
                errors.append(f"{tag}: pay_url looks like a placeholder: {url!r}")

    for c in p.get("proof") or []:
        if c.get("link") and not str(c["link"]).startswith("https://"):
            errors.append(f"proof link must be https: {c['link']!r}")

    # copy lint
    for path, s in walk_text(p):
        if "—" in s or "–" in s:
            errors.append(f"{path}: em/en dash, use a comma, period or hyphen")
        m = PLACEHOLDER.search(s)
        if m:
            errors.append(f"{path}: placeholder text {m.group(0)!r}")
        if VALUE_STACK.search(s):
            errors.append(f"{path}: '$X value' stacking, consultative style prices options only")
        low = s.lower()
        for w in KILL_WORDS:
            if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
                errors.append(f"{path}: kill-list word {w!r}")
        if re.search(r"\bbonus(es)?\b", low):
            warnings.append(f"{path}: mentions a bonus, no labelled bonus sections")
        if len(s.split()) > 90:
            warnings.append(f"{path}: {len(s.split())} words, split it (reads badly on a phone)")

    if p.get("guarantee"):
        warnings.append("guarantee present: confirm Aleem explicitly approved this guarantee")
    t = p.get("targets") or {}
    if t.get("items") and not re.search(r"target|guarantee|depend", (t.get("note") or ""), re.I):
        warnings.append("targets need a note saying they are targets, not guarantees, and what they depend on")
    return errors, warnings


def public_data(p, options, h):
    default = next((o for o in options if o.get("recommended")), options[0])
    return {
        "id": p["id"], "hash": h, "company": p["client"]["company"], "valid_until": p["valid_until"],
        "api": "/api/event", "default_option": default["id"], "contact_email": p["prepared_by"]["email"],
        "pay_methods": p.get("payment_methods") or PAY_METHODS.get(p.get("currency", "USD"), "card or bank transfer"),
        "options": [{k: o.get(k) for k in ("id", "name", "price_label", "due_label", "due_note", "pay_url")}
                    for o in options],
    }


def manifest_entry(p, options, h):
    """What the signing function trusts. Built from the same derivation as the page."""
    return {
        "hash": h, "valid_until": p["valid_until"], "company": p["client"]["company"],
        "contact_name": p["client"]["contact_name"],
        "options": {o["id"]: {"name": o["name"], "price": o["price"], "billing": o["billing"],
                              "price_label": o["price_label"], "due_amount": o["due_amount"],
                              "due_label": o["due_label"], "currency": o["currency"],
                              "has_pay_url": bool(o.get("pay_url"))} for o in options},
    }


def render_html(p, options, h):
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(loader=FileSystemLoader(str(SKILL / "assets")), autoescape=select_autoescape(["html", "j2"]))
    env.filters["longdate"] = longdate
    default = next((o for o in options if o.get("recommended")), options[0])
    return env.get_template("template.html.j2").render(
        p=p, agency=AGENCY, options=options, default_option=default["id"],
        default_option_name=default["name"], public_data=public_data(p, options, h))


def home_for(src, p, slug_arg):
    """Where this proposal lives: client-projects/<slug>/proposals/<id>/."""
    rel = None
    try:
        rel = src.resolve().relative_to(CLIENTS.resolve())
    except ValueError:
        pass
    slug = slug_arg or (rel.parts[0] if rel else None)
    if not slug:
        raise SystemExit("error: pass --client-slug, or put the JSON under client-projects/<slug>/")
    return slug, CLIENTS / slug / "proposals" / p["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--client-slug")
    ap.add_argument("--check", action="store_true", help="validate and lint only")
    a = ap.parse_args()

    src = Path(a.json)
    p = json.loads(src.read_text(encoding="utf-8-sig"))
    p.setdefault("currency", "USD")
    errors, warnings = validate(p)
    summary = {"errors": errors, "warnings": warnings}
    if errors or a.check:
        summary["ok"] = not errors
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        sys.exit(1 if errors else 0)

    if not p.get("id"):
        p["id"] = f"{slugify(p['client']['company'])}-{secrets.token_hex(5)}"
    slug, home = home_for(src, p, a.client_slug)
    options = derive_options(p)
    h = content_hash(p)
    html = render_html(p, options, h)  # render before touching disk, so a template error moves nothing

    home.mkdir(parents=True, exist_ok=True)
    dest = home / "proposal.json"
    dest.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if src.resolve() != dest.resolve():
        src.unlink()  # the draft moved into its home; edit dest from now on
    (home / "index.html").write_text(html, encoding="utf-8")

    meta_path = home / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"status": "draft"}
    if meta.get("status") == "approved" and meta.get("hash") != h:
        meta["status"] = "draft"
        warnings.append("content changed since approval: status reset to draft, re-approve before deploying")
    meta.update({"id": p["id"], "client_slug": slug, "hash": h,
                 "rendered_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    summary.update({"ok": True, "id": p["id"], "status": meta["status"], "hash": h,
                    "proposal_json": str(dest), "html": str(home / "index.html"),
                    "options": [{"id": o["id"], "price": o["price_label"], "due_to_start": o["due_label"],
                                 "pay_link": bool(o.get("pay_url"))} for o in options]})
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build data/system-graph.json - the command center's single graph source.

Merges (blueprint section 4):
  1. Nexis repo scan: skills, projects, rules, context, decisions (month clusters)
  2. Vault Graphify graph.json, namespaced vault:
  3. .understand-anything edges remapped onto surviving Nexis nodes (best effort)
  4. Cross-links: context mirrors, brain-sync -> vault, skill -> project mentions

Stdlib only. Idempotent: same inputs -> same output (modulo generated_at).
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
NEXIS = PROJECT.parents[1]  # projects/nexus-command-center -> repo root
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH") or r"C:\Users\qubit\OneDrive\Documents\agency-brain")
OUT = PROJECT / "data" / "system-graph.json"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S)


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def fm_field(text: str, field: str) -> str | None:
    m = FM_RE.match(text)
    if not m:
        return None
    fm = re.search(rf"^{field}:\s*(.+)$", m.group(1), re.M)
    return fm.group(1).strip().strip("\"'") if fm else None


def first_para(text: str) -> str:
    body = FM_RE.sub("", text, count=1)
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith(("#", "<", "*", "-", "|", ">", "!", "`", "[")):
            return s[:240]
    for line in body.splitlines():
        if line.strip().startswith("#"):
            return line.strip().lstrip("#").strip()[:240]
    return ""


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("#"):
            t = line.strip().lstrip("#").strip()
            if t:
                return t[:120]
    return fallback


def node(nid: str, label: str, ntype: str, group, summary: str, source: Path | str, size: float = 1.0) -> dict:
    return {
        "id": nid,
        "label": label,
        "type": ntype,
        "group": group,
        "summary": summary,
        "source_file": str(source),
        "size": round(size, 2),
    }


def link(src: str, tgt: str, relation: str, weight: float = 1.0) -> dict:
    return {"source": src, "target": tgt, "relation": relation, "weight": weight}


def scan_nexis(root: Path) -> tuple[list[dict], list[dict], int]:
    nodes: list[dict] = []
    links: list[dict] = []

    skills_dir = root / ".claude" / "skills"
    skill_folders = sorted(p for p in skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
    for sk in skill_folders:
        folder = sk.parent.name
        text = read(sk)
        name = fm_field(text, "name") or folder
        desc = fm_field(text, "description") or first_para(text)
        nodes.append(node(f"nexis:skill/{folder}", name, "skill", "skill", desc[:300], sk))

    proj_dir = root / "projects"
    if proj_dir.is_dir():
        for p in sorted(proj_dir.iterdir()):
            if not p.is_dir() or p.name.startswith("."):
                continue
            readme = p / "README.md"
            text = read(readme) if readme.exists() else ""
            nodes.append(
                node(
                    f"nexis:project/{p.name}",
                    title_of(text, p.name) if text else p.name,
                    "project",
                    "project",
                    first_para(text),
                    readme if readme.exists() else p,
                )
            )

    rules_dir = root / ".claude" / "rules"
    if rules_dir.is_dir():
        for r in sorted(rules_dir.glob("*.md")):
            text = read(r)
            nodes.append(node(f"nexis:rule/{r.stem}", title_of(text, r.stem), "rule", "rule", first_para(text), r))

    ctx_dir = root / "context"
    if ctx_dir.is_dir():
        for cx in sorted(ctx_dir.glob("*.md")):
            text = read(cx)
            nodes.append(node(f"nexis:context/{cx.stem}", title_of(text, cx.stem), "context", "context", first_para(text), cx))

    # Decisions: one cluster node per month, never one node per entry (blueprint risk #6).
    n_decisions = 0
    dec = root / "decisions" / "log.md"
    if dec.exists():
        months: dict[str, list[str]] = defaultdict(list)
        for line in read(dec).splitlines():
            m = re.match(r"^\[(\d{4}-\d{2})-\d{2}\]\s*(?:DECISION:)?\s*(.*)", line.strip())
            if m:
                months[m.group(1)].append(m.group(2).split("|")[0].strip()[:90])
        n_decisions = sum(len(v) for v in months.values())
        for month, entries in sorted(months.items()):
            summary = f"{len(entries)} decisions in {month}: " + "; ".join(entries[:3])
            nodes.append(
                node(
                    f"nexis:decisions/{month}",
                    f"Decisions {month}",
                    "decision-cluster",
                    "decision",
                    summary[:300],
                    dec,
                    size=1 + len(entries) * 0.15,
                )
            )
        ms = sorted(months)
        for a, b in zip(ms, ms[1:]):
            links.append(link(f"nexis:decisions/{a}", f"nexis:decisions/{b}", "precedes"))

    # Hubs: star anchors per type so the Nexis side reads as constellations,
    # not disconnected dust. Type "community" per the schema.
    ids = {n["id"] for n in nodes}
    hubs = [
        ("nexis:hub/nexis", "Nexis OS", "The Nexis agency operating repo - skills, projects, rules, context, decisions."),
        ("nexis:hub/skills", "Skills", "All Claude Code skills in .claude/skills/."),
        ("nexis:hub/projects", "Projects", "Active workstreams in projects/."),
        ("nexis:hub/rules", "Rules", "Always-active rules in .claude/rules/."),
        ("nexis:hub/context", "Context", "Ground-truth context files."),
        ("nexis:hub/decisions", "Decision Log", "Append-only decision log, clustered by month."),
    ]
    prefix_to_hub = {
        "nexis:skill/": "nexis:hub/skills",
        "nexis:project/": "nexis:hub/projects",
        "nexis:rule/": "nexis:hub/rules",
        "nexis:context/": "nexis:hub/context",
        "nexis:decisions/": "nexis:hub/decisions",
    }
    member_counts: dict[str, int] = defaultdict(int)
    for n in nodes:
        for prefix, hub in prefix_to_hub.items():
            if n["id"].startswith(prefix):
                links.append(link(hub, n["id"], "member", 0.5))
                member_counts[hub] += 1
                break
    for hid, label, summary in hubs:
        size = 3 + math.sqrt(member_counts.get(hid, 0))
        nodes.append(node(hid, label, "community", "hub", summary, root, size=size))
        if hid != "nexis:hub/nexis":
            links.append(link("nexis:hub/nexis", hid, "contains", 2))

    # Skill -> project mentions (regex over SKILL.md bodies, blueprint section 4).
    for sk in skill_folders:
        text = read(sk)
        for m in sorted(set(re.findall(r"projects/([A-Za-z0-9_-]+)", text))):
            tid = f"nexis:project/{m}"
            if tid in ids:
                links.append(link(f"nexis:skill/{sk.parent.name}", tid, "builds"))

    return nodes, links, n_decisions


def import_vault(vault: Path) -> tuple[list[dict], list[dict]]:
    gj = vault / "graphify-out" / "graph.json"
    if not gj.exists():
        return [], []
    try:
        data = json.loads(read(gj))
    except (json.JSONDecodeError, ValueError):
        return [], []

    def vtype(source_file: str, file_type: str) -> str:
        sf = source_file.replace("\\", "/")
        if sf.startswith("wiki/") or "/wiki/" in sf or file_type == "wiki":
            return "wiki"
        if sf.startswith("raw/") or "/raw/" in sf:
            return "raw"
        if sf.startswith("context/") or "/context/" in sf:
            return "context"
        return "asset"

    nodes: list[dict] = []
    for n in data.get("nodes", []):
        nid = f"vault:{n.get('id')}"
        sf = str(n.get("source_file") or "")
        src = str(vault / sf) if sf and not re.match(r"^[A-Za-z]:", sf) else sf
        nodes.append(
            node(
                nid,
                str(n.get("label") or n.get("id")),
                vtype(sf, str(n.get("file_type") or "").lower()),
                f"v{n.get('community', 0)}",
                str(n.get("summary") or "")[:300],
                src,
            )
        )
    links = [
        link(
            f"vault:{l.get('source')}",
            f"vault:{l.get('target')}",
            str(l.get("relation") or "related"),
            float(l.get("weight") or 1),
        )
        for l in data.get("links", data.get("edges", []))
    ]

    # Vault hub: anchor every disconnected vault component (union-find) so the
    # whole brain joins one constellation instead of scattering as islands.
    if nodes:
        parent = {n["id"]: n["id"] for n in nodes}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for l in links:
            if l["source"] in parent and l["target"] in parent:
                parent[find(l["source"])] = find(l["target"])
        anchors: dict[str, str] = {}
        for n in nodes:
            anchors.setdefault(find(n["id"]), n["id"])
        hub = node("vault:__hub__", "Agency Brain", "community", "hub",
                   "The NexusPoint second brain - Obsidian vault + LLM wiki + knowledge graph.",
                   vault, size=4)
        for first in anchors.values():
            links.append(link("vault:__hub__", first, "member", 0.5))
        nodes.append(hub)
    return nodes, links


def import_ua_edges(root: Path, nexis_nodes: list[dict]) -> list[dict]:
    """Best effort: remap understand-anything edges onto surviving Nexis nodes."""
    ua = root / ".understand-anything" / "tmp" / "ua-graph-0-full.json"
    if not ua.exists():
        return []
    try:
        data = json.loads(read(ua))
    except (json.JSONDecodeError, ValueError):
        return []

    def norm(p: str) -> str:
        p = p.replace("\\", "/").lower()
        rootstr = str(root).replace("\\", "/").lower()
        if p.startswith(rootstr):
            p = p[len(rootstr):].lstrip("/")
        return p

    by_path = {norm(n["source_file"]): n["id"] for n in nexis_nodes if n.get("source_file")}
    ua_path: dict[str, str] = {}
    for n in data.get("nodes", []):
        fp = n.get("filePath") or n.get("file_path") or ""
        if fp and n.get("id") is not None:
            ua_path[str(n["id"])] = norm(str(fp))

    out: list[dict] = []
    for e in data.get("edges", data.get("links", [])):
        try:
            s = by_path.get(ua_path.get(str(e.get("source")), ""))
            t = by_path.get(ua_path.get(str(e.get("target")), ""))
            if s and t and s != t:
                out.append(link(s, t, f"ua:{e.get('type', 'related')}", float(e.get("weight") or 1)))
        except (TypeError, ValueError):
            continue  # skip malformed entries per blueprint
    return out


def cross_links(nexis_nodes: list[dict], vault_nodes: list[dict]) -> list[dict]:
    out: list[dict] = []
    vault_ids = {n["id"] for n in vault_nodes}

    # context mirrors: nexis:context/<name> <-> vault node for context/<name>.md
    vault_by_ctx: dict[str, str] = {}
    for vn in vault_nodes:
        m = re.search(r"context[\\/]([A-Za-z0-9_-]+)\.md$", vn["source_file"], re.I)
        if m:
            vault_by_ctx[m.group(1).lower()] = vn["id"]
    for nn in nexis_nodes:
        if nn["id"].startswith("nexis:context/"):
            name = nn["id"].split("/", 1)[1].lower()
            if name in vault_by_ctx:
                out.append(link(nn["id"], vault_by_ctx[name], "mirrors", 2))

    # brain-sync skill -> the vault (its most anchored node, else any).
    if vault_nodes and any(n["id"] == "nexis:skill/brain-sync" for n in nexis_nodes):
        anchor = next(
            (vn["id"] for vn in vault_nodes if re.search(r"(CRITICAL_FACTS|CLAUDE)\.md$", vn["source_file"], re.I)),
            vault_nodes[0]["id"],
        )
        if anchor in vault_ids:
            out.append(link("nexis:skill/brain-sync", anchor, "syncs", 2))

    # Bridge the two halves: repo root <-> vault hub.
    if "vault:__hub__" in vault_ids and any(n["id"] == "nexis:hub/nexis" for n in nexis_nodes):
        out.append(link("nexis:hub/nexis", "vault:__hub__", "syncs", 2))
    return out


def build(root: Path, vault: Path) -> dict:
    nexis_nodes, nexis_links, n_decisions = scan_nexis(root)
    vault_nodes, vault_links = import_vault(vault)
    links = nexis_links + vault_links
    links += import_ua_edges(root, nexis_nodes)
    links += cross_links(nexis_nodes, vault_nodes)
    nodes = nexis_nodes + vault_nodes

    # Integrity: unique ids, endpoints must exist, no self-loops, dedup links.
    seen_ids: set[str] = set()
    uniq_nodes: list[dict] = []
    for n in nodes:
        if n["id"] not in seen_ids:
            seen_ids.add(n["id"])
            uniq_nodes.append(n)
    seen_links: set[tuple] = set()
    uniq_links: list[dict] = []
    for l in links:
        key = (l["source"], l["target"], l["relation"])
        if l["source"] in seen_ids and l["target"] in seen_ids and l["source"] != l["target"] and key not in seen_links:
            seen_links.add(key)
            uniq_links.append(l)

    # size = degree-scaled radius input (hubs keep their pre-set floor).
    deg: dict[str, int] = defaultdict(int)
    for l in uniq_links:
        deg[l["source"]] += 1
        deg[l["target"]] += 1
    for n in uniq_nodes:
        n["size"] = round(max(n["size"], 1 + math.sqrt(deg[n["id"]])), 2)

    counts = {
        "skills": sum(1 for n in uniq_nodes if n["type"] == "skill"),
        "projects": sum(1 for n in uniq_nodes if n["type"] == "project"),
        "wiki": sum(1 for n in uniq_nodes if n["type"] == "wiki"),
        "decisions": n_decisions,
        "nodes": len(uniq_nodes),
        "edges": len(uniq_links),
    }
    return {
        "meta": {"generated_at": datetime.now(timezone.utc).isoformat(), "counts": counts},
        "nodes": uniq_nodes,
        "links": uniq_links,
    }


def main() -> int:
    graph = build(NEXIS, VAULT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, indent=1), encoding="utf-8")
    c = graph["meta"]["counts"]
    print(
        f"system-graph.json written: {c['nodes']} nodes / {c['edges']} edges "
        f"(skills {c['skills']}, projects {c['projects']}, wiki {c['wiki']}, decisions {c['decisions']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

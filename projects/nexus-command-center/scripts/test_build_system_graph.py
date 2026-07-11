#!/usr/bin/env python3
"""Scanner self-check: fixture trees -> assert merge, namespacing, dedup, integrity."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_system_graph import build


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def make_fixtures(base: Path) -> tuple[Path, Path]:
    root = base / "nexis"
    vault = base / "vault"

    write(
        root / ".claude" / "skills" / "alpha" / "SKILL.md",
        "---\nname: Alpha Skill\ndescription: Does alpha things.\n---\n\nUses projects/proj-one heavily.\n",
    )
    write(root / ".claude" / "skills" / "beta" / "SKILL.md", "# Beta\n\nBeta skill body without frontmatter.\n")
    write(root / "projects" / "proj-one" / "README.md", "# Proj One\n\nA test project.\n")
    write(root / ".claude" / "rules" / "style.md", "# Style Rule\n\nAlways terse.\n")
    write(root / "context" / "me.md", "# About Me\n\nFounder profile.\n")
    write(root / "context" / "work.md", "# Work\n\nAgency overview.\n")
    write(
        root / "decisions" / "log.md",
        "# Log\n\n"
        "[2026-06-01] DECISION: pick A | REASONING: x | CONTEXT: y\n"
        "[2026-06-15] DECISION: pick B | REASONING: x | CONTEXT: y\n"
        "[2026-07-02] DECISION: pick C | REASONING: x | CONTEXT: y\n",
    )

    # understand-anything edge between two files that survive the scan
    ua = {
        "nodes": [
            {"id": "u1", "filePath": ".claude/skills/alpha/SKILL.md"},
            {"id": "u2", "filePath": "projects/proj-one/README.md"},
            {"id": "u3", "filePath": "not/in/scan.md"},
        ],
        "edges": [
            {"source": "u1", "target": "u2", "type": "imports", "weight": 2},
            {"source": "u1", "target": "u3", "type": "imports", "weight": 1},
        ],
    }
    write(root / ".understand-anything" / "tmp" / "ua-graph-0-full.json", json.dumps(ua))

    graphify = {
        "nodes": [
            {"id": 0, "label": "Offer", "file_type": "wiki", "source_file": "wiki/offer.md", "community": 1},
            {"id": 1, "label": "Me Mirror", "file_type": "md", "source_file": "context/me.md", "community": 2},
            {"id": 2, "label": "Critical Facts", "file_type": "md", "source_file": "CRITICAL_FACTS.md", "community": 2},
        ],
        "links": [
            {"source": 0, "target": 1, "relation": "mentions", "weight": 1},
            {"source": 0, "target": 2, "relation": "mentions", "weight": 1},
        ],
    }
    write(vault / "graphify-out" / "graph.json", json.dumps(graphify))
    return root, vault


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root, vault = make_fixtures(Path(td))
        g = build(root, vault)
        nodes = {n["id"]: n for n in g["nodes"]}
        links = g["links"]
        link_keys = {(l["source"], l["target"], l["relation"]) for l in links}

        # namespacing + presence
        assert "nexis:skill/alpha" in nodes and nodes["nexis:skill/alpha"]["label"] == "Alpha Skill"
        assert "nexis:skill/beta" in nodes  # frontmatter-less fallback
        assert "nexis:project/proj-one" in nodes
        assert "nexis:rule/style" in nodes
        assert "vault:0" in nodes and nodes["vault:0"]["type"] == "wiki"

        # unique ids
        assert len(nodes) == len(g["nodes"]), "duplicate node ids"

        # decisions clustered by month (2 months, 3 entries)
        clusters = [n for n in g["nodes"] if n["type"] == "decision-cluster"]
        assert {c["id"] for c in clusters} == {"nexis:decisions/2026-06", "nexis:decisions/2026-07"}
        assert g["meta"]["counts"]["decisions"] == 3

        # skill -> project mention link
        assert ("nexis:skill/alpha", "nexis:project/proj-one", "builds") in link_keys

        # ua edge remapped onto nexis ids; the edge to the unscanned file dropped
        assert ("nexis:skill/alpha", "nexis:project/proj-one", "ua:imports") in link_keys
        assert not any(l["relation"] == "ua:imports" and "not/in" in str(l) for l in links)

        # context mirror cross-link
        assert ("nexis:context/me", "vault:1", "mirrors") in link_keys

        # hubs anchor every typed node
        assert "nexis:hub/skills" in nodes and ("nexis:hub/skills", "nexis:skill/alpha", "member") in link_keys
        assert ("nexis:hub/nexis", "nexis:hub/projects", "contains") in link_keys

        # vault hub bridges the two halves
        assert "vault:__hub__" in nodes
        assert ("nexis:hub/nexis", "vault:__hub__", "syncs") in link_keys

        # link integrity: endpoints exist, no self-loops, no dupes
        for l in links:
            assert l["source"] in nodes and l["target"] in nodes, f"dangling link {l}"
            assert l["source"] != l["target"]
        assert len(link_keys) == len(links), "duplicate links"

        # counts honest
        assert g["meta"]["counts"]["nodes"] == len(g["nodes"])
        assert g["meta"]["counts"]["edges"] == len(links)
        assert g["meta"]["counts"]["skills"] == 2
        assert g["meta"]["counts"]["wiki"] == 1

    print("scanner selftest: OK")


if __name__ == "__main__":
    main()

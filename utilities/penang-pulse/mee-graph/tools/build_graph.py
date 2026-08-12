#!/usr/bin/env python3
"""Build and validate noodle-graph.json for Penang Pulse Mee-Search.

    cd mee-graph/tools && python3 build_graph.py

Writes ../data/noodle-graph.json and ../data/graph-stats.json, and fails loudly on
dangling edges, unknown node or edge types, unknown source ids, or duplicate ids.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src_sources import SOURCES          # noqa: E402
import src_nodes                          # noqa: E402
import src_dishes                         # noqa: E402  (registers dish/venue/episode nodes)
from src_nodes import NODES               # noqa: E402
from src_edges import EDGES, EDGE_TYPES   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

NODE_TYPES = {
    "region": "a place of origin or settlement, as specific as the evidence allows",
    "culture": "a community: Chinese dialect group, creole community, ethnic group",
    "wave": "a migration stream, ordinance or rupture that moved people",
    "dish": "a noodle dish, including ancestors and cousins outside Penang",
    "noodle": "a noodle type - a first-class node, because in Penang the noodle is the most "
              "reliable marker of which kitchen a dish came out of",
    "ingredient": "a signature ingredient or condiment",
    "technique": "a cooking method or service convention",
    "commodity": "an industrial or colonial product that changed what hawkers could cook",
    "media": "a media event that measurably changed a dish's economy",
    "concept": "a structural idea: the halal boundary, longevity noodles, naming logics",
    "name": "a name that collides across unrelated dishes",
    "venue": "a stall, kopitiam or food court",
    "episode": "one tasting in the Mee Myself and I series - tried or planned",
}

CONFIDENCE = ["high", "medium", "low", "disputed"]

# Colour and cluster hints for the visualisation layer. Kept in the data so the
# renderer does not have to hardcode a taxonomy.
# Palette is anchored on the Penang Pulse accent (#0f6e6e) so the prototypes in
# ../viz inherit the site's register rather than fighting it.
GROUPS = {
    "region": dict(cluster="place", colour="#4a6fa5"),
    "culture": dict(cluster="people", colour="#c2603a"),
    "wave": dict(cluster="history", colour="#8a6d3b"),
    "dish": dict(cluster="food", colour="#b8352f"),
    "noodle": dict(cluster="material", colour="#d4a13b"),
    "ingredient": dict(cluster="material", colour="#6f9455"),
    "technique": dict(cluster="craft", colour="#0f6e6e"),
    "commodity": dict(cluster="industry", colour="#8d6ca8"),
    "media": dict(cluster="industry", colour="#b06a8a"),
    "concept": dict(cluster="idea", colour="#5c5c5c"),
    "name": dict(cluster="idea", colour="#9c8f4e"),
    "venue": dict(cluster="place", colour="#3f7f9f"),
    "episode": dict(cluster="series", colour="#2f7f5f"),
}


# Per-community tones. `colour` is the node TYPE colour (used for legends and for
# type-coloured views); `tone` distinguishes individual communities, which the
# thread-flow, bowl-orbit and series views need in order to show a single bowl
# receiving contributions from several kitchens at once.
TONES = {
    # Chinese dialect groups - the terracotta family
    "c-hokkien": "#c2603a",
    "c-teochew": "#a8492f",
    "c-cantonese": "#d4794a",
    "c-hakka": "#8f4a2c",
    "c-hainanese": "#e0a06b",
    "c-foochow": "#b5673f",
    "c-henghua": "#cf8d63",
    # creole kitchens - rose
    "c-peranakan-penang": "#b06a8a",
    "c-peranakan-malacca": "#c98aa5",
    "c-phuket-baba": "#9c5578",
    "c-jawi-peranakan": "#8a4a6b",
    # South Asian - violet
    "c-tamil-muslim": "#8d6ca8",
    "c-marakkayar": "#7a5a95",
    "c-mappila": "#a487bd",
    "c-tamil-hindu": "#6b4f85",
    "c-chettiar": "#b9a0cd",
    # Arab / Persian - bronze
    "c-arab-hadhrami": "#8a6d3b",
    # Malay & Indonesian - green
    "c-malay-kedah": "#6f9455",
    "c-javanese": "#557a3f",
    "c-minangkabau": "#8aab72",
    "c-acehnese": "#43663a",
    # Siamese, Burmese, Bornean - teal / steel
    "c-siamese-my": "#0f6e6e",
    "c-burmese-penang": "#2f8f8a",
    "c-iban": "#3f7f9f",
    "c-kadazan-dusun": "#5f9fb5",
    # the supply chain
    "c-british-colonial": "#5c5c5c",
}


def fail(msg):
    print("BUILD FAILED: " + msg, file=sys.stderr)
    sys.exit(1)


def main():
    errors = []

    # ---------------------------------------------------------------- nodes
    by_id = {}
    for n in NODES:
        if n["id"] in by_id:
            errors.append("duplicate node id: %s" % n["id"])
        by_id[n["id"]] = n
        if n["type"] not in NODE_TYPES:
            errors.append("unknown node type %r on %s" % (n["type"], n["id"]))
        conf = n.get("confidence")
        if conf and conf not in CONFIDENCE:
            errors.append("bad confidence %r on %s" % (conf, n["id"]))
        for s in n.get("sources", []):
            if s not in SOURCES:
                errors.append("unknown source %r on node %s" % (s, n["id"]))

    # -------------------------------------------------------------- edges
    seen_edges = set()
    for i, e in enumerate(EDGES):
        eid = "e%04d" % (i + 1)
        e["id"] = eid
        if e["type"] not in EDGE_TYPES:
            errors.append("unknown edge type %r on %s" % (e["type"], eid))
        for end in ("source", "target"):
            if e[end] not in by_id:
                errors.append("dangling edge %s: %s -> %s (%s missing)"
                              % (eid, e["source"], e["target"], e[end]))
        if e["confidence"] not in CONFIDENCE:
            errors.append("bad confidence %r on %s" % (e["confidence"], eid))
        if not (0 < e["weight"] <= 1):
            errors.append("weight out of range on %s: %s" % (eid, e["weight"]))
        for s in e.get("sources", []):
            if s not in SOURCES:
                errors.append("unknown source %r on edge %s" % (s, eid))
        key = (e["type"], e["source"], e["target"])
        if key in seen_edges:
            errors.append("duplicate edge %s: %s" % (eid, key))
        seen_edges.add(key)

    # -------------------------------------- structural sanity on the model
    dishes = [n for n in NODES if n["type"] == "dish"]
    episodes = [n for n in NODES if n["type"] == "episode"]

    has_noodle = {e["source"] for e in EDGES if e["type"] == "uses_noodle"}
    for d in dishes:
        if d["id"] not in has_noodle:
            errors.append("dish %s has no uses_noodle edge" % d["id"])

    has_origin = {e["source"] for e in EDGES if e["type"] in ("originates_in", "attributed_to")}
    for d in dishes:
        if d["id"] not in has_origin:
            errors.append("dish %s has no originates_in or attributed_to edge" % d["id"])

    ep_dish = {e["source"] for e in EDGES if e["type"] == "of_dish"}
    for ep in episodes:
        if ep["id"] not in ep_dish:
            errors.append("episode %s is not linked to a dish" % ep["id"])
        if ep.get("status") == "tried" and ep.get("venue"):
            if not any(e["type"] == "tasted_at" and e["source"] == ep["id"] for e in EDGES):
                errors.append("tried episode %s has no tasted_at edge" % ep["id"])

    # every episode's declared dish/venue attribute must agree with its edges
    for ep in episodes:
        declared = ep.get("dish")
        edged = [e["target"] for e in EDGES if e["type"] == "of_dish" and e["source"] == ep["id"]]
        if declared and declared not in edged:
            errors.append("episode %s dish attribute %s disagrees with edges %s"
                          % (ep["id"], declared, edged))

    orphans = [n["id"] for n in NODES
               if not any(e["source"] == n["id"] or e["target"] == n["id"] for e in EDGES)]
    if orphans:
        errors.append("orphan nodes with no edges at all: %s" % ", ".join(sorted(orphans)))

    unused_sources = sorted(
        set(SOURCES) - {s for n in NODES for s in n.get("sources", [])}
        - {s for e in EDGES for s in e.get("sources", [])})

    if errors:
        for msg in errors:
            print("  - " + msg, file=sys.stderr)
        fail("%d problem(s) found" % len(errors))

    # ------------------------------------------------------------- assemble
    for n in NODES:
        n.update(GROUPS[n["type"]])
        # tone defaults to the type colour, so every node has one
        n["tone"] = TONES.get(n["id"], n["colour"])

    missing_tone = sorted(c["id"] for c in NODES
                          if c["type"] == "culture" and c["id"] not in TONES)
    if missing_tone:
        fail("culture nodes without a tone: %s" % ", ".join(missing_tone))

    checklist = dict(
        tried=sum(1 for e in episodes if e.get("status") == "tried"),
        planned=sum(1 for e in episodes if e.get("status") == "planned"),
    )

    graph = dict(
        meta=dict(
            title="Mee-Search — culture graph",
            subtitle="Where the bowls of Penang actually come from, and how confident we are "
                     "about each claim",
            project="Penang Pulse / Mee Myself and I",
            built=str(date.today()),
            version="1.0.0",
            license="Research dataset compiled for the Penang Pulse project. Source claims "
                    "belong to the cited works; the graph structure, confidence ratings and "
                    "flags are this project's editorial judgement.",
            howToRead=[
                "Every edge carries a `confidence` of high, medium, low or disputed. Read the "
                "disputed ones as invitations, not answers.",
                "`weight` is how load-bearing the relationship is, not how true it is. A weak "
                "high-confidence edge is a real but minor link; a strong disputed edge is a "
                "claim the whole story hangs on and nobody has proved.",
                "`originates_in` is geography, `carried_by` is whose kitchen, `attributed_to` is "
                "somebody's claim. They are deliberately separate.",
                "`confused_with` is not a genealogy. It records that the literature conflates "
                "two things, which is a fact about the sources rather than the food.",
                "`unevidenced_link` edges are deliberate refusals: links other people assert "
                "that this dataset declines to draw. They are the most useful edges in the file.",
                "Dish names in this corpus are unreliable evidence of origin and reliable "
                "evidence of the naming community's point of view.",
            ],
            nodeTypes=NODE_TYPES,
            edgeTypes=EDGE_TYPES,
            confidenceLevels=dict(
                high="multiple independent reputable sources agree, or documentary and archival "
                     "evidence exists",
                medium="single reputable source, or a consensus in food-writing literature "
                       "without scholarly backing",
                low="anecdotal, single weak source, or a repeated claim with no traceable origin",
                disputed="sources actively contradict each other; the graph carries the "
                         "disagreement rather than resolving it",
            ),
            checklist=checklist,
        ),
        sources={k: dict(id=k, **v) for k, v in SOURCES.items()},
        nodes=NODES,
        edges=EDGES,
    )

    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "noodle-graph.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # ---------------------------------------------------------------- stats
    node_counts = Counter(n["type"] for n in NODES)
    edge_counts = Counter(e["type"] for e in EDGES)
    conf_counts = Counter(e["confidence"] for e in EDGES)
    degree = defaultdict(int)
    for e in EDGES:
        degree[e["source"]] += 1
        degree[e["target"]] += 1
    hubs = sorted(degree.items(), key=lambda kv: -kv[1])[:15]
    flagged = [dict(id=n["id"], label=n["label"], flags=n["flags"])
               for n in NODES if n.get("flags")]

    stats = dict(
        built=str(date.today()),
        nodes=len(NODES), edges=len(EDGES), sources=len(SOURCES),
        nodesByType=dict(sorted(node_counts.items())),
        edgesByType=dict(sorted(edge_counts.items())),
        edgesByConfidence=dict(sorted(conf_counts.items())),
        sourcesByTier=dict(sorted(Counter(v["tier"] for v in SOURCES.values()).items())),
        topHubs=[dict(id=k, label=by_id[k]["label"], degree=v) for k, v in hubs],
        flaggedNodes=flagged,
        unevidencedLinks=[dict(source=e["source"], target=e["target"], note=e.get("note"))
                          for e in EDGES if e["type"] == "unevidenced_link"],
        disputedEdges=sum(1 for e in EDGES if e["confidence"] == "disputed"),
        unusedSources=unused_sources,
        checklist=checklist,
    )
    with open(os.path.join(DATA, "graph-stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # A browser-loadable copy so the ../viz prototypes work by double-click,
    # without needing a local web server (file:// blocks fetch of JSON).
    viz = os.path.abspath(os.path.join(HERE, "..", "viz"))
    if os.path.isdir(viz):
        with open(os.path.join(viz, "graph-data.js"), "w", encoding="utf-8") as fh:
            fh.write("/* Generated by tools/build_graph.py - do not edit. */\n")
            fh.write("window.MEE_GRAPH = ")
            json.dump(graph, fh, ensure_ascii=False, separators=(",", ":"))
            fh.write(";\n")
        print("    wrote viz/graph-data.js")

    print("OK  %d nodes, %d edges, %d sources -> %s"
          % (len(NODES), len(EDGES), len(SOURCES), out))
    print("    nodes:", dict(sorted(node_counts.items())))
    print("    edge confidence:", dict(sorted(conf_counts.items())))
    if unused_sources:
        print("    note: %d source(s) registered but not cited: %s"
              % (len(unused_sources), ", ".join(unused_sources)))


if __name__ == "__main__":
    main()

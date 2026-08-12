# Mee-Search — the Penang mee culture graph

A research dataset and a long-form narrative on where Penang's noodle dishes actually come
from: which Chinese prefecture, which creole marriage, which halal constraint, which
industrial commodity — and how confident anybody is entitled to be about each of it.

Built for **Mee Myself and I** on [penangpulse.com](https://penangpulse.com/). Both stages are
here: the dataset and the story, and seven animated prototypes over them in
[`viz/`](./viz/index.html).

```
mee-graph/
├── README.md                 you are here
├── narrative/                ~24,500 words, seven chapters
│   ├── 01-the-island-that-was-kedah.md
│   ├── 02-waves-and-dialects.md
│   ├── 03-the-creole-kitchens.md
│   ├── 04-mamak-chulia-hadhrami.md
│   ├── 05-malay-javanese-siamese.md
│   ├── 06-how-fusion-actually-happens.md
│   └── 07-dish-dossiers.md
├── data/
│   ├── noodle-graph.json     360 nodes · 1,017 edges · 137 sources
│   ├── graph-stats.json      counts, hubs, flags, refused links
│   └── SCHEMA.md             full schema + example queries + suggested views
├── viz/                      SEVEN WORKING ANIMATED PROTOTYPES + gallery
│                             open viz/index.html — vanilla HTML/CSS/JS + d3 v7,
│                             no build step, inherits the site's CSS tokens
├── research/                 the raw dossiers the narrative was built from,
│                             ~46,000 words with inline [S] citations and
│                             per-claim confidence labels — keep these, they
│                             contain far more than the narrative uses
└── tools/
    ├── src_sources.py        the source register, tiered by reliability
    ├── src_nodes.py          regions, cultures, waves, noodles, ingredients,
    │                         techniques, commodities, media, concepts, names
    ├── src_dishes.py         dishes, venues, episodes
    ├── src_edges.py          every relationship
    └── build_graph.py        assemble + validate → data/
```

## Rebuilding

```bash
cd mee-graph/tools && python3 build_graph.py
```

No dependencies. It refuses to write output if an edge dangles, a type is unknown, a source id
is wrong, a dish has no noodle, an episode is not linked to a dish, or a node ends up with no
edges at all. Edit the `src_*.py` files, never the JSON.

## What is in the graph

| | |
| --- | --- |
| **360 nodes** | 75 dishes · 62 regions · 45 ingredients · 44 episodes · 26 cultures · 20 venues · 19 noodles · 18 techniques · 17 waves · 15 concepts · 8 name collisions · 6 commodities · 5 media events |
| **1,017 edges** | 30 typed relationships, each with a weight and a confidence rating; ~230 carry an explanatory note and ~300 carry sources |
| **137 sources** | tiered: scholarly · reference · journalism · specialist · community · encyclopedic · commercial · media |
| **Confidence** | 702 high · 266 medium · 37 low · 12 disputed |

Every checklist entry is in there — tried, to-try, mainland, wild card and revisit — as an
`episode` node linked to its dish, its venue, its date and, where published, its live guide
slug on penangpulse.com. Which means the graph is simultaneously a cultural map and a
progress tracker.

## Visualisations

Stage two is built: **`viz/index.html`** is a gallery of seven animated prototypes over this
dataset. Force-directed drill-down, a zoomable radial hierarchy, an animated particle flow,
an orbital dish deconstruction, a timeline with a playhead, an evidence-dissolve view, and
the series' own route across the map. All vanilla HTML/CSS/JS plus d3, all responsive, all
verified in headless Chromium at desktop and phone widths. See `viz/README.md` for embedding
notes — including the one thing to change before production, which is vendoring d3 locally
rather than pulling it from a CDN into a PWA.

## Six things it turned up

**The noodle crosses the halal boundary; the sauce never does.** Yellow alkaline wheat noodle
was made in Chinese factories and sold to everybody, including Malay and Indian Muslim
hawkers. That single asymmetry generates most of Penang's dish-pairs — curry mee against curry
laksa, char kway teow against CKT kerang, kolo mee against *mi kolok*, mee jawa against mee
rebus. The noodle is shared infrastructure; the seasoning is where the community lives.

**Dish names are sociology, not etymology.** Three naming logics run at once: after the cook's
ethnicity (usually applied from outside, frequently wrong), after the noodle, and after the
process. "Hokkien mee" is three unrelated dishes in three cities. "You mee" has four referents.
"Sabah pan mee" names nothing that exists in Sabah. Names are reliable evidence of who was
doing the naming and unreliable evidence of where a dish came from.

**Laksa named a noodle for centuries before it named a soup.** The 1391 Biluluk inscription in
East Java glosses *hanglaksa* as "vermicelli maker." Wilkinson's 1901 dictionary lists *laksa*
as "vermicelli." An 1833 *Singapore Chronicle* manifest lists 24 baskets of laksa shipped from
Batavia. Which kills the Chinese "spicy sand" folk etymologies — they all describe the broth —
and reframes every argument about which laksa is original as badly posed.

**Industrial commodities are hidden protagonists.** British-commodified curry powder made
hawker curry economical. Tan Yong Him's Swallow-brand rempah *created and froze* modern Sarawak
laksa in the 1960s. Nestlé Maggi arrived in 1969 with the sauce and 1971 with the noodle, which
makes Maggi goreng the only dish here with a supply-chain birthday. MyKuali turned a Penang
serving convention into a global category in 2012. Every one is a datable node in a corpus of
otherwise fuzzy nineteenth-century origins.

**1949 is the hinge, and it is not about food.** Emergency-era immigration control closed the
pipeline that had run since 1786; by 1957, 81% of Penang's Chinese were locally born. After
that no fresh cohort arrived to correct or refresh the dialect repertoires. That is precisely
why Penang, KL and Singapore versions of "the same" dish have drifted so far apart — they
stopped being corrected against a common source at the same moment.

**The most repeated story in Penang food writing has no source.** Char kway teow's "fishermen
and farmers sold it in the evening for cheap energy" origin is on Wikipedia with two footnotes.
The first points at an NLB article that does not contain the claim. The second points at a 2016
newspaper health-scare piece. It is citation drift, not history — which is why every edge in
this dataset carries a confidence rating.

## The most useful view

Filter to `weight > 0.7 AND confidence IN (low, disputed)`. That is everything in Penang food
writing that is repeated confidently and known badly. It is a short list, and it is the most
interesting thing in the file.

Runner-up: the `unevidenced_link` edges — links other people assert that this dataset declines
to draw. Mohinga to asam laksa. Yi mein to instant noodles. Lam mee to loh mee. All Hokkien mee
to lor mee. Negative results are results, and a graph that only contains the connections people
believe in is just a rumour with better typography.

## Notes for the visualisation layer

`SCHEMA.md` has the full field reference and example queries; `viz/README.md` covers the built
prototypes. The design rules that matter: node `type` carries a `cluster` and a `colour` in the
data and each community additionally carries a `tone`, so the renderer never hardcodes a
taxonomy; edge `confidence` should drive opacity or dash pattern, because the honest view is the
interesting one; `weight` should drive thickness. And do not collapse `originates_in`,
`carried_by` and `attributed_to` into one relationship — the separation between geography,
kitchen and claim is doing most of the intellectual work.

## Caveats worth keeping visible

**Evidence quality is systematically worse for Malay and mamak dishes than for Chinese ones.**
Every Chinese dish here has at least a named founder story; mee udang at Sungai Dua has none,
despite being a substantial commercial cluster people drive across a bridge for. That is a bias
in the *sources*, not in the dishes, and a graph built naively on available sources will
inherit it. It is recorded as its own concept node so it can be corrected for.

**The load-bearing claim of Penang food history is unverified.** That the Teochews dominate the
island's street food trade despite Hokkien numerical dominance is repeated everywhere, Michelin
included, and no scholarly source establishes it. Everything in the "Penang food is Teochew
food with Hokkien names" thesis rests on it. Flagged as `medium` with an open-question marker.

**Some of the best leads are unread.** The Penang Teochew Association holds 2,316 registration
records from 1919, each listing the registrant's district of origin in Chaoshan. Young Mook
Cho's 2022 York PhD on the formation of Penang's Chinese community, 1786–1830. Vaughan's 1854
"Notes on the Chinese of Penang," quoted here only at second hand through Kuchler. Any of the
three would improve this dataset more than another twenty blog posts.

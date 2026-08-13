# Graph schema — `noodle-graph.json`

Built by `../tools/build_graph.py` — 362 nodes, 1,020 edges, 138 sources, 30 edge types. Run it after any edit to the `src_*.py` files; it
refuses to write output if an edge dangles, a type is unknown, a source id is wrong, a
dish has no noodle, or an episode is not linked to a dish.

```
mee-graph/
  data/
    noodle-graph.json   the dataset
    graph-stats.json    counts, hubs, flags, unevidenced links
    SCHEMA.md           this file
  narrative/            the long-form story, chapter by chapter
  tools/
    src_sources.py      138 sources, each with a reliability tier
    src_nodes.py        regions, cultures, waves, noodles, ingredients,
                        techniques, commodities, media, concepts, name collisions
    src_dishes.py       dishes, venues, episodes
    src_edges.py        every relationship
    build_graph.py      assemble + validate
```

## Top level

| Key | What |
| --- | --- |
| `meta` | title, build date, `nodeTypes`, `edgeTypes`, `confidenceLevels`, `howToRead`, checklist counts |
| `sources` | object keyed by source id → `{id, title, url, tier, note}` |
| `nodes` | array |
| `edges` | array |

## Node types

| Type | Count | What it is |
| --- | --- | --- |
| `region` | 62 | a place of origin or settlement, as specific as the evidence allows — Zhangzhou, not "China" |
| `culture` | 26 | a community: dialect group, creole community, ethnic group |
| `wave` | 17 | a migration stream, ordinance, or rupture that moved people |
| `dish` | 75 | noodle dishes, including ancestors and cousins outside Penang |
| `noodle` | 19 | noodle types — first-class, because in Penang the noodle is the most reliable marker of which kitchen a dish came out of |
| `ingredient` | 45 | signature ingredients and condiments |
| `technique` | 18 | cooking methods and service conventions |
| `commodity` | 6 | industrial or colonial products that changed what a hawker could cook |
| `media` | 5 | media events that measurably changed a dish's economy |
| `concept` | 15 | structural ideas: the halal boundary, longevity noodles, the three naming logics, citogenesis |
| `name` | 8 | names that collide across unrelated dishes |
| `venue` | 21 | stalls, kopitiams and food courts — the series' own plus reference stalls |
| `episode` | 45 | one tasting each, tried or planned |

Every node has `id`, `type`, `label`, plus a `cluster` and `colour` hint for the renderer.
Most carry `blurb`; many carry `confidence`, `sources`, and `flags`.

Dish nodes additionally carry: `zh`, `pojh`, `aka`, `malay`, `tamil`, `penangStatus`
(`core` | `present` | `rare` | `absent` | `ancestor` | `cousin` | `fiction`), `tryStatus`
(`tried` | `to-try` | `wildcard` | `off-list`), `style`, `etymology`, `penangVariation`,
`fusion`, `contested`, `ritual`, `significance`, `homeRegion`.

Episode nodes carry `dish`, `venue`, `date`, `status`, `seriesOrder`, `postSlug` (the live
Penang Pulse guide), `styleNote`, `revisitOf`, `mainland`.

## Edge types

Each edge: `id`, `type`, `source`, `target`, `weight`, `confidence`, optional `note` and
`sources`.

**People and places**

| Type | Direction | Licenses you to say |
| --- | --- | --- |
| `home_region` | culture → region | where this community came from |
| `settled_in` | culture → region | where it went |
| `migrated_via` | culture → wave | the stream, or the ordinance, that moved or stopped it |
| `occupied_niche` | culture → concept | the economic slot it took, and what that did to its food |

**Dish provenance — deliberately three separate edges**

| Type | Direction | Licenses you to say |
| --- | --- | --- |
| `originates_in` | dish → region | geography |
| `carried_by` | dish → culture | whose kitchen it actually comes out of |
| `attributed_to` | dish → culture | somebody *claims* this, and the claim may be wrong |

A dish can have several of each. Penang asam laksa `originates_in` both George Town and
Kedah, at `disputed` confidence, because the direction of travel is unresolved and the
graph declines to pick.

**Composition**

| Type | Direction |
| --- | --- |
| `uses_noodle` | dish → noodle |
| `uses_ingredient` | dish → ingredient |
| `uses_technique` | dish → technique |
| `contributed_by` | noodle \| ingredient \| technique → culture |

`contributed_by` is the fusion layer. It is what lets you ask "which threads are in this
bowl" and get an answer built from components rather than from a label.

**Dish to dish**

| Type | Licenses you to say |
| --- | --- |
| `derived_from` | A descends from B |
| `sibling_of` | common parent; neither derived from the other |
| `influenced_by` | borrowing without descent |
| `halal_variant_of` | the same dish rebuilt across the halal line |
| `shares_architecture` | same structural idea, independently arrived at |
| `co_sold_with` | sold from the same stall — a real transmission route, not a metaphor |
| `confused_with` | conflated in the literature. **Not** a genealogy claim |
| `false_cognate_of` | same name, unrelated dishes |
| `unevidenced_link` | a link others assert that this dataset declines to draw |
| `shares_name_with` | dish → a `name` node recording a collision (23 edges — one of the commonest types) |

**Forces**

| Type | Direction |
| --- | --- |
| `enabled_by` | dish → commodity \| wave \| technique |
| `standardised_by` | dish → commodity (an industrial product froze the recipe) |
| `popularised_by` | dish → media |
| `ritual_role` | dish → concept |
| `illustrates` | anything → concept |

**Series traceability**

| Type | Direction |
| --- | --- |
| `of_dish` | episode → dish |
| `tasted_at` | episode → venue |
| `revisit_of` | episode → episode |
| `reference_stall_for` | venue → dish |

## `weight` vs `confidence`

These are orthogonal and it matters.

- **`weight`** (0–1) is how *load-bearing* the relationship is. Kangkung in Penang Hokkien
  mee is 0.85 because you notice its absence; five-spice in koay chiap is 0.5.
- **`confidence`** is how well *evidenced* it is: `high`, `medium`, `low`, `disputed`.

So a low-weight high-confidence edge is a real but minor link. A **high-weight disputed
edge is the dangerous kind**: a claim the whole story hangs on that nobody has proved.
Filtering the graph to `weight > 0.7 AND confidence in (low, disputed)` gives you a
shortlist of everything in Penang food writing that is repeated confidently and known
badly. It is a short list, and it is the most interesting view in the dataset.

## Source tiers

`scholarly` · `reference` · `journalism` · `specialist` · `community` · `encyclopedic` ·
`commercial` · `media`. Roughly in descending order of how much weight they can bear.
The distinction between `specialist` (researched food history — Tony Boey, Khir Johari,
Wendy Hutton) and `media` (blogs and listicles) does real work here: most of what is known
about Malaysian hawker genealogy is `specialist`, and most of what is *believed* is `media`.

## Useful queries

```js
const g = await (await fetch('noodle-graph.json')).json();
const byId = Object.fromEntries(g.nodes.map(n => [n.id, n]));
const out  = id => g.edges.filter(e => e.source === id);
const into = id => g.edges.filter(e => e.target === id);
```

| Question | Query |
| --- | --- |
| Which threads are in this bowl? | `uses_*` from the dish, then `contributed_by` from each component |
| What has the series actually eaten? | nodes where `type === 'episode' && status === 'tried'`, then `of_dish` |
| What is Penang's densest cultural hub? | highest-degree `culture` node — it is `c-hokkien`, by a distance |
| What do we not know? | `edges.filter(e => e.confidence === 'disputed' \|\| e.type === 'unevidenced_link')` |
| Which claims are shaky *and* important? | `weight > 0.7 && ['low','disputed'].includes(confidence)` |
| Show only the halal boundary | edges of type `halal_variant_of`, plus nodes linked to `x-halal-boundary` |
| Trace one noodle across kitchens | `into('n-yellow-alkaline')` — it reaches Hokkien, Cantonese, Malay and Tamil Muslim dishes alike |

## Suggested views for the visualisation

1. **Threads** — cultures as hubs, dishes orbiting, edge colour by `carried_by` vs
   `attributed_to`. The single clearest picture of the island.
2. **Confidence** — the whole graph, edge opacity by confidence. Disputed edges glow. This
   is the honest view and probably the most interesting one.
3. **Noodle-first** — collapse to `noodle` nodes and watch `n-yellow-alkaline` sprawl across
   every community while `n-mee-sua` stays in one corner.
4. **Timeline** — `wave` nodes on an axis, dishes attached where their enabling event sits.
   Maggi goreng pins hard to 1971; almost nothing else pins at all.
5. **The series** — episodes as a path through the dish layer, with the unvisited dishes
   greyed. Effectively a map of what is left to eat.
6. **Name collisions** — just the eight `name` nodes and their dishes. Small, and it
   explains more about Malaysian food than any other subgraph this size.

"""Edge register for the Penang noodle culture graph.

Edge types, and what each one licenses you to claim
--------------------------------------------------
home_region            culture -> region      where this community came from
settled_in             culture -> region      where it went
migrated_via           culture -> wave        the stream that carried it
occupied_niche         culture -> concept     the economic slot it took, and what that did to food

originates_in          dish -> region         geographic origin
carried_by             dish -> culture        whose kitchen it comes out of
attributed_to          dish -> culture        a CLAIMED attribution, possibly contested
uses_noodle            dish -> noodle
uses_ingredient        dish -> ingredient
uses_technique         dish -> technique
contributed_by         noodle|ingredient|technique -> culture   which thread supplied this part

derived_from           dish -> dish           A descends from B
sibling_of             dish -> dish           common parent, neither derived from the other
influenced_by          dish -> dish           borrowing without descent
halal_variant_of       dish -> dish           the same dish rebuilt across the halal line
shares_architecture    dish -> dish           same structural idea, independent arrival
co_sold_with           dish -> dish           sold from the same stall - a real transmission route
confused_with          dish -> dish           conflated in the literature. NOT a genealogy claim
false_cognate_of       dish -> dish           same name, unrelated dishes
shares_name_with       dish -> name
unevidenced_link       dish -> dish           a link people assert that this graph declines to make

enabled_by             dish -> commodity|wave|technique
standardised_by        dish -> commodity      an industrial product froze the recipe
popularised_by         dish -> media
ritual_role            dish -> concept
illustrates            any -> concept

of_dish                episode -> dish
tasted_at              episode -> venue
revisit_of             episode -> episode
reference_stall_for    venue -> dish
"""

EDGES = []

EDGE_TYPES = {
    "home_region": "where a community came from",
    "settled_in": "where a community went",
    "migrated_via": "the migration stream that carried a community",
    "occupied_niche": "the economic slot a community took, and its consequence for food",
    "originates_in": "geographic origin of a dish",
    "carried_by": "whose kitchen a dish comes out of",
    "attributed_to": "a claimed attribution, possibly contested",
    "uses_noodle": "dish to noodle type",
    "uses_ingredient": "dish to signature ingredient",
    "uses_technique": "dish to cooking method",
    "contributed_by": "which cultural thread supplied a component",
    "derived_from": "descent",
    "sibling_of": "common parent, neither derived from the other",
    "influenced_by": "borrowing without descent",
    "halal_variant_of": "the same dish rebuilt across the halal line",
    "shares_architecture": "same structural idea, independently arrived at",
    "co_sold_with": "sold from the same stall",
    "confused_with": "conflated in the literature - not a genealogy claim",
    "false_cognate_of": "same name, unrelated dishes",
    "shares_name_with": "dish to a colliding name",
    "unevidenced_link": "a link others assert that this graph declines to make",
    "enabled_by": "a commodity, wave or technique that made the dish possible",
    "standardised_by": "an industrial product that froze the recipe",
    "popularised_by": "a media event that changed the dish's economy",
    "ritual_role": "ceremonial or calendrical function",
    "illustrates": "an example of a structural concept",
    "of_dish": "episode to dish",
    "tasted_at": "episode to venue",
    "revisit_of": "episode to a previous episode",
    "reference_stall_for": "venue to the dish it is a benchmark for",
}


def E(etype, src, tgt, weight=0.6, confidence="medium", note=None, sources=None):
    e = dict(type=etype, source=src, target=tgt, weight=weight, confidence=confidence)
    if note:
        e["note"] = note
    if sources:
        e["sources"] = sources
    EDGES.append(e)
    return e


# ==================================================== CULTURES -> REGIONS
for c, regions, conf in [
    ("c-hokkien", ["r-xiamen", "r-quanzhou", "r-zhangzhou", "r-anxi", "r-hui-an", "r-haicheng",
                   "r-nan-an"], "high"),
    ("c-teochew", ["r-chaoshan"], "high"),
    ("c-cantonese", ["r-guangzhou", "r-shahe", "r-sze-yup"], "high"),
    ("c-hakka", ["r-meizhou-dabu", "r-jiaying-meixian", "r-huizhou-gd", "r-yongding",
                 "r-zengcheng", "r-jieyang"], "high"),
    ("c-hainanese", ["r-hainan"], "high"),
    ("c-foochow", ["r-fuzhou", "r-ninghua"], "high"),
    ("c-henghua", ["r-putian"], "medium"),
    ("c-tamil-muslim", ["r-coromandel", "r-nagore", "r-kilakarai"], "high"),
    ("c-marakkayar", ["r-kilakarai", "r-nagore"], "high"),
    ("c-mappila", ["r-malabar"], "medium"),
    ("c-tamil-hindu", ["r-coromandel"], "high"),
    ("c-chettiar", ["r-chettinad"], "high"),
    ("c-arab-hadhrami", ["r-hadhramaut"], "high"),
    ("c-malay-kedah", ["r-kedah"], "high"),
    ("c-javanese", ["r-java-central", "r-java-east"], "high"),
    ("c-minangkabau", ["r-minangkabau"], "medium"),
    ("c-acehnese", ["r-aceh"], "high"),
    ("c-siamese-my", ["r-patani", "r-kedah"], "high"),
    ("c-peranakan-malacca", ["r-malacca"], "high"),
    ("c-phuket-baba", ["r-phuket"], "medium"),
]:
    for r in regions:
        E("home_region", c, r, weight=0.8, confidence=conf)

for c, regions in [
    ("c-hokkien", ["r-george-town", "r-penang-island", "r-deli-medan", "r-phuket", "r-singapore"]),
    ("c-teochew", ["r-seberang-perai", "r-bukit-mertajam", "r-kedah", "r-george-town",
                   "r-bangkok", "r-phnom-penh", "r-singapore", "r-kuching"]),
    ("c-cantonese", ["r-george-town", "r-ipoh-kinta", "r-kuala-lumpur", "r-hong-kong"]),
    ("c-hakka", ["r-penang-island", "r-taiping-larut", "r-kuala-lumpur", "r-ipoh-kinta",
                 "r-seremban", "r-kuching", "r-sabah", "r-tuaran"]),
    ("c-hainanese", ["r-george-town", "r-seremban", "r-johor", "r-singapore"]),
    ("c-foochow", ["r-sibu", "r-sitiawan", "r-george-town"]),
    ("c-tamil-muslim", ["r-george-town", "r-kedah"]),
    ("c-tamil-hindu", ["r-seberang-perai"]),
    ("c-javanese", ["r-seberang-perai", "r-johor", "r-suriname"]),
    ("c-arab-hadhrami", ["r-george-town", "r-aceh"]),
    ("c-peranakan-penang", ["r-george-town", "r-penang-island"]),
    ("c-siamese-my", ["r-penang-island"]),
    ("c-burmese-penang", ["r-penang-island"]),
    ("c-jawi-peranakan", ["r-george-town"]),
]:
    for r in regions:
        E("settled_in", c, r, weight=0.7, confidence="high")

E("home_region", "c-peranakan-penang", "r-haicheng", weight=0.5, confidence="medium",
  note="Chinese paternal line predominantly southern Fujian; maternal line Malay, Siamese and "
       "Burmese, which is why the kitchen is Southeast Asian.",
  sources=["peranakan-genetics"])
E("home_region", "c-peranakan-penang", "r-kedah", weight=0.6, confidence="medium",
  note="The maternal and substrate side. Reading Penang Nyonya cooking as a Chinese cuisine "
       "with Malay borrowings gets the direction backwards - the mothers' kitchen was the base.",
  sources=["kuroda-samsam", "michelin-malaysia-regional"])
E("derived_from", "c-peranakan-penang", "c-peranakan-malacca", weight=0.5, confidence="high",
  note="Fed from Malacca from 1786, but re-creolised in a northern environment - which is why it "
       "diverged rather than replicated.", sources=["kuchler-1965", "michelin-malaysia-regional"])
E("derived_from", "c-phuket-baba", "c-peranakan-penang", weight=0.5, confidence="medium",
  note="Hokkien migration to the Phuket tin frontier came substantially via Penang.",
  sources=["wong-big-five", "thai-peranakan-translocal"])
E("home_region", "c-jawi-peranakan", "r-coromandel", weight=0.6, confidence="high",
  note="Indian Muslim - predominantly Tamil, also Malabari - fathers.", sources=["wiki-jawi-peranakan"])
E("home_region", "c-jawi-peranakan", "r-hadhramaut", weight=0.4, confidence="medium",
  note="The community also absorbed Arab-Malay offspring and later intermarried with Syed "
       "families.", sources=["wiki-jawi-peranakan"])
E("home_region", "c-jawi-peranakan", "r-kedah", weight=0.6, confidence="high",
  note="Malay mothers - the same demographic mechanism as the Baba-Nyonya, with a different "
       "religion and therefore a different destiny.", sources=["wiki-jawi-peranakan"])


# ==================================================== CULTURES -> WAVES
E("migrated_via", "c-hokkien", "w-pre-1786-kedah", weight=0.8, confidence="high",
  note="Koh Lay Huan came from Kuala Muda, not from Fujian - Penang's founding Chinese elite was "
       "recruited from the neighbourhood.", sources=["penang-traveltips-koh-lay-huan"])
E("migrated_via", "c-peranakan-malacca", "w-malacca-baba", weight=0.8, confidence="high")
E("migrated_via", "c-hokkien", "w-sinkeh-coolie", weight=0.7, confidence="high")
E("migrated_via", "c-teochew", "w-sinkeh-coolie", weight=0.7, confidence="high")
E("migrated_via", "c-cantonese", "w-sinkeh-coolie", weight=0.7, confidence="high")
E("migrated_via", "c-hakka", "w-tin-boom", weight=0.9, confidence="high",
  note="In 1891, 64% of the 28,125 Chinese in Selangor's tin mines were Hakka.",
  sources=["voon-2024-hakka"])
E("migrated_via", "c-cantonese", "w-tin-boom", weight=0.7, confidence="high")
E("migrated_via", "c-hainanese", "w-sinkeh-coolie", weight=0.6, confidence="high",
  note="Late in the sequence, which is the whole story.", sources=["mothership-hainanese"])
E("migrated_via", "c-foochow", "w-1901-sibu-foochow", weight=0.9, confidence="high")
E("migrated_via", "c-foochow", "w-1903-sitiawan-foochow", weight=0.9, confidence="high")
E("migrated_via", "c-tamil-hindu", "w-kangani", weight=0.9, confidence="high")
E("migrated_via", "c-javanese", "w-javanese-labour", weight=0.9, confidence="high")
E("migrated_via", "c-arab-hadhrami", "w-hajj-port", weight=0.7, confidence="high")
E("migrated_via", "c-acehnese", "w-hajj-port", weight=0.6, confidence="high")
E("migrated_via", "c-tamil-muslim", "w-1786-founding", weight=0.7, confidence="high",
  note="Tamil Muslim traders arrived within days of Light's landing, having already worked the "
       "Kedah coast for centuries.", sources=["areca-chulia", "wiki-chulia-street"])

for w in ["w-1932-aliens", "w-japanese-occupation", "w-1949-closure"]:
    for c in ["c-hokkien", "c-teochew", "c-cantonese", "c-hakka", "c-hainanese"]:
        E("migrated_via", c, w, weight=0.4, confidence="high",
          note="Constraint rather than transport: these are the events that closed the pipeline.")

E("illustrates", "w-1949-closure", "x-substrate-marker", weight=0.8, confidence="high",
  note="After 1949 no fresh cohort arrived to correct or refresh the dialect repertoires, so "
       "every subsequent change is endogenous - which is exactly why Penang, KL and Singapore "
       "versions of the same dish diverged so far.", sources=["muse-emergency-immigration"])
E("illustrates", "w-1932-aliens", "x-hawker-apprenticeship", weight=0.5, confidence="medium",
  note="The 1930s female influx is the demographic precondition for family-run stalls and for "
       "home cooking crossing into commercial street food.", sources=["nlb-immigration-1932"])


# ============================================== CULTURES -> NICHE CONCEPTS
E("occupied_niche", "c-hainanese", "x-kopitiam", weight=0.95, confidence="high",
  note="An institution created by occupational accident: the last group to arrive found the "
       "trades taken and the kitchens open.", sources=["mothership-hainanese", "kuchler-1965"])
E("occupied_niche", "c-hainanese", "x-domestic-service", weight=0.95, confidence="high",
  sources=["mothership-hainanese", "johorkaki-katong-laksa"])
E("occupied_niche", "c-tamil-muslim", "x-mamak-stall", weight=0.95, confidence="high",
  sources=["oed-mamak", "wiki-mee-goreng-mamak"])
E("occupied_niche", "c-tamil-muslim", "x-halal-boundary", weight=0.9, confidence="high",
  note="Halal is the enabling constraint, not an incidental attribute: it is what let this "
       "community sell across both other kitchens.", sources=["wiki-mee-goreng-mamak"])
E("occupied_niche", "c-teochew", "x-hawker-apprenticeship", weight=0.6, confidence="medium",
  note="The claim that Teochews dominated Penang hawking rests on repetition, not scholarship. "
       "Recorded as an open question.", sources=["michelin-ckt"])
E("occupied_niche", "c-hokkien", "x-northern-triangle", weight=0.85, confidence="high",
  note="The Big Five dominated the Penang-Phuket-Deli supply circuit.", sources=["wong-big-five"])
E("occupied_niche", "c-peranakan-penang", "x-northern-triangle", weight=0.7, confidence="high")
E("occupied_niche", "c-arab-hadhrami", "w-hajj-port", weight=0.8, confidence="high")
E("illustrates", "c-jawi-peranakan", "x-evidence-asymmetry", weight=0.7, confidence="medium",
  note="A well-documented community whose FOOD is barely documented at all, because it was elite "
       "and celebratory rather than hawker - which is why it left almost no mark on the canon and "
       "is nearly extinct.", sources=["heritasian-jawi", "wiki-jawi-peranakan"])
E("illustrates", "c-hokkien", "x-naming-after-cook", weight=0.9, confidence="high",
  note="Hokkien was the lingua franca of the Penang street, so Teochew and Cantonese dishes "
       "acquired Hokkien names. Naming language is evidence of prestige, not of provenance.",
  sources=["michelin-ckt", "johorkaki-hokkien-mee"])
E("illustrates", "c-british-colonial", "x-halal-boundary", weight=0.4, confidence="medium",
  note="The kapitan system made the communities legally and residentially distinct, which is part "
       "of why Penang produced parallel named lineages rather than a melting pot.",
  sources=["wiki-kapitan-keling-mosque"])


# ================================== COMPONENTS -> CONTRIBUTING CULTURES
for n, c, conf, w in [
    ("n-yellow-alkaline", "c-hokkien", "high", 0.9),
    ("n-tai-lok-mee", "c-hokkien", "high", 0.8),
    ("n-koay-teow", "c-teochew", "high", 0.85),
    ("n-koay-teow", "c-cantonese", "high", 0.6),
    ("n-bee-hoon", "c-hokkien", "high", 0.85),
    ("n-bee-hoon", "c-henghua", "medium", 0.5),
    ("n-mee-sua", "c-hokkien", "high", 0.8),
    ("n-mee-sua", "c-foochow", "high", 0.8),
    ("n-mee-kia-youmian", "c-cantonese", "high", 0.85),
    ("n-mee-pok", "c-teochew", "high", 0.85),
    ("n-yi-mein", "c-cantonese", "high", 0.85),
    ("n-pan-mee-dough", "c-hakka", "high", 0.8),
    ("n-pan-mee-dough", "c-hokkien", "medium", 0.5),
    ("n-ccf-sheet", "c-cantonese", "high", 0.85),
    ("n-koay-chiap-sheet", "c-teochew", "high", 0.85),
    ("n-lo-shi-fun", "c-cantonese", "medium", 0.6),
    ("n-lo-shi-fun", "c-hakka", "medium", 0.6),
    ("n-fish-noodle", "c-foochow", "medium", 0.8),
    ("n-laksa-noodle", "c-malay-kedah", "medium", 0.6),
    ("n-idiyappam", "c-tamil-hindu", "high", 0.8),
    ("n-thai-sen-range", "c-teochew", "high", 0.6),
]:
    E("contributed_by", n, c, weight=w, confidence=conf)

E("contributed_by", "n-maggi-block", "c-british-colonial", weight=0.3, confidence="low",
  note="Not colonial at all, strictly - Swiss brand, Nestle ownership, 1971 Malaysian launch. "
       "Linked here only to mark it as an industrial rather than a community contribution.",
  sources=["nestle-maggi-malaysia"])

for i, c, conf, w in [
    ("i-belacan", "c-malay-kedah", "high", 0.9),
    ("i-hae-ko", "c-peranakan-penang", "high", 0.7),
    ("i-hae-ko", "c-javanese", "medium", 0.5),
    ("i-sambal", "c-malay-kedah", "high", 0.85),
    ("i-santan", "c-malay-kedah", "high", 0.85),
    ("i-asam-jawa", "c-malay-kedah", "high", 0.85),
    ("i-asam-gelugur", "c-malay-kedah", "high", 0.85),
    ("i-bunga-kantan", "c-malay-kedah", "high", 0.8),
    ("i-bunga-kantan", "c-siamese-my", "medium", 0.5),
    ("i-daun-kesum", "c-malay-kedah", "high", 0.8),
    ("i-curry-powder", "c-tamil-muslim", "high", 0.7),
    ("i-curry-powder", "c-british-colonial", "high", 0.8),
    ("i-curry-leaf", "c-tamil-hindu", "medium", 0.7),
    ("i-taucu", "c-hokkien", "high", 0.6),
    ("i-taucu", "c-javanese", "high", 0.7),
    ("i-sweet-potato", "c-javanese", "medium", 0.6),
    ("i-peanut", "c-javanese", "high", 0.7),
    ("i-kicap-manis", "c-javanese", "medium", 0.6),
    ("i-dark-soy", "c-cantonese", "medium", 0.6),
    ("i-tomato-ketchup", "c-british-colonial", "high", 0.7),
    ("i-lard", "c-hokkien", "high", 0.6),
    ("i-lard", "c-hakka", "high", 0.6),
    ("i-pork-blood", "c-hokkien", "medium", 0.6),
    ("i-cockles", "c-teochew", "medium", 0.6),
    ("i-prawn-heads", "c-hokkien", "high", 0.85),
    ("i-ti-poh", "c-cantonese", "medium", 0.6),
    ("i-ti-poh", "c-teochew", "medium", 0.6),
    ("i-ikan-bilis", "c-malay-kedah", "high", 0.8),
    ("i-ikan-kembung", "c-malay-kedah", "high", 0.8),
    ("i-kangkung", "c-malay-kedah", "high", 0.7),
    ("i-char-siu", "c-cantonese", "high", 0.85),
    ("i-five-spice", "c-hokkien", "high", 0.7),
    ("i-sweet-spice-quartet", "c-arab-hadhrami", "medium", 0.7),
    ("i-sweet-spice-quartet", "c-jawi-peranakan", "medium", 0.6),
    ("i-black-vinegar", "c-teochew", "high", 0.7),
    ("i-calamansi", "c-malay-kedah", "medium", 0.6),
    ("i-sayur-manis", "c-hakka", "medium", 0.6),
    ("i-ghee", "c-jawi-peranakan", "medium", 0.7),
    ("i-nut-thickeners", "c-jawi-peranakan", "low", 0.6),
    ("i-red-rice-wine", "c-foochow", "high", 0.9),
    ("i-evaporated-milk", "c-british-colonial", "medium", 0.6),
    ("i-thai-blood", "c-siamese-my", "high", 0.7),
    ("i-lihing", "c-kadazan-dusun", "medium", 0.8),
    ("i-gau-wong", "c-cantonese", "high", 0.7),
    ("i-ground-dried-shrimp", "c-peranakan-malacca", "medium", 0.6),
    ("i-sotong", "c-tamil-muslim", "medium", 0.5),
    ("i-duck-egg", "c-teochew", "medium", 0.5),
]:
    E("contributed_by", i, c, weight=w, confidence=conf)

for t, c, conf, w in [
    ("t-rempah", "c-malay-kedah", "high", 0.85),
    ("t-rempah", "c-peranakan-penang", "high", 0.8),
    ("t-lou-braise", "c-teochew", "high", 0.8),
    ("t-lou-braise", "c-hokkien", "high", 0.7),
    ("t-wok-hei", "c-cantonese", "high", 0.7),
    ("t-wok-hei", "c-hokkien", "high", 0.6),
    ("t-kon-lo", "c-cantonese", "high", 0.6),
    ("t-kon-lo", "c-hakka", "high", 0.7),
    ("t-alkaline-noodle", "c-hokkien", "high", 0.8),
    ("t-fry-then-rehydrate", "c-cantonese", "high", 0.7),
    ("t-starch-gravy", "c-hokkien", "high", 0.7),
    ("t-hand-tearing", "c-hokkien", "high", 0.7),
    ("t-clear-broth", "c-teochew", "high", 0.9),
    ("t-egg-ribbon", "c-cantonese", "high", 0.85),
    ("t-kandar-pole", "c-tamil-muslim", "high", 0.85),
    ("t-mixed-noodle", "c-hokkien", "medium", 0.6),
    ("t-halal-substitution", "c-tamil-muslim", "high", 0.85),
    ("t-sambal-on-side", "c-peranakan-penang", "medium", 0.6),
]:
    E("contributed_by", t, c, weight=w, confidence=conf)

E("contributed_by", "t-halal-substitution", "c-malay-kedah", weight=0.6, confidence="high")


# ============================================= DISHES: ORIGIN AND CARRIER
def origin(dish, region, culture=None, w=0.8, conf="high", note=None, sources=None):
    E("originates_in", dish, region, weight=w, confidence=conf, note=note, sources=sources)
    if culture:
        E("carried_by", dish, culture, weight=w, confidence=conf, sources=sources)


origin("d-hokkien-mee-penang", "r-xiamen", "c-hokkien", note="Via the surviving Xiamen prawn "
       "noodle, carried by Fujian labour migration roughly 1830s-1930s.",
       sources=["johorkaki-hokkien-mee"])
E("originates_in", "d-hokkien-mee-penang", "r-george-town", weight=0.9, confidence="high",
  note="The dish as eaten is Penang's, not Xiamen's: kangkung and cooked-in sambal belacan are "
       "local.", sources=["johorkaki-hokkien-mee"])
origin("d-char-kway-teow", "r-chaoshan", "c-teochew", conf="medium",
       note="Chaozhou is the presumed point of origin; the invention event is undocumented.",
       sources=["michelin-ckt"])
E("originates_in", "d-char-kway-teow", "r-george-town", weight=0.8, confidence="medium")
E("carried_by", "d-char-kway-teow", "c-hokkien", weight=0.5, confidence="medium",
  note="19th-century accounts describe both Hokkien and Teochew dockworkers, fishermen and "
       "cockle-gatherers hawking in the evening. The name is Hokkien.",
  sources=["cj-my-ckt-origins"])
origin("d-koay-teow-thng", "r-chaoshan", "c-teochew", sources=["penang-wikia-kuey-teow-thng"])
origin("d-lor-mee-penang", "r-zhangzhou", "c-hokkien", conf="medium",
       note="Repeated across sources; no primary Chinese-language documentation surfaced.",
       sources=["wiki-lor-mee"])
E("carried_by", "d-lor-mee-penang", "c-hainanese", weight=0.35, confidence="low",
  note="Malay Mail describes Penang lor mee as formed under Hokkien AND Hainanese influence. Food "
       "journalism, not scholarship.", sources=["johorkaki-hokkien-mee"])
origin("d-lam-mee", "r-george-town", "c-peranakan-penang", conf="medium",
       note="A Penang and northern-Malaysian dish; it does not exist as a named hawker item in "
            "Singapore or KL in the same way.", sources=["foodpanda-lam-mee"])
E("carried_by", "d-lam-mee", "c-hokkien", weight=0.6, confidence="medium",
  note="Hokkien base, Nyonya adjustment.")
origin("d-wantan-mee", "r-guangzhou", "c-cantonese", sources=["wiki-wonton-noodles"])
origin("d-curry-mee-penang", "r-george-town", "c-peranakan-penang", conf="medium",
       note="Culinary architecture unambiguously Peranakan; no specific household invention "
            "claim survives.", sources=["wiki-laksa", "penang-wikia-white-curry"])
E("carried_by", "d-curry-mee-penang", "c-hokkien", weight=0.6, confidence="medium")
E("attributed_to", "d-curry-mee-penang", "c-hainanese", weight=0.3, confidence="low",
  note="Widely asserted, demonstrated nowhere for Penang curry mee specifically. The mechanism is "
       "documented only for Singapore's Katong laksa.", sources=["johorkaki-katong-laksa"])
E("attributed_to", "d-curry-mee-penang", "c-tamil-muslim", weight=0.5, confidence="medium",
  note="Not as cooks but as suppliers: the Chulia Street spice trade is what made the curry "
       "component purchasable.", sources=["oed-curry"])
origin("d-mee-suah-koh", "r-quanzhou", "c-hokkien", sources=["carryitlikeharry-misua"])
origin("d-jawa-mee", "r-george-town", conf="low",
       note="Origin genuinely unclear. Three accounts: Chinese-Javanese Peranakans from Medan and "
            "Malacca; direct Javanese or Minangkabau settlers; or a local Penang Chinese invention "
            "wearing an exotic name.", sources=["malaymail-mee-jawa"])
E("attributed_to", "d-jawa-mee", "c-javanese", weight=0.6, confidence="low",
  sources=["malaymail-mee-jawa", "nlb-mee-jawa"])
E("attributed_to", "d-jawa-mee", "c-peranakan-penang", weight=0.5, confidence="low",
  note="The 'Jawa Peranakan' - Chinese-Javanese - account.", sources=["malaymail-mee-jawa"])
E("attributed_to", "d-jawa-mee", "c-minangkabau", weight=0.3, confidence="low",
  sources=["malaymail-mee-jawa"])
E("carried_by", "d-jawa-mee", "c-hokkien", weight=0.6, confidence="medium",
  note="Whoever brought it, in Penang it is cooked by Chinese hawkers, on pork or prawn stock, "
       "and without taucu.", sources=["nlb-mee-jawa"])
origin("d-mee-rebus", "r-java-central", "c-javanese", w=0.55, conf="low",
       note="NLB notes the Javanese derivation is often asserted 'although the latter dish bears "
            "little resemblance to mee rebus in its current form'.", sources=["nlb-mee-rebus"])
E("attributed_to", "d-mee-rebus", "c-tamil-muslim", weight=0.85, confidence="medium",
  note="NLB's opening line commits to this: mee rebus 'was originally peddled by Indian Muslim "
       "immigrants', working from a kandar pole and carrying it south from the northern states. "
       "The strongest single attribution.", sources=["nlb-mee-rebus"])
E("attributed_to", "d-mee-rebus", "c-malay-kedah", weight=0.6, confidence="medium")
E("originates_in", "d-mee-rebus", "r-singapore", weight=0.4, confidence="medium",
  note="Khir Johari holds it was created in Singapore before WWII.",
  sources=["khir-johari-malay-food"])
origin("d-lemak-laksa", "r-george-town", "c-peranakan-penang", conf="medium",
       sources=["wiki-laksa"])
origin("d-kolo-mee", "r-kuching", "c-hakka", conf="medium",
       note="Via Dabu, Meizhou, with Kiew Shao Nyap of Baihou as credited pioneer, Kuching 1920s.",
       sources=["medium-kolo-mee", "wiki-kolo-mee"])
E("attributed_to", "d-kolo-mee", "c-foochow", weight=0.2, confidence="low",
  note="Rejected. Sources assigning kolo mee to the Foochow are conflating Kuching with Sibu; the "
       "Foochow noodle is kampua mee.", sources=["borneo-post-sarawak-mee"])
origin("d-pan-mee", "r-kuala-lumpur", "c-hakka", conf="high",
       note="Hakka parent tradition, but the dish as sold - anchovy stock, three noodle forms at "
            "one stall - is Malaysian and Klang-Valley-centred.", sources=["wiki-banmian"])
E("carried_by", "d-pan-mee", "c-hokkien", weight=0.5, confidence="high",
  note="The hand-tearing mee hoon kueh line.", sources=["wiki-banmian"])
origin("d-asam-laksa", "r-george-town", "c-peranakan-penang", conf="medium",
       sources=["hutton-nyonya", "wiki-laksa"])
E("originates_in", "d-asam-laksa", "r-kedah", weight=0.6, confidence="disputed",
  note="Direction of travel unresolved. Penang was Kedah until 1786 and the island's Malay "
       "substrate is Kedahan, so a Peranakan elaboration of an existing Kedah sour fish laksa is "
       "at least as plausible as the reverse.", sources=["wiki-laksa", "ummi-laksa-guide"])
E("carried_by", "d-asam-laksa", "c-malay-kedah", weight=0.6, confidence="medium")
E("influenced_by", "d-asam-laksa", "d-mi-kathi", weight=0.2, confidence="low",
  note="Only in the loose sense that Penang Nyonya cooks worked in a shared northern-peninsula "
       "sour-hot idiom. No direct link is claimed.", sources=["hutton-nyonya"])
origin("d-white-curry-mee", "r-george-town", "c-peranakan-penang", conf="low",
       note="A real Penang serving convention, named and globalised much later.",
       sources=["penang-wikia-white-curry"])
origin("d-mee-goreng-mamak", "r-george-town", "c-tamil-muslim", conf="medium",
       note="Penang credited as origin, early 1900s; widely stated, archivally undemonstrated.",
       sources=["wiki-mee-goreng-mamak"])
origin("d-maggi-goreng", "r-george-town", "c-tamil-muslim", conf="medium",
       note="Cannot predate 1971.", sources=["nestle-maggi-malaysia"])
origin("d-char-bee-hoon", "r-xiamen", "c-hokkien", sources=["wiki-penang-cuisine"])
origin("d-koay-chiap", "r-chaoshan", "c-teochew", sources=["wiki-kway-chap"])
origin("d-bak-chor-mee", "r-singapore", "c-teochew", conf="medium",
       note="Chaoshan template, Singapore creation. Chen Lianfu actually came from Zhao'an in "
            "Fujian and learned the trade in Chaozhou - the dish sits on the Hokkien/Teochew "
            "boundary.", sources=["johorkaki-bcm"])
E("originates_in", "d-bak-chor-mee", "r-zhao-an", weight=0.5, confidence="medium",
  sources=["johorkaki-bcm"])
origin("d-duck-koay-teow", "r-chaoshan", "c-teochew", sources=["lum-lai-duck"])
E("originates_in", "d-duck-koay-teow", "r-george-town", weight=0.7, confidence="high",
  note="Kimberley Street - Swatow Kay - is the historical anchor, and the Penang habit of keeping "
       "the soup clear while braising the meat dark is local.",
  sources=["johorkaki-bcm", "lum-lai-duck"])
origin("d-beef-noodles-my", "r-kuala-lumpur", conf="disputed",
       note="A 1930s-40s Malayan hawker development, made by Hainanese AND Hakka hawkers. The "
            "'came from Hainan Island' line is not evidenced.",
       sources=["soong-kee", "yean-kee-kluang"])
E("attributed_to", "d-beef-noodles-my", "c-hainanese", weight=0.5, confidence="disputed",
  sources=["yean-kee-kluang"])
E("attributed_to", "d-beef-noodles-my", "c-hakka", weight=0.5, confidence="disputed",
  sources=["soong-kee"])
origin("d-fish-head-bee-hoon", "r-singapore", "c-teochew", conf="medium",
       sources=["wiki-fish-soup-bee-hoon"])
origin("d-chee-cheong-fun", "r-guangzhou", "c-cantonese", sources=["wiki-chee-cheong-fun"])
E("originates_in", "d-chee-cheong-fun", "r-george-town", weight=0.7, confidence="high",
  note="The hae ko and thnee cheo dressing is Penang-specific and entirely non-Cantonese.",
  sources=["penang-wikia-ccf"])
origin("d-mee-soto", "r-java-east", "c-javanese", sources=["wiki-mee-soto"])
origin("d-yi-mein", "r-guangzhou", "c-cantonese", conf="medium", sources=["wiki-yi-mein"])
E("originates_in", "d-yi-mein", "r-huizhou-gd", weight=0.6, confidence="medium",
  note="Yi Bingshou was prefect of Huizhou; his ancestral county was Ninghua in Fujian.",
  sources=["wiki-yi-mein"])
origin("d-ipoh-hor-fun", "r-ipoh-kinta", "c-cantonese", conf="medium",
       sources=["ipoh-echo-kai-si-hor-fun"])
E("carried_by", "d-ipoh-hor-fun", "c-hokkien", weight=0.6, confidence="medium",
  note="The two most celebrated stalls were founded by Hokkiens from Nan'an - which is why the "
       "broth combines chicken and prawn, in the Hokkien manner.",
  sources=["ipoh-echo-kai-si-hor-fun"])
origin("d-thai-boat-noodles", "r-rangsit", "c-teochew", conf="medium",
       sources=["wiki-boat-noodles"])
origin("d-tom-yum-mee", "r-patani", "c-siamese-my", conf="medium", sources=["wiki-boat-noodles"])
E("originates_in", "d-tom-yum-mee", "r-seberang-perai", weight=0.6, confidence="medium",
  note="Raja Uda and Butterworth are a recognised Penang cluster, and the thick red chilli-paste "
       "style is a local development.", sources=["michelin-ckt"])
origin("d-sarawak-laksa", "r-kuching", "c-teochew", conf="medium",
       note="Goh Lik Teck, Teochew, Carpenter Street, 1940s - single-sourced to a 2015 state "
            "tourism guide chapter that does not describe the dish.",
       sources=["johorkaki-sarawak-laksa", "ong-flavours-of-sarawak"])
E("attributed_to", "d-sarawak-laksa", "c-foochow", weight=0.2, confidence="low",
  note="Rejected - the same Kuching/Sibu conflation that afflicts kolo mee.",
  sources=["borneo-post-sarawak-mee"])
origin("d-bihun-goreng", "r-george-town", "c-tamil-muslim", conf="medium")
E("carried_by", "d-bihun-goreng", "c-malay-kedah", weight=0.7, confidence="high")
origin("d-chilli-pan-mee", "r-kuala-lumpur", "c-hakka", conf="medium",
       note="Kin Kin, 1985, Chow Kit - a documented 1980s KL invention on a Hakka substrate, NOT "
            "a traditional Hakka dish.", sources=["kin-kin", "rakyat-post-kin-kin"])
origin("d-longevity-mee-sua", "r-quanzhou", "c-hokkien", sources=["carryitlikeharry-misua"])
E("carried_by", "d-longevity-mee-sua", "c-foochow", weight=0.7, confidence="high",
  sources=["danielfooddiary-foochow"])
origin("d-hokkien-char-penang", "r-george-town", "c-hokkien",
       sources=["johorkaki-kl-sg-hokkien"])
origin("d-mee-sotong", "r-george-town", "c-tamil-muslim", conf="medium", sources=["hameed-pata"])
origin("d-mee-udang", "r-penang-island", "c-malay-kedah", conf="medium",
       sources=["penang-traveltips-mee-udang"])
origin("d-mee-siam", "r-george-town", "c-peranakan-penang", conf="disputed",
       note="Four named disputants: Hutton (Penang), Sylvia Tan (Malay), Tan Chee-Beng (wholly "
            "Peranakan), Chua Beng Huat (the question is malformed).",
       sources=["wiki-mee-siam", "hutton-nyonya"])
E("attributed_to", "d-mee-siam", "c-malay-kedah", weight=0.5, confidence="disputed",
  sources=["wiki-mee-siam"])
E("attributed_to", "d-mee-siam", "c-siamese-my", weight=0.25, confidence="low",
  note="The name references Thai flavour or a Thai-imported noodle, not Thai provenance - there "
       "is no such dish in Thailand.", sources=["nlb-mee-siam"])
origin("d-char-koay-kak", "r-chaoshan", "c-teochew", conf="medium",
       sources=["visitpenang-char-koay-kak"])
origin("d-mee-hailam", "r-george-town", "c-hainanese", conf="high",
       note="A Malayan invention by Hainanese cooks, not a transplant from Hainan.",
       sources=["tasteasianfood-mee-hailam"])
origin("d-wat-tan-hor", "r-guangzhou", "c-cantonese", sources=["wiki-penang-cuisine"])
origin("d-hakka-mee", "r-meizhou-dabu", "c-hakka", conf="medium", sources=["michelin-hakka-kl"])
origin("d-mee-hoon-kueh", "r-kuala-lumpur", "c-hokkien", sources=["wiki-banmian"])
origin("d-pasembur-mee-rojak", "r-george-town", "c-tamil-muslim", conf="disputed",
       sources=["wiki-pasembur"])
origin("d-you-mee", "r-kuala-lumpur", "c-cantonese", conf="medium",
       note="Not a dish - a noodle option on a pan mee board.", sources=["wiki-banmian"])

# ancestors and cousins
origin("d-xiamen-prawn-noodle", "r-xiamen", "c-hokkien", sources=["johorkaki-hokkien-mee"])
origin("d-quanzhou-mian-xian-hu", "r-quanzhou", "c-hokkien", sources=["carryitlikeharry-misua"])
origin("d-zhangzhou-lor-mian", "r-zhangzhou", "c-hokkien", conf="medium", sources=["wiki-lor-mee"])
origin("d-guangzhou-wonton-noodle", "r-guangzhou", "c-cantonese", sources=["wiki-wonton-noodles"])
origin("d-chaoshan-kway-teow-soup", "r-chaoshan", "c-teochew", sources=["ccs-city-teochew"])
origin("d-chaoshan-kway-chap", "r-chaoshan", "c-teochew", sources=["wiki-kway-chap"])
origin("d-chaoshan-gan-mian", "r-chaoshan", "c-teochew", conf="medium", sources=["johorkaki-bcm"])
origin("d-dabu-yan-mee", "r-meizhou-dabu", "c-hakka", conf="medium", sources=["medium-kolo-mee"])
origin("d-lanzhou-beef-noodle", "r-lanzhou", w=0.95, sources=["wiki-lanzhou-beef-noodle"])
origin("d-taiwan-beef-noodle", "r-taiwan", sources=["wiki-taiwanese-beef-noodle"])
origin("d-kl-hokkien-mee", "r-kuala-lumpur", "c-hokkien", conf="medium", sources=["kim-lian-kee"])
E("originates_in", "d-kl-hokkien-mee", "r-anxi", weight=0.5, confidence="medium",
  sources=["kim-lian-kee"])
origin("d-singapore-hokkien-mee", "r-singapore", "c-hokkien", conf="medium",
       sources=["johorkaki-kl-sg-hokkien"])
origin("d-singapore-lor-mee", "r-singapore", "c-hokkien", sources=["wiki-lor-mee"])
origin("d-hu-tieu-nam-vang", "r-phnom-penh", "c-teochew", sources=["penang-wikia-kuey-teow-thng"])
origin("d-thai-bamee-ped", "r-bangkok", "c-teochew", sources=["wiki-boat-noodles"])
origin("d-mie-jawa-indonesia", "r-java-central", "c-javanese", sources=["nlb-mee-jawa"])
origin("d-soto-ayam", "r-java-east", "c-javanese", sources=["wiki-mee-soto"])
origin("d-saoto-suriname", "r-suriname", "c-javanese", conf="medium", sources=["wiki-mee-soto"])
origin("d-mi-kathi", "r-patani", "c-siamese-my", conf="medium", sources=["wiki-mee-siam"])
origin("d-singapore-noodles-hk", "r-hong-kong", "c-cantonese", sources=["wiki-singapore-noodles"])
origin("d-kampua-mee", "r-sibu", "c-foochow", conf="medium", sources=["borneo-post-sarawak-mee"])
origin("d-sang-nyuk-mee", "r-tawau", "c-hakka", conf="medium", sources=["wiki-sang-nyuk-mee"])
origin("d-tuaran-mee", "r-tuaran", "c-hakka", conf="medium", sources=["wiki-tuaran-mee"])
origin("d-laksa-kedah", "r-kedah", "c-malay-kedah", sources=["wiki-laksa"])
origin("d-curry-laksa-kl", "r-kuala-lumpur", "c-peranakan-malacca", conf="low",
       note="Carrier attribution is weak: the coconut-laksa architecture is Peranakan, but the "
            "Klang Valley bowl is a multi-community hawker dish with no single kitchen behind it.",
       sources=["wiki-laksa"])
origin("d-katong-laksa", "r-singapore", "c-peranakan-malacca", conf="medium",
       sources=["johorkaki-katong-laksa"])
E("carried_by", "d-katong-laksa", "c-hainanese", weight=0.7, confidence="medium",
  note="Peranakan recipe, Hainanese hawker - the transmission, not the invention.",
  sources=["johorkaki-katong-laksa"])
origin("d-johor-laksa", "r-johor", "c-malay-kedah", conf="medium", sources=["wiki-laksa"])
origin("d-mee-bandung", "r-johor", "c-malay-kedah", conf="medium", sources=["nlb-mee-rebus"])
origin("d-heng-hwa-bee-hoon", "r-putian", "c-henghua", conf="medium", sources=["kuchler-1965"])
origin("d-fuzhou-red-wine-mee-sua", "r-fuzhou", "c-foochow", sources=["danielfooddiary-foochow"])
origin("d-mohinga", "r-george-town", "c-burmese-penang", conf="low",
       note="Present in Penang through the Burmese community; no link to any Penang dish is "
            "claimed.", sources=["malaymail-beyond-hokkien"])


# ============================================================ DISH -> NOODLE
for d, ns in [
    ("d-hokkien-mee-penang", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-char-kway-teow", ["n-koay-teow", "n-lo-shi-fun"]),
    ("d-koay-teow-thng", ["n-koay-teow", "n-bee-hoon"]),
    ("d-lor-mee-penang", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-lam-mee", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-wantan-mee", ["n-mee-kia-youmian"]),
    ("d-curry-mee-penang", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-mee-suah-koh", ["n-mee-sua"]),
    ("d-jawa-mee", ["n-yellow-alkaline"]),
    ("d-mee-rebus", ["n-yellow-alkaline"]),
    ("d-lemak-laksa", ["n-laksa-noodle"]),
    ("d-kolo-mee", ["n-mee-kia-youmian"]),
    ("d-pan-mee", ["n-pan-mee-dough"]),
    ("d-mee-hoon-kueh", ["n-pan-mee-dough"]),
    ("d-asam-laksa", ["n-laksa-noodle"]),
    ("d-white-curry-mee", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-mee-goreng-mamak", ["n-yellow-alkaline"]),
    ("d-maggi-goreng", ["n-maggi-block"]),
    ("d-char-bee-hoon", ["n-bee-hoon"]),
    ("d-koay-chiap", ["n-koay-chiap-sheet"]),
    ("d-bak-chor-mee", ["n-mee-pok", "n-mee-kia-youmian"]),
    ("d-duck-koay-teow", ["n-koay-teow"]),
    ("d-beef-noodles-my", ["n-yellow-alkaline", "n-koay-teow", "n-bee-hoon"]),
    ("d-fish-head-bee-hoon", ["n-bee-hoon", "n-yi-mein"]),
    ("d-chee-cheong-fun", ["n-ccf-sheet"]),
    ("d-mee-soto", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-you-mee", ["n-mee-kia-youmian", "n-pan-mee-dough"]),
    ("d-yi-mein", ["n-yi-mein"]),
    ("d-ipoh-hor-fun", ["n-koay-teow"]),
    ("d-thai-boat-noodles", ["n-thai-sen-range"]),
    ("d-tom-yum-mee", ["n-bee-hoon", "n-yellow-alkaline"]),
    ("d-sarawak-laksa", ["n-bee-hoon"]),
    ("d-bihun-goreng", ["n-bee-hoon"]),
    ("d-chilli-pan-mee", ["n-pan-mee-dough"]),
    ("d-longevity-mee-sua", ["n-mee-sua"]),
    ("d-hokkien-char-penang", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-mee-sotong", ["n-yellow-alkaline"]),
    ("d-mee-udang", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-mee-siam", ["n-bee-hoon"]),
    ("d-mee-hailam", ["n-yellow-alkaline"]),
    ("d-wat-tan-hor", ["n-koay-teow", "n-yi-mein"]),
    ("d-hakka-mee", ["n-mee-kia-youmian"]),
    ("d-pasembur-mee-rojak", ["n-yellow-alkaline"]),
    ("d-xiamen-prawn-noodle", ["n-yellow-alkaline"]),
    ("d-quanzhou-mian-xian-hu", ["n-mee-sua"]),
    ("d-zhangzhou-lor-mian", ["n-yellow-alkaline"]),
    ("d-guangzhou-wonton-noodle", ["n-mee-kia-youmian"]),
    ("d-chaoshan-kway-teow-soup", ["n-koay-teow"]),
    ("d-chaoshan-kway-chap", ["n-koay-chiap-sheet"]),
    ("d-chaoshan-gan-mian", ["n-mee-pok"]),
    ("d-dabu-yan-mee", ["n-mee-kia-youmian"]),
    ("d-lanzhou-beef-noodle", ["n-yellow-alkaline"]),
    ("d-taiwan-beef-noodle", ["n-yellow-alkaline"]),
    ("d-kl-hokkien-mee", ["n-tai-lok-mee"]),
    ("d-singapore-hokkien-mee", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-singapore-lor-mee", ["n-yellow-alkaline"]),
    ("d-hu-tieu-nam-vang", ["n-koay-teow"]),
    ("d-thai-bamee-ped", ["n-thai-sen-range"]),
    ("d-mie-jawa-indonesia", ["n-yellow-alkaline"]),
    ("d-soto-ayam", ["n-bee-hoon"]),
    ("d-saoto-suriname", ["n-bee-hoon"]),
    ("d-mi-kathi", ["n-bee-hoon"]),
    ("d-singapore-noodles-hk", ["n-bee-hoon"]),
    ("d-kampua-mee", ["n-mee-kia-youmian"]),
    ("d-sang-nyuk-mee", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-tuaran-mee", ["n-yi-mein", "n-mee-kia-youmian"]),
    ("d-laksa-kedah", ["n-laksa-noodle"]),
    ("d-curry-laksa-kl", ["n-yellow-alkaline", "n-bee-hoon"]),
    ("d-katong-laksa", ["n-laksa-noodle"]),
    ("d-johor-laksa", ["n-laksa-noodle"]),
    ("d-mee-bandung", ["n-yellow-alkaline"]),
    ("d-heng-hwa-bee-hoon", ["n-bee-hoon"]),
    ("d-fuzhou-red-wine-mee-sua", ["n-mee-sua"]),
    ("d-mohinga", ["n-bee-hoon"]),
]:
    for i, n in enumerate(ns):
        E("uses_noodle", d, n, weight=0.9 if i == 0 else 0.5, confidence="high")

E("uses_noodle", "d-char-koay-kak", "n-koay-teow", weight=0.4, confidence="medium",
  note="Strictly a different cut of the same steamed rice cake - cubes rather than ribbons. Same "
       "粿 technology, different geometry.", sources=["visitpenang-char-koay-kak"])
E("uses_noodle", "d-char-kway-teow", "n-tapioca-wartime", weight=0.2, confidence="medium",
  note="Occupation-era only, and in Singapore: tapioca noodles fried in red palm oil.",
  sources=["nlb-ckt"])
E("uses_noodle", "d-mee-soto", "n-idiyappam", weight=0.1, confidence="low",
  note="Not the noodle, but the adjacency worth noting: in Malaysia mee soto is often served over "
       "lontong or nasi impit instead, which is the more purely Javanese configuration.",
  sources=["wiki-mee-soto"])


# ======================================================= DISH -> INGREDIENT
for d, ings in [
    ("d-hokkien-mee-penang", ["i-prawn-heads", "i-sambal", "i-belacan", "i-kangkung", "i-lard"]),
    ("d-char-kway-teow", ["i-lard", "i-cockles", "i-duck-egg", "i-dark-soy", "i-belacan"]),
    ("d-koay-teow-thng", ["i-ti-poh", "i-lard"]),
    ("d-lor-mee-penang", ["i-five-spice", "i-prawn-heads", "i-black-vinegar"]),
    ("d-lam-mee", ["i-prawn-heads", "i-sambal", "i-belacan", "i-calamansi"]),
    ("d-wantan-mee", ["i-char-siu", "i-dark-soy", "i-lard", "i-ti-poh"]),
    ("d-curry-mee-penang", ["i-curry-powder", "i-santan", "i-pork-blood", "i-cockles",
                            "i-sambal", "i-prawn-heads", "i-daun-kesum"]),
    ("d-white-curry-mee", ["i-curry-powder", "i-santan", "i-sambal"]),
    ("d-mee-suah-koh", ["i-five-spice"]),
    ("d-jawa-mee", ["i-sweet-potato", "i-peanut", "i-sambal", "i-calamansi"]),
    ("d-mee-rebus", ["i-sweet-potato", "i-peanut", "i-taucu", "i-curry-powder", "i-calamansi"]),
    ("d-lemak-laksa", ["i-santan", "i-belacan", "i-daun-kesum", "i-sambal"]),
    ("d-kolo-mee", ["i-lard", "i-char-siu", "i-dark-soy"]),
    ("d-pan-mee", ["i-ikan-bilis", "i-sayur-manis", "i-sambal"]),
    ("d-mee-hoon-kueh", ["i-ikan-bilis"]),
    ("d-asam-laksa", ["i-ikan-kembung", "i-asam-jawa", "i-asam-gelugur", "i-bunga-kantan",
                      "i-daun-kesum", "i-hae-ko", "i-belacan", "i-pineapple"]),
    ("d-mee-goreng-mamak", ["i-tomato-ketchup", "i-kicap-manis", "i-calamansi", "i-curry-leaf",
                            "i-sotong"]),
    ("d-maggi-goreng", ["i-tomato-ketchup", "i-calamansi"]),
    ("d-char-bee-hoon", ["i-dark-soy"]),
    ("d-koay-chiap", ["i-five-spice", "i-kiam-chai"]),
    ("d-bak-chor-mee", ["i-black-vinegar", "i-lard", "i-fish-sauce"]),
    ("d-duck-koay-teow", ["i-ti-poh", "i-five-spice"]),
    ("d-beef-noodles-my", ["i-five-spice"]),
    ("d-fish-head-bee-hoon", ["i-evaporated-milk", "i-kiam-chai"]),
    ("d-chee-cheong-fun", ["i-hae-ko"]),
    ("d-mee-soto", ["i-calamansi"]),
    ("d-yi-mein", ["i-gau-wong", "i-shiitake"]),
    ("d-ipoh-hor-fun", ["i-prawn-heads"]),
    ("d-thai-boat-noodles", ["i-thai-blood", "i-fermented-beancurd", "i-five-spice"]),
    ("d-tom-yum-mee", ["i-bunga-kantan", "i-calamansi"]),
    ("d-sarawak-laksa", ["i-santan", "i-peanut", "i-belacan", "i-prawn-heads", "i-asam-jawa",
                         "i-sweet-spice-quartet"]),
    ("d-bihun-goreng", ["i-tomato-ketchup", "i-kicap-manis", "i-belacan"]),
    ("d-chilli-pan-mee", ["i-ikan-bilis"]),
    ("d-longevity-mee-sua", ["i-red-rice-wine", "i-gau-wong"]),
    ("d-hokkien-char-penang", ["i-dark-soy", "i-lard", "i-prawn-heads"]),
    ("d-mee-sotong", ["i-sotong", "i-tomato-ketchup", "i-sambal", "i-calamansi"]),
    ("d-mee-udang", ["i-tomato-ketchup", "i-asam-jawa"]),
    ("d-mee-siam", ["i-taucu", "i-asam-jawa", "i-belacan", "i-calamansi"]),
    ("d-mee-hailam", ["i-dark-soy", "i-calamansi"]),
    ("d-wat-tan-hor", ["i-dark-soy"]),
    ("d-hakka-mee", ["i-lard", "i-shiitake"]),
    ("d-pasembur-mee-rojak", ["i-sweet-potato", "i-peanut", "i-asam-jawa"]),
    ("d-xiamen-prawn-noodle", ["i-prawn-heads"]),
    ("d-katong-laksa", ["i-ground-dried-shrimp", "i-santan", "i-daun-kesum"]),
    ("d-curry-laksa-kl", ["i-santan", "i-cockles", "i-curry-powder"]),
    ("d-laksa-kedah", ["i-ikan-kembung", "i-asam-gelugur", "i-belacan"]),
    ("d-fuzhou-red-wine-mee-sua", ["i-red-rice-wine"]),
    ("d-tuaran-mee", ["i-char-siu", "i-lihing"]),
    ("d-sang-nyuk-mee", ["i-lard", "i-dark-soy"]),
    ("d-kl-hokkien-mee", ["i-dark-soy", "i-lard", "i-ti-poh", "i-belacan"]),
    ("d-singapore-lor-mee", ["i-black-vinegar", "i-five-spice"]),
    ("d-singapore-noodles-hk", ["i-curry-powder", "i-char-siu"]),
    ("d-mi-kathi", ["i-santan", "i-taucu", "i-asam-jawa"]),
    ("d-char-koay-kak", ["i-dark-soy"]),
    ("d-mohinga", ["i-asam-jawa"]),
]:
    for i, ing in enumerate(ings):
        E("uses_ingredient", d, ing, weight=0.85 if i < 3 else 0.5, confidence="high")


# ======================================================== DISH -> TECHNIQUE
for d, techs in [
    ("d-hokkien-mee-penang", ["t-prawn-head-dry-fry", "t-mixed-noodle"]),
    ("d-char-kway-teow", ["t-wok-hei"]),
    ("d-koay-teow-thng", ["t-clear-broth"]),
    ("d-lor-mee-penang", ["t-lou-braise", "t-starch-gravy", "t-mixed-noodle"]),
    ("d-lam-mee", ["t-clear-broth", "t-sambal-on-side"]),
    ("d-wantan-mee", ["t-kon-lo"]),
    ("d-curry-mee-penang", ["t-rempah", "t-sambal-on-side", "t-mixed-noodle"]),
    ("d-white-curry-mee", ["t-sambal-on-side"]),
    ("d-jawa-mee", ["t-sweet-potato-thickening"]),
    ("d-mee-rebus", ["t-sweet-potato-thickening", "t-kandar-pole"]),
    ("d-lemak-laksa", ["t-rempah"]),
    ("d-asam-laksa", ["t-rempah"]),
    ("d-kolo-mee", ["t-kon-lo"]),
    ("d-hakka-mee", ["t-kon-lo"]),
    ("d-bak-chor-mee", ["t-kon-lo", "t-kandar-pole"]),
    ("d-pan-mee", ["t-hand-tearing"]),
    ("d-mee-hoon-kueh", ["t-hand-tearing"]),
    ("d-mee-goreng-mamak", ["t-wok-hei", "t-halal-substitution"]),
    ("d-maggi-goreng", ["t-halal-substitution"]),
    ("d-bihun-goreng", ["t-halal-substitution"]),
    ("d-mee-sotong", ["t-wok-hei", "t-halal-substitution"]),
    ("d-char-bee-hoon", ["t-wok-hei"]),
    ("d-koay-chiap", ["t-lou-braise"]),
    ("d-duck-koay-teow", ["t-lou-braise", "t-clear-broth"]),
    ("d-yi-mein", ["t-fry-then-rehydrate"]),
    ("d-tuaran-mee", ["t-fry-then-rehydrate", "t-wok-hei"]),
    ("d-wat-tan-hor", ["t-egg-ribbon", "t-wok-hei", "t-starch-gravy"]),
    ("d-ipoh-hor-fun", ["t-clear-broth", "t-prawn-head-dry-fry"]),
    ("d-hokkien-char-penang", ["t-wok-hei", "t-mixed-noodle"]),
    ("d-kl-hokkien-mee", ["t-wok-hei", "t-lou-braise"]),
    ("d-sarawak-laksa", ["t-rempah"]),
    ("d-katong-laksa", ["t-rempah", "t-ground-dried-shrimp-thickening"]),
    ("d-thai-boat-noodles", ["t-blood-thickening", "t-lou-braise"]),
    ("d-singapore-lor-mee", ["t-lou-braise", "t-starch-gravy"]),
    ("d-mee-siam", ["t-rempah"]),
    ("d-mee-udang", ["t-sweet-potato-thickening"]),
    ("d-mee-bandung", ["t-sweet-potato-thickening"]),
    ("d-pasembur-mee-rojak", ["t-sweet-potato-thickening"]),
    ("d-fish-head-bee-hoon", ["t-clear-broth"]),
    ("d-longevity-mee-sua", ["t-clear-broth"]),
    ("d-sang-nyuk-mee", ["t-kon-lo", "t-clear-broth"]),
    ("d-chaoshan-kway-chap", ["t-lou-braise"]),
    ("d-lanzhou-beef-noodle", ["t-clear-broth", "t-halal-substitution"]),
]:
    for i, t in enumerate(techs):
        E("uses_technique", d, t, weight=0.8 if i == 0 else 0.5, confidence="high")

E("uses_technique", "d-char-kway-teow", "t-alkaline-noodle", weight=0.2, confidence="high",
  note="Not for its own noodle, which is rice - but Singapore's version mixes in yellow wheat "
       "noodle and Penang's does not, which is one of the cleanest markers between them.",
  sources=["michelin-ckt"])


# ================================================= DESCENT AND SIBLINGHOOD
E("derived_from", "d-hokkien-mee-penang", "d-xiamen-prawn-noodle", weight=0.9, confidence="high",
  note="Direct descent, with two documented substitutions: kangkung for coriander, and sambal "
       "belacan cooked into the stock in place of raw minced garlic.",
  sources=["johorkaki-hokkien-mee"])
E("derived_from", "d-mee-suah-koh", "d-quanzhou-mian-xian-hu", weight=0.9, confidence="medium",
  note="Almost unchanged, which is the interesting part: the least adaptable dish survived as a "
       "niche while its siblings creolised.", sources=["carryitlikeharry-misua"])
E("derived_from", "d-lor-mee-penang", "d-zhangzhou-lor-mian", weight=0.7, confidence="medium",
  sources=["wiki-lor-mee"])
E("derived_from", "d-singapore-lor-mee", "d-zhangzhou-lor-mian", weight=0.7, confidence="medium",
  sources=["wiki-lor-mee"])
E("derived_from", "d-lam-mee", "d-lor-mee-penang", weight=0.5, confidence="low",
  note="The account Penang cooks give: Baba-Nyonya descendants of Fujian immigrants adjusted an "
       "inherited lor mee until it branched off. It kept the structure - noodle, poured liquid, "
       "assembled toppings - and discarded the defining lor braise. Family-tradition history.",
  sources=["foodpanda-lam-mee"])
E("derived_from", "d-kl-hokkien-mee", "d-zhangzhou-lor-mian", weight=0.5, confidence="medium",
  note="The one specifically evidenced lor-mee-to-Hokkien-mee link: Ong Kim Lian started with a "
       "starchy Hokkien festival noodle soup and mutated it under competitive pressure.",
  sources=["kim-lian-kee"])
E("unevidenced_link", "d-hokkien-mee-penang", "d-zhangzhou-lor-mian", weight=0.2,
  confidence="low",
  note="Wikipedia asserts that ALL Hokkien mee variants descend from lor mee, without citation, "
       "and it conflates two different Fujianese traditions - a starchy braise and a prawn broth. "
       "This graph declines to draw the descent edge.", sources=["wiki-hokkien-mee"])
E("derived_from", "d-wantan-mee", "d-guangzhou-wonton-noodle", weight=0.85, confidence="high",
  note="With one large caveat: the Malaysian DRY dark-soy form has no Guangzhou antecedent and "
       "nobody has dated the divergence.", sources=["wiki-wonton-noodles"])
E("derived_from", "d-koay-teow-thng", "d-chaoshan-kway-teow-soup", weight=0.9, confidence="high")
E("derived_from", "d-char-kway-teow", "d-chaoshan-kway-teow-soup", weight=0.5, confidence="medium",
  note="The fried and boiled halves of one Teochew rice-noodle tradition, rather than one from "
       "the other.", sources=["michelin-ckt"])
E("derived_from", "d-koay-chiap", "d-chaoshan-kway-chap", weight=0.85, confidence="high",
  note="With two diaspora changes: pork becomes duck in Penang, and the ancestral WHITE rice-milk "
       "broth becomes a dark soy braise.", sources=["wiki-kway-chap", "roots-kway-chap"])
E("derived_from", "d-bak-chor-mee", "d-chaoshan-gan-mian", weight=0.8, confidence="medium",
  sources=["johorkaki-bcm"])
E("derived_from", "d-duck-koay-teow", "d-chaoshan-kway-teow-soup", weight=0.8, confidence="high")
E("derived_from", "d-kolo-mee", "d-dabu-yan-mee", weight=0.8, confidence="medium",
  sources=["medium-kolo-mee"])
E("derived_from", "d-hakka-mee", "d-dabu-yan-mee", weight=0.8, confidence="medium",
  sources=["michelin-hakka-kl"])
E("derived_from", "d-chilli-pan-mee", "d-pan-mee", weight=0.9, confidence="medium",
  note="Kin Kin, 1985. A documented invention, not a tradition.", sources=["kin-kin"])
E("derived_from", "d-maggi-goreng", "d-mee-goreng-mamak", weight=0.95, confidence="high",
  note="A substitution variant. Cannot predate 1971.", sources=["nestle-maggi-malaysia"])
E("derived_from", "d-mee-sotong", "d-mee-goreng-mamak", weight=0.8, confidence="medium",
  sources=["hameed-pata"])
E("derived_from", "d-bihun-goreng", "d-mee-goreng-mamak", weight=0.6, confidence="medium",
  note="Same seasoning logic, different starch - and in the Chinese case the descent runs the "
       "other way, from char bee hoon.", sources=["wiki-mee-goreng-mamak"])
E("derived_from", "d-mee-soto", "d-soto-ayam", weight=0.9, confidence="high",
  sources=["wiki-mee-soto"])
E("derived_from", "d-saoto-suriname", "d-soto-ayam", weight=0.9, confidence="medium",
  sources=["wiki-mee-soto"])
E("derived_from", "d-white-curry-mee", "d-curry-mee-penang", weight=0.85, confidence="medium",
  note="Or arguably not derived at all - sambal-on-the-side is the normal Penang convention, so "
       "'white curry mee' may just be a retrospective name for what Penang curry mee always was.",
  sources=["penang-wikia-white-curry"])
E("derived_from", "d-mee-hoon-kueh", "d-pan-mee", weight=0.5, confidence="high",
  note="Better modelled as two forming methods for one dough than as parent and child - the same "
       "stall sells both.", sources=["wiki-banmian"])
E("derived_from", "d-tuaran-mee", "d-pan-mee", weight=0.3, confidence="low",
  note="Not descent so much as replacement: Tuaran mee displaced knife-cut noodles in Sabah "
       "within living memory, shifting a Hakka hand-cut wheat tradition to a fried egg-noodle one.",
  sources=["wiki-tuaran-mee"])
E("derived_from", "d-katong-laksa", "d-lemak-laksa", weight=0.7, confidence="medium",
  sources=["johorkaki-katong-laksa"])
E("derived_from", "d-thai-bamee-ped", "d-chaoshan-kway-teow-soup", weight=0.6, confidence="high")
E("derived_from", "d-hu-tieu-nam-vang", "d-chaoshan-kway-teow-soup", weight=0.8, confidence="high")
E("derived_from", "d-thai-boat-noodles", "d-chaoshan-kway-teow-soup", weight=0.5, confidence="medium",
  sources=["wiki-boat-noodles"])
E("derived_from", "d-longevity-mee-sua", "d-quanzhou-mian-xian-hu", weight=0.4, confidence="medium",
  note="Shared noodle and region rather than descent - the ritual line and the porridge line are "
       "parallel uses of the same thread.", sources=["carryitlikeharry-misua"])
E("derived_from", "d-fuzhou-red-wine-mee-sua", "d-longevity-mee-sua", weight=0.5, confidence="high",
  note="The Foochow branch of the same ritual noodle.", sources=["danielfooddiary-foochow"])
E("derived_from", "d-char-koay-kak", "d-chaoshan-kway-teow-soup", weight=0.4, confidence="medium",
  note="Same steamed rice-cake technology, cut into cubes instead of ribbons.",
  sources=["visitpenang-char-koay-kak"])
E("derived_from", "d-ipoh-hor-fun", "d-chaoshan-kway-teow-soup", weight=0.3, confidence="low",
  note="Same noodle in a clear broth, but a different dialect group, a different stock philosophy "
       "and a different protein. Cousinhood at most.", sources=["ipoh-echo-kai-si-hor-fun"])
E("derived_from", "d-wat-tan-hor", "d-ipoh-hor-fun", weight=0.4, confidence="medium",
  note="Same noodle, fried with egg gravy instead of served in soup.")
E("influenced_by", "d-singapore-noodles-hk", "d-char-bee-hoon", weight=0.4, confidence="medium",
  note="A Hong Kong reworking of the fried-bee-hoon format with colonial curry powder added, then "
       "named after a city that does not eat it. Deliberately NOT a derived_from edge - the name "
       "asserts a descent that did not happen, which is the point of the node.",
  sources=["wiki-singapore-noodles"])

for a, b, note in [
    ("d-char-kway-teow", "d-koay-teow-thng",
     "The fried and the boiled halves of one Teochew rice-noodle tradition."),
    ("d-koay-chiap", "d-duck-koay-teow",
     "Same lou braise, different starch, different broth clarity - and in Penang the same duck."),
    ("d-curry-mee-penang", "d-lemak-laksa",
     "The same coconut-curry-noodle family, distinguished by regional convention, noodle choice "
     "and toppings rather than by any hard line."),
    ("d-curry-mee-penang", "d-curry-laksa-kl", "Regional siblings; the KL bowl is richer."),
    ("d-asam-laksa", "d-laksa-kedah", "Direction of travel unresolved. Model as siblings with the "
     "uncertainty encoded rather than picking a parent."),
    ("d-asam-laksa", "d-johor-laksa", "Related only through the word laksa - which is the point."),
    ("d-mee-rebus", "d-jawa-mee", "Two hawker solutions to the same problem, converged on the "
     "same starch and garnish set, arrived at from opposite sides of the halal line, then "
     "borrowed from each other on shared streets. NLB treats mee jawa as a variant of mee rebus; "
     "Penang treats them as separate dishes. Both are defensible."),
    ("d-mee-rebus", "d-mee-bandung", "Same sweet-potato-thickened family."),
    ("d-mee-rebus", "d-mee-udang", "Same tomato-and-gravy logic, built around large prawns."),
    ("d-mee-udang", "d-jawa-mee", "Timothy Tye describes mee udang as 'primarily a Malay dish "
     "similar to the Jawa Mee sold by Chinese hawkers'."),
    ("d-hokkien-char-penang", "d-char-kway-teow", "Penang Hokkien char is closer in spirit to CKT "
     "than to its KL namesake."),
    ("d-kolo-mee", "d-hakka-mee", "Both descend from Dabu; one went to Borneo, one stayed on the "
     "peninsula."),
    ("d-kolo-mee", "d-kampua-mee", "The Kuching Hakka noodle and the Sibu Foochow noodle - "
     "constantly conflated, and the conflation is why kolo mee gets called Foochow."),
    ("d-sang-nyuk-mee", "d-kolo-mee", "Both dry-tossed in lard and dark soy with soup on the side."),
    ("d-yi-mein", "d-longevity-mee-sua", "Two noodles, one ritual function, split by dialect: yi "
     "mein at Cantonese and Hakka banquets, mee sua in Hokkien, Teochew and Foochow households."),
    ("d-beef-noodles-my", "d-lanzhou-beef-noodle", "Unrelated except by the English name."),
    ("d-beef-noodles-my", "d-taiwan-beef-noodle", "Unrelated except by the English name."),
    ("d-mee-siam", "d-mee-rebus", "The taucu-plus-tamarind-plus-dried-shrimp triad is the same "
     "flavour spine, minus the sweet potato."),
    ("d-fish-head-bee-hoon", "d-koay-teow-thng", "Functional analogues: the Singapore Teochew and "
     "Penang Teochew answers to 'clear broth plus poached toppings'."),
    ("d-fish-head-bee-hoon", "d-asam-laksa", "Fish broth over rice noodle - identical ingredients, "
     "nothing else in common. A useful reminder that ingredient overlap is not kinship."),
    ("d-bak-chor-mee", "d-koay-teow-thng", "Penang's Teochew hawkers took the rice-noodle niche "
     "where Singapore's took the wheat one, so koay teow th'ng is bak chor mee's soup cousin."),
    ("d-tom-yum-mee", "d-curry-mee-penang", "Sour-hot noodle soups occupying the same slot in a "
     "Penang eater's week - which is a real relationship even without a genealogical one."),
    ("d-heng-hwa-bee-hoon", "d-char-bee-hoon", "Same noodle family, a finer Putian product."),
    ("d-mohinga", "d-laksa-kedah", "Conceptual siblings only: fish broth, rice noodles, sour and "
     "herbal garnish. No transmission is established and none is claimed."),
]:
    E("sibling_of", a, b, weight=0.6, confidence="medium", note=note)

E("unevidenced_link", "d-mohinga", "d-asam-laksa", weight=0.15, confidence="low",
  note="Explicitly recorded as a NON-link. The resemblance is real and the Burmese community in "
       "Penang is real, but no source establishes transmission. Do not assert it.",
  sources=["malaymail-beyond-hokkien"])
E("unevidenced_link", "d-yi-mein", "d-maggi-goreng", weight=0.15, confidence="low",
  note="Yi mein is routinely called 'the ancestor of instant noodles'. The fry-dry-rehydrate "
       "technique parallel is real; the line of descent to Ando Momofuku's 1958 product is not "
       "demonstrated. Kept as a technique link, refused as an ancestry link.",
  sources=["wiki-yi-mein"])
E("unevidenced_link", "d-lam-mee", "d-singapore-lor-mee", weight=0.15, confidence="low",
  note="The 'lam mee is loh mee re-pronounced in Cantonese' story. Rejected on four grounds - see "
       "the name node.", sources=["foodpanda-lam-mee"])


# ==================================================== HALAL PAIRS AND SPLITS
E("halal_variant_of", "d-mee-goreng-mamak", "d-hokkien-char-penang", weight=0.6,
  confidence="medium",
  note="Not a direct rebuild of this specific dish, but the mechanism is exactly this: keep the "
       "Chinese noodle, taugeh, tofu and wok; remove pork and lard; add sambal, curry leaf, "
       "tomato and tamarind.", sources=["wiki-mee-goreng-mamak"])
E("halal_variant_of", "d-bihun-goreng", "d-char-bee-hoon", weight=0.7, confidence="high",
  note="Three traditions, one noodle, and they coexist street by street without merging.",
  sources=["wiki-mee-goreng-mamak"])
E("halal_variant_of", "d-mee-rebus", "d-jawa-mee", weight=0.6, confidence="medium",
  note="The halal and non-halal faces of the sweet-potato-gravy noodle. Penang mee jawa uses pork "
       "or prawn stock; mee rebus uses mutton, beef or grago and taucu.",
  sources=["nlb-mee-rebus", "nlb-mee-jawa"])
E("halal_variant_of", "d-laksa-kedah", "d-asam-laksa", weight=0.5, confidence="medium",
  note="Laksa Kedah is halal by default and contains no hae ko; Penang asam laksa's defining "
       "condiment is a Chinese-manufactured fermented prawn paste.", sources=["wiki-laksa"])
E("halal_variant_of", "d-tom-yum-mee", "d-curry-mee-penang", weight=0.4, confidence="low",
  note="Not a rebuild, but it is how the sour-hot noodle soup slot is filled on the halal side of "
       "the street.")
E("illustrates", "d-kolo-mee", "x-halal-boundary", weight=0.8, confidence="high",
  note="One of the very few Chinese-origin pork dishes to have generated a fully accepted halal "
       "parallel with its own indigenous-language names - mi kolok, mi kering, mi rangkai.",
  sources=["wiki-kolo-mee"])
E("illustrates", "d-curry-mee-penang", "x-halal-boundary", weight=0.85, confidence="high",
  note="A dish with Indian spice and Malay coconut, permanently fixed on the Chinese side by "
       "cubes of pig's blood.", sources=["penang-wikia-white-curry"])
E("illustrates", "d-char-kway-teow", "x-halal-boundary", weight=0.6, confidence="medium",
  note="Halal versions omit lard and pork, use beef or chicken, and often push kerang to the "
       "front as the star - filling the flavour hole the lard left.", sources=["wiki-char-kway-teow"])
E("illustrates", "d-beef-noodles-my", "x-beef-taboo", weight=0.9, confidence="medium")


# ================================================ CO-SOLD AND CONFUSED WITH
for a, b, note, conf in [
    ("d-hokkien-mee-penang", "d-lor-mee-penang",
     "Usually the same stall, off the same prawn broth thickened with tapioca flour and egg - an "
     "efficiency that has quietly hybridised the two dishes on the island.", "medium"),
    ("d-mee-rebus", "d-mee-goreng-mamak",
     "NLB records that mee rebus stalls 'usually also offer mee goreng' because the ingredients "
     "overlap. A stall-level co-occurrence is a real transmission mechanism.", "high"),
    ("d-mee-goreng-mamak", "d-pasembur-mee-rojak",
     "Sold side by side, sharing fritters, boiled potato, tofu and often the same red sauce base. "
     "At Bangkok Lane the mee goreng gravy is borrowed from the pasembur stall next door.", "high"),
    ("d-mee-goreng-mamak", "d-maggi-goreng", "Same wok, same sauce, different noodle.", "high"),
    ("d-mee-sotong", "d-mee-goreng-mamak",
     "The same mamak wok and the same sambal base, with sotong cooked into the sauce. Ordering "
     "one usually means the other is on the board.", "high"),
    ("d-mee-soto", "d-mee-rebus", "Both standard on a mamak board.", "high"),
    ("d-koay-teow-thng", "d-koay-chiap",
     "Frequently sold from one cart in Penang, which is exactly how the naming confusion "
     "propagates.", "medium"),
    ("d-chee-cheong-fun", "d-koay-teow-thng",
     "Penang chee cheong fun carts often sit beside koay teow th'ng and loh bak stalls - the "
     "eaten-with layer of the island's hawker economy.", "medium"),
    ("d-asam-laksa", "d-lemak-laksa",
     "Sometimes sold as a half-and-half hybrid in one bowl.", "medium"),
    ("d-char-bee-hoon", "d-hokkien-char-penang",
     "Both on the economy bee hoon tray.", "high"),
    ("d-pan-mee", "d-you-mee",
     "Not two dishes: one dough sold in three forms from one stall. 'You mee' is the round thin "
     "option on the board.", "high"),
]:
    E("co_sold_with", a, b, weight=0.7, confidence=conf, note=note)

for a, b, note in [
    ("d-lor-mee-penang", "d-lam-mee",
     "Systematically conflated, including by Malaysian sources. Different broths, different "
     "dialect registers, different ritual status."),
    ("d-lor-mee-penang", "d-kl-hokkien-mee",
     "Both Hokkien, both starchy or braised, and the KL dish is genuinely descended from a "
     "starchy Hokkien noodle - which is why the confusion is understandable and still wrong."),
    ("d-koay-chiap", "d-koay-teow-thng",
     "Distinguished at the level of the name - 汁 gravy against 湯 soup - and still confused "
     "constantly, with 'koay chiak' floating around Penang menus."),
    ("d-ipoh-hor-fun", "d-koay-teow-thng",
     "Outsiders conflate them; they differ in dialect group, stock philosophy and protein."),
    ("d-pan-mee", "d-sang-nyuk-mee",
     "What Penang stalls call 'Sabah pan mee' is more likely pan mee with sayur manis, and the "
     "dry fried-pork version is closer to Sabah's actual sang nyuk mee kon lau."),
    ("d-kolo-mee", "d-wantan-mee",
     "Same idea - thin egg noodle tossed dry in fat and soy, char siu on top, soup on the side - "
     "reached from Hakka and Cantonese traditions respectively. Convergent siblings with a "
     "Cantonese borrowing edge, not parent and child."),
    ("d-hokkien-mee-penang", "d-kl-hokkien-mee", "One name, two unrelated dishes."),
    ("d-hokkien-mee-penang", "d-singapore-hokkien-mee", "One name, two unrelated dishes."),
    ("d-lor-mee-penang", "d-singapore-lor-mee",
     "Genuinely related, and genuinely not the same dish: pourable against near-gelatinous."),
]:
    E("confused_with", a, b, weight=0.5, confidence="high", note=note)

E("false_cognate_of", "d-jawa-mee", "d-mie-jawa-indonesia", weight=0.9, confidence="high",
  note="Penang mee jawa is a sweet-potato-gravy noodle; Indonesian mie jawa is a charcoal-cooked "
       "chicken noodle in clear broth. Same name, unrelated dishes.", sources=["nlb-mee-jawa"])
E("false_cognate_of", "d-singapore-noodles-hk", "d-char-bee-hoon", weight=0.8, confidence="high",
  note="A place-name that is marketing, not provenance.", sources=["wiki-singapore-noodles"])
E("false_cognate_of", "d-mee-siam", "d-mi-kathi", weight=0.4, confidence="low",
  note="Not strictly a false cognate - mee siam's name may honestly reference a Thai-imported "
       "noodle - but there is no dish called mee siam in Thailand.", sources=["nlb-mee-siam"])

for d in ["d-hokkien-mee-penang", "d-kl-hokkien-mee", "d-singapore-hokkien-mee",
          "d-hokkien-char-penang"]:
    E("shares_name_with", d, "nm-hokkien-mee", weight=0.9, confidence="high")
for d in ["d-asam-laksa", "d-lemak-laksa", "d-laksa-kedah", "d-sarawak-laksa", "d-katong-laksa",
          "d-johor-laksa", "d-curry-mee-penang", "d-curry-laksa-kl"]:
    E("shares_name_with", d, "nm-laksa", weight=0.8, confidence="high")
for d in ["d-you-mee", "d-yi-mein", "d-pan-mee"]:
    E("shares_name_with", d, "nm-you-mee", weight=0.8, confidence="high")
E("shares_name_with", "d-lam-mee", "nm-lam-vs-lor", weight=0.9, confidence="high")
E("shares_name_with", "d-lor-mee-penang", "nm-lam-vs-lor", weight=0.9, confidence="high")
E("shares_name_with", "d-koay-chiap", "nm-koay-chiap-vs-teow", weight=0.9, confidence="high")
E("shares_name_with", "d-koay-teow-thng", "nm-koay-chiap-vs-teow", weight=0.9, confidence="high")
E("shares_name_with", "d-singapore-noodles-hk", "nm-singapore-noodles", weight=0.95,
  confidence="high")
E("shares_name_with", "d-chee-cheong-fun", "nm-chee-cheong-fun", weight=0.95, confidence="high")
E("shares_name_with", "d-pan-mee", "nm-sabah-pan-mee", weight=0.9, confidence="medium")
E("shares_name_with", "d-sang-nyuk-mee", "nm-sabah-pan-mee", weight=0.6, confidence="medium")

for a, b, note in [
    ("d-hakka-mee", "d-bak-chor-mee",
     "Minced pork over dry-tossed egg noodle with soup on the side. Hakka and Teochew, arrived at "
     "independently or by mutual borrowing."),
    ("d-hakka-mee", "d-wantan-mee",
     "Same architecture, Cantonese execution - and in Penang wantan mee occupies the slot Hakka "
     "mee holds in Ipoh and Seremban."),
    ("d-kolo-mee", "d-bak-chor-mee", "Three dialect groups, one architecture."),
    ("d-mee-jawa-placeholder", "d-mee-jawa-placeholder", "unused"),
]:
    if a != "d-mee-jawa-placeholder":
        E("shares_architecture", a, b, weight=0.6, confidence="medium", note=note)

E("shares_architecture", "d-jawa-mee", "d-pasembur-mee-rojak", weight=0.75, confidence="medium",
  note="The same flavour space - sweet-potato-and-peanut gravy over yellow noodles with fritters "
       "and egg - reached from a Chinese kitchen on one side and an Indian-Muslim one on the "
       "other, on the same street. No single source states the relationship, which is itself a "
       "gap worth noting.", sources=["wiki-pasembur", "malaymail-mee-jawa"])
E("shares_architecture", "d-mee-sotong", "d-char-kway-teow", weight=0.6, confidence="medium",
  note="A dark, sweet-savoury, wok-fried seafood noodle - the same conceptual slot, reached "
       "through an entirely Indian-Muslim route. The counter-example to any model that treats "
       "Penang's fried-noodle culture as Chinese-only.", sources=["hameed-pata"])
E("shares_architecture", "d-mee-suah-koh", "d-lor-mee-penang", weight=0.4, confidence="low",
  note="Both starchy and thickened, from opposite directions: one by collapsing the noodle, the "
       "other by thickening the liquid.")


# ============================================== INFLUENCE, ENABLEMENT, MEDIA
E("influenced_by", "d-kolo-mee", "d-wantan-mee", weight=0.5, confidence="medium",
  note="Char siu and probably the dark-soy 'black' variant are Cantonese borrowings into the "
       "Hakka line.", sources=["medium-kolo-mee"])
E("influenced_by", "d-jawa-mee", "d-pasembur-mee-rojak", weight=0.5, confidence="low",
  note="Bidirectional in practice, on shared streets. Paired with the reverse edge.")
E("influenced_by", "d-pasembur-mee-rojak", "d-jawa-mee", weight=0.5, confidence="low",
  note="The other half of the pair. Neither direction is documented; the co-location is.")
E("influenced_by", "d-mee-goreng-mamak", "d-pasembur-mee-rojak", weight=0.6, confidence="medium",
  note="At Bangkok Lane the gravy is literally borrowed from the pasembur stall.",
  sources=["wiki-pasembur"])
E("influenced_by", "d-mee-hailam", "d-hokkien-char-penang", weight=0.5, confidence="medium",
  note="Hainanese cooks working a Hokkien noodle format for non-Chinese palates.",
  sources=["tasteasianfood-mee-hailam"])
E("influenced_by", "d-ipoh-hor-fun", "d-hokkien-mee-penang", weight=0.5, confidence="medium",
  note="The prawn-shell element in a Cantonese dish, because the founding stallholders were "
       "Hokkien and the Hokkien palate combines meat and seafood in one bowl.",
  sources=["ipoh-echo-kai-si-hor-fun"])
E("influenced_by", "d-sarawak-laksa", "d-hokkien-mee-penang", weight=0.4, confidence="low",
  note="Tony Boey's component reading: prawn stock from the Hokkien prawn noodle, chicken stock "
       "Cantonese, coconut Nyonya, peanut from Malay satay sauce. Informed inference, presented "
       "as such.", sources=["johorkaki-sarawak-laksa"])
E("influenced_by", "d-asam-laksa", "d-laksa-kedah", weight=0.5, confidence="disputed",
  note="Or the reverse. The graph carries the uncertainty in both directions rather than "
       "resolving it.", sources=["wiki-laksa"])
E("influenced_by", "d-laksa-kedah", "d-asam-laksa", weight=0.5, confidence="disputed")

E("enabled_by", "d-curry-mee-penang", "cm-curry-powder", weight=0.85, confidence="high",
  note="A pre-ground, shelf-stable, cheap blend is what makes a hawker curry economically "
       "possible - no daily rempah-pounding.", sources=["oed-curry"])
for d in ["d-mee-goreng-mamak", "d-mee-rebus", "d-curry-laksa-kl", "d-singapore-noodles-hk",
          "d-bihun-goreng"]:
    E("enabled_by", d, "cm-curry-powder", weight=0.6, confidence="high", sources=["oed-curry"])
E("enabled_by", "d-maggi-goreng", "cm-maggi", weight=0.95, confidence="high",
  note="The hard date in the corpus: 1971.", sources=["nestle-maggi-malaysia"])
E("enabled_by", "d-mee-goreng-mamak", "cm-maggi", weight=0.5, confidence="medium",
  note="Not the noodle - the bottled chilli and tomato sauce, which arrived in 1969.",
  sources=["nestle-maggi-malaysia"])
for d in ["d-hokkien-mee-penang", "d-mee-goreng-mamak", "d-mee-rebus", "d-mee-soto",
          "d-curry-mee-penang", "d-lor-mee-penang", "d-kl-hokkien-mee"]:
    E("enabled_by", d, "cm-noodle-factory", weight=0.6, confidence="medium",
      note="The noodle is Chinese infrastructure sold to everybody. Without industrial alkaline "
           "noodle there is no mamak fried noodle and no Malay mee rebus.")
E("standardised_by", "d-sarawak-laksa", "cm-swallow-rempah", weight=0.9, confidence="medium",
  note="Tan Yong Him's premix from the 1960s created and then froze the modern dish. The best-"
       "documented case of an industrial paste inventing a tradition.",
  sources=["johorkaki-sarawak-laksa"])
E("standardised_by", "d-white-curry-mee", "cm-mykuali", weight=0.9, confidence="high",
  note="A serving convention became a named global dish category through a 2012 instant product.",
  sources=["mykuali", "penang-wikia-white-curry"])
E("enabled_by", "d-fish-head-bee-hoon", "cm-condensed-milk", weight=0.6, confidence="medium",
  sources=["wiki-fish-soup-bee-hoon"])
E("enabled_by", "d-char-kway-teow", "w-japanese-occupation", weight=0.3, confidence="medium",
  note="Not origin - adaptation. Tapioca noodles and red palm oil during the Occupation, and a "
       "1950s bean-sprout growers' strike that put cai xin in the bowl for good.",
  sources=["nlb-ckt"])
E("enabled_by", "d-mee-rebus", "t-kandar-pole", weight=0.6, confidence="medium",
  sources=["nlb-mee-rebus"])
E("enabled_by", "d-mee-goreng-mamak", "w-hajj-port", weight=0.3, confidence="low",
  note="Interpretation, not evidence: the pilgrim trade concentrated a floating Muslim population "
       "eating in the same lanes and created demand for portable halal wheat food.",
  sources=["malaymail-beyond-hokkien"])

E("popularised_by", "d-asam-laksa", "m-cnn-2011", weight=0.85, confidence="high",
  sources=["cnn-go-2011"])
E("popularised_by", "d-sarawak-laksa", "m-bourdain-2005", weight=0.85, confidence="medium",
  sources=["bourdain-no-reservations-borneo"])
E("popularised_by", "d-white-curry-mee", "m-ramen-rater-2014", weight=0.8, confidence="high",
  sources=["mykuali"])
E("popularised_by", "d-kolo-mee", "m-heritage-2024", weight=0.6, confidence="high",
  sources=["heritage-2024-declaration"])
for d in ["d-curry-mee-penang", "d-duck-koay-teow", "d-tom-yum-mee", "d-char-kway-teow"]:
    E("popularised_by", d, "m-michelin-my", weight=0.5, confidence="medium",
      sources=["michelin-ckt"])

E("ritual_role", "d-lam-mee", "x-longevity-noodle", weight=0.9, confidence="high",
  note="The Penang Nyonya branch of the longevity noodle.", sources=["carryitlikeharry-misua"])
E("ritual_role", "d-longevity-mee-sua", "x-longevity-noodle", weight=0.95, confidence="high")
E("ritual_role", "d-yi-mein", "x-longevity-noodle", weight=0.85, confidence="high",
  note="The Cantonese and Hakka banquet branch.", sources=["wiki-yi-mein"])
E("ritual_role", "d-fuzhou-red-wine-mee-sua", "x-longevity-noodle", weight=0.85, confidence="high",
  note="Also the confinement food - the wine and ginger are 'heating'.",
  sources=["danielfooddiary-foochow"])
E("ritual_role", "d-mee-suah-koh", "x-longevity-noodle", weight=0.4, confidence="medium",
  note="Same noodle, non-ritual use. Worth an edge because it shows the thread doing everyday "
       "work as well as ceremonial work.")


# ================================================= DISHES -> CONCEPTS
for d, x, w, note in [
    ("d-hokkien-mee-penang", "x-naming-after-cook", 0.9,
     "Named after the cook's dialect group, from outside, and then adopted."),
    ("d-mee-goreng-mamak", "x-naming-after-cook", 0.9,
     "Chinese noun, Malay verb, Tamil honorific - the whole fusion in four syllables."),
    ("d-jawa-mee", "x-naming-after-cook", 0.8, "A name asserting an origin the dish only partly has."),
    ("d-mee-siam", "x-naming-after-cook", 0.8, "An exonym for a dish that does not exist in Siam."),
    ("d-mee-hailam", "x-naming-after-cook", 0.8, None),
    ("d-char-kway-teow", "x-naming-after-noodle", 0.9, None),
    ("d-curry-mee-penang", "x-naming-after-noodle", 0.95,
     "curry MEE or curry LAKSA depending purely on which noodle is in the bowl."),
    ("d-maggi-goreng", "x-naming-after-noodle", 0.9, None),
    ("d-kolo-mee", "x-naming-after-process", 0.8, None),
    ("d-mee-rebus", "x-naming-after-process", 0.9, None),
    ("d-lor-mee-penang", "x-naming-after-process", 0.9, None),
    ("d-lam-mee", "x-naming-after-process", 0.85, "Named for the gesture of pouring."),
    ("d-char-kway-teow", "x-citogenesis", 0.9,
     "The textbook case: the 'fishermen and farmers' origin is unsupported by the very footnotes "
     "cited for it."),
    ("d-ipoh-hor-fun", "x-citogenesis", 0.7, "The limestone-water claim."),
    ("d-chilli-pan-mee", "x-citogenesis", 0.6,
     "Wikipedia's citation for 'invented in Chow Kit' is a 2017 food blog."),
    ("d-thai-boat-noodles", "x-citogenesis", 0.6, "The medieval Ayutthaya claim."),
    ("d-beef-noodles-my", "x-citogenesis", 0.6, "'Hainanese beef noodles came from Hainan.'"),
    ("d-mee-udang", "x-evidence-asymmetry", 0.85, None),
    ("d-pasembur-mee-rojak", "x-evidence-asymmetry", 0.6, None),
    ("d-pan-mee", "x-substrate-marker", 0.85, "Anchovy stock is the naturalisation marker."),
    ("d-hokkien-mee-penang", "x-substrate-marker", 0.85, "Kangkung and cooked-in sambal."),
    ("d-chee-cheong-fun", "x-substrate-marker", 0.9, "Hae ko on a Cantonese sheet."),
    ("d-katong-laksa", "x-domestic-service", 0.9, None),
    ("d-mee-hailam", "x-domestic-service", 0.8, None),
    ("d-asam-laksa", "x-northern-triangle", 0.8,
     "The sour-hot register is northern-peninsula regional cuisine, not cross-border borrowing."),
    ("d-lemak-laksa", "x-northern-triangle", 0.6, "Locally called 'Siamese laksa'."),
    ("d-char-bee-hoon", "x-economy-bee-hoon", 0.9, None),
    ("d-mee-goreng-mamak", "x-mamak-stall", 0.9, None),
    ("d-maggi-goreng", "x-mamak-stall", 0.9, None),
    ("d-mee-rebus", "x-mamak-stall", 0.7, None),
    ("d-mee-soto", "x-mamak-stall", 0.7, None),
    ("d-mee-sotong", "x-mamak-stall", 0.8, None),
    ("d-mee-hailam", "x-kopitiam", 0.7, None),
    ("d-koay-teow-thng", "x-hawker-apprenticeship", 0.6,
     "Two episodes at two stalls in this series produced two different bowls of nominally the "
     "same dish - which is air tangan in action."),
]:
    E("illustrates", d, x, weight=w, confidence="medium", note=note)

E("illustrates", "d-mee-sotong", "x-halal-boundary", weight=0.75, confidence="high",
  note="A wok-fried seafood noodle in the char-kway-teow slot, built entirely on the halal side "
       "of the street. The clearest single proof that Penang's fried-noodle culture is not "
       "Chinese-only.", sources=["pp-field-mee-sotong"])
E("illustrates", "d-mee-sotong", "x-evidence-asymmetry", weight=0.5, confidence="medium",
  note="Two stall lineages, four dates between them, and not a document anywhere - the same "
       "documentation gap that affects every mamak and Malay dish in this dataset.",
  sources=["pp-field-mee-sotong"])

E("illustrates", "d-lanzhou-beef-noodle", "x-citogenesis", weight=0.4, confidence="high",
  note="Included as the control: a noodle origin with a name, a date, a municipal standard and a "
       "museum. Everything Malaysian in this graph should be read against it.",
  sources=["wiki-lanzhou-beef-noodle"])
E("illustrates", "n-yellow-alkaline", "x-halal-boundary", weight=0.8, confidence="high",
  note="The noodle crosses the boundary freely; the sauce never does. That asymmetry is the "
       "single most productive fact in Penang's noodle culture.")


# ==================================================== EPISODES AND VENUES
_EPISODES = [
    ("ep-01-jawa-mee", "d-jawa-mee", "v-33-best-food-hub", None),
    ("ep-02-pan-mee-soup", "d-pan-mee", "v-pulau-tikus-hawker", None),
    ("ep-03-kolo-mee", "d-kolo-mee", "v-hock-beng-88", None),
    ("ep-04-lam-mee", "d-lam-mee", "v-hock-beng-88", None),
    ("ep-05-hokkien-mee", "d-hokkien-mee-penang", "v-restoran-77", None),
    ("ep-06-mee-suah-koh", "d-mee-suah-koh", "v-33-best-food-hub", None),
    ("ep-07-char-kway-teow", "d-char-kway-teow", "v-restoran-77", None),
    ("ep-08-wantan-mee", "d-wantan-mee", "v-cheah-yew-market", None),
    ("ep-09-curry-mee", "d-curry-mee-penang", "v-restoran-77", None),
    ("ep-10-koay-teow-thng", "d-koay-teow-thng", "v-sin-hup-aun", None),
    ("ep-11-lor-mee", "d-lor-mee-penang", "v-cheah-yew-market", None),
    ("ep-12-mee-rebus", "d-mee-rebus", "v-33-best-food-hub", None),
    ("ep-13-lemak-laksa", "d-lemak-laksa", "v-sin-yong-wah", None),
    ("ep-14-pan-mee-dry", "d-pan-mee", "v-sabah-pan-mee-pt", "ep-02-pan-mee-soup"),
    ("ep-15-koay-teow-thng-ah-liang", "d-koay-teow-thng", "v-pulau-tikus-hidden",
     "ep-10-koay-teow-thng"),
    ("ep-16-mee-sotong", "d-mee-sotong", "v-sin-hup-aun", None),
    ("ep-17-mohinga", "d-mohinga", "v-mingalarpar", None),
]
for ep, dish, venue, revisit in _EPISODES:
    E("of_dish", ep, dish, weight=1.0, confidence="high")
    E("tasted_at", ep, venue, weight=1.0, confidence="high")
    if revisit:
        E("revisit_of", ep, revisit, weight=1.0, confidence="high")

_PLANNED = [
    ("ep-p-white-curry-mee", "d-white-curry-mee", None),
    ("ep-p-asam-laksa", "d-asam-laksa", None),
    ("ep-p-mee-goreng-mamak", "d-mee-goreng-mamak", None),
    ("ep-p-maggi-goreng", "d-maggi-goreng", None),
    ("ep-p-bee-hoon", "d-char-bee-hoon", None),
    ("ep-p-koay-chiap", "d-koay-chiap", None),
    ("ep-p-bak-chor-mee", "d-bak-chor-mee", None),
    ("ep-p-duck-noodle", "d-duck-koay-teow", None),
    ("ep-p-beef-noodles", "d-beef-noodles-my", None),
    ("ep-p-fish-head-bee-hoon", "d-fish-head-bee-hoon", None),
    ("ep-p-chee-cheong-fun", "d-chee-cheong-fun", None),
    ("ep-p-ban-mian", "d-pan-mee", None),
    ("ep-p-mee-soto", "d-mee-soto", None),
    ("ep-p-you-mee", "d-you-mee", None),
    ("ep-p-yi-mein", "d-yi-mein", None),
    ("ep-p-ipoh-hor-fun", "d-ipoh-hor-fun", None),
    ("ep-p-tom-yum", "d-tom-yum-mee", None),
    ("ep-p-tom-yum", "d-thai-boat-noodles", None),
    ("ep-p-sarawak-laksa", "d-sarawak-laksa", None),
    ("ep-p-bihun-goreng", "d-bihun-goreng", None),
    ("ep-p-mainland-curry-mee", "d-curry-mee-penang", None),
    ("ep-p-mainland-wantan-mee", "d-wantan-mee", None),
    ("ep-p-mainland-kopitiam", "d-char-bee-hoon", None),
    ("ep-p-bm-surprise", "d-char-kway-teow", None),
    ("ep-p-chilli-pan-mee", "d-chilli-pan-mee", None),
    ("ep-p-festival-noodles", "d-longevity-mee-sua", None),
    ("ep-p-cmeepo-wildcard", "d-mee-suah-koh", None),
    ("ep-p-wantan-mee-dry", "d-wantan-mee", "ep-08-wantan-mee"),
    ("ep-p-curry-mee-variant", "d-curry-mee-penang", "ep-09-curry-mee"),
]
for ep, dish, revisit in _PLANNED:
    E("of_dish", ep, dish, weight=1.0, confidence="high")
    if revisit:
        E("revisit_of", ep, revisit, weight=1.0, confidence="high")

# ============================================= HISTORY THAT NEEDED CONNECTING
E("migrated_via", "c-hokkien", "w-1867-riots", weight=0.5, confidence="high",
  note="Toh Peh Kong was led in 1867 by Khoo Thean Teik, of one of the Big Five Hokkien clans - "
       "the direct link between respectable clan power and street power.",
  sources=["wiki-1867-riots"])
E("migrated_via", "c-cantonese", "w-1867-riots", weight=0.4, confidence="disputed",
  note="Sources give three mutually contradictory dialect-to-society mappings for 1867. Any "
       "single mapping should be treated as unsafe.", sources=["wiki-1867-riots", "voon-2024-hakka"])
E("illustrates", "w-1867-riots", "x-halal-boundary", weight=0.25, confidence="low",
  note="Weak but worth recording: Ghee Hin was allied with the mainly Malay White Flag faction "
       "and Toh Peh Kong with the Red Flag, so Penang's communal fault lines in 1867 already ran "
       "across rather than between ethnic groups.", sources=["wiki-1867-riots"])
E("migrated_via", "c-hokkien", "w-1877-protectorate", weight=0.4, confidence="high",
  note="Penang was one of three Protectorate ports, so it was a place of ENTRY as much as a "
       "destination - every pioneer opening the tin fields of southern Siam, Larut and Kinta was "
       "based here.", sources=["nlb-chinese-immigrants-1877", "kuchler-1965"])
E("migrated_via", "c-teochew", "w-1877-protectorate", weight=0.35, confidence="high",
  sources=["nlb-chinese-immigrants-1877"])
E("illustrates", "w-suez-1869", "x-northern-triangle", weight=0.7, confidence="high",
  note="Suez moved the main trade route from the Sunda Strait to the Straits of Malacca, which is "
       "what turned Penang from a naval outpost into the commercial capital of a maritime region.",
  sources=["kuchler-1965"])
E("migrated_via", "c-hokkien", "w-suez-1869", weight=0.5, confidence="high",
  sources=["kuchler-1965"])
E("migrated_via", "c-siamese-my", "w-post2000-thai", weight=0.5, confidence="medium",
  note="A commercial diffusion, not a heritage layer - important not to conflate the two.",
  sources=["wiki-boat-noodles"])
E("enabled_by", "d-tom-yum-mee", "w-post2000-thai", weight=0.8, confidence="medium",
  sources=["wiki-boat-noodles"])
E("enabled_by", "d-thai-boat-noodles", "w-post2000-thai", weight=0.8, confidence="medium",
  sources=["wiki-boat-noodles"])
E("carried_by", "d-kolo-mee", "c-iban", weight=0.5, confidence="high",
  note="Not as originators but as adopters, which is the more interesting relationship: Iban and "
       "Malay Sarawakians eat mi kolok widely, and the halal version has its own Iban names.",
  sources=["wiki-kolo-mee"])
E("settled_in", "c-iban", "r-kuching", weight=0.6, confidence="high")
E("originates_in", "d-kolo-mee", "r-brunei", weight=0.2, confidence="medium",
  note="Not an origin - a diffusion endpoint. Kolo mee is popular in Brunei, including as an "
       "instant product.", sources=["wiki-kolo-mee"])
E("home_region", "c-british-colonial", "r-madras", weight=0.5, confidence="high",
  note="Where British civil servants commissioned reproducible curry blends from local spice "
       "merchants from the 1830s - the standardisation that made hawker curry possible.",
  sources=["oed-curry"])
E("enabled_by", "cm-curry-powder", "r-madras", weight=0.8, confidence="high",
  sources=["oed-curry"])
E("uses_noodle", "d-mee-siam", "n-tang-hoon", weight=0.15, confidence="low",
  note="Not standard - recorded because glass noodle and rice vermicelli are routinely blurred on "
       "English menus, and the graph should keep them apart.", sources=["wiki-penang-cuisine"])
E("contributed_by", "n-tang-hoon", "c-peranakan-penang", weight=0.5, confidence="medium",
  note="Its real Penang home is Nyonya chap chai rather than any noodle dish - which is why it "
       "sits at the edge of this graph.", sources=["wiki-penang-cuisine"])


E("reference_stall_for", "v-jones-road-mee-sotong", "d-mee-sotong", weight=0.85,
  confidence="medium",
  note="The second of the two Penang mee sotong lineages, alongside Hameed 'Pata'. It leads with "
       "sambal gravy where Padang Kota Lama leads with a dark squid sauce.",
  sources=["pp-field-mee-sotong"])
E("tasted_at", "ep-16-mee-sotong", "v-jones-road-mee-sotong", weight=0.9, confidence="high",
  note="Eaten at Sin Hup Aun Cafe, but the stall carries its own Jones Road identity - the cook "
       "moved, the name came with him.", sources=["pp-field-mee-sotong"])
E("reference_stall_for", "v-mingalarpar", "d-mohinga", weight=0.85, confidence="high",
  note="The series' Penang Mohinga bowl. A restaurant, not a hawker stall - which is how "
       "Burmese food actually shows up here.",
  sources=["pp-field-mohinga"])

for v, d in [
    ("v-kim-lian-kee", "d-kl-hokkien-mee"),
    ("v-kin-kin", "d-chilli-pan-mee"),
    ("v-air-itam-curry-mee", "d-curry-mee-penang"),
    ("v-air-itam-curry-mee", "d-white-curry-mee"),
    ("v-hameed-pata", "d-mee-sotong"),
    ("v-bangkok-lane", "d-mee-goreng-mamak"),
    ("v-lum-lai", "d-duck-koay-teow"),
    ("v-choon-hui", "d-sarawak-laksa"),
    ("v-soong-kee", "d-beef-noodles-my"),
    ("v-thean-chun", "d-ipoh-hor-fun"),
    ("v-ghee-lian", "d-tom-yum-mee"),
    ("v-sabah-pan-mee-pt", "d-pan-mee"),
]:
    E("reference_stall_for", v, d, weight=0.8, confidence="medium")

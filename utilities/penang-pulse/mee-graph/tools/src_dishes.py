"""Dish, venue and episode nodes for the Penang noodle culture graph.

`penangStatus` values
---------------------
core       a Penang signature dish
present    genuinely sold in Penang, not a Penang invention
rare        sold in Penang but hard to find
absent     eaten elsewhere; here for comparison only
ancestor   the upstream dish in China, India, Java or Thailand
cousin     a parallel diaspora dish, sibling rather than parent
fiction    a dish whose name asserts an origin it does not have

`tryStatus` values track the Mee Myself and I checklist: tried, to-try,
wildcard, revisit, off-list (not on the checklist but belongs on the map).
"""

from src_nodes import N


def D(nid, label, **kw):
    kw.setdefault("penangStatus", "present")
    kw.setdefault("tryStatus", "off-list")
    return N(nid, "dish", label, **kw)


# ============================================ PENANG CORE - TRIED
D("d-hokkien-mee-penang", "Penang Hokkien Mee (Hae Mee / Prawn Mee)",
  zh="福建麵 / 蝦麵", aka=["hae mee", "hē-mī", "prawn mee", "har mee", "mee yoke"],
  malay="mi udang", penangStatus="core", tryStatus="tried",
  style="soup", etymology="福建 Fujian + 麵 noodle. A diaspora name: nobody in Fujian calls a "
        "dish 'Fujian noodles'. It is an ethnic label applied from outside, then adopted. "
        "蝦 hē = prawn.",
  blurb="Broth of prawn heads and shells dry-fried first to caramelise, then boiled for hours "
        "with pork bones. Blanched noodles - yellow, bee hoon, or 'chap' for mixed. Kangkung, "
        "bean sprouts, halved hard-boiled egg, sliced pork, prawns, fried shallots, lard.",
  penangVariation="Two documented substitutions turn the Xiamen dish into a Penang one: "
        "kangkung replaces coriander, and sambal belacan is cooked INTO the stock where Xiamen "
        "uses raw minced garlic for heat and no sambal at all. Extra sambal still comes on the "
        "side. Singapore's prawn noodle is the same ancestor gone darker and pepper-forward, "
        "with neither the sambal nor the kangkung.",
  contested="The Xiamen origin is one of the best-supported claims in the whole corpus. The "
        "competing 'invented in WWII from prawn-head scraps' story fails twice over: the parent "
        "dish 厦门虾面 still exists in Xiamen, and an eyewitness account of occupied Penang says "
        "there were essentially no noodles and hardly any rice. Treat the wartime story as "
        "folklore. Wikipedia's separate claim that all Hokkien mee variants descend from lor "
        "mee is uncited and should be read as a hypothesis.",
  confidence="high", sources=["johorkaki-hokkien-mee", "wiki-hokkien-mee", "nlb-hokkien-prawn"])

D("d-char-kway-teow", "Char Kway Teow", zh="炒粿條", pojh="chhá-kóe-tiâu",
  aka=["char koay teow", "CKT", "炒貴刁"], malay="kuetiau goreng (DBP, 2021)",
  penangStatus="core", tryStatus="tried", style="fried",
  etymology="炒 stir-fry + 粿 steamed rice-flour cake + 條 strip. Literally 'stir-fried "
        "rice-cake strips', which is exactly what a flat rice noodle is. Note the Cantonese "
        "corruption 炒貴刁, characters chosen purely for sound and meaning nothing - the dish "
        "name travelled back into China as a loanword.",
  blurb="Very high heat for wok hei; lard and crisp lard croutons; garlic; light and dark soy; "
        "chilli paste; whole prawns; blood cockles; Chinese chives; lup cheong; bean sprouts; "
        "egg. Penang signatures: duck egg rather than chicken, and a banana leaf on the plate.",
  penangVariation="Lighter and less sweet than Singapore's, because the sweet dark soy is "
        "omitted or minimised. Penang cuts thinner ribbons and does not mix in yellow noodle. "
        "Penang also fries a lo shi fun version Singapore does not have. Bukit Mertajam has a "
        "wetter, gravy-finished char koay teow basah locally associated with the Malay "
        "community.",
  contested="The name is Hokkien; the dish is Teochew. That mismatch is the interesting datum, "
        "not an error - Hokkien was the lingua franca of the Penang street, and both languages "
        "are Southern Min so kóe-tiâu is comprehensible in either. What IS an error is the "
        "universally repeated 'fishermen, farmers and cockle-gatherers sold it in the evening "
        "to supplement their income' origin. Chasing Wikipedia's footnotes: the first points at "
        "an NLB article that does not contain the claim, the second at a 2016 newspaper health-"
        "scare piece. Plausible, but essentially unsourced - the single most-repeated unverified "
        "claim in Malaysian and Singaporean food writing.",
  confidence="medium", sources=["michelin-ckt", "nlb-ckt", "wiki-char-kway-teow", "cj-my-ckt-origins"],
  flags=["fishermen-origin-unevidenced"])

D("d-koay-teow-thng", "Koay Teow Th'ng", zh="粿條湯", pojh="kóe-tiâu thng",
  malay="sup kuetiau", penangStatus="core", tryStatus="tried", style="soup",
  etymology="湯 thng = soup. Its regional cousins share the same two Teochew syllables: hủ "
        "tiếu in Vietnam, kuy teav in Cambodia, ก๋วยเตี๋ยว kuaitiao in Thailand. That is one of "
        "the strongest single pieces of evidence anywhere for the Teochew maritime diaspora as "
        "a food-distribution network.",
  blurb="A deliberately clear broth - the aesthetic opposite of char kway teow - simmered for "
        "hours from pork, chicken or duck bones, very often with dried flounder. Fish balls, "
        "fish cake, minced pork, pork slices, offal, lettuce, spring onion, fried garlic, white "
        "pepper. Chilli in light soy on the side.",
  penangVariation="Three parallel sub-types - pork, duck and a less common chicken - with duck "
        "the prestige option, historically associated with Lorong Ngah Aboo off Kimberley "
        "Street. Penang bowls are meatier than Singapore's, which leans on fish balls as the "
        "point of the dish. Ipoh's kai si hor fun is a genuinely different dish outsiders "
        "conflate with it.",
  contested="No inventor claim exists, which is itself informative: this is a base, not a "
        "creation.",
  confidence="high", sources=["penang-wikia-kuey-teow-thng", "streetbite-koay-teow-thng"])

D("d-lor-mee-penang", "Penang Lor Mee", zh="滷麵", pojh="ló͘-mī",
  aka=["loh mee", "lu mian"], penangStatus="core", tryStatus="tried", style="gravy",
  etymology="滷 ló͘ is the master-stock braise word - the same 滷 as in lor bak and lor tan. "
        "In lor mee the braising liquid is thickened with starch. lor is a technique, not a dish.",
  blurb="Yellow noodle and/or bee hoon under a five-spice-scented starch-thickened gravy, with "
        "prawn, pork, egg and fish cake.",
  penangVariation="Not the same dish as Singapore lor mee. Penang's gravy is pourable rather "
        "than near-gelatinous, chicken- or prawn-stock based, and lighter. Crucially, Penang lor "
        "mee is usually sold at the SAME stall as Penang Hokkien mee, off the same prawn broth "
        "thickened with tapioca flour and egg - an efficiency that has quietly hybridised the "
        "two dishes on the island.",
  contested="The Zhangzhou attribution is repeated across sources but no primary Chinese-"
        "language documentation surfaced. Putian's own lor mee is lighter, less starched and "
        "seafood-based, which suggests the thick-gravy form is regionally specific within "
        "Fujian rather than universal. Note also the false friend: Henan 卤面 uses the same "
        "characters for an unrelated dish. Malay Mail's claim of Hainanese influence on Penang "
        "lor mee is food journalism, not scholarship. And do NOT read the warm sweet spices as "
        "Arab-derived: five-spice is Chinese.",
  confidence="medium", sources=["wiki-lor-mee", "johorkaki-hokkien-mee"])

D("d-lam-mee", "Lam Mee (Nyonya Birthday Noodles)", zh="淋麵 (disputed)",
  aka=["seh jit mee 生日麵", "Nyonya lam mee", "birthday mee"],
  penangStatus="core", tryStatus="tried", style="soup",
  etymology="If 淋麵: 淋 = to pour liquid over. 'Drenched noodles' - named for a gesture, which "
        "is unusual and rather charming. 燜麵 'to braise covered' is also seen but fits the "
        "preparation less well.",
  blurb="A light, clear-but-rich broth from prawns plus pork ribs or chicken carcass, poured "
        "over the noodles at serving. Finely shredded toppings arranged on top: shredded "
        "omelette, chicken, prawns, blanched bean sprouts, long beans, fried shallots. Sambal "
        "belacan and calamansi on the side - without which Penangites say it is not lam mee.",
  penangVariation="Essentially a Penang and northern-Malaysian dish, and far more a home and "
        "celebration dish than a hawker one; hawker versions are widely described as inferior "
        "to home-cooked. Note what it did to its parent: it kept lor mee's structure - noodle, "
        "poured liquid, assembled toppings - and discarded the defining lor braise, replacing "
        "dark soy and starch with clear prawn stock.",
  ritual="A birthday and longevity dish, prepared for milestone birthdays at 60, 70 and 80, as "
        "an offering for prayers and for distribution to relatives, traditionally with a large "
        "red ang ku kueh. Penang is distinctive in having elevated lam mee into the birthday "
        "role where most Hokkien households use mee sua.",
  contested="The 'lam mee is loh mee re-pronounced in Cantonese' account is probably wrong - see "
        "the name node. The Penang cooks' own account, that Baba-Nyonya descendants of Fujian "
        "immigrants progressively adjusted an inherited lor mee to Nyonya taste until it branched "
        "off, is family-tradition history but internally consistent.",
  confidence="medium", sources=["foodpanda-lam-mee", "carryitlikeharry-misua"])

D("d-wantan-mee", "Wantan Mee", zh="雲吞麵", aka=["wan tan mee", "kon lo mee 乾撈麵", "wanton mee"],
  malay="mi wantan", penangStatus="present", tryStatus="tried", style="dry or soup",
  etymology="雲吞 wan tan is a Cantonese phonetic rendering of 餛飩 húntún, and the characters "
        "chosen mean 'swallowing clouds' - a poetic re-spelling for the way the dumplings "
        "float. 乾撈 = dry-tossed, the same 撈 as in lo hei.",
  blurb="Thin springy egg noodle; wontons; red-glazed char siu; choy sum; pickled green chilli "
        "in vinegar; fried shallots or lard. The dry version's sauce is caramelised dark soy, "
        "light soy, sesame oil and lard, with a small bowl of soup and more wontons alongside.",
  penangVariation="A Cantonese-minority dish on a Hokkien-majority island, which is why it "
        "reads as slightly imported next to Hokkien mee. Penang's is somewhat less dark than "
        "Klang Valley versions, with the pickled chilli prominent, and some stalls do a "
        "chilli-sauce-forward 'red' version.",
  contested="Guangzhou origin is solid. The Malaysian dark-soy DRY form is the interesting part: "
        "it has no Guangzhou antecedent and should be treated as a Malayan innovation. Nobody "
        "has dated when or why the divergence happened. Hong Kong went the opposite way, "
        "prizing a clear dried-flounder stock and prawn-forward wontons.",
  confidence="high", sources=["wiki-wonton-noodles", "visitpenang-wanton-mee", "jkkn-culture-mapping"])

D("d-curry-mee-penang", "Penang Curry Mee", zh="咖喱麵", malay="mi kari",
  aka=["curry laksa (south of Penang)", "laksa lemak (Singapore)"],
  penangStatus="core", tryStatus="tried", style="soup",
  etymology="Follow the word: Tamil kari கறி 'sauce' → Portuguese caril → English curry → "
        "phonetically back into Chinese as 咖喱 → into a Hokkien mouth. Four languages for one "
        "word before it reaches the stall.",
  blurb="Broth of prawn shells, coconut milk and curry spices. Coagulated pig's blood cubes, "
        "cuttlefish, prawns, cockles, tofu puffs, long beans, bean sprouts, mint, and a "
        "separately served sambal the eater stirs in.",
  penangVariation="It is called curry MEE where yellow noodle or bee hoon is used and curry "
        "LAKSA where thick round laksa noodle is used - the cleanest example in the corpus of a "
        "dish named after its noodle rather than its sauce. Penang's distinguishing features "
        "against Singapore are the pork blood and the stir-it-in sambal; against the Klang "
        "Valley, a thinner and less coconut-forward broth.",
  fusion="A genuine four-way fusion, component by component. Noodle: Chinese. Curry spice base: "
        "South Indian and Indian-Muslim, materially enabled by British-commodified curry powder. "
        "Coconut milk, sambal, belacan and daun kesum: Malay and Nyonya. Pork blood, pork and "
        "lard: Chinese, and specifically non-halal, which permanently fixes the dish on the "
        "Chinese side of the boundary despite its Indian and Malay components.",
  contested="The oldest documented Penang lineage is the Air Itam stall of the Lim sisters, "
        "whose mother was selling by 1946 - but that dates a STALL, not a dish. The Hainanese "
        "claim is asserted widely and demonstrated nowhere for Penang curry mee specifically; "
        "the mechanism is documented only for Singapore's Katong laksa. The santan-rempah-daun "
        "kesum architecture is unambiguously Peranakan, but no specific Nyonya household "
        "invention claim survives scrutiny. The line that curry mee 'became popular in the "
        "1970s-80s among workers' is content-farm material and is contradicted by the 1946 "
        "stall evidence.",
  confidence="medium", sources=["penang-wikia-white-curry", "air-itam-curry-mee",
                                "oed-curry", "wiki-laksa"])

D("d-mee-suah-koh", "Mee Suah Koh", zh="麵線糊", pojh="mī-sòaⁿ-kô͘",
  aka=["mee suah tau", "misua gor", "mian xian hu"], penangStatus="rare", tryStatus="tried",
  style="porridge-noodle",
  etymology="麵 noodle + 線 thread + 糊 paste, pulp, congee. 'Misua pulp' - the noodles cooked "
        "until they collapse into a starchy porridge, which is the point rather than an accident.",
  blurb="A sticky, gluey vermicelli soup, often topped with shredded crab meat, sold in only a "
        "handful of Penang coffee shops.",
  penangVariation="This is the most interesting node in the tried list, because it is a LOW-"
        "FREQUENCY SURVIVAL. In Xiamen and Quanzhou 面线糊 is mainstream breakfast street food "
        "with a huge array of add-ins. In Penang it survives as a niche, preserving the "
        "ancestral Quanzhou form almost unchanged while its more adaptable siblings - Hokkien "
        "mee, lor mee - creolised heavily. Adaptation and survival are not the same thing.",
  confidence="medium", sources=["carryitlikeharry-misua"])

D("d-jawa-mee", "Jawa Mee (Mee Jawa)", aka=["mee rojak (at some stalls)", "mi Jawa"],
  penangStatus="core", tryStatus="tried", style="gravy",
  etymology="'Java noodles' - a name asserting a Javanese origin the dish only partly has. Note "
        "that Penang mee jawa and Indonesian mie jawa are FALSE COGNATES: the Javanese dish is "
        "a charcoal-cooked chicken noodle in clear or lightly thickened broth, nothing like it.",
  blurb="Blanched yellow noodles under a thick sweet-savoury gravy of boiled sweet potato, "
        "tomato paste and shrimp stock - or pork-rib stock at Chinese stalls, which fixes it as "
        "non-halal. Bean sprouts, boiled potato, hard-boiled egg, fried beancurd, prawn "
        "fritters, shredded lettuce, fried shallots, ground peanuts, crisp fritter shards, lime "
        "and sambal.",
  penangVariation="The Penang Chinese version uses little or no turmeric, fennel, curry powder "
        "or rempah - which is exactly what separates it from Malay and Indonesian versions - and "
        "notably omits taucu. Penangites call it 'the sweet Jawa mee'. Johor's is savoury, built "
        "on shallot, garlic, ginger, lemongrass and dried shrimp, and boosted with curry and "
        "turmeric powder when meatless.",
  contested="Three competing accounts. Chinese-Javanese Peranakans migrating from Medan and "
        "Malacca developed it locally; or direct Javanese or Minangkabau settlers introduced it; "
        "or it is a local Penang Chinese invention wearing an exotic name. Malay Mail's "
        "assessment is the honest default and the graph adopts it: the origin is unclear, but "
        "the name points at the Java Peranakan heyday and the ingredients point at several "
        "cultures at once. NLB adds a wonderfully unromantic detail - the Penang gravy is "
        "flavoured with a can of tomato soup.",
  confidence="low", sources=["malaymail-mee-jawa", "nlb-mee-jawa"])

D("d-mee-rebus", "Mee Rebus", malay="mi rebus", zh="马来卤面 ('Malay lor mee')",
  aka=["mie kuah"], penangStatus="core", tryStatus="tried", style="gravy",
  etymology="Malay rebus = to boil or blanch. 'Boiled noodles' - named, like lam mee, for a "
        "process rather than a flavour. The Chinese-Malaysian folk name for it, 'Malay lor mee', "
        "is a small masterpiece of cross-community classification.",
  blurb="Blanched yellow noodles under kuah: a thick gravy of grago shrimp, flour, sugar and "
        "salt, aromatised with lemongrass, ginger and shallots, enriched with mutton, prawns or "
        "crab, thickened with mashed sweet potato and sometimes ground peanut, and seasoned with "
        "curry powder, taucu and palm sugar. Bean sprouts, halved egg, tau kwa, fried shallots, "
        "green chilli, a drizzle of dark soy and calamansi.",
  penangVariation="Mee rebus and Penang mee jawa are the most confused pair in Malaysian food "
        "writing. They share the noodle, the sweet-potato thickening, the ground peanut, the "
        "garnish set and the lime. They differ on which side of the halal line they sit, on "
        "taucu versus tomato, on whether the gravy is actively spiced or barely spiced, and on "
        "whether fritters are integral. Model them as SIBLINGS with mutual influence, not as "
        "parent and child.",
  contested="Four live theories: derived from mie jawa (though NLB notes the Javanese dish bears "
        "little resemblance to the current form); carried south from the northern states by "
        "Indian Muslim peddlers working from a kandar pole (NLB's own opening line commits to "
        "this, which makes it the strongest single attribution); created in Singapore before "
        "WWII per Khir Johari; or a 15th-17th century Penang Peranakan dish, which is implausible "
        "on its face since alkaline yellow wheat noodles were not a mass commodity here then.",
  confidence="medium", sources=["nlb-mee-rebus", "khir-johari-malay-food"])

D("d-lemak-laksa", "Lemak Laksa (Nyonya Laksa)", aka=["laksa lemak", "laksa Nyonya",
  "'Siamese laksa' (Penang usage)"], penangStatus="present", tryStatus="tried", style="soup",
  etymology="lemak is a Malay culinary descriptor, not a dish name: it denotes the specific "
        "quality of richness that coconut milk imparts. Nyonya signals Peranakan provenance and "
        "the fact that Peranakan cuisine is women's cuisine.",
  blurb="Coconut-milk gravy over a rempah of shallot, garlic, candlenut, lemongrass, galangal, "
        "turmeric, dried chilli and belacan; dried shrimp; prawn, fish cake, tau pok, bean "
        "sprouts, egg; daun kesum; sambal on the side.",
  penangVariation="Decisively secondary to asam laksa in Penang, sometimes sold as a half-and-"
        "half hybrid in one bowl. The revealing detail is that Penang cooks call the coconut "
        "version 'Siamese' - since Thai laksa IS the coconut one, this is internal evidence "
        "that Penang's own self-understanding places the sour, coconut-free style as the local "
        "norm and the creamy style as the imported other.",
  contested="Laksa lemak and curry mee are the same coconut-curry-noodle family, distinguished "
        "by regional convention, noodle choice and toppings rather than by any hard line - "
        "Wikipedia says outright that 'laksa' is an alternate name for curry mee. Any claim of "
        "directional descent between them is unsupported.",
  confidence="medium", sources=["wiki-laksa", "michelin-malaysia-regional"])

D("d-kolo-mee", "Kolo Mee", zh="哥羅麵 / 乾撈麵", malay="mi kolok",
  aka=["mee kolo", "mi kering (Iban)", "mi rangkai (Iban)"],
  penangStatus="present", tryStatus="tried", style="dry", homeRegion="r-kuching",
  etymology="'Kolo' is the same 撈 lou toss-word as in kon lo mee and lo hei - 'dry mix, dry "
        "tossed'. The characters 哥羅 are purely phonetic. Gazetted as a Malaysian heritage food "
        "in the 2024 Declaration of Heritage Objects.",
  blurb="Thin springy egg noodles blanched, shocked and tossed in rendered pork fat and crisp "
        "lard, shallot oil and fried shallots, and light soy; topped with minced pork, sliced "
        "char siu, spring onion, pickled green chilli, with a bowl of clear soup on the side. "
        "Three canonical styles: white/plain, red with char siu marinade tossed through, and "
        "black with dark soy.",
  contested="Hakka, not Foochow. The evidence: the dish derives from Hakka Tai Pu / yan mee "
        "('salted noodles') from Dabu county, Meizhou, and the credited pioneer is Kiew Shao "
        "Nyap, a native of Baihou, Dabu, who reached Kuching in the 1920s. Sources that assign "
        "kolo mee to the Foochow are conflating Kuching - Hakka, Hokkien and Teochew - with "
        "Sibu, which is Foochow and whose noodle is kampua mee. The same conflation afflicts "
        "Sarawak laksa. The char siu is probably a Cantonese contribution, so the Cantonese and "
        "Hakka lines converged here.",
  halalNote="One of the very few Chinese-origin pork dishes in this graph to have generated a "
        "fully accepted halal parallel with its own indigenous-language names.",
  confidence="medium", sources=["wiki-kolo-mee", "medium-kolo-mee", "borneo-post-sarawak-mee",
                                "heritage-2024-declaration"])

D("d-pan-mee", "Pan Mee / Ban Mian", zh="板麵", pojh="pán-mī",
  aka=["ban mian", "mee hoon kueh 麵粉粿", "man-foon-cha-guo (Hakka)", "dao-ma-chet 刀嬤切"],
  penangStatus="present", tryStatus="tried", style="soup or dry", homeRegion="r-kuala-lumpur",
  etymology="板 = board or plank. The usual gloss is that Hakka cooks cut dough into strands "
        "against a wooden straight-edge; that the character describes the flat plank-like shape "
        "is at least as plausible and is what most Malaysians assume. Note the terminological "
        "trap: Fujian 拌麵 (tossed, peanut) is a different dish with a near-identical romanisation.",
  blurb="Fresh hand-formed non-alkaline wheat noodle in a dried-anchovy stock with crisp ikan "
        "bilis garnish, minced pork, dried shiitake, sweet potato leaves or sayur manis, and a "
        "poached egg. Sambal on the side; vinegar to balance.",
  penangVariation="Not a Penang dish. Penang's Chinese population is Hokkien-dominant with a "
        "small Hakka presence; pan mee's centre of gravity is the Klang Valley and the Hakka "
        "tin-belt towns. Where it appears in Penang it is a late-20th-century import.",
  contested="What is sold today is a hybrid, and Wikipedia's formulation is the useful one: the "
        "Hakka shaved dough off a block, the Hokkien rolled and tore it, and the modern hawker "
        "merges both under the Hakka name. The ikan bilis stock is the single clearest marker "
        "that pan mee is a Malaysian dish rather than a transplanted Chinese one - mainland ban "
        "mian uses pork or plain water stock.",
  confidence="high", sources=["wiki-banmian", "radii-chinese-noodles", "voon-2024-hakka"])

# ==================================== PENANG - STILL TO TRY
D("d-asam-laksa", "Penang Asam Laksa", zh="亞參叻沙", malay="laksa asam / laksa Pulau Pinang",
  penangStatus="core", tryStatus="to-try", style="soup",
  blurb="Poached and flaked ikan kembung in a broth soured with tamarind and asam gelugur, "
        "spiced with a rempah of dried chilli, shallot, lemongrass, galangal and belacan. Thick "
        "round rice noodles. A garnish battery of shredded pineapple, cucumber, raw onion, mint, "
        "sliced bunga kantan, and a dark dollop of hae ko swirled in at the end. NO coconut milk "
        "at all - the single most important contrast with the entire curry-laksa family.",
  penangVariation="Against laksa Kedah, the differences are precise and small: Penang shreds "
        "the fish into visible strands where Kedah pounds it into the broth; Penang leads with "
        "tamarind juice where Kedah leads with dried gelugur slices; Penang uses fresh red "
        "chilli where Kedah uses dried; Penang adds pineapple, bunga kantan and hae ko where "
        "Kedah adds daun selom and sambal kelapa. Against Johor laksa - grilled wolf herring, "
        "thick coconut gravy, served with spaghetti - it is a different animal entirely.",
  contested="Direction of travel genuinely unresolved. Penang was part of Kedah until 1786 and "
        "the island's Malay substrate IS Kedahan, so it is at least as plausible that Penang "
        "asam laksa is a Peranakan-Chinese elaboration of an existing Kedah Malay sour fish "
        "laksa - adding hae ko, pineapple and Nyonya knife-work - as that the influence ran the "
        "other way. English-language sources overwhelmingly narrate Penang as origin and Kedah "
        "as variant; that is almost certainly an artefact of Penang's tourism prominence rather "
        "than evidence. The graph encodes the uncertainty rather than picking a side.",
  confidence="medium", sources=["wiki-laksa", "hutton-nyonya", "season-with-spice-asam-laksa",
                                "ummi-laksa-guide"],
  flags=["penang-first-framing-is-probable-prominence-bias"])

D("d-white-curry-mee", "Penang White Curry Mee", malay="mi kari putih",
  penangStatus="core", tryStatus="to-try", style="soup",
  blurb="A curry mee in which the coconut-and-spice broth is kept pale and mild and the chilli "
        "sambal is served entirely separately, so the eater controls the dose.",
  contested="Both real and marketed, and the marketing came second. The Air Itam sisters, whose "
        "stall dates from 1946, have sold exactly this configuration for over sixty years, and "
        "Tony Boey names them among the pioneers while stating plainly that nobody knows who "
        "invented it. More to the point, sambal-on-the-side is the NORMAL Penang curry mee "
        "convention, not an exception - so 'white curry mee' is arguably just an accurate name "
        "for what Penang curry mee always was, coined retrospectively to distinguish it from "
        "redder southern curry laksa. What is unambiguous is the reification: the phrase became "
        "an international dish category through MyKuali's 2012 instant product and its 2014 "
        "Ramen Rater ranking. Flag any source presenting it as an ancient named tradition as "
        "overclaiming.",
  confidence="medium", sources=["penang-wikia-white-curry", "mykuali", "air-itam-curry-mee"],
  flags=["post-2012-reification"])

D("d-mee-goreng-mamak", "Mee Goreng Mamak", zh="印度炒面", malay="mi goreng mamak",
  penangStatus="core", tryStatus="to-try", style="fried",
  etymology="mee from Hokkien 麵, goreng Malay for 'fried', mamak from Tamil மாமா 'maternal "
        "uncle'. Chinese noun + Malay verb + Tamil honorific: the entire fusion encoded in four "
        "syllables. This is the single most efficient illustration of Penang creolisation "
        "available.",
  blurb="Yellow noodles wok-fried hard with bottled tomato and chilli sauce, kicap manis, boiled "
        "potato cubes, firm tofu, cabbage, bean sprouts, egg scrambled through, mutton or "
        "chicken, sometimes sotong; finished with calamansi, fried shallot and coriander.",
  penangVariation="Penang is credited as the origin, with Bangkok Lane Mee Goreng in Pulau Tikus "
        "cited among the oldest, from a pushcart, now over ninety years old. The Penang style is "
        "notably WET - gravy is added, and at Bangkok Lane it is borrowed from the adjacent "
        "pasembur stall, which is a transmission mechanism you can watch happening.",
  fusion="The dish cannot be found in India, and the community distinction is material. Tamil "
        "HINDU migration went overwhelmingly into estate work with a different food repertoire. "
        "Tamil MUSLIM migration was mercantile and urban - and being Muslim, they could sell to "
        "Malays and buy Chinese noodles. Halal is the enabling constraint that created the mamak "
        "stall as an inter-communal institution.",
  contested="The Penang-origin claim is widely stated and archivally undemonstrated. The claim "
        "that it arose by adapting Chinese fried noodles is structurally sound even if "
        "undocumented - the wok, the noodle and the format are transparently Chinese. Indonesian "
        "mie goreng is a parallel but genealogically separate solution to the same problem, "
        "sweetened with kecap manis.",
  confidence="medium", sources=["wiki-mee-goreng-mamak", "oed-mamak"])

D("d-maggi-goreng", "Maggi Goreng", penangStatus="core", tryStatus="to-try", style="fried",
  blurb="Mee goreng mamak with the fresh yellow noodle swapped for a rehydrated Maggi block, "
        "usually the Kari flavour, with or without the sachet. A substitution variant, not an "
        "independent invention - which makes it the cleanest possible example of an industrial "
        "product entering a traditional preparation.",
  contested="No inventor is recorded, and none should be accepted. The value of this dish to the "
        "graph is chronological: Maggi arrived in Malaysia in 1969 with tomato ketchup and chilli "
        "sauce, and in 1971 with two-minute noodles in Kari and Ayam. Maggi goreng therefore "
        "CANNOT predate 1971. Almost every other dish here has a fuzzy nineteenth-century origin; "
        "this one has a supply-chain birthday, and it anchors the timeline.",
  confidence="medium", sources=["nestle-maggi-malaysia", "wiki-mee-goreng-mamak"])

D("d-char-bee-hoon", "Char Bee Hoon / Fried Bee Hoon", zh="炒米粉", malay="bihun goreng (Chinese style)",
  penangStatus="core", tryStatus="to-try", style="fried",
  blurb="Rice vermicelli wok-fried with garlic, shallot, egg, cabbage or choy sum, bean sprouts, "
        "dried shrimp, sometimes pork or fishcake; light and dark soy and white pepper. In "
        "Penang this is the backbone of the economy bee hoon breakfast tray, sold by selection.",
  penangVariation="Penang's bee hoon culture is Hokkien-standard rather than distinctive - which "
        "is itself worth saying, because it means bee hoon is the neutral carrier the island "
        "uses to make every other dish available in a second form.",
  confidence="high", sources=["wiki-penang-cuisine"])

D("d-koay-chiap", "Koay Chiap", zh="粿汁", pojh="kóe-chiap",
  aka=["kway chap", "kuay jap", "koay chiak (Penang spelling variant)"],
  penangStatus="present", tryStatus="to-try", style="braise",
  etymology="粿 rice-flour sheet + 汁 juice, broth, gravy. Crucially 汁 chiap is NOT 湯 th'ng: "
        "the dish is named for a thick soy-dark braising liquid, not a clear soup, which "
        "distinguishes it from koay teow th'ng at the level of the name.",
  blurb="Broad flat rice sheets, folded loosely, in a dark lou braise with five-spice, star "
        "anise and cassia. Braised meat and offal, braised egg, tau kwa and tau pok, preserved "
        "salted vegetable, peanuts; chilli-vinegar dip.",
  penangVariation="Penang substitutes DUCK for pork - duck meat and duck offal alongside pig's "
        "ear, braised egg and beancurd - which is consistent with the island's Teochew hawkers "
        "having built their whole repertoire around duck. Overwhelmingly evening and supper trade.",
  contested="Teochew provenance is solid. The 'Ming dynasty, 400 years ago' dating that "
        "circulates is folk chronology. The genuinely valuable datum is the three-way divergence "
        "by host country: the Chaoshan home form has a WHITE broth made with rice milk, the "
        "Straits form is a dark soy braise, and the Thai form is clear. One diaspora dish, three "
        "countries, three broths - and the ancestral form is not the dark one.",
  confidence="high", sources=["wiki-kway-chap", "roots-kway-chap"])

D("d-bak-chor-mee", "Bak Chor Mee", zh="肉脞麵", pojh="bah-chhò-mī",
  penangStatus="rare", tryStatus="to-try", style="dry or soup", homeRegion="r-singapore",
  etymology="Literally 'minced-meat noodle'. The character 脞 (cuǒ, finely chopped) is rare "
        "enough that many stalls write 肉挫 instead.",
  blurb="Blanched minced pork, pork slices, pork liver, braised shiitake, meatballs or fish "
        "balls, wonton, crisp lard croutons, fried garlic, scallion, coriander, Teochew fish "
        "sauce. The dry version's chilli-paste-plus-black-vinegar dressing is the identifying "
        "signature. Diner chooses mee pok or mee kia - that choice is the dish's main axis.",
  penangVariation="Weakly present in Penang, and the reasons are instructive. Demography: "
        "Penang's Teochew community, historically around Kimberley Street - Swatow Kay - is real "
        "but far smaller than Singapore's. Niche occupancy: Penang's Teochew hawkers took the "
        "RICE-noodle niche, koay teow th'ng and koay chiap, rather than the wheat-noodle one, "
        "and koay teow th'ng is functionally bak chor mee's soup cousin with rice noodle "
        "substituted. And condiment culture: the chilli-and-black-vinegar dressing is a 1950s "
        "Singapore development, postdating the period when Penang and Singapore hawker "
        "repertoires were most freely exchanged.",
  contested="The best-provenanced lineage in the entire corpus, and worth stating carefully. "
        "Chen Lianfu left Zhao'an county, FUJIAN - not Chaozhou - in the late 1910s, learned the "
        "noodle trade in Chaozhou city, emigrated to Singapore in the 1920s and hawked in Chai "
        "Chee from a shoulder-pole stall following street-opera crowds; the load bent his back "
        "and his stall became 'Hunchback Noodle'. Eleven descendant stalls still operate and one "
        "supplier still makes the noodle. Note that Zhao'an speech is Hokkien-Teochew "
        "transitional, and the dish's name is Hokkien while its seasoning is Teochew - it sits "
        "ON the boundary rather than inside one tradition.",
  confidence="medium", sources=["johorkaki-bcm", "wiki-mee-pok", "straits-times-bcm"])

D("d-duck-koay-teow", "Duck Koay Teow Th'ng", zh="鴨肉粿條湯",
  penangStatus="core", tryStatus="to-try", style="soup",
  blurb="Clear duck-and-pork-bone broth with dried flounder; poached or braised duck slices and "
        "offal, fish balls (sometimes eel-meat), fish cake, minced pork, fried shallot, spring "
        "onion, celery leaf, white pepper.",
  penangVariation="Penang keeps the SOUP clear and the MEAT braised dark - two techniques in one "
        "bowl, deliberately not mixed. Singapore more often serves braised duck over rice, or "
        "uses the braising liquid itself as the broth, producing a dark bowl. Penang also uses "
        "fish balls and fish cake far more heavily than Chaoshan practice.",
  contested="Teochew, and duck is the Teochew meat of choice. The best-documented Penang lineage "
        "is Lum Lai, founded in the late 1970s by Lau Lum Lai as an itinerant pushcart. Bangkok's "
        "bamee ped tun uses the same five-spice braise from the same Teochew migration, so "
        "Penang and Bangkok duck noodles are siblings, not ancestor and descendant.",
  confidence="high", sources=["lum-lai-duck", "penang-wikia-kuey-teow-thng"])

D("d-beef-noodles-my", "Malaysian Beef Noodles", zh="牛肉麵",
  penangStatus="present", tryStatus="to-try", style="soup or dry",
  blurb="Two Malaysian styles. Clear: beef-bone broth, beef slices, tripe, tendon, beef balls, "
        "coriander, fried garlic and shallot - the Hainanese-associated style. Herbal or braised: "
        "dang gui, wolfberry, cinnamon and star anise, darker and sweeter - associated with the "
        "Klang Valley and Hakka stalls.",
  contested="Disputed, and the honest position is that Malaysian beef noodles are a 1930s-40s "
        "Malayan hawker development made by Hainanese AND Hakka hawkers. Named lineages pull "
        "both ways: KBN King's Seremban traces to Goh Hian Hai, who came from Hainan in the "
        "1940s; Yean Kee in Kluang began as a pushcart in the old market in 1930; but Soong Kee "
        "in KL was started in 1945 by Hakka hawker-chef Siew Koy Soong and its house tradition "
        "derives the dish from Tai Po Hakka noodles, not Hainanese cooking at all. One Malaysian "
        "source traces 'Hainanese beef noodles' to Swatow. The ubiquitous line that they came "
        "from Hainan Island is not evidenced - Hainan's own cuisine is not notably beef-centric.",
  confidence="disputed", sources=["soong-kee", "yean-kee-kluang", "wiki-taiwanese-beef-noodle"],
  flags=["hainan-import-claim-unevidenced"])

D("d-fish-head-bee-hoon", "Fish Head Bee Hoon / Fish Soup Noodles", zh="鱼头米粉",
  penangStatus="rare", tryStatus="to-try", style="soup", homeRegion="r-singapore",
  blurb="Fish stock from boiled bones - snakehead most commonly, also pomfret, batang, garoupa. "
        "Sliced or deep-fried fish, tomato, salted vegetable, yam, ginger, a splash of Chinese "
        "wine or brandy at the end, fried shallot, chilli padi in light soy.",
  penangVariation="A Singapore dish, weakly represented in Penang. Penang's Teochew hawkers "
        "occupy the adjacent niche with fish-ball koay teow th'ng, and Penang's fish-noodle "
        "energy goes into asam laksa - a fish-and-rice-noodle soup in a completely different "
        "idiom, sharing the ingredients and nothing else.",
  contested="Teochew with Hokkien overlap, developed in Singapore, dated to at least the 1920s. "
        "On the white version: genuine emulsion comes from long-boiled bones, but the far more "
        "common route is added evaporated milk, and Teochew purists reject it. The frequent blog "
        "claim that evaporated milk was a Hainanese British-influenced innovation is unsourced.",
  confidence="medium", sources=["wiki-fish-soup-bee-hoon"])

D("d-chee-cheong-fun", "Penang Chee Cheong Fun", zh="豬腸粉",
  penangStatus="core", tryStatus="to-try", style="steamed",
  blurb="Steamed rice sheet, rolled and cut into segments, drenched in hae ko blended with "
        "thnee cheo, then topped with sesame seeds, fried shallot, chilli paste and sometimes "
        "crushed peanuts. Sweet, faintly funky-fishy, dark.",
  penangVariation="The clearest single example in the Penang repertoire of a CANTONESE carrier "
        "dish reseasoned with a Malay-archipelago fermented-seafood condiment. Same noodle as "
        "Hong Kong, KL and Ipoh; radically different flavour vector - Penang is the only version "
        "whose sauce is built on fermented shrimp rather than soy, bean or sesame. KL uses sweet "
        "fermented bean paste; Ipoh runs a dry version with dried shrimp and a wet one flooded "
        "with curry; Hong Kong treats the sheet as the point and the sauce as incidental.",
  confidence="high", sources=["penang-wikia-ccf", "wiki-chee-cheong-fun"])

D("d-mee-soto", "Mee Soto", malay="mi soto", penangStatus="present", tryStatus="to-try",
  style="soup",
  etymology="soto is the Javanese generic for a spiced meat-and-broth soup, and one widely "
        "cited etymology derives it from a Chinese offal-soup term via Hokkien or Teochew - "
        "which would make soto itself a Chinese loan into Javanese. Appropriate, since soto's "
        "early vendors in Java were often Chinese. The recursion is pleasing: soto is already a "
        "Sino-Javanese creole dish before it becomes a Malay dish in Penang.",
  blurb="Clear but deeply aromatic turmeric-yellow chicken broth with lemongrass, galangal, "
        "garlic, shallot, candlenut, coriander seed and cumin; shredded poached chicken, bean "
        "sprouts, Chinese celery, fried shallots, and near-obligatory begedil - mashed-potato-"
        "and-beef fritters, themselves a Dutch frikadel loan into Indonesian. Sambal kicap on "
        "the side.",
  penangVariation="The clearest Javanese node in the Penang graph, and it demonstrates that the "
        "Javanese thread reached Penang as a WHOLE DISH rather than only as ingredients - unlike "
        "petis and taucu, which arrived as components and dissolved into other dishes. Mamak "
        "versions run spicier and sometimes more curry-inflected, and sit beside mee goreng and "
        "mee rebus on the same board.",
  confidence="high", sources=["wiki-mee-soto"])

D("d-you-mee", "'You Mee' - the noodle option, not a dish", zh="幼麵",
  penangStatus="present", tryStatus="to-try",
  blurb="In a Malaysian pan mee shop, 'you mee' is a menu option: the thin round strand version "
        "of the same dough sold as ban mian and mee hoon kueh. It is not a separate dish, and "
        "the physical noodle is identical to Hokkien/Teochew mee kia and to Cantonese wonton "
        "noodle. See the name node for the other three things people mean by the phrase.",
  confidence="high", sources=["wiki-banmian", "wiki-mee-pok"])

D("d-yi-mein", "Yi Mein / E-Fu Noodles", zh="伊麵 / 伊府麵", aka=["yee mee", "i fu mie", "sau mein 壽麵"],
  penangStatus="present", tryStatus="to-try", style="braised or soup",
  etymology="'The Yi family's noodle', after Yi Bingshou (1754-1815), Qing calligrapher, poet "
        "and prefect of Huizhou; 府 fu denotes the official's residence.",
  blurb="The canonical banquet form is 乾燒伊麵, braised dry with shiitake and yellow Chinese "
        "chives in oyster sauce - the two are near-obligatory. Also crab and lobster versions, "
        "and in soup.",
  penangVariation="In Malaysia 'yee mee' is everyday coffeeshop food rather than banquet food: "
        "claypot yee mee, wat tan yee mee, soupy yee mee with fishcake and liver. Penang stalls "
        "offer it as an interchangeable noodle alongside koay teow, bee hoon and yellow mee.",
  ritual="A longevity noodle - served at birthdays and Lunar New Year, strands not to be cut. "
        "Specifically the main dish at Hakka birthday banquets.",
  contested="Two traditional origin tellings, neither contemporaneously documented: deliberate "
        "invention of a shelf-stable pre-cooked noodle for unexpected guests, or a cook dropping "
        "noodles into hot oil by accident. The widely repeated claim that yi mein is 'the "
        "precursor of instant noodles' is a rhetorical framing, not a demonstrated descent to "
        "Ando Momofuku's 1958 product - though the fry-dry-rehydrate parallel is real and belongs "
        "in the graph as a technique link.",
  confidence="medium", sources=["wiki-yi-mein"])

D("d-ipoh-hor-fun", "Ipoh Hor Fun / Kai Si Hor Fun", zh="怡保雞絲河粉",
  penangStatus="absent", tryStatus="to-try", style="soup", homeRegion="r-ipoh-kinta",
  blurb="Silky thin hor fun in a clear broth of chicken PLUS prawn heads and shells, with "
        "poached shredded chicken, blanched prawns, chives, and pickled green chilli in soy.",
  contested="Cantonese in origin - hor fun is named after Shahe in Guangzhou - but the complication "
        "is the good part. Ipoh Echo reports that the two most celebrated kai si hor fun stalls, "
        "Thean Chun and the Loke Wooi Kee stall, were founded by HOKKIEN immigrants from Nan'an, "
        "Fujian. Their reading: the Hokkien palate is used to combining meat and seafood in one "
        "bowl, as in Hokkien mee, which is why Ipoh's version is a prawn-and-chicken broth rather "
        "than a pure chicken one. The prawn element - Tanjung Tualang shells boiled down for the "
        "orange tint - is a local innovation absent from the Chinese original. Separately: the "
        "universally repeated limestone-water claim is NOT evidenced for noodles. The geology is "
        "real and the bean-sprout version is the strongest of the family, but no published "
        "analysis links Ipoh water chemistry to rice-noodle texture, which is dominated by rice "
        "variety, flour age, hydration and steaming. The honest formulation: Ipoh has a "
        "concentrated, competitive, multi-generational noodle trade and attributes its results "
        "to the water.",
  confidence="medium", sources=["ipoh-echo-kai-si-hor-fun", "cgtn-cantonese-ipoh"],
  flags=["limestone-water-claim-unevidenced"])

D("d-thai-boat-noodles", "Thai Boat Noodles", zh="—", aka=["kuay teow reua", "ก๋วยเตี๋ยวเรือ"],
  penangStatus="present", tryStatus="to-try", style="soup", homeRegion="r-rangsit",
  blurb="Both pork and beef in one bowl; dark soy; fermented bean curd; cinnamon and star anise; "
        "meatballs, liver, morning glory, bean sprouts, fried garlic, pork cracklings, holy "
        "basil, chilli flakes - and the defining thickener, fresh pig's or cow's blood mixed with "
        "salt and spices, which gives the near-black colour.",
  penangVariation="A 21st-century import to Malaysia, arriving through Thai restaurant chains, "
        "the northern-Malaysian appetite for Thai food, and cross-border traffic. A restaurant "
        "dish in Penang, not a hawker-cart dish, and the blood is often omitted.",
  contested="The small bowl has a good functional explanation: one vendor paddled, cooked, "
        "served, took money and washed up alone, and a large bowl would spill in the hand-off "
        "from boat to bank. But claims that boat noodles were sold from canoes in Ayutthaya "
        "between the 12th and 16th centuries are almost certainly anachronistic - the dish's own "
        "name is a Teochew loanword, mass Teochew settlement in Siam dates from the late 18th "
        "century, and Rangsit's canals were dug in the 1890s. The story that the dark broth "
        "existed to hide blood residue from butchering is food-media rationalisation.",
  confidence="medium", sources=["wiki-boat-noodles"],
  flags=["medieval-ayutthaya-claim-likely-false"])

D("d-tom-yum-mee", "Tom Yum Noodles", malay="mi tom yam", penangStatus="present",
  tryStatus="to-try", style="soup",
  blurb="In Penang, effectively a naturalised local dish: sold in Chinese coffeeshops, at Malay "
        "warung and at Thai-run stalls, with Raja Uda and Butterworth a recognised mainland "
        "cluster.",
  penangVariation="The Penang style is a thick, red, chilli-paste-heavy broth with a heavy hand "
        "of lime and bunga kantan, distinguished by local writers from the clear, tangy, "
        "herb-forward Thai style. Customers select their own ingredients from a tray, which is a "
        "Malaysian hawker convention rather than a Thai one. Ghee Lian on Perak Road opened in "
        "2012 with a green tom yum noodle - local invention inside an imported category.",
  confidence="medium", sources=["wiki-boat-noodles", "michelin-ckt"])

D("d-sarawak-laksa", "Sarawak Laksa", penangStatus="rare", tryStatus="to-try", style="soup",
  homeRegion="r-kuching",
  blurb="Thin rice vermicelli - NOT thick laksa noodle, which is a meaningful divergence. A "
        "rempah of garlic, shallot, lemongrass, galangal, peanuts, candlenuts, dried and fresh "
        "chilli, coriander, cumin, fennel, sesame, cinnamon, star anise, pepper and belacan; a "
        "broth of prawn stock, chicken stock, coconut milk and tamarind; finished with sambal "
        "belacan and calamansi.",
  fusion="Tony Boey's component analysis is the most useful framing available: prawn stock from "
        "the Hokkien prawn noodle, chicken stock Cantonese, coconut milk Nyonya and Malay, "
        "peanut from Malay satay sauce. Presented as inference, not documented fact.",
  contested="Kuching, not Sibu - the credited originator, Goh Lik Teck, was TEOCHEW, peddling on "
        "Carpenter Street in the 1940s, and the sole traceable source for that is a single "
        "chapter in a 2015 state tourism guide which gives no description of what Goh's laksa "
        "was actually like. Flag any source attributing Sarawak laksa to the Foochow as "
        "conflating Kuching with Sibu. The real mechanism of standardisation is industrial: Tan "
        "Yong Him's Swallow-brand rempah premix from the 1960s created and then froze the modern "
        "dish, thirty years before MyKuali did the same for white curry mee.",
  confidence="medium", sources=["johorkaki-sarawak-laksa", "ong-flavours-of-sarawak",
                                "bourdain-no-reservations-borneo"])

D("d-bihun-goreng", "Bihun Goreng (Malay & Mamak styles)", malay="bihun goreng",
  penangStatus="core", tryStatus="to-try", style="fried",
  blurb="Three parallel traditions use the same noodle and do not merge. Chinese char bee hoon "
        "is soy-forward, garlic-and-shallot based, comparatively pale. Malay bihun goreng is "
        "built on a pounded dried-chilli rempah with kicap manis, tomato, egg and tofu puffs. "
        "Mamak bihun goreng adds bottled tomato ketchup and chilli sauce, sweeter and tangier "
        "than the Malay style and milder than mee goreng mamak, finished with lime.",
  penangVariation="They coexist street by street without merging, because of the halal boundary. "
        "That is the entire point: the noodle is shared infrastructure, the seasoning is where "
        "the community lives.",
  confidence="high", sources=["wiki-mee-goreng-mamak", "wiki-penang-cuisine"])

D("d-chilli-pan-mee", "Chilli Pan Mee", penangStatus="present", tryStatus="wildcard",
  style="dry", homeRegion="r-kuala-lumpur",
  blurb="Dry noodles at spaghetti gauge with minced pork, fried shallot, crisp anchovies, a "
        "poached egg stirred through, and a proprietary dried-chilli-flake condiment.",
  contested="One of the better-attested Malaysian invention claims and still thin. Restoran Kin "
        "Kin, founded 1985 by Tan Kok Hong at a stall under a tree in Chow Kit. Tan's own "
        "account: he sold conventional pan mee in clear pork broth, noticed customers spooning "
        "chilli in, and built a dry version around a chilli condiment he still does not sell "
        "separately; the runny egg came later. The evidence base is his testimony repeated across "
        "food media for three decades with no competing claimant - and Wikipedia's citation for "
        "'invented in Chow Kit' is a 2017 food blog, which is exactly the citation-laundering "
        "pattern to watch for. Flag the frequent blog assertion that chilli pan mee is 'a "
        "traditional Hakka dish': it is a documented 1980s KL invention on a Hakka substrate.",
  confidence="medium", sources=["kin-kin", "rakyat-post-kin-kin", "wiki-banmian"],
  flags=["not-traditional-hakka"])

D("d-longevity-mee-sua", "Longevity / Birthday Mee Sua", zh="長壽麵 / 麵線",
  penangStatus="present", tryStatus="wildcard", style="soup",
  blurb="Mee sua in a sesame-oil-and-rice-wine or clear chicken broth with a hard-boiled egg "
        "dyed red. Long unbroken strands mean long life; the noodles must not be cut, and ideally "
        "each strand is eaten whole. The red egg extends the full-month newborn custom to all "
        "birthdays. Chives go in because Hokkiens hear 韮 as 久, 'a long time'.",
  penangVariation="The Foochow variant is ang jiu mee sua - mee sua in red glutinous-rice-wine "
        "lees chicken soup, standard for birthdays, post-partum confinement and New Year in "
        "Sitiawan and Sarawak. In Penang Nyonya households the birthday noodle is lam mee instead.",
  confidence="high", sources=["carryitlikeharry-misua", "danielfooddiary-foochow"])

# ==================================== OFF-LIST PENANG DISHES THAT BELONG ON THE MAP
D("d-hokkien-char-penang", "Penang Hokkien Char", zh="福建炒", penangStatus="core",
  tryStatus="off-list", style="fried",
  blurb="Yellow mee plus bee hoon, only a tinge of dark soy, prawns, pork, egg, bean sprout and "
        "chives, with smoky wok hei dominant over sauce. Light brown rather than black.",
  penangVariation="Penangites use 'Hokkien char' precisely to avoid the collision with Penang "
        "Hokkien mee, which is a soup. The dish is closer in spirit to char kway teow than to KL "
        "Hokkien mee.", confidence="high", sources=["johorkaki-kl-sg-hokkien"])

D("d-mee-sotong", "Mee Sotong (Penang mamak)", malay="mee sotong",
  aka=["mee sotong sambal", "mee goreng sotong", "Jones Road mee goreng"],
  penangStatus="core", tryStatus="tried", style="fried",
  blurb="Yellow noodles wok-tossed in a sweet-spicy sambal or squid sauce built on a "
        "chilli-and-tomato base with the squid's own liquor; boiled potato, bean sprouts, egg, "
        "fried tofu; fried shallots and a calamansi wedge that is not optional. The squid is "
        "sliced thin and cooked INTO the sauce rather than laid on top.",
  penangVariation="A Penang-only mamak invention, and by most accounts not found elsewhere in "
        "this form. Two distinct stall lineages, which is worth keeping apart: **Hameed 'Pata'** "
        "at Kota Selera, Padang Kota Lama, whose family account has the father selling mee rebus "
        "and mee goreng from 1942 with the sotong specialisation dating to 1978; and **Jones "
        "Road**, from the Jalan Jones / Tingkat Jones T-junction in Pulau Tikus since the 1980s, "
        "now operating out of Sin Hup Aun Cafe. The Jones Road version leads with sambal gravy "
        "rather than a dark squid sauce - the same wet/dry split that runs through Penang mee "
        "goreng generally.",
  significance="The clean counter-example to any model that treats Penang's fried-noodle culture "
        "as Chinese-only: a sweet-savoury, wok-fried seafood noodle occupying the same conceptual "
        "slot as char kway teow, arrived at through an entirely Indian-Muslim route. It is also "
        "the dish that finally puts a Tamil-Muslim-carried bowl into the series - the mamak "
        "thread was the largest hole in the run.",
  contested="Both lineages are stall-sourced family history with no archival support, which is "
        "the norm for this genre. The dates - 1942, 1978, 'the 1980s' - should be read as "
        "tradition rather than record.",
  confidence="medium", sources=["hameed-pata", "pp-field-mee-sotong"])

D("d-mee-udang", "Mee Udang", malay="mee udang", penangStatus="core", tryStatus="off-list",
  style="gravy or fried",
  blurb="Whole unpeeled prawns - size is the selling point - in a tomato-based gravy with chilli "
        "paste, shallot, garlic and tamarind; boiled egg, sliced green chilli, sometimes squid, "
        "lime, bean sprouts. Ordered rebus or goreng.",
  penangVariation="A Malay dish structurally related to mee jawa and mee rebus - the same "
        "tomato-and-chilli gravy logic - built around large prawns. Two clusters: Teluk Kumbar on "
        "the island's southwest coast, which has become a style name used all over Penang, and "
        "Sungai Dua on the mainland near the Muda estuary and its prawn fishery.",
  contested="No source documents when or by whom mee udang was established at Sungai Dua. Food "
        "media treat it as a destination without a history. This is exactly the kind of recent, "
        "undocumented MALAY hawker geography that Chinese hawker dishes get written up for and "
        "Malay ones do not - a bias in the sources, not in the dishes.",
  confidence="medium", sources=["penang-traveltips-mee-udang"], flags=["documentation-gap"])

D("d-mee-siam", "Mee Siam", malay="mi siam", penangStatus="present", tryStatus="off-list",
  style="dry or gravy",
  etymology="'Siamese noodles' - and there is no such dish in Thai cuisine. Khir Johari's "
        "reading is the most economical: the name refers to the Thai-imported dried vermicelli, "
        "not to the dish, exactly as laksa originally named a noodle. The alternative reading is "
        "that it names a flavour register - hot, sour, sweet - that Malayan eaters heard as "
        "'Thai-tasting'.",
  blurb="Rice vermicelli with a rempah of dried chilli, shallot, garlic, candlenut, lemongrass "
        "and belacan; taucu; tamarind; sugar; dried shrimp; prawns; firm beancurd; bean sprouts; "
        "garlic chives; hard-boiled egg; lime. Note the taucu-plus-tamarind-plus-dried-shrimp "
        "triad - it is exactly the flavour spine of mee rebus, minus the sweet potato.",
  penangVariation="Malaysia including Penang runs the dry stir-fried version; Singapore's "
        "canonical form is wet, fried bee hoon in a spicy-sweet-sour gravy.",
  contested="Four named disputants, and the graph carries all four rather than resolving them. "
        "Wendy Hutton: originates in Penang, carried south by Straits Chinese families in the "
        "early 1800s. Sylvia Tan: Malay origin. Tan Chee-Beng: wholly Peranakan. Chua Beng Huat: "
        "an example of hybridity, i.e. the question is malformed. Note the floor date - the first "
        "Singapore newspaper mention is 1950, hawkers at the Esplanade selling to evening "
        "strollers. If any Thai dish is the ancestor, mi kathi is the candidate, but the "
        "direction of borrowing is undetermined and mi kathi is coconut-based.",
  confidence="disputed", sources=["wiki-mee-siam", "nlb-mee-siam", "hutton-nyonya",
                                  "khir-johari-malay-food"])

D("d-char-koay-kak", "Char Koay Kak", zh="炒粿角", penangStatus="core", tryStatus="off-list",
  style="fried",
  blurb="Cubes of steamed rice-flour cake wok-fried with egg, bean sprouts, chives, preserved "
        "radish and dark soy. Attributed to Penang's Teochew community, who brought the steamed "
        "rice-cake tradition from southern China, with traces of Hokkien influence in the "
        "ingredients. The same 粿 as in char kway teow - a different cut of the same technology.",
  confidence="medium", sources=["visitpenang-char-koay-kak"])

D("d-mee-hailam", "Mee Hailam", zh="海南麵", penangStatus="present", tryStatus="off-list",
  style="fried",
  blurb="Stir-fried yellow egg noodles with chicken, pork or seafood and abundant vegetables in "
        "a dark-soy-seasoned gravy, served with calamansi.",
  significance="The Hainanese contribution to noodles is ADAPTIVE rather than ancestral. This is "
        "a Malayan invention by Hainanese cooks, not a transplant from Hainan - the noodle "
        "equivalent of chicken chop and 'Western food'. It is what happens when the only dialect "
        "group whose economic niche was cooking, and cooking for non-Chinese employers, opens "
        "its own shop.", confidence="high", sources=["tasteasianfood-mee-hailam", "mothership-hainanese"])

D("d-wat-tan-hor", "Wat Tan Hor", zh="滑蛋河", aka=["char hor fun", "moonlight hor fun 月光河"],
  penangStatus="present", tryStatus="off-list", style="fried with gravy",
  etymology="滑 wat silky + 蛋 tan egg + 河 hor fun. 'Silky-egg hor fun'. Moonlight is named for "
        "the raw yolk set on top, resembling a moon, stirred through by the diner.",
  blurb="The noodles are first fried hard and dry over high heat to build wok hei and char the "
        "edges - essential - then plated and covered with stock thickened with cornflour into "
        "which beaten egg is drizzled in ribbons at the last second. The same gravy is routinely "
        "poured over yee mee or crisp-fried egg noodle instead.",
  penangVariation="Present in Cantonese-run tai chow stalls rather than as a signature hawker "
        "dish. Ipoh and the Klang Valley are the strongholds.",
  contested="No named inventor and no useful origin legend, which is itself notable: wat tan hor "
        "is a technique dish, not a story dish.", confidence="high", sources=["wiki-penang-cuisine"])

D("d-hakka-mee", "Hakka Mee", zh="客家麵", penangStatus="rare", tryStatus="off-list", style="dry",
  homeRegion="r-meizhou-dabu",
  blurb="Springy egg noodles tossed in lard and shallot oil with light soy, topped with minced "
        "pork braised with dried shiitake, fried shallot, a few blanched greens, and soup on the "
        "side. Conventionally paired with yong tau foo.",
  significance="The minced-pork-over-dry-tossed-egg-noodle-with-soup-on-the-side architecture is "
        "shared by Hakka mee, Sarawak kolo mee, Sabah sang nyuk mee kon lau, KL's Hakka dry beef "
        "noodle and Teochew dry bak chor mee. Three dialect groups, one architecture, arrived at "
        "independently or by mutual borrowing - which is why the graph carries a shared-"
        "architecture relation distinct from descent.",
  confidence="medium", sources=["michelin-hakka-kl", "voon-2024-hakka"])

D("d-mee-hoon-kueh", "Mee Hoon Kueh", zh="麵粉粿", penangStatus="present", tryStatus="off-list",
  style="soup",
  blurb="The Hokkien method: the same pan mee dough rolled flat and torn by hand into irregular "
        "bite-sized pieces. Best modelled as a variant of pan mee rather than a separate dish - "
        "the same stall sells both.", confidence="high", sources=["wiki-banmian"])

D("d-pasembur-mee-rojak", "Pasembur & Mee Rojak", malay="pasembur / rojak mamak",
  penangStatus="core", tryStatus="off-list", style="salad / tossed noodle",
  blurb="Shredded cucumber and sengkuang, bean sprouts, potato, boiled egg, fried tofu, prawn "
        "and flour fritters, sometimes cuttlefish, chopped to order and drenched in a bright "
        "orange-red sweet-spicy gravy of mashed sweet potato, ground roasted peanuts, chilli and "
        "tamarind. There is also a version with yellow noodles added, sold as mee rojak.",
  significance="Penang mee jawa and Penang mee rojak occupy the SAME flavour space - sweet-potato-"
        "and-peanut gravy over yellow noodles with fritters and egg - reached from two different "
        "kitchens, Chinese on one side and Indian-Muslim on the other, and they have almost "
        "certainly influenced each other on the same street. The distinguishing variables are the "
        "stock, whether the sauce is poured over or tossed through, and tomato paste against "
        "tamarind and chilli.",
  contested="Genuinely three-way disputed: most food historians place its creation with Indian "
        "Muslim hawkers in 20th-century Penang; a competing account has the sauce brought by "
        "Indian Muslim traders in the 18th century; a third credits the Kareem family, selling "
        "in George Town since 1945. The etymology is unresolved.",
  confidence="disputed", sources=["wiki-pasembur"])

# ==================================== ANCESTORS AND COUSINS OUTSIDE PENANG
D("d-xiamen-prawn-noodle", "Xiamen Prawn Noodle", zh="廈門蝦麵 / 夏麵",
  penangStatus="ancestor", homeRegion="r-xiamen",
  blurb="Built on fried prawn heads and pork bones, with prawns and pork slices, optionally "
        "intestine, prawn balls, char siu and duck blood. Unspiced; garnished with coriander and "
        "raw minced garlic. Treated as a seasonal SUMMER dish - hence the pun 夏麵, since 廈 Xia "
        "(Amoy) and 夏 xià (summer) are homophones and the prawns are best in summer.",
  significance="Its survival is what kills the 'Penang Hokkien mee was invented in wartime "
        "scarcity' story.", confidence="high", sources=["johorkaki-hokkien-mee"])

D("d-quanzhou-mian-xian-hu", "Quanzhou Mian Xian Hu", zh="麵線糊", penangStatus="ancestor",
  homeRegion="r-quanzhou",
  blurb="Mainstream breakfast street food in Xiamen and Quanzhou today, with a huge array of "
        "add-ins - offal, oyster, fried fritter. The dish Penang's mee suah koh preserves almost "
        "unchanged as a niche.", confidence="high", sources=["carryitlikeharry-misua"])

D("d-zhangzhou-lor-mian", "Zhangzhou Lor Mian", zh="滷麵", penangStatus="ancestor",
  homeRegion="r-zhangzhou",
  blurb="Thick yellow noodles in a viscous starch-thickened gravy. Sometimes traced to the Tang "
        "as an early fusion of a northern noodle base with southern seafood - and note Putian's "
        "lighter, less-starched, seafood-based version, which suggests the thick-gravy form is "
        "regionally specific within Fujian.", confidence="medium", sources=["wiki-lor-mee"])

D("d-guangzhou-wonton-noodle", "Guangzhou Wonton Noodle", zh="雲吞麵", penangStatus="ancestor",
  homeRegion="r-guangzhou",
  blurb="Noodles and wontons served together in hot soup with vegetables. The dumpling ancestor "
        "húntún goes back to the Tang; the modern wonton-noodle form developed in Qing Guangzhou, "
        "with formal introduction dated to the Tongzhi reign when a Hunan native opened a "
        "noodle restaurant specialising in it. Mak Woon-chi carried it to Hong Kong.",
  confidence="high", sources=["wiki-wonton-noodles"])

D("d-chaoshan-kway-teow-soup", "Chaoshan Kway Teow Soup", zh="粿條湯", penangStatus="ancestor",
  homeRegion="r-chaoshan",
  blurb="The base from which koay teow th'ng, hủ tiếu, kuy teav and Thai kuaitiao all descend. "
        "The Teochew are credited with exporting the RICE-noodle habit into mainland Southeast "
        "Asia, where wheat does not grow well.", confidence="high",
  sources=["penang-wikia-kuey-teow-thng", "ccs-city-teochew"])

D("d-chaoshan-kway-chap", "Chaoshan Kway Chap", zh="粿汁", penangStatus="ancestor",
  homeRegion="r-chaoshan",
  blurb="The ancestral form has a WHITE, opaque broth made with rice milk - not soy-dark at all. "
        "The dark Straits braise is a diaspora development.", confidence="high",
  sources=["wiki-kway-chap", "roots-kway-chap"])

D("d-chaoshan-gan-mian", "Chaoshan Minced Pork Noodle", zh="潮汕干面",
  penangStatus="ancestor", homeRegion="r-chaoshan",
  blurb="Soup or dry noodle with minced meat, offal and dumplings - the template Chen Lianfu "
        "carried to Chai Chee.", confidence="medium", sources=["johorkaki-bcm"])

D("d-dabu-yan-mee", "Dabu Tai Pu / Yan Mee", zh="大埔麵", penangStatus="ancestor",
  homeRegion="r-meizhou-dabu",
  blurb="'Salted noodles'. The Hakka parent of Sarawak kolo mee and of peninsular Hakka mee, and "
        "arguably of KL's Soong Kee dry beef noodle too.", confidence="medium",
  sources=["medium-kolo-mee", "soong-kee"])

D("d-lanzhou-beef-noodle", "Lanzhou Beef Noodles", zh="蘭州牛肉拉面",
  penangStatus="cousin", homeRegion="r-lanzhou",
  blurb="Codified in 1915 by Ma Baozi, a Hui Muslim cook who hawked from a shoulder pole before "
        "opening a shop. His five-element standard: clear broth, white radish, red chilli oil, "
        "green herbs, yellow noodles. Halal by construction, hand-pulled. Present in Penang only "
        "since the 2010s as mainland chain restaurants.",
  significance="The best-documented noodle origin in this graph, with a museum and a municipal "
        "standard - included precisely as the benchmark against which every Malaysian oral-"
        "tradition origin story should be measured.",
  confidence="high", sources=["wiki-lanzhou-beef-noodle"])

D("d-taiwan-beef-noodle", "Taiwanese Red-Braised Beef Noodle", zh="紅燒牛肉麵",
  penangStatus="cousin", homeRegion="r-taiwan",
  blurb="Created in Taiwan, not China, by KMT veterans from Sichuan settled in military "
        "dependants' villages after 1949, first around Gangshan in Kaohsiung using the local "
        "spicy broad-bean paste; then Taipei. Toned down for a broader market and now Taiwan's "
        "de facto national dish. In Penang a restaurant category, not a hawker tradition.",
  confidence="high", sources=["wiki-taiwanese-beef-noodle"])

D("d-kl-hokkien-mee", "KL Hokkien Mee (Hokkien Char Mee)", zh="福建炒麵",
  aka=["tai lok mee 大碌麵", "black noodles"], penangStatus="cousin", homeRegion="r-kuala-lumpur",
  blurb="Thick yellow noodles stir-fried then braise-fried in dark soy with pork, pork liver, "
        "squid, fish cake and cabbage, over a raging charcoal fire, with crisp lard croutons and "
        "sambal belacan on the side.",
  contested="Attributed to Ong Kim Lian of Anxi county, Fujian, who arrived around 1905, started "
        "with a starchy Hokkien festival noodle soup, reinvented it under competitive pressure, "
        "and moved to Petaling Street in 1927 to found Kim Lian Kee. Asked what it was called he "
        "reportedly said 'Hokkien mee', because he was Hokkien and he had cooked it. The 1927 "
        "date and the continuous business are real evidence; the invention claim is family oral "
        "history, and at least one retelling calls the founder 'Wong' mid-article. Treat as a "
        "strong tradition, not a fact.", confidence="medium",
  sources=["kim-lian-kee", "johorkaki-kl-sg-hokkien"])

D("d-singapore-hokkien-mee", "Singapore Hokkien Mee", penangStatus="cousin",
  homeRegion="r-singapore",
  blurb="A wok-fried yellow-noodle-and-bee-hoon dish moistened with prawn stock, served with "
        "sambal and calamansi, sometimes on an opeh palm-bark leaf. Attributed to Fujianese "
        "sailors frying surplus factory noodles over charcoal along Rochor Road after WWII - "
        "widely repeated, plausible, and resting on food-writing tradition rather than archives.",
  confidence="medium", sources=["johorkaki-kl-sg-hokkien"])

D("d-singapore-lor-mee", "Singapore Lor Mee", zh="滷麵", penangStatus="cousin",
  homeRegion="r-singapore",
  blurb="Very thick, dark, glossy cornstarch gravy; ngo hiang five-spice pork rolls; fish cake; "
        "fried fish bits; meat dumplings; half a braised egg - and critically, black vinegar and "
        "raw minced garlic added at the table. Near-gelatinous where Penang's is pourable.",
  confidence="high", sources=["wiki-lor-mee"])

D("d-hu-tieu-nam-vang", "Hủ Tiếu Nam Vang", penangStatus="cousin", homeRegion="r-phnom-penh",
  blurb="Literally 'Phnom Penh koay teow'. Same two Teochew syllables, same clear-broth logic, "
        "with the local pork-and-seafood, rock-sugar and fish-sauce register added. Proof of the "
        "Teochew maritime diaspora as a distribution network rather than a set of isolated "
        "communities.", confidence="high", sources=["penang-wikia-kuey-teow-thng"])

D("d-thai-bamee-ped", "Bamee Ped Tun", penangStatus="cousin", homeRegion="r-bangkok",
  blurb="Braised duck egg noodle using the same five-spice Teochew braise, arriving in Thailand "
        "with 19th and early-20th-century Teochew migration, plus a sweeter braise and the "
        "universal Thai table condiment set. Note that Thai บะหมี่ bamee is a direct loan of "
        "Teochew 肉麵 - the Thai word for egg noodle is a Chinese dialect word, which fixes the "
        "direction of transmission.", confidence="high", sources=["wiki-boat-noodles"])

D("d-mie-jawa-indonesia", "Indonesian Mie Jawa / Bakmi Godhog", penangStatus="cousin",
  homeRegion="r-java-central",
  blurb="Cooked to order over a charcoal anglo, chicken-based, with cabbage and egg, in clear or "
        "lightly thickened broth; the tek-tek name comes from the sound vendors make striking "
        "their woks. An entirely different dish from Penang mee jawa - the two are FALSE COGNATES, "
        "which is worth an explicit edge in the graph.",
  confidence="high", sources=["nlb-mee-jawa"])

D("d-soto-ayam", "Soto Ayam", penangStatus="ancestor", homeRegion="r-java-east",
  blurb="Argued to derive from a Chinese spiced-offal-soup term, acculturated in 19th-century "
        "Java with turmeric and local aromatics. Soto Lamongan and soto Madura are the direct "
        "ancestors of Malaysian mee soto, carried by Javanese and Madurese migrants, probably in "
        "the early 1900s.", confidence="high", sources=["wiki-mee-soto"])

D("d-saoto-suriname", "Saoto (Suriname)", penangStatus="cousin", homeRegion="r-suriname",
  blurb="Javanese indentured labourers carried soto to the Dutch Caribbean. Included as the far "
        "end of the same diaspora that put mee soto on a Penang mamak board - the graph should be "
        "able to show that a Penang dish has a cousin in South America.",
  confidence="medium", sources=["wiki-mee-soto"])

D("d-mi-kathi", "Mi Kathi (Thailand)", penangStatus="cousin", homeRegion="r-patani",
  blurb="Rice vermicelli stir-fried in a coconut, minced pork, prawn, beancurd, salted soybean, "
        "bean sprout and tamarind sauce, eaten in central Thailand, served with sliced omelette "
        "and banana blossom. If any Thai dish is the mee siam ancestor, this is the candidate - "
        "but the direction of borrowing is undetermined and mi kathi is coconut-based where "
        "classic mee siam is not.", confidence="medium", sources=["wiki-mee-siam"])

D("d-singapore-noodles-hk", "'Singapore Noodles'", zh="星洲炒米", penangStatus="fiction",
  homeRegion="r-hong-kong",
  blurb="Rice vermicelli stir-fried with curry powder, char siu, prawn, egg, onion, capsicum and "
        "bean sprouts. A Hong Kong invention of roughly the 1950s-60s, named after Singapore for "
        "exotic appeal, not sold in Singapore except to tourists, and using curry powder that "
        "Singapore's own fried bee hoon does not contain. Included as the graph's worked example "
        "of a fictitious geographic attribution.",
  confidence="high", sources=["wiki-singapore-noodles"])

D("d-kampua-mee", "Kampua Mee", penangStatus="cousin", homeRegion="r-sibu",
  blurb="The Sibu Foochow dry noodle - the actual Foochow noodle, as against kolo mee, which is "
        "the Kuching Hakka one. Sarawak's 'mee' triad is commonly given as kolo, kampua and "
        "ketchup mee.", confidence="medium", sources=["borneo-post-sarawak-mee"])

D("d-sang-nyuk-mee", "Sang Nyuk Mee", zh="生肉麵", penangStatus="cousin", homeRegion="r-tawau",
  blurb="'Fresh meat noodle'. Sabah's actual signature pork noodle: yellow egg noodle or bee "
        "hoon in a peppery clear pork broth, or kon lau - dry-tossed in dark soy and rendered "
        "lard with lard croutons and soup on the side. Reported as invented in 1979 by two "
        "brothers in Tawau. This, not any 'Sabah pan mee', is the dry fried-pork Sabahan noodle.",
  confidence="medium", sources=["wiki-sang-nyuk-mee"])

D("d-tuaran-mee", "Tuaran Mee", zh="斗亞蘭麵", penangStatus="cousin", homeRegion="r-tuaran",
  blurb="Handmade egg noodle cooked in three stages - deep or shallow fried until crisp, briefly "
        "boiled to rehydrate, then stir-fried with egg, vegetables and meat, so the egg coats the "
        "strands into a golden gloss. Char siu, choy sum, sometimes prawn; served with chun kien "
        "spring rolls and sometimes lihing.",
  contested="Created in 1952 by a 'Madam Si' and spreading through Sabah's Hakka communities in "
        "the late 1970s - single-sourced. The better-supported part of the claim is structural: "
        "Tuaran mee REPLACED knife-cut noodles, meaning Sabah's Hakka noodle culture shifted from "
        "a hand-cut wheat-dough tradition to a fried egg-noodle tradition within living memory. "
        "The name is a retronym: Sabahan Hakkas simply said chao men until then.",
  confidence="medium", sources=["wiki-tuaran-mee", "guardian-tuaran-mee"])

D("d-laksa-kedah", "Laksa Kedah / Laksa Utara", penangStatus="cousin", homeRegion="r-kedah",
  blurb="Ikan kembung or selayang POUNDED to a fine paste into the broth, soured mainly with "
        "dried asam keping slices, dried chilli predominant, garnished with belacan, daun selom "
        "and often sambal kelapa. Thicker, smoother, greyer, milder than Penang's, and often "
        "served with a boiled egg. Kedah - Malaysia's rice bowl - makes its own noodles, a point "
        "of local pride.",
  significance="A MALAY dish, not a Peranakan one: halal by default, and with no hae ko in the "
        "classic form. The direction of travel between it and Penang asam laksa is genuinely "
        "unresolved, and the English-language habit of narrating Penang as origin is probably "
        "prominence bias.", confidence="medium", sources=["wiki-laksa", "ummi-laksa-guide"])

D("d-curry-laksa-kl", "Klang Valley Curry Laksa", penangStatus="cousin",
  homeRegion="r-kuala-lumpur",
  blurb="Deep-fried tofu, cockles, long beans and mint as signatures; yellow mee and/or bee "
        "hoon; generally richer and more coconut-forward than Penang's curry mee.",
  confidence="medium", sources=["wiki-laksa"])

D("d-katong-laksa", "Katong Laksa", zh="加東叻沙", penangStatus="cousin", homeRegion="r-singapore",
  blurb="Coconut gravy thickened not only with santan but with GROUND DRIED SHRIMP, giving the "
        "characteristic slightly sandy texture - the observable fact behind the bogus 'spicy "
        "sand' laksa etymology. The noodle is cut short so the whole bowl can be eaten with a "
        "spoon alone: a hawker-speed adaptation with a large cultural payload.",
  contested="Its street career has a documented mechanism: Hainanese domestic workers who cooked "
        "for Peranakan employers learned the household laksa and took it onto the street in "
        "Katong when jobs were scarce after 1945. Plausible, internally consistent, widely "
        "repeated in Singapore food history, and not archivally proven. It is the clearest single "
        "case of domestic service as the channel by which Peranakan home cooking became public "
        "hawker food.", confidence="medium", sources=["johorkaki-katong-laksa", "wiki-laksa"])

D("d-johor-laksa", "Johor Laksa", penangStatus="cousin", homeRegion="r-johor",
  blurb="Grilled wolf herring, thick coconut gravy, and famously served with SPAGHETTI. Included "
        "because it is the reductio of the whole laksa naming problem: if this is laksa, then "
        "laksa names neither a noodle nor a broth but a place in the meal.",
  confidence="medium", sources=["wiki-laksa"])

D("d-mee-bandung", "Mee Bandung Muar", penangStatus="cousin", homeRegion="r-johor",
  blurb="Beef stock with prawns and chillies, thickened with mashed sweet potato, garnished with "
        "fried shallots, boiled egg and spring onion. Closely related to mee rebus, and nothing "
        "to do with Bandung in Java - bandung in Malay denotes a pairing or mixture.",
  confidence="medium", sources=["nlb-mee-rebus"])

D("d-heng-hwa-bee-hoon", "Fried Heng Hwa Bee Hoon", penangStatus="cousin", homeRegion="r-putian",
  blurb="A distinct named item across the Straits, built on Putian's finer, silkier bee hoon. "
        "The culinary calling card of a small dialect group that most dialect maps omit entirely.",
  confidence="medium", sources=["kuchler-1965"])

D("d-fuzhou-red-wine-mee-sua", "Ang Jiu Chicken Mee Sua", zh="紅酒雞麵線",
  penangStatus="cousin", homeRegion="r-fuzhou",
  blurb="Mee sua in red glutinous-rice-wine-lees chicken soup: the Foochow signature, standard "
        "for birthdays, post-partum confinement and Chinese New Year in Sitiawan and Sarawak.",
  confidence="high", sources=["danielfooddiary-foochow"])

D("d-mohinga", "Mohinga (Myanmar)", penangStatus="cousin", homeRegion="r-george-town",
  blurb="Burmese fish-and-rice-noodle breakfast soup. Conceptually a sibling of laksa utara - "
        "fish broth, rice noodles, sour and herbal garnish - and Penang has had a Burmese "
        "community since the early 19th century. But NO source establishes direct transmission, "
        "and the graph records the absence of a link rather than inventing one. Included as an "
        "explicit negative result.",
  confidence="low", sources=["malaymail-beyond-hokkien"], flags=["speculative-do-not-assert"])


# ================================================================== VENUES
def V(nid, label, **kw):
    kw.setdefault("kind", "hawker")
    return N(nid, "venue", label, **kw)

V("v-33-best-food-hub", "33 Best Food Hub", area="Tanjung Tokong, Penang", role="series venue",
  blurb="Three episodes: Jawa Mee, Mee Suah Koh, Mee Rebus - which is a nice accident, since "
        "those three sit on three different cultural threads.")
V("v-hock-beng-88", "Hock Beng 88 Food Court", area="Pulau Tikus, Penang", role="series venue",
  blurb="Kolo Mee and Lam Mee: a Sarawak Hakka dry noodle and a Penang Nyonya birthday soup, "
        "from the same food court.")
V("v-restoran-77", "Restoran 77 Food Yard", area="Penang", role="series venue",
  blurb="Hokkien/Prawn Mee, Char Kway Teow and Curry Mee - the Hokkien, Teochew and fusion legs "
        "of the island canon in one yard.")
V("v-cheah-yew-market", "Cheah Yew Market", area="Penang", role="series venue",
  blurb="Wantan Mee (soup) and Lor Mee: the Cantonese and Hokkien poles.")
V("v-sin-hup-aun", "Sin Hup Aun Cafe", area="Penang", role="series venue",
  blurb="Instant Cook koay teow th'ng.")
V("v-sin-yong-wah", "Sin Yong Wah Coffee Shop", area="Pulau Tikus, Penang", role="series venue",
  blurb="Granny Q's lemak laksa.")
V("v-sabah-pan-mee-pt", "Sabah Pan Mee, Pulau Tikus", area="Pulau Tikus, Penang",
  role="series venue", blurb="Soup and dry versions, two episodes apart.")
V("v-pulau-tikus-hidden", "Pulau Tikus Hidden Food Court", area="Pulau Tikus, Penang",
  role="series venue", blurb="Ah Liang's koay teow th'ng.")
V("v-pulau-tikus-hawker", "Pulau Tikus hawker area", area="Pulau Tikus, Penang",
  role="series venue")
V("v-kim-lian-kee", "Kim Lian Kee", area="Petaling Street, Kuala Lumpur", role="reference stall",
  kind="restaurant", founded="1927",
  blurb="Still cooking KL Hokkien mee over charcoal on the street it moved to in 1927.")
V("v-kin-kin", "Restoran Kin Kin", area="Kampung Baru, Kuala Lumpur", role="reference stall",
  kind="restaurant", founded="1985", blurb="Chilli pan mee, from a stall under a tree in Chow Kit.")
V("v-air-itam-curry-mee", "The Lim sisters' curry mee stall", area="Air Itam, Penang",
  role="reference stall", founded="1946",
  blurb="Michelin-recognised, three generations, and the oldest documented Penang curry mee "
        "lineage - which dates a stall, not a dish.")
V("v-hameed-pata", "Hameed 'Pata' Special Mee Sotong", area="Padang Kota Lama, Penang",
  role="reference stall", founded="mee rebus and mee goreng from 1942; mee sotong from 1978")
V("v-jones-road-mee-sotong", "Jones Road Famous Mee Sotong Sambal",
  area="now at Sin Hup Aun Cafe, Jalan Pasar / Solok Moulmein, Pulau Tikus",
  role="series venue", founded="1980s, originally at the Jalan Jones / Tingkat Jones T-junction",
  blurb="A relocated stall rather than a relocated shop: the Jones Road name travelled with the "
        "cook into somebody else's kopitiam, which is how most Penang hawker lineages actually "
        "survive.")
V("v-bangkok-lane", "Bangkok Lane Mee Goreng", area="Pulau Tikus, Penang", role="reference stall",
  founded="over 90 years, from a pushcart",
  blurb="Borrows its gravy from the pasembur stall next door - hybridisation you can watch.")
V("v-lum-lai", "Lum Lai Duck Meat Koay Teow Th'ng", area="Cecil Street Market, Penang",
  role="reference stall", founded="late 1970s")
V("v-choon-hui", "Choon Hui Cafe", area="Ban Hock Road, Kuching", role="reference stall",
  blurb="Where Bourdain ate Sarawak laksa two mornings running in 2005.")
V("v-soong-kee", "Soong Kee Beef Noodles", area="Kuala Lumpur", role="reference stall",
  founded="1945", blurb="Hakka, and its house tradition traces the dish to Dabu, not Hainan.")
V("v-thean-chun", "Thean Chun", area="Ipoh", role="reference stall",
  blurb="Founded by Hokkiens from Nan'an, and famous for a Cantonese dish.")
V("v-ghee-lian", "Ghee Lian", area="Perak Road, Penang", role="reference stall", founded="2012",
  blurb="Michelin Bib, and a green tom yum noodle - local invention inside an imported category.")


# ================================================================ EPISODES
def EP(nid, label, dish, **kw):
    kw["dish"] = dish
    kw.setdefault("status", "tried")
    return N(nid, "episode", label, **kw)

EP("ep-01-jawa-mee", "Jawa Mee at 33 Best Food Hub", "d-jawa-mee",
   date="2026-07-20", venue="v-33-best-food-hub", postSlug="jawa-mee-33", seriesOrder=1)
EP("ep-02-pan-mee-soup", "Sabah Pan Mee (soup)", "d-pan-mee",
   date="2026-07", venue="v-pulau-tikus-hawker", postSlug="sabah-pan-mee", seriesOrder=2,
   styleNote="soup",
   note="Sold as 'Sabah pan mee'. No dish by that name is documented in Sabah - see the name "
        "node. Most likely ordinary pan mee made with sayur manis.")
EP("ep-03-kolo-mee", "Kolo Mee at Hock Beng 88", "d-kolo-mee",
   date="2026-07", venue="v-hock-beng-88", postSlug="kolo-mee", seriesOrder=3,
   styleNote="SL Special")
EP("ep-04-lam-mee", "Lam Mee at Hock Beng 88", "d-lam-mee",
   date="2026-07-22", venue="v-hock-beng-88", postSlug="lam-mee-88", seriesOrder=4)
EP("ep-05-hokkien-mee", "Hokkien / Prawn Mee at Restoran 77", "d-hokkien-mee-penang",
   date="2026-07-23", venue="v-restoran-77",
   postSlug="hokkien-prawn-mee-at-restoran-77-food-yard", seriesOrder=5)
EP("ep-06-mee-suah-koh", "Mee Suah Koh at 33 Best Food Hub", "d-mee-suah-koh",
   date="2026-07-23", venue="v-33-best-food-hub",
   postSlug="mee-suah-koh-at-33-best-food-hub", seriesOrder=6,
   note="The rarest bowl on the tried list, and the closest to an unmodified Quanzhou form.")
EP("ep-07-char-kway-teow", "Char Kway Teow at Restoran 77", "d-char-kway-teow",
   date="2026-07-24", venue="v-restoran-77",
   postSlug="char-kway-teow-at-restoran-77-food-yard", seriesOrder=7)
EP("ep-08-wantan-mee", "Wantan Mee (soup) at Cheah Yew Market", "d-wantan-mee",
   date="2026-07-27", venue="v-cheah-yew-market",
   postSlug="wantan-mee-in-cheah-yew-market", seriesOrder=8, styleNote="soup")
EP("ep-09-curry-mee", "Curry Mee at Restoran 77", "d-curry-mee-penang",
   date="2026-07-28", venue="v-restoran-77",
   postSlug="curry-mee-in-restoran-77-food-yard", seriesOrder=9, styleNote="coconut")
EP("ep-10-koay-teow-thng", "Instant Cook Koay Teow Th'ng at Sin Hup Aun", "d-koay-teow-thng",
   date="2026-07-29", venue="v-sin-hup-aun",
   postSlug="instant-cook-koay-teow-at-sin-hup-aun-cafe", seriesOrder=10)
EP("ep-11-lor-mee", "Lor Mee at Cheah Yew Market", "d-lor-mee-penang",
   date="2026-07-30", venue="v-cheah-yew-market", postSlug="lor-mee-in-cheah-yew-market",
   seriesOrder=11)
EP("ep-12-mee-rebus", "Mee Rebus at 33 Best Food Hub", "d-mee-rebus",
   date="2026-07-31", venue="v-33-best-food-hub", postSlug="mee-rebus-at-33-best-food-hub",
   seriesOrder=12)
EP("ep-13-lemak-laksa", "Granny Q's Lemak Laksa at Sin Yong Wah", "d-lemak-laksa",
   date="2026-08-07", venue="v-sin-yong-wah",
   postSlug="granny-q-lemak-laksa-at-sin-yong-wah-coffee-shop", seriesOrder=13)
EP("ep-14-pan-mee-dry", "Dry Sabah Pan Mee (fried pork)", "d-pan-mee",
   date="2026-08-10", venue="v-sabah-pan-mee-pt",
   postSlug="sabah-pan-mee-dry-fried-pork-version", seriesOrder=14, styleNote="dry, fried pork",
   revisitOf="ep-02-pan-mee-soup",
   note="The dry fried-pork configuration is closer to Sabah's actual sang nyuk mee kon lau than "
        "to peninsular pan mee.")
EP("ep-15-koay-teow-thng-ah-liang", "Ah Liang's Koay Teow Th'ng", "d-koay-teow-thng",
   date="2026-08-11", venue="v-pulau-tikus-hidden", postSlug="ah-liang-koay-teow-th-ng",
   seriesOrder=15, revisitOf="ep-10-koay-teow-thng")

EP("ep-16-mee-sotong", "Jones Road Famous Mee Sotong Sambal", "d-mee-sotong",
   date="2026-08-12", venue="v-sin-hup-aun",
   postSlug="jones-road-famous-mee-sotong-sambal", seriesOrder=16,
   styleNote="sambal gravy, sotong",
   note="The first Tamil-Muslim-carried bowl in the series, and the second episode at Sin Hup "
        "Aun Cafe after the Instant Cook koay teow th'ng.")

# planned episodes - island classics
EP("ep-p-white-curry-mee", "White Curry Mee", "d-white-curry-mee", status="planned",
   note="Paler, silkier coconut; spice mostly on the side. Distinct from the Restoran 77 bowl.")
EP("ep-p-asam-laksa", "Asam Laksa", "d-asam-laksa", status="planned",
   note="Noodle-adjacent, still counts for the series.")
EP("ep-p-mee-goreng-mamak", "Mee Goreng Mamak", "d-mee-goreng-mamak", status="planned")
EP("ep-p-maggi-goreng", "Maggi Goreng", "d-maggi-goreng", status="planned",
   note="Late-night / mamak energy.")
EP("ep-p-bee-hoon", "Bee Hoon", "d-char-bee-hoon", status="planned",
   note="Fried or soup - pick a clear style per episode.")
EP("ep-p-koay-chiap", "Koay Chiak", "d-koay-chiap", status="planned",
   note="Listed on the checklist as 'Koay Chiak' - short rice noodles / dumpling-noodle hybrid. "
        "The dish is koay chiap: broad folded rice sheets in a dark braise.")
EP("ep-p-bak-chor-mee", "Bak Chor Mee", "d-bak-chor-mee", status="planned",
   note="If you find a stall that actually does it well here - and the graph explains why that "
        "is hard in Penang.")
EP("ep-p-duck-noodle", "Duck noodle / duck kway teow", "d-duck-koay-teow", status="planned")
EP("ep-p-beef-noodles", "Beef noodles", "d-beef-noodles-my", status="planned",
   note="Clear or herbal, whichever shows up.")
EP("ep-p-fish-head-bee-hoon", "Fish head bee hoon", "d-fish-head-bee-hoon", status="planned")
EP("ep-p-chee-cheong-fun", "Chee cheong fun", "d-chee-cheong-fun", status="planned",
   note="Edge case; optional if you want a stretch 'noodle'.")
# planned - regional / immigrant
EP("ep-p-ban-mian", "Ban mian", "d-pan-mee", status="planned",
   note="Only if a stall brands it separately from Sabah pan mee.")
EP("ep-p-mee-soto", "Mee Soto", "d-mee-soto", status="planned")
EP("ep-p-you-mee", "You mee", "d-you-mee", status="planned",
   note="Oil-tossed / light dry style. Worth asking the stall which of four noodles they mean.")
EP("ep-p-yi-mein", "Cantonese yi mein / e-fu", "d-yi-mein", status="planned",
   note="Braised or birthday-style.")
EP("ep-p-ipoh-hor-fun", "Ipoh hor fun", "d-ipoh-hor-fun", status="planned")
EP("ep-p-tom-yum", "Thai boat noodles / tom yum noodles", "d-tom-yum-mee", status="planned",
   note="Only if a regular hawker cart, not a full Thai restaurant detour.")
EP("ep-p-sarawak-laksa", "Sarawak laksa", "d-sarawak-laksa", status="planned",
   note="Rare; grab it if you actually find it.")
EP("ep-p-bihun-goreng", "Bihun goreng / char beehoon", "d-bihun-goreng", status="planned")
# planned - mainland slots
EP("ep-p-mainland-curry-mee", "Mainland curry mee", "d-curry-mee-penang", status="planned",
   mainland=True, note="Butterworth / Perai / BM. Venue TBD.")
EP("ep-p-mainland-wantan-mee", "Mainland wantan mee", "d-wantan-mee", status="planned",
   mainland=True, note="Kopitiam classic. Venue TBD.")
EP("ep-p-mainland-kopitiam", "Mainland kopitiam noodles", "d-char-bee-hoon", status="planned",
   mainland=True, note="Whatever the queue is actually ordering. Dish to be confirmed on arrival.")
EP("ep-p-bm-surprise", "One Seberang / Bukit Mertajam surprise bowl", "d-char-kway-teow",
   status="planned", mainland=True,
   note="Dish name to be filled when tasted. Bukit Mertajam is a Teochew enclave and home of "
        "char koay teow basah - a strong candidate.")
# planned - wildcards and revisits
EP("ep-p-chilli-pan-mee", "Thong Soon / named dry chilli pan mee", "d-chilli-pan-mee",
   status="planned", note="Only if clearly different from a prior pan mee episode.")
EP("ep-p-festival-noodles", "Seasonal / festival noodles", "d-longevity-mee-sua", status="planned",
   note="Longevity, CNY, or stall specials.")
EP("ep-p-cmeepo-wildcard", "Whatever C-Mee-PO can't identify at first glance",
   "d-mee-suah-koh", status="planned", wildcard=True,
   note="The open slot. Linked provisionally to mee suah koh because that is the closest thing "
        "on the tried list to an unidentifiable bowl - a low-frequency survival that most Penang "
        "food writing does not cover. Re-point this edge when the actual bowl turns up.")
EP("ep-p-wantan-mee-dry", "Wantan Mee (dry / kon lo)", "d-wantan-mee", status="planned",
   revisitOf="ep-08-wantan-mee", note="The kon lo half of the dish, after the Cheah Yew soup.")
EP("ep-p-curry-mee-variant", "Curry Mee variants beyond White", "d-curry-mee-penang",
   status="planned", revisitOf="ep-09-curry-mee",
   note="Only if clearly different from Restoran 77.")

# 6. How fusion actually happens

"Fusion" is a lazy word for what happened in Penang. It suggests things dissolving into each
other, and nothing here dissolved. What Penang has is a set of parallel named lineages that
borrowed from each other through a small number of specific, describable mechanisms — most of
them economic rather than culinary.

Naming those mechanisms is more useful than listing influences, because a mechanism predicts
things a list cannot.

---

## Seven mechanisms

### 1. Marriage

Migrant men, no migrant women, local wives — and therefore children with a father's language,
religion or trade and a **mother's kitchen**. This produced the Baba-Nyonya, the Jawi Peranakan,
and the Phuket Baba. It is why the Nyonya kitchen is a Southeast Asian kitchen with Chinese
ingredients rather than the reverse, and why Penang Hokkien is a Chinese language full of Malay
words for household objects.

*Predicts:* creole cuisines will be technique-Malay and prestige-Chinese, and their vocabulary
will be Malay wherever the object is domestic and Chinese wherever the object is commercial.
Which is what you find.

### 2. Halal boundary work

The single strongest structural force in Penang's noodle culture, and the most productive.
Indian Muslim cooks rebuilt Chinese dishes without pork and with South Indian spice, and the
result was not a compromise but a whole new repertoire.

*Predicts:* systematic dish **pairs** rather than one melting pot. Curry mee against curry laksa.
Char kway teow against CKT kerang, where the *kerang* gets promoted to star to fill the flavour
hole the lard left. Kolo mee against *mi kolok*, which has its own Iban names. Penang mee jawa
against mee rebus. And it predicts that the noodle will cross the boundary freely while the
sauce never does — which is exactly the asymmetry you observe, and it is the structural
fact everything else in this dataset hangs off.

### 3. Commodification of spice

British-invented, shelf-stable **curry powder** made Indian flavour purchasable by non-Indian
cooks. A Hokkien hawker could not maintain a Tamil spice-roasting practice; he could buy a
packet.

*Predicts:* curry appears in Chinese Penang cooking only *after* the commodity exists, and it
appears as a *bought* component rather than a rebuilt technique. Which is why Penang curry mee
uses curry powder while Penang asam laksa uses a pounded rempah: one was purchased, the other
was inherited from a mother.

### 4. Labour and port geography

Dock coolies at Weld Quay produced nasi kandar and its flooded plate. Estate workers at the
plantation gates produced teh tarik. Pilgrims waiting weeks on Acheen Street for a ship to
Jeddah produced a demand for portable halal wheat food. A prawn fishery at the Muda estuary
produced a mee udang cluster at Sungai Dua.

*Predicts:* dish geography tracks employment geography, not taste. And where a cluster looks
inexplicable, look for the industry.

### 5. Domestic service

Hainanese cooks learned European and Peranakan household cooking in their employers' kitchens,
then took it onto the street when jobs were scarce after 1945. Singapore's Katong laksa is the
documented case: no Peranakan family would have let an heirloom recipe be peddled as street
food, so the cook was the leak.

*Predicts:* the elite home cuisines of Penang should reach the street *only* through the people
employed to cook them — which explains both what got out (chicken rice, chicken chop, mee
Hailam, coconut laksa) and what did not (Jawi Peranakan cuisine, which employed a smaller
service class and left almost no hawker trace at all).

### 6. Co-selling

Not a metaphor, an actual mechanism, and it is under-recorded. Penang lor mee and Penang Hokkien
mee are usually the same stall, off the same prawn broth thickened with tapioca flour and egg —
an efficiency that has quietly hybridised two dishes. Mee rebus stalls sell mee goreng because
the ingredients overlap. At Bangkok Lane the mee goreng gravy is borrowed from the pasembur stall
next door. Koay teow th'ng and koay chiap come off one cart, which is how their names got
confused in the first place.

*Predicts:* dishes sold together will converge, and their genealogies will get mixed up in the
literature in proportion to how often they share a cart. This dataset carries `co_sold_with` as
a first-class edge type for exactly that reason.

### 7. Industrial standardisation

The one nobody wants in the story, and it is everywhere.

| Commodity | Date | What it did |
| --- | --- | --- |
| Commodified curry powder | London 1784, Madras 1830s | made hawker curry economical |
| Chinese noodle factories | 19th–20th c. | made the alkaline yellow noodle universal, and available to Malay and Indian Muslim kitchens |
| Condensed and evaporated milk | colonial | teh tarik; "milk soup" fish bee hoon |
| Tan Yong Him's Swallow rempah | 1960s, Kuching | **created and froze** modern Sarawak laksa |
| Nestlé Maggi | 1969 sauces, **1971 noodles** | made Maggi goreng possible; cannot predate 1971 |
| MyKuali | 2012 | turned a Penang serving convention into a named global dish category |

Two of these deserve emphasis because they are the same story thirty years apart.

**Sarawak laksa** today is substantially the product of Tan Yong Him, a Kuching fruit seller who
developed a laksa rempah premix and became the first to mass-produce it under the Swallow brand.
Hawkers bought his base and tuned it with fresh spices from the Indian shops on Jalan Gambir.
Competitor bird brands followed — Parrot, Eagle, Double Swallow, Rooster. Tan died in 1993. The
"traditional" dish that Bourdain called the Breakfast of the Gods is standardised around a
commercial paste from the 1960s.

**White curry mee** is the same mechanism running in public. Sambal-on-the-side is the *normal*
Penang curry mee convention, attested at least to the 1940s stall generation, and Tony Boey names
the Air Itam sisters among its pioneers while stating plainly that nobody knows who invented it.
Then MyKuali launched an instant product in 2012, The Ramen Rater ranked it first of all time in
2014, and a serving convention became a dish with a name. Model it honestly: a real tradition
that was *named, reified and globalised* by the instant-noodle industry, and flag any source
presenting it as an ancient named tradition as overclaiming.

*Predicts:* wherever a dish is unusually consistent across many stalls, look for a premix.

### And a bonus: media events as nodes

CNN Go put Penang asam laksa at number seven in the World's 50 Most Delicious Foods on 21 July
2011 — the only Malaysian entry in the top ten, ahead of tom yum goong and ice cream. (CNN Travel
re-promoted the list in 2020, which is why half the internet misdates it.) Bourdain ate Sarawak
laksa at Choon Hui Café on two consecutive mornings in 2005 and called it the Breakfast of the
Gods; before that the dish rarely travelled off the island. Michelin's arrival in Malaysia
changed queues, prices and succession planning at named stalls.

These are not footnotes. They are forces, and the dataset carries them as `media` nodes with
`popularised_by` edges, because a ranking that appears on stall signage and in instant-noodle
marketing has become part of the dish.

---

## Three naming logics, and why dish names lie

Almost all the confusion in Malaysian noodle writing comes from mixing up three different naming
conventions.

**Named after the cook's ethnicity.** Hokkien mee, mee jawa, mee siam, mee goreng *mamak*, mee
Hailam. These names are usually applied **from outside** the community, and they are frequently
wrong about origin — nobody in Fujian calls a dish "Fujian noodles." They are reliable evidence
of *the naming community's point of view* and unreliable evidence of provenance.

**Named after the noodle.** Char kway teow, kolo mee, Maggi goreng — and, best of all, the curry
mee / curry laksa split, which is the *same dish* called *mee* where yellow noodle or bee hoon is
used and *laksa* where thick round rice noodle is used. Both *laksa* and *mee siam* originally
named noodles rather than dishes.

**Named after the process.** *Lam mee* "poured," *mee rebus* "boiled," *lor mee* "braised," *char
kway teow* "stir-fried," *kolo mee* "tossed." The most honest of the three, and the one that
produces the fewest false genealogies.

Which gives a working rule: **dish names in this corpus are unreliable evidence of origin and
reliable evidence of who was doing the naming.** Read them as sociology, not etymology.

### The collisions worth knowing

**"Hokkien mee" is three unrelated dishes.** Penang: a spicy prawn-head soup noodle. Kuala
Lumpur: thick yellow noodles braise-fried black in dark soy with lard croutons. Singapore: a pale
wet fry of mixed yellow mee and bee hoon in prawn stock. One ethnonym, zero relationship beyond
the makers' shared ancestry — because in each city a Hokkien hawker named his signature after
himself, at roughly the same period, with no coordination. Penangites resolve it by calling the
local fried dish "Hokkien char"; KL people call the soup "prawn mee."

**"You mee" has four referents.** 幼麵 *yau min*, the thin round egg noodle, identical to mee kia
and to wonton noodle — this is what a pan mee shop means, and it is a noodle option, not a dish.
伊麵 *yee mee*, the fried dried e-fu brick. 魚麵, a real Foochow fish-paste noodle. And 油麵, an
alias for ordinary yellow noodle. Nearly every English food blog using the phrase does so without
specifying which.

**"Mee pok" means the wide one.** 麵薄 is "thin" in the sense of *shallow in cross-section* — a
flat ribbon. It is the broader of the mee pok / mee kia pair, and it trips up every English
speaker who meets it.

**Koay chiap is not koay teow.** 汁 *chiap* is gravy; 湯 *th'ng* is soup. One is a broad folded
sheet in a dark braise, the other a cut ribbon in a clear broth. They are distinguished at the
level of the name and confused constantly anyway, because the same cart sells both.

**Chee cheong fun contains no pig intestine.** 豬腸粉 describes the shape of the rolled sheet.
Chinese dish names describe what things look like at least as often as what they contain.

**"Singapore noodles" is from Hong Kong.** Cantonese chefs in post-war Hong Kong fried rice
vermicelli with the curry powder that was abundant in the colony through British-Indian trade and
named it after Singapore for exotic appeal. It is not sold in Singapore except to tourists, and
Singapore's own fried bee hoon uses no curry powder at all. This dataset keeps a node for it
because "fictitious geographic attribution" is a category any honest food graph needs to be able
to represent.

**"Sabah pan mee" is a name with no dish behind it.** No dish by that name is documented in
Sabah. Sabah's real items are *sang nyuk mee* and the district-noodle set — Tuaran, Beaufort,
Tenom, Tamparuli, Kota Belud. What a Penang stall selling "Sabah pan mee" is most likely offering
is ordinary pan mee made with *sayur manis* instead of sweet potato leaves, under a name that
borrows Sabah's genuine Hakka noodle reputation. The name is doing real commercial work even
though it denotes nothing at home.

---

## The laksa problem, properly stated

Worth doing carefully, because it is the most-mangled etymology in Southeast Asian food.

Two live hypotheses. **Persian *lākhshah***, "slippery noodle," adopted by the *Oxford Companion
to Food*, with genuinely impressive comparative weight: Russian *lapsha*, Ukrainian *lokshyna*,
Yiddish *lokshen*, Uyghur *laghman*, Afghan *lakhchak*, Lithuanian *lakštiniai* — a whole Eurasian
noodle-word family. And **Sinitic 辣沙**, "spicy sand," referring to the gritty texture from ground
dried prawns, which is more semantically informative and fits the Peranakan Min-speaking
transmission context.

Then two weaker ones. **Sanskrit *lakṣa*, "one hundred thousand"** — read as "many," alluding to
the multitude of ingredients or strands — is popular, and the homophony is genuine because *laksa*
is a real Malay numeral. But it is semantically weak. And **老鼠粉** *loh shi fun*, the rat-tail
noodle, is sometimes floated and has **no support anywhere in the literature**. Drop it.

But the decisive evidence is not about the root at all. It is about the **referent**, and it is
archival:

- The **Biluluk copper-plate inscription, East Java, 1391** contains *hanglaksa*, glossed in Kawi
  as "vermicelli maker." The word was in use for noodles in the archipelago six hundred years ago
  — long before the Peranakan communities usually credited with inventing laksa existed.
- **Wilkinson's 1901 *Malay-English Dictionary*** lists *laksa* both as a numeral and as
  "vermicelli," ascribing the latter to the Persian word.
- An **1833 *Singapore Chronicle* cargo manifest** lists "24 baskets of laksa" shipped from
  Batavia — where laksa unambiguously means the **raw noodle**.
- Sundanese Baduy communities hold a *ngalaksa* harvest ceremony centred on making a rice-flour
  laksa.

So: **laksa named a noodle for centuries before it named a soup.** That single fact kills the
Chinese folk etymologies, which all describe the *broth*, and it reframes every "which laksa is
the original" argument as badly posed. Tony Boey, who chased this further than anyone, states
flatly that the Chinese derivations are "not supported by evidence (so far)."

The dataset therefore carries `nm-laksa` as a name node linking eight different dishes, and
marks the *etymology itself* `disputed`, rather than assigning laksa an origin. That is not
fence-sitting. It is the finding.

---

## Citogenesis, and the claims that do not survive

The reason this dataset has confidence ratings at all is a failure mode common enough to deserve
a name. The chain runs: a stall owner tells a journalist a family story → the journalist prints it
→ twenty blogs copy the journalist → Wikipedia cites a blog → everyone thereafter cites Wikipedia.

The textbook case is **char kway teow**. The universally repeated origin — that it "was often sold
by fishermen, farmers and cockle-gatherers who doubled as hawkers in the evening to supplement
their income," and that "the high fat content and low cost made it attractive as a cheap source
of energy" — is on Wikipedia with two footnotes. Follow them. The first points at Singapore NLB's
Infopedia article, which **does not contain the claim**; it says only that CKT "began as a simple
meal for the ordinary man." The second points at a **2016 newspaper health-scare piece** titled
"Kick your char kway teow habit."

The story is *plausible* — it is a cheap, calorie-dense hawker dish, and cockles do come from
cockle-gatherers. But it is not sourced. It is citation drift, and it is the single most-repeated
unverified claim in Malaysian and Singaporean food writing.

Others on the list, with what is actually wrong:

- **"All Hokkien mee variants descend from lor mee."** Uncited on Wikipedia, and it conflates two
  different Fujianese traditions — a starchy braise and a prawn broth. One specific descent *is*
  evidenced: Ong Kim Lian started KL Hokkien mee from a starchy Hokkien festival noodle. That is
  not a general law.
- **Ipoh's limestone water makes better noodles.** The geology is real and the groundwater is
  genuinely hard. The bean-sprout version is the strongest of the family and even that is
  asserted rather than demonstrated. For *noodles* there is no published analysis at all, and
  rice-noodle texture is dominated by rice variety, flour age, starch ratio, hydration and
  steaming — all under the maker's control. The honest formulation: Ipoh has a concentrated,
  competitive, multi-generational noodle trade and attributes its results to the water.
- **Boat noodles in twelfth-to-sixteenth-century Ayutthaya.** Anachronistic. The dish's own name
  is a Teochew loanword, mass Teochew settlement in Siam dates from the late eighteenth century,
  and Rangsit's canals were dug in the 1890s. Canal-boat vending in Ayutthaya is plausible; *kuay
  teow reua as we know it* is a late dish.
- **The dark boat-noodle broth hides blood residue from butchering.** Food-media
  rationalisation, undocumented.
- **Lam mee is loh mee re-pronounced in Cantonese.** Fails four ways — see Chapter 3.
- **Chilli pan mee is a traditional Hakka dish.** It is a documented 1985 KL invention by Tan Kok
  Hong at Kin Kin, on a Hakka substrate.
- **Kolo mee and Sarawak laksa are Foochow.** Both are Kuching dishes; the Foochow noodle is
  kampua, from Sibu, three hundred kilometres away on a different river system.
- **Hainanese beef noodles came from Hainan Island.** Not evidenced; Hainan's own cuisine is not
  notably beef-centric. Malaysian beef noodles are a 1930s–40s Malayan hawker development made by
  Hainanese *and* Hakka hawkers.
- **Evaporated milk in fish soup was a Hainanese British-influenced innovation.** Unsourced.
- **Yi mein is the ancestor of instant noodles.** A rhetorical framing. The fry-dry-rehydrate
  technique parallel is real; the line of descent to Ando Momofuku's 1958 product is not
  demonstrated. The dataset keeps the technique link and refuses the ancestry link.
- **Kedah laksa uses eel.** On Wikipedia, contradicted by Malay-language sources, which
  consistently say kembung or selayang.
- **Penang Hokkien mee was invented in wartime scarcity.** The parent dish still exists in Xiamen,
  and an eyewitness account of occupied Penang says there were essentially no noodles and hardly
  any rice.

And for calibration, the control case. **Lanzhou beef noodles** were codified in 1915 by Ma
Baozi, a Hui Muslim cook who hawked from a shoulder pole before opening a shop, to a
five-element standard — clear broth, white radish, red chilli oil, green herbs, yellow noodles.
There is a museum and a municipal specification, and although a competing Qing-era account
circulates, the twentieth-century codification is documented in a way nothing here is. That is
what a well-evidenced noodle origin looks like. Everything Malaysian in this dataset should be read against it, and almost nothing measures
up — which is not a criticism of the food. It is a description of the archive.

---

## Two better tests than origin stories

If origin stories are unreliable, what should you actually look at?

**The substrate ingredient.** Anchovy stock in pan mee. *Sayur manis* in Sabah. Hae ko on Penang
chee cheong fun. Kangkung in Penang Hokkien mee. Tomato and lime in mamak bihun. Dried flounder
across northern Malaysia. Sambal belacan served with everything. **These are the points at which
a Chinese dish became a Malaysian one, and they are far more reliable evidence of local
adaptation than any founder's grandson.** Mainland ban mian uses pork or plain water stock; put
*ikan bilis* in it and you are eating a Malaysian dish, whatever the character on the signboard.

**Dialect group beats nationality as a predictor.** Teochew hawkers made clear broths and braised
duck in Penang, Bangkok and Singapore alike. Hakka hawkers made dry-tossed minced-pork noodles
in Ipoh, Kuching and Kota Kinabalu alike. Hokkien hawkers made starchy braises and prawn stocks
everywhere they went. The variation *within* a dialect tradition across three countries is often
smaller than the variation *between* two dialect traditions on the same street.

Which is the finding that most shaped how the dataset is built, and the reason it makes
`culture` a first-class node type rather than a tag on a dish. In Penang, the relevant unit was
never the nation and it was rarely the town. It was the prefecture your great-grandfather left,
the decade he left it, and the trade that was still available when he arrived.

**Sources for this chapter:** Tony Boey (Johor Kaki) on the laksa word, on Sarawak laksa and the
Swallow rempah industry, on Katong laksa, and on the Xiamen prawn-noodle precedent; OED on curry
and curry powder; *Oxford Companion to Food* on laksa; Wilkinson's 1901 *Malay-English
Dictionary*; the Biluluk 1391 inscription; the 1833 *Singapore Chronicle* manifest via NLB
newspaper archives; Nestlé Malaysia on the Maggi timeline; MyKuali and The Ramen Rater; CNN Go
(2011); Bourdain, *No Reservations*, Borneo (2005); Singapore NLB Infopedia on char kway teow and
mee rebus; Wikipedia on char kway teow, Hokkien mee, banmian, boat noodles, Singapore-style
noodles, yi mein and Lanzhou beef noodles; Ipoh Echo on kai si hor fun; The Rakyat Post on Kin
Kin; Borneo Post on kolo, kampua and ketchup mee; Penang Institute on hawker knowledge
transmission and *air tangan*.

"""Node register for the Penang noodle culture graph.

Node types
----------
region     a place of origin or settlement, as specific as the evidence allows
culture    a community: Chinese dialect group, creole community, ethnic group
wave       a migration stream, ordinance, or historical rupture that moved people
dish       a noodle dish, including ancestors and cousins outside Penang
noodle     a noodle type, treated as a first-class node because in Penang the
           noodle is the most reliable marker of which kitchen a dish came from
ingredient a signature ingredient or condiment
technique  a cooking method or service convention
commodity  an industrial or colonial product that changed what hawkers could cook
media      a media event that measurably changed a dish's economy
concept    a structural idea: the halal boundary, longevity noodles, naming logics
name       a name that collides across unrelated dishes
venue      a stall, kopitiam or food court
episode    one tasting in the Mee Myself and I series - tried or planned
"""

NODES = []


def N(nid, ntype, label, **kw):
    node = dict(id=nid, type=ntype, label=label)
    node.update(kw)
    NODES.append(node)
    return nid


# =============================================================== REGIONS
# --- southern Fujian: the Hokkien source ports -------------------------
N("r-xiamen", "region", "Xiamen (Amoy) 廈門", country="China", admin="Fujian",
  blurb="Seaport, treaty port, and the origin of the prawn-head noodle broth that "
        "became Penang Hokkien mee. George Town and Xiamen formalised twin-city "
        "status in 2021.", sources=["johorkaki-hokkien-mee", "kuchler-1965"])
N("r-quanzhou", "region", "Quanzhou 泉州", country="China", admin="Fujian",
  blurb="Home of mee sua (麵線) manufacture and of the mian xian hu porridge-noodle "
        "form that survives in Penang as mee suah koh.", sources=["kuchler-1965"])
N("r-zhangzhou", "region", "Zhangzhou 漳州", country="China", admin="Fujian",
  blurb="Jiulong River valley. Penang Hokkien derives from a Zhangzhou sub-dialect, "
        "and lor mee is attributed here.", sources=["kuchler-1965", "wiki-penangite-chinese", "wiki-lor-mee"])
N("r-anxi", "region", "Anxi county 安溪", country="China", admin="Fujian",
  blurb="Home county of Ong Kim Lian, who founded Kim Lian Kee in KL in 1927.",
  sources=["kim-lian-kee"])
N("r-hui-an", "region", "Hui'an county 惠安", country="China", admin="Fujian",
  blurb="Supplied Penang's trishaw pullers, who clustered around Magazine Road and "
        "Noordin Street.", sources=["kuchler-1965"])
N("r-haicheng", "region", "Haicheng 海澄 / Sin Kang 新江", country="China", admin="Fujian",
  blurb="Ancestral neighbourhood of Penang's Big Five Hokkien clans; the Khoo came "
        "specifically from Sin Kang village.", sources=["kuchler-1965", "khookongsi-official"])
N("r-nan-an", "region", "Nan'an county 南安", country="China", admin="Fujian",
  blurb="Home county of the Hokkien founders of Ipoh's two most celebrated kai si hor "
        "fun stalls - a Cantonese dish made famous by Hokkien hands.",
  sources=["ipoh-echo-kai-si-hor-fun"])
N("r-putian", "region", "Putian 莆田 / Heng Hwa 興化", country="China", admin="Fujian",
  blurb="Puxian Min speakers, neither Hokkien nor Foochow. Their finer, silkier bee "
        "hoon is their culinary calling card. Putian also has a lighter, seafood-based, "
        "less-starched lor mee.", sources=["wiki-lor-mee", "kuchler-1965"])
N("r-fuzhou", "region", "Fuzhou 福州 (Foochow / Hokchiu)", country="China", admin="Fujian",
  blurb="Mindong, eastern Fujian. Fish balls stuffed with minced pork, red glutinous "
        "rice wine, and the mee sua traditions that reached Sibu and Sitiawan.",
  sources=["danielfooddiary-foochow", "kuchler-1965"])
N("r-ninghua", "region", "Ninghua county 寧化", country="China", admin="Fujian",
  blurb="Yi Bingshou's ancestral county, sometimes named as the pre-Cantonese home of "
        "yi mein.", sources=["wiki-yi-mein"])
N("r-zhao-an", "region", "Zhao'an county 詔安", country="China", admin="Fujian",
  blurb="A Fujian county on the Guangdong border with Hokkien-Teochew transitional "
        "speech. Chen Lianfu, the traceable father of bak chor mee, left here in the "
        "late 1910s.", sources=["johorkaki-bcm"])
N("r-yongding", "region", "Yongding county 永定", country="China", admin="Fujian",
  blurb="A Hakka county in Fujian whose associations joined Penang's Kwangtung & "
        "Tengchow umbrella on the basis of shared speech, not shared province - the "
        "cleanest proof that province does not equal dialect.",
  sources=["malaymail-beyond-hokkien", "voon-2024-hakka"])

# --- eastern Guangdong: Teochew --------------------------------------
N("r-chaoshan", "region", "Chaoshan 潮汕 (Chaozhou + Shantou/Swatow)", country="China",
  admin="Guangdong",
  blurb="The lower Han River valley, a fruit-growing region. Most Penang Teochews came "
        "from small villages here. Source of kway teow, the lou braise, braised duck, "
        "and the clear-broth aesthetic.",
  sources=["kuchler-1965", "ccs-city-teochew", "penang-traveltips-teochew"])
N("r-jieyang", "region", "Jieyang 揭陽 / Hepo 河婆", country="China", admin="Guangdong",
  blurb="A Hakka pocket inside the Teochew region; Hepo Hakkas went overwhelmingly to "
        "Johor.", sources=["voon-2024-hakka"])

# --- Pearl River delta: Cantonese ------------------------------------
N("r-guangzhou", "region", "Guangzhou 廣州", country="China", admin="Guangdong",
  blurb="Hub of Cantonese cuisine. Wonton noodles took their modern form here in the "
        "Qing; the Shahe district gave hor fun its name.",
  sources=["wiki-wonton-noodles", "ipoh-echo-kai-si-hor-fun"])
N("r-shahe", "region", "Shahe 沙河, Tianhe District, Guangzhou", country="China",
  admin="Guangdong",
  blurb="The district after which 沙河粉 / 河粉 - flat rice noodle - is named. The same "
        "physical noodle Teochews call 粿條.", sources=["ipoh-echo-kai-si-hor-fun"])
N("r-sze-yup", "region", "Sze Yup 四邑 (Taishan, Kaiping, Enping, Xinhui)", country="China",
  admin="Guangdong",
  blurb="The four western-delta counties that also supplied most Chinese emigration to "
        "America.", sources=["malaymail-beyond-hokkien", "kuchler-1965"])
N("r-huizhou-gd", "region", "Huizhou 惠州", country="China", admin="Guangdong",
  blurb="Hakka uplands. Huizhou Hakkas manned the Larut and Selangor mines and founded "
        "Kuala Lumpur under Yap Ah Loy. Yi Bingshou was prefect here.",
  sources=["voon-2024-hakka", "wiki-yi-mein"])
N("r-meizhou-dabu", "region", "Dabu (Tai Po) county 大埔, Meizhou 梅州", country="China",
  admin="Guangdong",
  blurb="Home of Tai Po / yan mee salted noodles - the parent of Sarawak kolo mee and "
        "of peninsular Hakka mee. Kiew Shao Nyap came from Baihou village here.",
  sources=["medium-kolo-mee", "wiki-kolo-mee", "voon-2024-hakka"])
N("r-jiaying-meixian", "region", "Jiaying / Meixian 嘉應・梅縣", country="China",
  admin="Guangdong",
  blurb="Vaughan's 1854 survey found Penang's Hakkas came 'nearly all' from Jiaying and "
        "its environs.", sources=["kuchler-1965", "voon-2024-hakka"])
N("r-zengcheng", "region", "Zengcheng 增城", country="China", admin="Guangdong",
  blurb="Chung Keng Kwee's Larut mine workers were largely Zengcheng Hakkas of the Hai "
        "San society.", sources=["voon-2024-hakka"])

# --- Hainan, and elsewhere in China ----------------------------------
N("r-hainan", "region", "Hainan island 海南", country="China", admin="Hainan",
  blurb="Penang's Hainanese came overwhelmingly from Haikou and Qiongshan, with a "
        "smaller Wenchang group - a correction to the usual 'Wenchang/Qionghai' "
        "formulation.", sources=["kuchler-1965", "mothership-hainanese"])
N("r-lanzhou", "region", "Lanzhou, Gansu 蘭州", country="China", admin="Gansu",
  blurb="Hui Muslim hand-pulled beef noodles, codified by Ma Baozi in 1915 to a "
        "five-element municipal standard. The best-documented noodle origin anywhere in "
        "this graph.", sources=["wiki-lanzhou-beef-noodle"])

# --- India, Arabia ----------------------------------------------------
N("r-coromandel", "region", "Coromandel coast, Tamil Nadu", country="India",
  blurb="The 'Chulia' country of East India Company usage, conventionally connected to "
        "the Chola. Tamil Muslim traders were working the Kedah coast for centuries "
        "before 1786 and reached Penang within days of Light's landing.",
  sources=["wiki-chulia-street", "areca-chulia"])
N("r-nagore", "region", "Nagore & Nagapattinam", country="India", admin="Tamil Nadu",
  blurb="Home of the Sufi saint Syed Shahul Hamid, whose cult Tamil Muslim traders "
        "carried to Chulia Street, where the Nagore Durgha Sheriff still stands.",
  sources=["penang-traveltips-nagore"])
N("r-kilakarai", "region", "Kilakarai & Kayalpatnam", country="India", admin="Tamil Nadu",
  blurb="Marakkayar maritime trading ports. The Marakkayar trace descent from Arab "
        "seafarers who married South Indian women - Arab-Indian creolisation one step "
        "upstream of Penang's.", sources=["wiki-chulia-street"])
N("r-malabar", "region", "Malabar coast, Kerala", country="India",
  blurb="Mappila / Malabar Muslims. Lebuh Chulia was originally Malabar Street. The "
        "likely conduit for the Malabar parotta lineage that became roti canai.",
  sources=["wiki-chulia-street", "taste-roti-canai"])
N("r-chettinad", "region", "Chettinad (Sivagangai & Pudukottai)", country="India",
  admin="Tamil Nadu",
  blurb="Home of the Nattukottai Chettiar merchant-bankers who clustered on Lebuh Penang "
        "and built the Waterfall Road Thendayuthapani temple.",
  sources=["malaymail-beyond-hokkien"])
N("r-madras", "region", "Madras", country="India",
  blurb="Where British civil servants standardised reproducible curry blends from the "
        "1830s - the commodity that made hawker curry economical.",
  sources=["oed-curry"])
N("r-hadhramaut", "region", "Hadhramaut", country="Yemen",
  blurb="Sayyid lineages from this valley traded, married and settled across the Malay "
        "archipelago from roughly the 13th century, carrying religious prestige that "
        "converted into commercial leverage.", sources=["wiki-murtabak"])

# --- the northern triangle and the peninsula --------------------------
N("r-kedah", "region", "Kedah", country="Malaysia",
  blurb="Penang was Kedah territory, ceded 1786. The island's Malay substrate is Kedah "
        "Malay, and Kedah was a Siamese tributary for centuries - so the northern "
        "political horizon was Bangkok and Ava, not Malacca.",
  sources=["kuroda-samsam", "penang-traveltips-koh-lay-huan"])
N("r-george-town", "region", "George Town, Penang", country="Malaysia",
  blurb="Founded 1786. Three-quarters of its Chinese were Hokkien and Cantonese in 1957; "
        "86% of all Penang Cantonese lived here. The Cantonese, Hakka and Hokkien "
        "enclaves all intersected Little India.",
  sources=["kuchler-1965", "malaymail-beyond-hokkien"])
N("r-penang-island", "region", "Penang Island", country="Malaysia",
  blurb="Fishing settlements almost exclusively Hokkien; nearly all vegetable farmers on "
        "the Penang Hill slopes and in Balik Pulau were Hakka.", sources=["kuchler-1965"])
N("r-seberang-perai", "region", "Province Wellesley / Seberang Perai", country="Malaysia",
  blurb="Acquired 1800. The colony's food supply, and the destination for Tamil and "
        "Javanese estate labour - which is why the mainland's noodle centre of gravity "
        "is Malay and Javanese where the island's is Chinese.",
  sources=["kuchler-1965", "wiki-demographics-penang"])
N("r-bukit-mertajam", "region", "Bukit Mertajam (Dua Sua Kar)", country="Malaysia",
  blurb="A Teochew cash-crop enclave on the mainland, still Teochew-identified. Home of "
        "the wetter char koay teow basah, locally associated with the Malay community.",
  sources=["wiki-penangite-chinese", "cj-my-ckt-origins"])
N("r-malacca", "region", "Malacca",
  country="Malaysia",
  blurb="The older Peranakan community, 15th-16th century. Baba families relocated north "
        "to the new free port from 1786, so Penang Nyonya culture is simultaneously a "
        "Malacca offshoot and a fresh northern creolisation.",
  sources=["kuchler-1965", "michelin-malaysia-regional"])
N("r-kuala-lumpur", "region", "Kuala Lumpur & Klang Valley", country="Malaysia",
  blurb="Founded by Hakkas under Yap Ah Loy. Cantonese and Hokkien near-parity by 2000. "
        "Home of KL Hokkien mee, chilli pan mee, and Ampang yong tau foo.",
  sources=["voon-2024-hakka", "kim-lian-kee", "kin-kin"])
N("r-ipoh-kinta", "region", "Ipoh & the Kinta Valley", country="Malaysia",
  blurb="A Cantonese-and-Hakka tin town: Cantonese 32.6% of Perak's Chinese by 2000. "
        "Kinta produced 80% of Perak's tin ore by 1895.",
  sources=["voon-2024-hakka", "cgtn-cantonese-ipoh"])
N("r-taiping-larut", "region", "Taiping & the Larut tin fields", country="Malaysia",
  blurb="Tin found in the 1840s; ~20,000 Chinese by 1862, 30-40,000 a decade later. The "
        "Larut Wars were fought here between Hakka sub-groups organised as rival secret "
        "societies, financed out of Penang.", sources=["voon-2024-hakka", "wiki-larut-wars"])
N("r-seremban", "region", "Seremban", country="Malaysia",
  blurb="A Hakka town; the claimed birthplace of Hakka mee and of yee sang.",
  sources=["michelin-hakka-kl", "wiki-yusheng"])
N("r-sitiawan", "region", "Sitiawan, Perak", country="Malaysia",
  blurb="A 1903 Foochow Methodist agricultural colony, planted deliberately to feed the "
        "growing coolie population. One of Malaysia's two hand-pulled mee sua centres.",
  sources=["ipoh-echo-foochow-sitiawan"])
N("r-johor", "region", "Johor", country="Malaysia",
  blurb="Hepo Hakka settlement; mee rebus with tapioca and beef stock; mee bandung from "
        "Muar; and a laksa with grilled wolf herring served over spaghetti.",
  sources=["voon-2024-hakka", "nlb-mee-rebus", "wiki-laksa"])
N("r-kuching", "region", "Kuching, Sarawak", country="Malaysia",
  blurb="Huizhou Hakka, Hokkien and Teochew settlement. Home of kolo mee and Sarawak "
        "laksa - both routinely and wrongly attributed to the Foochow of Sibu.",
  sources=["borneo-post-sarawak-mee", "medium-kolo-mee"])
N("r-sibu", "region", "Sibu, Sarawak (Sin Hockchew)", country="Malaysia",
  blurb="Wong Nai Siong's 1901 Foochow colony - 72 pioneers, over 1,000 Christian "
        "Foochows by 1903. Foochows were 34.8% of Sarawak's Chinese by 2000. Home of "
        "kampua mee, not kolo mee.", sources=["wiki-wong-nai-siong", "voon-2024-hakka"])
N("r-tuaran", "region", "Tuaran, Sabah", country="Malaysia",
  blurb="A west-coast town whose fried egg noodle became a retronym: Sabahan Hakkas said "
        "chao men until the Tuaran style spread in the late 1970s.",
  sources=["wiki-tuaran-mee", "guardian-tuaran-mee"])
N("r-tawau", "region", "Tawau, Sabah", country="Malaysia",
  blurb="Where sang nyuk mee is reported invented in 1979.", sources=["wiki-sang-nyuk-mee"])
N("r-sabah", "region", "Sabah", country="Malaysia",
  blurb="The one Malaysian state with a Hakka-majority Chinese population - 58% by 2000, "
        "recruited by the British North Borneo Chartered Company, including a Basel "
        "Mission Christian Hakka stream. Its noodles are named by district, not dialect.",
  sources=["voon-2024-hakka", "cna-sabah-noodles"])
N("r-singapore", "region", "Singapore", country="Singapore",
  blurb="A Hokkien-majority island with the region's second-largest Teochew community - "
        "enough density to turn a Teochew hawker dish into a national one. Almost every "
        "dish in this graph has a Singapore twin that diverged after 1949.",
  sources=["johorkaki-bcm", "muse-emergency-immigration"])
N("r-hong-kong", "region", "Hong Kong", country="China",
  blurb="Where Mak Woon-chi took Guangzhou wonton noodles, and where Cantonese chefs "
        "invented 'Singapore noodles' out of colonial curry powder.",
  sources=["wiki-wonton-noodles", "wiki-singapore-noodles"])
N("r-taiwan", "region", "Taiwan", country="Taiwan",
  blurb="Where KMT veterans from Sichuan created red-braised beef noodle soup in the "
        "Gangshan military dependants' villages after 1949.",
  sources=["wiki-taiwanese-beef-noodle"])
N("r-phuket", "region", "Phuket & Ranong", country="Thailand",
  blurb="Hokkien migration to the Siamese tin frontier came substantially via Penang, "
        "producing the Phuket Baba community - locally Baba-Nyonya - which sustained a "
        "translocal identity oriented on Penang.",
  sources=["wong-big-five", "thai-peranakan-translocal"])
N("r-rangsit", "region", "Rangsit & Ayutthaya, central Thailand", country="Thailand",
  blurb="Canal country. Teochew settlers sold noodles from boats; the small bowl exists "
        "because one vendor paddled, cooked, served, took money and washed up alone. "
        "Rangsit's canals were dug in the 1890s, which is why 12th-century Ayutthaya "
        "boat-noodle claims fail.", sources=["wiki-boat-noodles"])
N("r-bangkok", "region", "Bangkok", country="Thailand",
  blurb="Teochew braised-duck noodles here and in Penang are siblings, not ancestor and "
        "descendant. Thai bamee and kuaitiao are both Teochew loanwords.",
  sources=["wiki-boat-noodles"])
N("r-patani", "region", "Patani & southern Thailand", country="Thailand",
  blurb="The sour-and-hot register Penang Nyonya cooking shares with southern Thai food "
        "is better read as one northern-peninsula regional cuisine than as borrowing "
        "across a border that barely existed.", sources=["kuroda-samsam", "michelin-malaysia-regional"])
N("r-deli-medan", "region", "Deli / Medan, North Sumatra", country="Indonesia",
  blurb="Tobacco plantation belt supplied out of Penang by the Big Five. Medan Hokkien is "
        "closely related to Penang Hokkien.", sources=["wong-big-five"])
N("r-aceh", "region", "Aceh", country="Indonesia",
  blurb="Pepper trade partner and the origin of Penang's Acheen Street enclave. Syed "
        "Mohamed Alatas ran arms from Penang to the Acehnese resistance after the Dutch "
        "attack of the early 1870s.", sources=["malaymail-beyond-hokkien"])
N("r-java-central", "region", "Central Java (Yogyakarta, Surakarta)", country="Indonesia",
  blurb="Home of bakmi jawa / mie godhog, of pecel's peanut sauce logic, and of petis - "
        "the thick shrimp reduction cognate with Penang's hae ko.",
  sources=["nlb-mee-jawa", "wiki-mee-soto"])
N("r-java-east", "region", "East Java & Madura", country="Indonesia",
  blurb="Soto Lamongan and soto Madura are the direct ancestors of Malaysian mee soto. The "
        "1391 Biluluk inscription with hanglaksa is also from East Java.",
  sources=["wiki-mee-soto", "biluluk-1391"])
N("r-minangkabau", "region", "Minangkabau, West Sumatra", country="Indonesia",
  blurb="Usually associated with Negeri Sembilan, but Minangkabau also settled Penang, "
        "Kedah, Perak and Pahang - and are one of the candidate carriers of mee jawa.",
  sources=["malaymail-mee-jawa"])
N("r-phnom-penh", "region", "Phnom Penh & the Mekong delta", country="Cambodia",
  blurb="hu tieu Nam Vang means, literally, 'Phnom Penh koay teow'. The Teochew diaspora "
        "carried the same two syllables to Vietnam, Cambodia and Thailand.",
  sources=["penang-wikia-kuey-teow-thng"])
N("r-brunei", "region", "Brunei", country="Brunei",
  blurb="Kolo mee is popular here too, including as an instant product.",
  sources=["wiki-kolo-mee"])
N("r-suriname", "region", "Suriname", country="Suriname",
  blurb="Javanese indentured labourers carried soto to the Dutch Caribbean, where it is "
        "saoto - the far end of the same diaspora that brought mee soto to Penang.",
  sources=["wiki-mee-soto"])


# =============================================================== CULTURES
N("c-hokkien", "culture", "Hokkien (Hoklo) 福建", family="Chinese dialect group",
  penangShare="38.0% in 1957; 54.2% by 2000; ~64% by mother tongue in 2010",
  arrival="from 1786, continuous",
  niche="trade, shopkeeping, shipping, fishing, tailoring, spice plantations, revenue "
        "farming. Beach Street was the Hokkien-Teochew wholesale spine.",
  blurb="The first and largest group, and the reason Hokkien became the lingua franca of "
        "the Penang street - which is why Teochew and Cantonese dishes carry Hokkien "
        "names. Penang Hokkien is a Zhangzhou sub-dialect saturated with Malay loanwords.",
  confidence="high", sources=["kuchler-1965", "wiki-penangite-chinese", "penang-traveltips-hokkien",
                              "ccs-city-big-five"])
N("c-teochew", "culture", "Teochew 潮州", family="Chinese dialect group",
  penangShare="9.8% in 1957; 22.3% by 2000",
  arrival="18th century onward, in large numbers",
  niche="agriculture and cash crops above all - gambier, pepper, sugar at Perai; "
        "fishermen in Kedah and north Perak; grocers and petty traders in town. 40% of "
        "Penang Teochews lived rurally in 1957.",
  blurb="Numerically third, but credited with Penang's street-food repertoire: char kuey "
        "teow, koay teow th'ng, char kuey kak, koay chiap. Note carefully - that "
        "hawking-dominance claim is repeated everywhere including by Michelin, and no "
        "scholarly source establishes it. It is the load-bearing unverified claim of "
        "Penang food history.",
  confidence="medium", sources=["kuchler-1965", "ccs-city-teochew", "michelin-ckt"],
  flags=["hawking-dominance-unverified"])
N("c-cantonese", "culture", "Cantonese 廣府", family="Chinese dialect group",
  penangShare="16.5% in 1957 falling to ~8-12% later; 86% of them lived in George Town",
  arrival="present from 1801 (Loo Pun Hong carpenters' guild); demographic surge late 19th c.",
  niche="the artisan and craft niche - carpenters, blacksmiths, shoemakers, masons, "
        "goldsmiths (36 of 90 shophouses at Campbell Street x Rope Walk), photographers, "
        "barbers, restaurant and dim sum trade on Cintra Street.",
  blurb="A minority on a Hokkien island, which is why wantan mee, yi mein, chee cheong "
        "fun and wat tan hor all read as slightly imported in Penang. Beware the census: "
        "Cantonese organised by place of origin (hui kuan) while Hokkiens organised by "
        "surname (kongsi), so association records overstate Cantonese numbers.",
  confidence="high", sources=["kuchler-1965", "malaymail-beyond-hokkien", "malaymail-loo-pun-hong",
                              "penang-wikia-kwangtung"])
N("c-hakka", "culture", "Hakka 客家", family="Chinese dialect group",
  penangShare="7.3% in 1957; 60% of them lived in the countryside",
  arrival="association in Penang by 1801; mass wave on the tin boom from mid-19th c.",
  niche="mining first - 64% of Selangor's 28,125 tin-mine Chinese in 1891 were Hakka - "
        "then Chinese medicine halls, textiles, pawnbroking; in Penang the vegetable "
        "farmers and rubber planters of Balik Pulau and the Penang Hill slopes.",
  blurb="The only one of the five groups from entirely inland China, which is why their "
        "food is wheat-dough and preserved-meat rather than seafood. Hakka women did not "
        "foot-bind and worked as dulang washers. Penang is the weakest Malaysian site for "
        "Hakka noodle culture; Sabah, Ampang and Seremban are the strongest.",
  confidence="high", sources=["voon-2024-hakka", "kuchler-1965", "taiwan-panorama-hakka",
                              "michelin-yong-tau-foo"])
N("c-hainanese", "culture", "Hainanese (Kheng Chew) 海南", family="Chinese dialect group",
  penangShare="2.8% in 1957 - 8,436 people",
  arrival="LATE. This is the pivotal fact.",
  niche="unable to break into trades already locked up, they took service work - "
        "houseboys, domestic servants, ships' crew, and cooks for British and Straits "
        "Chinese households - then converted those skills into hotels, restaurants and "
        "the kopitiam.",
  blurb="The smallest group and the most consequential for food. Hainanese occupational "
        "disadvantage produced Malaysia's entire colonial-fusion cuisine: chicken rice, "
        "chicken chop, mee Hailam, wok-roasted kopi. They were the only dialect group "
        "whose economic niche literally was cooking - and cooking for non-Chinese "
        "employers at that.",
  confidence="high", sources=["mothership-hainanese", "malaymail-beyond-hokkien",
                              "kuchler-1965", "wiki-hainanese-chicken-rice",
                              "hainan-temple-penang"])
N("c-foochow", "culture", "Foochow / Hokchiu 福州", family="Chinese dialect group",
  penangShare="1.2% in 1957 - 3,638 including Hokchia",
  arrival="1901 Sibu, 1903 Sitiawan - both engineered mission colonies, not chain migration",
  niche="agricultural colonists in Borneo and Perak; in Penang, hotels and restaurants "
        "alongside the Hainanese.",
  blurb="Fuzhou fish balls stuffed with minced pork, red glutinous rice wine, kampua mee, "
        "hand-pulled mee sua. Constantly and wrongly credited with kolo mee and Sarawak "
        "laksa, which are Kuching dishes; the Foochow noodle is kampua, from Sibu.",
  confidence="high", sources=["wiki-wong-nai-siong", "ipoh-echo-foochow-sitiawan",
                              "borneo-post-sarawak-mee"])
N("c-henghua", "culture", "Heng Hwa / Xinghua 興化", family="Chinese dialect group",
  penangShare="378 people in 1957",
  blurb="Puxian Min speakers from Putian, neither Hokkien nor Foochow. Their finer, "
        "silkier bee hoon is a named speciality across the Straits.",
  confidence="medium", sources=["kuchler-1965"])
N("c-peranakan-penang", "culture", "Penang Peranakan (Baba-Nyonya)", family="creole community",
  arrival="largely a 19th-century formation, fed from Malacca and by direct Fujian arrivals",
  blurb="Hokkien traders married Malay, Siamese and Burmese women. Unlike Malacca and "
        "Singapore, Penang Peranakans did NOT shift to Baba Malay - they kept Hokkien, "
        "heavily loaded with Malay loanwords. Their kitchen is the sour, herbal, "
        "coconut-light northern register: tamarind, asam gelugur, torch ginger, laksa leaf, "
        "and almost no santan in the signature dish.",
  confidence="high", sources=["michelin-malaysia-regional", "adriancheah-nyonya",
                              "peranakan-genetics", "hutton-nyonya"])
N("c-peranakan-malacca", "culture", "Malacca & Singapore Peranakan", family="creole community",
  blurb="The older community, 15th-16th century. Shifted to Baba Malay - Malay lexicon on "
        "Hokkien grammar. Heavier santan, candlenut, buah keluak; acidity comparatively "
        "disfavoured. The control group against which Penang's difference is measured.",
  confidence="high", sources=["michelin-malaysia-regional"])
N("c-phuket-baba", "culture", "Phuket Baba (Thai Peranakan)", family="creole community",
  blurb="Hokkien tin migrants who reached Phuket via Penang. Recent scholarship argues "
        "they did not simply assimilate into Thai-ness but sustained a translocal identity "
        "with Penang as reference node.",
  confidence="medium", sources=["thai-peranakan-translocal", "wong-big-five"])
N("c-jawi-peranakan", "culture", "Jawi Peranakan / Jawi Pekan", family="creole community",
  blurb="Penang's own creole Muslim elite: locally born Malay-speaking Muslims descended "
        "from Indian Muslim or Arab fathers and Malay mothers. Merchants, landlords, "
        "English-educated, and financiers of the Jawi Peranakkan newspaper (1876-1895), "
        "the first Malay-language newspaper. Being Muslim, they were assimilable into "
        "Malay identity in a way the Chinese Peranakans were not - and after the Depression "
        "most registered simply as Malay.",
  confidence="high", sources=["wiki-jawi-peranakan", "nlb-jawi-newspaper", "iium-jawi-peranakan"])
N("c-tamil-muslim", "culture", "Tamil Muslim / Mamak", family="ethnic community",
  arrival="operating on the Kedah coast for centuries before 1786; in Penang within days "
          "of Light's landing. 7,886 'Chulias' in the 1833 Penang census.",
  niche="mercantile and urban - traders, shopkeepers, hawkers, and the stall that became "
        "an institution.",
  blurb="From Tamil maamaa, 'maternal uncle'. Halal is not an incidental attribute of "
        "this community's food; it is the enabling constraint. A Tamil Muslim vendor could "
        "buy Chinese wheat noodles and sell cooked food to Malays, occupying the one niche "
        "between the Chinese and Malay kitchens that nobody else could hold.",
  confidence="high", sources=["oed-mamak", "wiki-chulia-street", "areca-chulia",
                              "cambridge-yearning-mamak", "wiki-roti-canai", "wiki-teh-tarik"])
N("c-marakkayar", "culture", "Marakkayar / Maraikayar", family="ethnic community",
  blurb="A maritime trading community of the Coromandel ports tracing descent from Arab "
        "seafarers who married South Indian women. Cauder Mohideen Merican, a Marakkayar, "
        "was Penang's first Kapitan Keling in 1801. 'Merican' is the Malaysian surname "
        "marker.", confidence="high", sources=["wiki-kapitan-keling-mosque", "wiki-chulia-street"])
N("c-mappila", "culture", "Mappila / Malabar Muslim", family="ethnic community",
  blurb="Kerala Muslims, the original settlers of what was Malabar Street before it was "
        "renamed Chulia Street in 1798. The likely conduit for the Malabar parotta lineage.",
  confidence="medium", sources=["wiki-chulia-street", "taste-roti-canai"])
N("c-tamil-hindu", "culture", "Tamil (non-Muslim) labour migration", family="ethnic community",
  arrival="indenture then the kangani system; over 1.7 million Indians recruited into "
          "Malaya c.1840-1942; kangani abolished 1938",
  blurb="Almost entirely a labour story rather than a trading one - estates in Province "
        "Wellesley and beyond. Their food footprint in Penang is the vegetarian South "
        "Indian one plus putu mayam, not the hawker noodle canon. The distinction from "
        "the Tamil Muslim thread is material, not pedantic.",
  confidence="high", sources=["malaymail-beyond-hokkien"])
N("c-chettiar", "culture", "Nattukottai Chettiar (Nagarathar)", family="ethnic community",
  blurb="Merchant-bankers from Sivagangai and Pudukottai who financed much of the region's "
        "commerce from Lebuh Penang and built the Waterfall Road Murugan temple around "
        "1854 - today the terminus of Penang's Thaipusam procession.",
  confidence="high", sources=["malaymail-beyond-hokkien"])
N("c-arab-hadhrami", "culture", "Arab / Hadhrami", family="ethnic community",
  blurb="Sayyid lineages trading in Kedah and Penang ports. Tengku Syed Hussain Al-Aidid - "
        "Arab trader and member of the Acehnese royal house - moved to Penang in 1792, "
        "founded the Acheen Street Mosque in 1808, and held jurisdiction under Islamic "
        "rather than colonial law. Their most food-relevant legacy is the hajj trade.",
  confidence="high", sources=["malaymail-beyond-hokkien", "wiki-murtabak"])
N("c-malay-kedah", "culture", "Kedah Malay", family="ethnic community",
  blurb="The substrate. Penang's Malay dishes are best read as urbanised Kedah dishes: "
        "the rice-bowl, inshore-fish, tamarind-sour foodways of the north, continuous with "
        "southern Thai cooking rather than with Johor-Riau.",
  confidence="high", sources=["kuroda-samsam", "wiki-laksa"])
N("c-javanese", "culture", "Javanese", family="ethnic community",
  arrival="the largest Netherlands Indies stream into Penang and Province Wellesley; much "
          "of it estate labour, and in the early 20th century indentured kuli kontrak",
  blurb="Reached Penang as whole dishes, not just ingredients: soto became mee soto, and "
        "the pecel/petis logic of peanut-and-sweet-potato sauce underwrites mee rebus and "
        "mee jawa. Post-independence ethnic classification folded them into 'Malay', which "
        "erased the genealogy from official view even as the dish names preserved it.",
  confidence="high", sources=["wiki-mee-soto", "nlb-mee-rebus", "nlb-mee-jawa"])
N("c-minangkabau", "culture", "Minangkabau", family="ethnic community",
  blurb="One of the candidate carriers of mee jawa into Penang, alongside the Chinese-"
        "Javanese Peranakan account.", confidence="low", sources=["malaymail-mee-jawa"])
N("c-acehnese", "culture", "Acehnese", family="ethnic community",
  blurb="Older and commercial rather than labour: the pepper trade, and the Lebuh Acheh "
        "enclave that remains the most legible Malay-Muslim quarter of George Town.",
  confidence="high", sources=["malaymail-beyond-hokkien"])
N("c-siamese-my", "culture", "Malaysian Siamese", family="ethnic community",
  blurb="Concentrated in the former Siamese tributary states, with a long-settled Penang "
        "community. Wat Chayamangkalaram (1845) is the oldest Siamese temple on the island. "
        "The Samsam of inland Kedah - Tai-speaking, mostly Muslim - show the boundary was "
        "gradual, not a line.", confidence="high", sources=["kuroda-samsam"])
N("c-burmese-penang", "culture", "Burmese Penang", family="ethnic community",
  blurb="Dhammikarama, whose land was bought on 1 August 1803 by one 'Nonya' Betong for "
        "390 Spanish dollars, is the oldest Buddhist temple in traditional Burmese style "
        "outside Myanmar - and sits directly opposite the Siamese temple in Pulau Tikus. "
        "The Peranakan honorific on a Burmese transaction in 1803 says everything about "
        "how entangled these communities were.", confidence="high",
  sources=["malaymail-beyond-hokkien"])
N("c-iban", "culture", "Iban", family="ethnic community",
  blurb="Iban and Malay Sarawakians eat mi kolok widely, which is why halal kolo mee has "
        "its own indigenous-language names - mi kering, mi rangkai.",
  confidence="high", sources=["wiki-kolo-mee"])
N("c-kadazan-dusun", "culture", "Kadazan-Dusun", family="ethnic community",
  blurb="Lihing, their rice wine, is worked into Tuaran mee - an indigenous Bornean "
        "borrowing with no peninsular equivalent.", confidence="medium",
  sources=["wiki-tuaran-mee"])
N("c-british-colonial", "culture", "British colonial administration & commerce",
  family="colonial apparatus",
  blurb="Not a cuisine but a supply chain. The free port, the coolie ordinances, the "
        "plantation economy, standardised curry powder, condensed milk, bottled sauce, and "
        "the European households in whose kitchens Hainanese cooks learned their trade.",
  confidence="high", sources=["oed-curry", "muse-emergency-immigration", "mothership-hainanese"])


# ==================================================================== WAVES
N("w-pre-1786-kedah", "wave", "Pre-1786: the Chinese of Kedah", period="before 1786",
  blurb="Light did not import settlers from China - he recruited them from the "
        "Malay-Siamese world next door. Koh Lay Huan, a Hokkien merchant who had rebelled "
        "against the Qing and based himself at Kuala Muda, Kedah, brought boatloads of "
        "Chinese and Malay settlers and became the first and only Kapitan Cina of George "
        "Town in May 1787. Penang's founding Chinese elite were already regional political "
        "operators, not fresh migrants.",
  confidence="high", sources=["penang-traveltips-koh-lay-huan", "kuchler-1965"])
N("w-1786-founding", "wave", "1786: the founding of George Town", period="1786-1830",
  blurb="Light landed 11 August 1786 on Kedah territory. James Low's 1836 list already "
        "names Hokkien, Zhangzhou, Jiaying Hakka, Teochew and multiple Cantonese "
        "sub-districts - every dialect group in this graph was present within fifty years.",
  confidence="high", sources=["kuchler-1965", "wiki-demographics-penang",
                              "penang-traveltips-goddess-mercy"])
N("w-malacca-baba", "wave", "Peranakan relocation from Dutch Malacca", period="from 1786",
  blurb="Baba families moved north to the new British free port. So Penang's Chinese "
        "community was layered from day one: a Malacca-Peranakan and Kedah-Hokkien "
        "mercantile stratum on top, direct arrivals from Fujian and Guangdong beneath. "
        "That layering is the origin of the Penang distinction between Nyonya home cooking "
        "and sinkeh hawker cooking.",
  confidence="high", sources=["kuchler-1965", "wiki-penangite-chinese"])
N("w-sinkeh-coolie", "wave", "The sinkeh and the credit-ticket system", period="1840s-1930s",
  blurb="New guests (新客) who could not pay their passage; brokers advanced the fare and "
        "controlled the contract. Over a million Chinese migrated to British Malaya between "
        "the 1870s and 1930s. Penang was a port of entry, not merely a destination - every "
        "pioneer opening the tin fields of southern Siam, Larut and Kinta was based here.",
  confidence="high", sources=["kuchler-1965", "nlb-chinese-immigrants-1877", "voon-2024-hakka"])
N("w-suez-1869", "wave", "The Suez Canal and the Straits route", period="1869 onward",
  blurb="Four structural shifts made Penang: Suez moving the main trade route from the "
        "Sunda Strait to the Straits of Malacca, British intervention intensifying tin "
        "extraction, the Dutch opening Sumatra's east-coast plantation belt, and the "
        "introduction of Hevea rubber.", confidence="high", sources=["kuchler-1965"])
N("w-tin-boom", "wave", "Tin, Larut and the secret societies", period="1840s-1900s",
  blurb="Tin was the engine and it organised labour by dialect and sub-dialect. Of ~80-90 "
        "shophouses in Larut in 1865, 70-80 were owned by Haishan Hakkas, 11 by Huizhou "
        "Hakkas, 2 by Hainanese. Note that no single dialect-to-society mapping survives "
        "scrutiny: sources give three mutually contradictory alignments for 1867, and the "
        "Penang alignment differed from the Perak one.",
  confidence="disputed", sources=["voon-2024-hakka", "wiki-larut-wars", "wiki-1867-riots"],
  flags=["dialect-to-society-mapping-unsafe"])
N("w-1867-riots", "wave", "The 1867 Penang Riots", period="3-12 August 1867",
  blurb="Ten days. Gee Hin (~20,000) against Toh Peh Kong (~9,000), the latter led by Khoo "
        "Thean Teik - a member of one of the Big Five Hokkien clans, which is the crucial "
        "link between respectable clan power and street power. Triggered by a rambutan skin "
        "thrown in an argument. Over 100 dead; each faction paid a 5,000-dollar 'voluntary "
        "penalty'; the Suppression of Dangerous Societies Ordinance followed in 1869.",
  confidence="high", sources=["wiki-1867-riots", "penang-traveltips-riots"])
N("w-1877-protectorate", "wave", "Chinese Immigrants Ordinance & the Protectorate",
  period="1877",
  blurb="Licensed coolie brokers and depots; protectorates in Singapore, Penang and "
        "Malacca. Regulation arrived roughly thirty years after the abuses became notorious.",
  confidence="high", sources=["nlb-chinese-immigrants-1877"])
N("w-1901-sibu-foochow", "wave", "Wong Nai Siong's Foochow colony at Sibu", period="1901",
  blurb="A Methodist negotiated with Rajah Charles Brooke, recruited Fuzhou farmers, and "
        "landed 72 pioneers. Over 1,000 Christian Foochows in 'Sin Hockchew' by 1903. "
        "Engineered settlement, not chain migration - which is why Sarawak's dialect map "
        "looks nothing like the peninsula's.",
  confidence="high", sources=["wiki-wong-nai-siong"])
N("w-1903-sitiawan-foochow", "wave", "The Sitiawan Foochow colony", period="1903",
  blurb="The government contracted the Methodist Episcopal Mission to plant Foochow farmers "
        "at Sitiawan explicitly to feed the growing coolie population. Malaysia's noodle "
        "geography was, in this one case, agricultural policy.",
  confidence="high", sources=["ipoh-echo-foochow-sitiawan"])
N("w-kangani", "wave", "Indenture and the kangani system", period="c.1840-1938",
  blurb="Over 1.7 million Indians recruited into Malaya. The kangani was an experienced "
        "Tamil worker sent home with cash advances to recruit kin and neighbours, "
        "leveraging village, caste and kinship ties - a system that reliably slid into debt "
        "bondage. Dominant after 1910 when rubber boomed; abolished 1938.",
  confidence="high", sources=["malaymail-beyond-hokkien"])
N("w-javanese-labour", "wave", "Javanese and Sumatran migration into Penang & the mainland",
  period="19th-20th century",
  blurb="Javanese, Minangkabau, Bugis, Banjar, Bawean, Mandailing and Acehnese, much of it "
        "estate labour into Province Wellesley. Malaysian ethnic classification later "
        "folded all of them into 'Malay'.", confidence="high",
  sources=["nlb-mee-jawa", "wiki-mee-soto"])
N("w-hajj-port", "wave", "Penang as a hajj pilgrim port", period="19th-early 20th century",
  blurb="Before air travel, Acheen Street organised the hajj for the whole northern region. "
        "Pilgrims from North Sumatra, southern Siam and the northern peninsula assembled "
        "there, sometimes for weeks, to arrange passage and buy provisions. That produced a "
        "floating population of Muslims from across the region eating in the same lanes, and "
        "a demand for portable, spice-heavy, halal, wheat-based food. The food-transmission "
        "inference is reasoned rather than directly sourced.",
  confidence="medium", sources=["malaymail-beyond-hokkien"], flags=["interpretation"])
N("w-1932-aliens", "wave", "The Aliens Ordinance", period="1930, in force 1 April 1933",
  blurb="Quotas capped adult Chinese males while Chinese women were actively encouraged to "
        "enter, to correct a grossly male-skewed sex ratio. The food-history consequence is "
        "inferential but strong: the 1930s female influx is the demographic precondition for "
        "family-run hawker stalls, and for home cooking crossing into commercial street "
        "food. Bachelor-society eating-out became family enterprise.",
  confidence="medium", sources=["nlb-immigration-1932", "immigration-dept-history"],
  flags=["interpretation"])
N("w-japanese-occupation", "wave", "The Japanese Occupation", period="1941-45",
  blurb="Sook Ching purges targeted Penang Chinese. For food history the useful corrective "
        "is an eyewitness account that during those years there were essentially no noodles "
        "and hardly any rice in Penang, with sustenance from tapioca and cassava - which "
        "undermines the popular story that Penang Hokkien mee was 'invented' in wartime "
        "scarcity. In Singapore, char kway teow was made with tapioca noodles fried in red "
        "palm oil, so wartime CKT was red.",
  confidence="medium", sources=["johorkaki-hokkien-mee", "nlb-ckt"])
N("w-1949-closure", "wave", "The Emergency and the closing of the pipeline",
  period="1948-1960, key ordinance July 1949",
  blurb="Emergency regulations ended the mass influx that had run since 1786. By 1952 "
        "citizenship extended to most Malaya-born with a Malaya-born parent; by 1957, 81% of "
        "Penang's Chinese were locally born. This is the hinge of the whole graph: after it, "
        "no fresh cohort arrived from China to correct or refresh the dialect repertoires. "
        "Everything since is endogenous local evolution - which is exactly why Penang, "
        "Singapore and KL versions of 'the same' dish diverged so far.",
  confidence="high", sources=["muse-emergency-immigration", "kuchler-1965"])
N("w-post2000-thai", "wave", "Late commercial diffusion of Thai food", period="1990s-2020s",
  blurb="Tom yum noodles and boat noodles are recent arrivals via Thai restaurants, Thai-"
        "Malaysian cooks and cross-border traffic through Bukit Kayu Hitam and Padang Besar. "
        "Important not to conflate them with the older Siamese substrate.",
  confidence="medium", sources=["wiki-boat-noodles"])


# ================================================================= NOODLES
N("n-yellow-alkaline", "noodle", "Yellow alkaline wheat noodle", zh="黃麵 / 油麵",
  malay="mi kuning", material="wheat + kansui (sodium/potassium carbonate)",
  marker="Hokkien staple; the pan-Malayan default",
  blurb="Alkali converts colourless flavonoid pigments in wheat flour to yellow ionic "
        "forms, strengthens the gluten network, and gives the springy, heat-resistant "
        "texture that survives a wok. This is why the same noodle turns up in Hokkien mee, "
        "KL Hokkien char, curry mee, mee rebus, mee goreng mamak and mee soto: it was the "
        "cheap, durable, factory-made noodle of the Straits, sold to everybody. The noodle "
        "is Chinese infrastructure; the sauce is where ethnicity lives.",
  confidence="high", sources=["johorkaki-hokkien-mee", "wiki-mee-goreng-mamak"])
N("n-tai-lok-mee", "noodle", "Thick yellow noodle (tai lok mee)", zh="大碌麵",
  material="wheat + alkali, 4-5 mm diameter",
  blurb="The fat noodle KL Hokkien mee is built on, and the source of that dish's Cantonese "
        "nickname.", confidence="high", sources=["kim-lian-kee"])
N("n-koay-teow", "noodle", "Flat rice noodle", zh="粿條 (Teochew) / 河粉 (Cantonese)",
  malay="kuetiau", material="steamed rice sheet, cut into ribbons",
  marker="Teochew and Cantonese - two names, near-identical product",
  blurb="粿 is a steamed rice-flour cake and 條 a long narrow strip, so char kway teow is "
        "literally 'stir-fried rice-cake strips'. The Cantonese 河粉 'river flour' names the "
        "same object from a different angle, after Shahe in Guangzhou. Penang cuts thinner "
        "ribbons than Singapore.",
  confidence="high", sources=["wiki-char-kway-teow", "ipoh-echo-kai-si-hor-fun", "michelin-ckt"])
N("n-bee-hoon", "noodle", "Rice vermicelli", zh="米粉", malay="bihun",
  material="extruded rice flour, dried", marker="Hokkien; the halal-safe default",
  blurb="The international name for the product is a Hokkien word - both 'bee hoon' and "
        "'bihun' descend from 米粉 read in Southern Min, which is a direct index of who "
        "carried it around the world. Penang's second-most-used noodle, and half of the "
        "island's characteristic mixed-noodle bowl.",
  confidence="high", sources=["wiki-penang-cuisine"])
N("n-laksa-noodle", "noodle", "Thick round rice laksa noodle", zh="叻沙粉",
  malay="mi laksa / lai fun", material="thick extruded rice noodle",
  blurb="A 1930s photograph caption of a Penang laksa hawker calls it an 'elongated rice "
        "cake'. In Katong laksa it is cut short so the bowl can be eaten with a spoon alone "
        "- a hawker-speed adaptation with a large cultural payload.",
  confidence="high", sources=["johorkaki-laksa-word", "wiki-laksa"])
N("n-mee-sua", "noodle", "Salted wheat thread", zh="麵線", malay="mi sua",
  material="wheat, hand-pulled, heavily salted, sun-dried",
  marker="Quanzhou and Fuzhou Hokkien; ritual food",
  blurb="麵 noodle + 線 thread. The salt is a processing aid that makes the dough extensible, "
        "not a seasoning choice. Cooks in seconds and disintegrates if overcooked - which is "
        "the entire point of the 糊 porridge form.",
  confidence="high", sources=["carryitlikeharry-misua"])
N("n-mee-kia-youmian", "noodle", "Thin round egg noodle", zh="幼麵 / 麵仔",
  aka=["you mee", "yau min", "mee kia", "wantan mee noodle"],
  material="wheat + egg + alkali, drawn thin and round",
  marker="Cantonese (Guangzhou), and the Teochew mee kia",
  blurb="幼 in Cantonese means fine or delicate, not young. Mee kia - 'child noodle', with "
        "the Hokkien diminutive 仔 - and Cantonese yau min denote the SAME physical noodle "
        "through two dialect lexicons. This is the single most confused term in Malaysian "
        "noodle vocabulary.",
  confidence="high", sources=["wiki-mee-pok", "wiki-banmian"])
N("n-mee-pok", "noodle", "Flat egg noodle (mee pok)", zh="麵薄",
  material="wheat + egg + lye, flat ribbon 4-6 mm wide", marker="Chaoshan Teochew",
  blurb="'Thin' here means shallow in cross-section, not narrow - mee pok is the WIDER of "
        "the mee pok / mee kia pair, which trips up every English speaker who meets it.",
  confidence="high", sources=["wiki-mee-pok"])
N("n-yi-mein", "noodle", "E-fu noodle brick", zh="伊麵 / 伊府麵", aka=["yee mee", "e-fu"],
  material="wheat + egg + lye, boiled or steamed, deep-fried and dried into a flat brick",
  marker="Cantonese banquet cooking",
  blurb="A shelf-stable pre-cooked noodle, rehydrated on demand - the technique that would "
        "much later be industrialised as instant noodles. Note that the popular line calling "
        "yi mein 'the ancestor of instant noodles' is a rhetorical framing, not a "
        "demonstrated line of descent to Ando Momofuku's 1958 product.",
  confidence="high", sources=["wiki-yi-mein"])
N("n-pan-mee-dough", "noodle", "Hand-cut or hand-torn wheat dough noodle", zh="板麵",
  aka=["ban mian", "pan mee"], material="wheat, water, salt, often egg - non-alkaline",
  marker="Hakka, with a parallel Hokkien tradition",
  blurb="板 means board or plank. Three forms are sold at the same stall and Malaysians treat "
        "them as one family: hand-torn irregular pieces (mee hoon kueh, the Hokkien method), "
        "flat cut strips about 1 cm wide, and near-round spaghetti-gauge strands sold as "
        "'you mee'. What is sold today is a hybrid: the Hakka shaved dough off a block, the "
        "Hokkien rolled and tore it, and the modern stall merges both under the Hakka name.",
  confidence="high", sources=["wiki-banmian", "radii-chinese-noodles"])
N("n-ccf-sheet", "noodle", "Steamed rice-flour sheet", zh="豬腸粉 / 腸粉",
  material="rice flour, water, sometimes tapioca or wheat starch, steamed thin and rolled",
  marker="Cantonese",
  blurb="'Pig intestine noodle' contains no offal - the name describes the rolled sheet's "
        "resemblance to a length of intestine. The same technology family reaches Vietnamese "
        "banh cuon and Chaozhou pork-intestine rice rolls.",
  confidence="high", sources=["wiki-chee-cheong-fun", "penang-wikia-ccf"])
N("n-koay-chiap-sheet", "noodle", "Broad flat rice sheet (koay chiap)", zh="粿汁",
  material="rice sheet, wider and floppier than koay teow, folded into loose triangles",
  marker="Teochew",
  blurb="Closer to a lasagne sheet than to a ribbon. The phonetic proximity of koay chiap / "
        "koay teow / 'koay chiak' generates persistent confusion, not helped by Penang "
        "stalls selling both from one cart.",
  confidence="high", sources=["wiki-kway-chap"])
N("n-maggi-block", "noodle", "Instant fried noodle block", malay="Maggi",
  material="wheat, flash-fried", marker="Nestle, Malaysia from 1971",
  blurb="The only noodle in this graph with a supply-chain birthday.",
  confidence="high", sources=["nestle-maggi-malaysia"])
N("n-lo-shi-fun", "noodle", "Rat-tail noodle", zh="老鼠粉 / 鼠麵", aka=["mee tai bak", "loh shi fun"],
  material="short tapered extruded rice noodle", marker="Cantonese and Hakka",
  blurb="Penang fries these with char kway teow ingredients, a version Singapore does not "
        "have. Note: this noodle is sometimes floated as a laksa etymology - there is no "
        "support for that anywhere in the literature and the resemblance is coincidental.",
  confidence="medium", sources=["michelin-ckt", "johorkaki-laksa-word"],
  flags=["not-a-laksa-etymology"])
N("n-tang-hoon", "noodle", "Glass noodle", zh="冬粉 / 粉絲", malay="suun",
  material="mung-bean starch",
  blurb="Routinely blurred with bee hoon on English menus. The carrier in Nyonya chap chai.",
  confidence="high", sources=["wiki-penang-cuisine"])
N("n-fish-noodle", "noodle", "Fish-paste noodle", zh="魚麵", aka=["yu mee"],
  material="pounded fish paste, sometimes with no wheat flour at all",
  marker="Foochow - Sibu, Serikei, Sitiawan, Yong Peng",
  blurb="A genuine, distinct, low-frequency product, and the third of four things people "
        "mean when they say 'you mee'.", confidence="medium", sources=["borneo-post-sarawak-mee"])
N("n-idiyappam", "noodle", "String hopper / putu mayam", tamil="idiyappam",
  material="rice-flour dough extruded through a sieve and steamed",
  marker="Tamil, ancient - placed in the Tamil country by the 1st century CE on Sangam "
         "evidence",
  blurb="Worth stating for the structural point: extrusion as a noodle technology arrived "
        "in the peninsula from at least two directions, Chinese and South Indian, and "
        "idiyappam, Malay putu mayang and Chinese loh shi fun occupy adjacent niches.",
  confidence="high", sources=["malaymail-beyond-hokkien"])
N("n-tapioca-wartime", "noodle", "Wartime tapioca noodle", period="1942-45",
  blurb="Used because tapioca was cheap, and fried in red palm oil - so occupation-era char "
        "kway teow was red. Sourced to a National Archives of Singapore oral history "
        "interview, which is unusually good evidence for a food claim.",
  confidence="medium", sources=["nlb-ckt"])
N("n-thai-sen-range", "noodle", "Thai sen range", zh="—",
  material="sen yai (wide rice), sen lek (narrow rice), sen mee (vermicelli), bamee (egg)",
  blurb="Thai noodle vocabulary is structurally Chinese: kuaitiao is a loan of Teochew 粿條 "
        "and bamee of Teochew 肉麵. The direction of transmission is not in doubt.",
  confidence="high", sources=["wiki-boat-noodles"])


# ============================================================= INGREDIENTS
def ING(nid, label, **kw):
    return N(nid, "ingredient", label, **kw)

ING("i-belacan", "Belacan", malay="belacan", role="fermented shrimp paste, toasted before use",
    blurb="An indigenous Southeast Asian umami source standing in the position that "
          "fermented soybean occupies in Chinese cooking. Non-negotiable in Nyonya cooking.",
    origin="c-malay-kedah", confidence="high", sources=["adriancheah-nyonya"])
ING("i-hae-ko", "Hae ko / petis udang", zh="蝦膏", malay="petis udang / otak udang",
    role="thick black molasses-like fermented prawn paste",
    blurb="A Chinese-Penang manufactured product - Cheong Kim Chuan is the George Town "
          "institution - whose Malay name points to the Javanese petis tradition. It is the "
          "single ingredient that makes Penang asam laksa taste like Penang rather than like "
          "Kedah, and it also anchors Penang rojak and Penang chee cheong fun. One condiment "
          "crossing the Chinese/Malay line three times.",
    confidence="high", sources=["wiki-laksa", "penang-wikia-ccf"])
ING("i-sambal", "Sambal", malay="sambal", role="pounded chilli relish",
    blurb="In Penang Hokkien mee the sambal is cooked INTO the broth, which is the clearest "
          "single divergence from both Xiamen and Singapore. In curry mee it is served on the "
          "side for the eater to dose. Same ingredient, opposite conventions, one island.",
    confidence="high", sources=["johorkaki-hokkien-mee"])
ING("i-santan", "Coconut milk (santan)", malay="santan", role="enrichment",
    blurb="The axis on which the laksa family splits. Malacca and Singapore Nyonya cooking "
          "leans on it; Penang's signature laksa contains none at all - and Penang cooks call "
          "the coconut version 'Siamese', which tells you where they think the local norm lies.",
    confidence="high", sources=["michelin-malaysia-regional", "wiki-laksa"])
ING("i-asam-jawa", "Tamarind (asam jawa)", malay="asam jawa", role="souring agent, as pulp/juice",
    confidence="high", sources=["wiki-laksa"])
ING("i-asam-gelugur", "Asam gelugur / asam keping", malay="asam gelugur",
    role="dried slices of Garcinia atroviridis, native to the peninsula",
    blurb="Penang asam laksa uses tamarind juice with gelugur; laksa Kedah leads with the "
          "dried slices. A small difference that is one of the few reliable markers between "
          "the two.", confidence="medium", sources=["wiki-laksa", "ummi-laksa-guide"])
ING("i-bunga-kantan", "Torch ginger bud (bunga kantan)", malay="bunga kantan",
    role="Etlingera elatior, shredded", blurb="The signature perfume of Penang asam laksa, "
    "and the herbal top-note that most distinguishes the Penang Nyonya register.",
    confidence="high", sources=["wiki-laksa", "adriancheah-nyonya"])
ING("i-daun-kesum", "Laksa leaf (daun kesum)", malay="daun kesum",
    role="Persicaria odorata / Vietnamese coriander", confidence="high", sources=["wiki-laksa"])
ING("i-curry-powder", "Curry powder", tamil="from kari கறி",
    role="pre-ground, shelf-stable spice blend",
    blurb="The word is Tamil for a spiced sauce, not a dish. But pre-mixed curry POWDER is a "
          "British 18th-century invention - first advertised in London in 1784, standardised "
          "in Madras from the 1830s. That matters enormously: a Hokkien hawker could not "
          "realistically maintain a Tamil spice-roasting practice, but he could buy a packet. "
          "Commodified curry powder is what made curry portable into a Chinese wok.",
    confidence="high", sources=["oed-curry"])
ING("i-curry-leaf", "Curry leaf", tamil="karuvepillai",
    role="Murraya koenigii", blurb="Planted in Indian Penang backyards and adopted by Chinese "
    "and Malay cooks - travelled the same route as the powder but as a plant.",
    confidence="medium", sources=["oed-curry"])
ING("i-taucu", "Fermented soybean paste (taucu)", zh="豆醬", malay="taucu / taucheo",
    role="salted fermented soybean",
    blurb="The umami spine of mee rebus and mee siam. Note the elegant detail: Penang's "
          "CHINESE mee jawa omits taucu, because the Malay version had already made this "
          "Chinese-origin ingredient its signature.",
    confidence="high", sources=["nlb-mee-rebus", "nlb-mee-jawa"])
ING("i-sweet-potato", "Sweet potato", malay="keledek", role="gravy thickener, mashed",
    blurb="The starch that unites mee rebus, mee jawa, pasembur gravy and mee bandung. Four "
          "dishes, two kitchens, one thickening solution to the same economic problem: how do "
          "you make a small amount of expensive protein flavour a large amount of cheap noodle.",
    confidence="high", sources=["nlb-mee-rebus", "wiki-pasembur"])
ING("i-peanut", "Groundnut / peanut", malay="kacang tanah", role="ground, as thickener and body",
    blurb="Shared by Javanese pecel, Malay satay sauce, pasembur gravy, mee rebus, mee jawa "
          "and - unexpectedly - the Sarawak laksa rempah.",
    confidence="high", sources=["johorkaki-sarawak-laksa", "wiki-pasembur"])
ING("i-kicap-manis", "Sweet soy (kicap manis)", malay="kicap manis", role="sweet dark soy",
    confidence="high", sources=["wiki-mee-goreng-mamak"])
ING("i-dark-soy", "Dark soy / caramelised soy", zh="黑醬油", role="colour and sweetness",
    blurb="The Malaysian dry wantan mee's caramelised dark soy has no Guangzhou antecedent - "
          "it is a Malayan innovation. KL Hokkien mee is defined by how much of it goes in.",
    confidence="high", sources=["wiki-wonton-noodles", "kim-lian-kee"])
ING("i-tomato-ketchup", "Bottled tomato and chilli sauce", role="industrial condiment",
    blurb="The reason mee goreng mamak is red-orange. Maggi brought both to Malaysia in 1969 - "
          "two years before it brought the noodles.",
    confidence="high", sources=["nestle-maggi-malaysia", "wiki-mee-goreng-mamak"])
ING("i-lard", "Pork lard and lard croutons", zh="豬油 / 豬油粕", role="fat and texture",
    blurb="chee yau char - crisp lard croutons - are non-negotiable in KL Hokkien mee and in "
          "classic kolo mee. Singapore hawkers were pushed off lard by the 1999 pig virus "
          "epidemic and a 2006 health campaign; Penang was not.",
    confidence="high", sources=["michelin-ckt", "wiki-kolo-mee"])
ING("i-pork-blood", "Coagulated pig's blood", role="cubes in broth",
    blurb="The Penang curry mee signature, and the thing that fixes the dish permanently on "
          "the non-halal side of the boundary despite its Indian and Malay components.",
    confidence="high", sources=["penang-wikia-white-curry", "wiki-laksa"])
ING("i-cockles", "Blood cockles", malay="kerang", zh="蚶", role="shellfish",
    blurb="Shared by char kway teow, curry mee and KL curry laksa. In halal Malay CKT the "
          "kerang is often pushed to the front as the star, filling the flavour hole left by "
          "the lard.", confidence="high", sources=["michelin-ckt", "wiki-char-kway-teow"])
ING("i-prawn-heads", "Prawn heads and shells", role="stock base, dry-fried first",
    blurb="The technique - 爆香, caramelising the heads before boiling - is what makes the "
          "Penang Hokkien mee broth. Its reach is wider than people notice: Ipoh's kai si hor "
          "fun gets its orange cast from Tanjung Tualang prawn shells, an innovation with no "
          "Chinese antecedent.", confidence="high",
    sources=["johorkaki-hokkien-mee", "ipoh-echo-kai-si-hor-fun"])
ING("i-ti-poh", "Dried flounder (ti poh)", zh="地魚 / 大地魚", role="umami base",
    blurb="Northern Malaysia's quiet secret weapon, in koay teow th'ng, duck noodle broth, "
          "KL Hokkien mee stock and Hong Kong wonton soup alike.",
    confidence="high", sources=["penang-wikia-kuey-teow-thng", "kim-lian-kee"])
ING("i-ikan-bilis", "Dried anchovy (ikan bilis)", malay="ikan bilis", role="stock and garnish",
    blurb="Mainland Chinese ban mian uses pork or plain water stock; Malaysian pan mee is "
          "built on dried anchovy, a Malay-archipelago pantry staple. That single substitution "
          "is the clearest marker that pan mee is a Malaysian dish, not a transplanted "
          "Chinese one.", confidence="high", sources=["wiki-banmian"])
ING("i-ikan-kembung", "Indian mackerel (ikan kembung)", malay="ikan kembung",
    role="poached and flaked", blurb="Penang shreds it into visible strands; Kedah pounds it "
    "into the broth. Wikipedia's claim that Kedah uses eel is contradicted by Malay-language "
    "sources.", confidence="medium", sources=["wiki-laksa", "ummi-laksa-guide"],
    flags=["kedah-eel-claim-disputed"])
ING("i-kangkung", "Water spinach (kangkung)", zh="通菜", malay="kangkung",
    blurb="Near-obligatory in Penang Hokkien mee and absent in both Xiamen and Singapore. "
          "Xiamen garnishes with coriander; Penang swapped in the local green. One of the two "
          "documented substitutions that turn a Fujian dish into a Penang one.",
    confidence="high", sources=["johorkaki-hokkien-mee"])
ING("i-duck-egg", "Duck egg", blurb="Richer and more custardy than chicken egg. Singapore "
    "switched to chicken eggs in the 1950s-60s as duck farming ceased; Penang kept the duck "
    "egg in char kway teow.", confidence="high", sources=["michelin-ckt"])
ING("i-char-siu", "Char siu", zh="叉燒", role="red-glazed Cantonese barbecued pork",
    blurb="A Cantonese contribution that migrated onto Hakka kolo mee, producing its 'red' "
          "style - the visible point at which two dialect lines converged in Sarawak.",
    confidence="medium", sources=["wiki-kolo-mee", "medium-kolo-mee"])
ING("i-five-spice", "Five-spice", zh="五香粉", role="star anise, cassia, clove, fennel, "
    "Sichuan pepper", blurb="Important caution: five-spice is Chinese and star anise is a "
    "Chinese native. Penang lor mee's warm sweet-spice aroma is NOT Arab-derived. Cassia, "
    "clove, cardamom and star anise circulated on the same Indian Ocean routes for a "
    "millennium, so the register in Penang has genuinely convergent Chinese and Arab-Indian "
    "sources. Frame it as convergence, never as one-way influence.",
    confidence="high", sources=["wiki-lor-mee"], flags=["not-arab-derived"])
ING("i-sweet-spice-quartet", "The 'four friends': cinnamon, clove, star anise, cardamom",
    role="Arab / Indo-Persian aromatic register",
    blurb="The Jawi Peranakan sweet-spice signature, and the shared vocabulary between "
          "murtabak, korma, biryani and - by convergence, not descent - the Chinese lor braise.",
    confidence="medium", sources=["heritasian-jawi"])
ING("i-black-vinegar", "Chinese black vinegar", zh="黑醋", role="table condiment",
    blurb="Diagnostic of lor mee and of dry bak chor mee. Its absence from Penang lam mee is "
          "one of the reasons the 'lam mee is just loh mee' story fails.",
    confidence="high", sources=["wiki-lor-mee", "johorkaki-bcm"])
ING("i-calamansi", "Calamansi (limau kesturi)", malay="limau kesturi", role="finishing acid",
    confidence="high", sources=["wiki-mee-goreng-mamak"])
ING("i-sayur-manis", "Sayur manis / mani cai", zh="馬尼菜", malay="sayur manis / cekur manis",
    role="Sauropus androgynus", blurb="Marketed in the peninsula as 'Sabah vegetable'. Not a "
    "Chinese vegetable - a Southeast Asian one, and its adoption into a Hakka wheat-noodle "
    "soup is a clean case of substrate ingredient displacing homeland ingredient. It also "
    "carries a documented toxicity risk: a 1994-95 Taiwan epidemic of bronchiolitis "
    "obliterans among people eating it raw or juiced in quantity. It must be cooked. Food "
    "writing about Sabah veg almost never says so.",
    confidence="high", sources=["sauropus-toxicity", "wiki-banmian"])
ING("i-ghee", "Ghee (minyak sapi)", malay="minyak sapi",
    blurb="Primary cooking fat in Jawi Peranakan cooking, in place of coconut or palm oil - "
          "an Indo-Persian rather than Malay choice.", confidence="medium",
    sources=["heritasian-jawi"])
ING("i-nut-thickeners", "Nut and seed thickeners: almond, cashew, poppy seed",
    blurb="Jawi Peranakan gravies are smooth and non-oily because they are thickened with "
          "ground nuts and poppy seed rather than with coconut. Single-source; flagged.",
    confidence="low", sources=["heritasian-jawi"], flags=["single-source"])
ING("i-red-rice-wine", "Red glutinous rice wine", zh="紅糟 / 紅酒",
    blurb="Indispensable at Foochow celebrations, and the reason ang jiu chicken mee sua is "
          "the Foochow birthday, confinement and New Year dish.",
    confidence="high", sources=["danielfooddiary-foochow"])
ING("i-evaporated-milk", "Evaporated milk", role="shortcut to a cloudy 'milk soup'",
    blurb="Genuine white fish broth comes from long-boiled bones; the milk version is the "
          "shortcut, and Teochew purists reject it. The frequent blog claim that it was a "
          "Hainanese British-influenced innovation is unsourced.",
    confidence="medium", sources=["wiki-fish-soup-bee-hoon"], flags=["hainanese-claim-unsourced"])
ING("i-thai-blood", "Fresh pig's or cow's blood", role="broth thickener",
    blurb="Mixed with salt and spices, it gives boat-noodle broth its body and near-black "
          "colour. The claim that the dark broth existed to hide blood residue from butchering "
          "is a food-media rationalisation, not documented.",
    confidence="high", sources=["wiki-boat-noodles"], flags=["concealment-story-unevidenced"])
ING("i-lihing", "Lihing (Kadazan-Dusun rice wine)", blurb="Worked into Tuaran mee or served "
    "alongside - a direct indigenous-Sabahan borrowing with no peninsular equivalent.",
    confidence="medium", sources=["wiki-tuaran-mee"])
ING("i-gau-wong", "Yellow Chinese chives", zh="韮黃",
    blurb="Near-obligatory with braised yi mein. Hokkiens associate 韮 with 久, 'a long time', "
          "which is why chives turn up in longevity noodles.",
    confidence="high", sources=["wiki-yi-mein", "carryitlikeharry-misua"])
ING("i-ground-dried-shrimp", "Ground dried shrimp",
    blurb="Katong laksa thickens with it, giving the characteristically slightly sandy "
          "texture - which is the observable fact that generated the bogus 辣沙 'spicy sand' "
          "laksa etymology.", confidence="high", sources=["wiki-laksa", "johorkaki-laksa-word"])
ING("i-sotong", "Sotong (squid)", malay="sotong",
    blurb="Cooked into the sauce, not laid on top, in Penang mee sotong.",
    confidence="high", sources=["hameed-pata"])
ING("i-pineapple", "Pineapple", malay="nanas", role="shredded garnish",
    blurb="One of the Penang asam laksa garnishes absent from laksa Kedah - a small marker with "
          "outsized diagnostic value.", confidence="high", sources=["wiki-laksa"])
ING("i-kiam-chai", "Preserved salted vegetable", zh="鹹菜", role="sour-salty counterweight",
    blurb="Teochew pantry staple, in koay chiap and in fish soup alike.",
    confidence="high", sources=["wiki-kway-chap"])
ING("i-fish-sauce", "Teochew fish sauce", role="seasoning",
    blurb="With black vinegar, the identifying half of the bak chor mee dressing - and one of the "
          "reasons the dish reads Teochew even though its name is Hokkien.",
    confidence="high", sources=["johorkaki-bcm"])
ING("i-shiitake", "Dried shiitake", zh="香菇", role="braised, minced or sliced",
    blurb="Near-obligatory with braised yi mein, in the Hakka minced-pork topping, and in pan mee.",
    confidence="high", sources=["wiki-yi-mein", "wiki-banmian"])
ING("i-fermented-beancurd", "Fermented bean curd", zh="腐乳", malay="tauhu yi",
    blurb="One of the flavour anchors of Thai boat-noodle broth, and of the char siu glaze that "
          "reddens kolo mee.", confidence="medium", sources=["wiki-boat-noodles"])


# ============================================================== TECHNIQUES
def TECH(nid, label, **kw):
    return N(nid, "technique", label, **kw)

TECH("t-rempah", "Pounding and frying rempah until it pecah minyak",
     blurb="The defining technical act of Nyonya cooking: an aromatic paste hand-pounded in "
           "a granite batu lesung, hardest ingredients first, then fried long in oil until "
           "the oil separates and the paste darkens from crimson to maroon. This single "
           "procedure is what separates Nyonya food from mainstream Chinese cooking, which "
           "relies on stock, wok heat and soy rather than a pounded wet spice base.",
     origin="c-malay-kedah", confidence="high", sources=["adriancheah-nyonya", "michelin-malaysia-regional"])
TECH("t-lou-braise", "The lou master-stock braise", zh="滷",
     blurb="Dark, spiced, soy-based braising liquid with five-spice, star anise, cassia and "
           "garlic. lor is a TECHNIQUE, not a dish - the same 滷 as in lor bak and lor tan. "
           "Hokkien in the lor mee line, Teochew in the braised-duck and koay chiap line.",
     confidence="high", sources=["wiki-lor-mee", "wiki-kway-chap"])
TECH("t-wok-hei", "Wok hei", zh="鑊氣",
     blurb="The smoky char that only comes off a raging fire. What separates a good char kway "
           "teow, a good KL Hokkien mee and a good wat tan hor from a bad one.",
     confidence="high", sources=["michelin-ckt", "kim-lian-kee"])
TECH("t-kon-lo", "Dry-tossing", zh="乾撈",
     blurb="The same 撈 as in lo hei. Noodles blanched, shocked and tossed in fat and "
           "seasoning, with soup demoted to a side bowl. Reached independently by Cantonese "
           "(kon lo wantan mee), Hakka (kolo mee, Hakka mee), Teochew (dry bak chor mee) and "
           "Sabahan Hakka (sang nyuk mee kon lau).",
     confidence="high", sources=["wiki-kolo-mee", "wiki-wonton-noodles"])
TECH("t-alkaline-noodle", "Alkaline noodle making", zh="鹼水麵",
     blurb="Kansui treatment yellows the flour, strengthens the gluten network, and produces "
           "a noodle that survives a wok. The industrial basis of Straits noodle culture.",
     confidence="high", sources=["johorkaki-hokkien-mee"])
TECH("t-fry-then-rehydrate", "Fry, dry, then rehydrate",
     blurb="Yi mein's core trick, reached independently by Tuaran mee's three-stage cooking - "
           "fry crisp, boil to rehydrate, then stir-fry - and industrialised as instant noodles.",
     confidence="high", sources=["wiki-yi-mein", "wiki-tuaran-mee"])
TECH("t-starch-gravy", "Starch-thickened gravy",
     blurb="Cornflour and beaten egg in lor mee; cornflour and egg ribbons in wat tan hor; "
           "mashed sweet potato in mee rebus and mee jawa. Three unrelated kitchens solving "
           "the same problem with the starch each had to hand.",
     confidence="high", sources=["wiki-lor-mee", "nlb-mee-rebus"])
TECH("t-hand-tearing", "Hand-tearing dough", zh="麵粉粿",
     blurb="The Hokkien method for mee hoon kueh: dough rolled flat and torn into irregular "
           "bite-sized pieces. Modern stalls hand-tear only this form and use a pasta roller "
           "for the rest.", confidence="high", sources=["wiki-banmian"])
TECH("t-clear-broth", "The Teochew clear broth",
     blurb="'Preserve the original flavour of the ingredient.' The aesthetic opposite of "
           "char kway teow, and the reason Penang duck noodle keeps the soup clear while "
           "braising the meat dark - two techniques, one bowl, deliberately not mixed.",
     confidence="high", sources=["penang-wikia-kuey-teow-thng", "lum-lai-duck"])
TECH("t-egg-ribbon", "Streaming beaten egg into thickened stock", zh="滑蛋",
     blurb="Core Cantonese wok practice, and the whole point of wat tan hor. Notably a "
           "technique dish with no origin legend at all - which is itself worth recording.",
     confidence="high", sources=["wiki-penang-cuisine"])
TECH("t-kandar-pole", "Hawking from a shoulder pole", malay="kandar",
     blurb="One vendor, two containers, cooked to order. It gave nasi kandar its name and its "
           "flooded-plate service style, and it is the same apparatus Indian Muslim peddlers "
           "used to carry mee rebus south, and that Chen Lianfu's bent back made famous as "
           "'Hunchback Noodle'. A mobile-vendor economy fossilised into a serving convention.",
     confidence="high", sources=["wiki-nasi-kandar", "nlb-mee-rebus", "johorkaki-bcm"])
TECH("t-mixed-noodle", "Mixing two noodles in one bowl (chap)",
     blurb="Yellow mee plus bee hoon, in whatever ratio the customer asks for. A Straits "
           "innovation, routine in Penang Hokkien mee, curry mee and lor mee, and so ordinary "
           "on the island that nobody comments on it.",
     confidence="high", sources=["johorkaki-hokkien-mee", "wiki-penang-cuisine"])
TECH("t-halal-substitution", "Halal substitution",
     blurb="Systematic, not accidental: keep the Chinese noodle, the taugeh, the tofu and the "
           "wok; remove the pork and lard; add sambal, curry leaf, tomato and tamarind. It "
           "generates matched dish-pairs across the whole canon - curry mee against curry "
           "laksa, CKT against CKT kerang, kolo mee against mi kolok, Penang mee jawa against "
           "mee rebus.", confidence="high", sources=["wiki-mee-goreng-mamak", "wiki-kolo-mee"])
TECH("t-prawn-head-dry-fry", "Dry-frying prawn heads before boiling", zh="爆香",
     blurb="Caramelise the heads and shells first, then boil for hours with pork bones. This one "
           "step is what makes the Penang Hokkien mee broth, and its reach is wider than people "
           "notice - Ipoh's kai si hor fun gets its orange cast the same way, from Tanjung Tualang "
           "shells, with no Chinese antecedent.",
     confidence="high", sources=["johorkaki-hokkien-mee", "ipoh-echo-kai-si-hor-fun"])
TECH("t-sweet-potato-thickening", "Thickening a gravy with mashed sweet potato",
     blurb="The Malay-Javanese answer to the same problem cornflour solves in the Chinese "
           "kitchen: how to make a small amount of expensive protein flavour a large amount of "
           "cheap noodle. It unites mee rebus, mee jawa, mee bandung, mee udang and pasembur "
           "gravy - four dishes, two kitchens, one starch.",
     confidence="high", sources=["nlb-mee-rebus", "wiki-pasembur"])
TECH("t-ground-dried-shrimp-thickening", "Thickening with ground dried shrimp",
     blurb="Katong laksa's method, and the reason its gravy has a faintly sandy body - which is "
           "the observable fact that generated the 'spicy sand' laksa etymology.",
     confidence="high", sources=["wiki-laksa", "johorkaki-laksa-word"])
TECH("t-blood-thickening", "Thickening a broth with fresh blood",
     blurb="Pig's or cow's blood mixed with salt and spices gives Thai boat-noodle broth its body "
           "and near-black colour. The claim that the dark broth existed to conceal blood residue "
           "from butchering is a food-media rationalisation.",
     confidence="high", sources=["wiki-boat-noodles"])
TECH("t-sambal-on-side", "Sambal served separately",
     blurb="The eater doses their own heat. The normal Penang curry mee convention, and the "
           "structural feature that 'white curry mee' names.",
     confidence="high", sources=["penang-wikia-white-curry"])


# ============================================================= COMMODITIES
N("cm-curry-powder", "commodity", "Commodified curry powder", period="London 1784; Madras 1830s",
  blurb="First advertised commercially by Sorlie's Perfumery Warehouse, Piccadilly, in 1784; "
        "standardised in Madras from the 1830s by British civil servants commissioning "
        "reproducible blends from local spice merchants. A pre-ground, shelf-stable, cheap "
        "blend is precisely what makes a hawker curry economically possible. This is a real "
        "and underappreciated causal link between empire and street food.",
  confidence="high", sources=["oed-curry"])
N("cm-noodle-factory", "commodity", "Chinese noodle factories", period="19th-20th century",
  blurb="The unglamorous protagonist. Alkaline yellow noodle produced industrially and sold "
        "to every kitchen on the island, including Malay and Indian Muslim ones. Without it "
        "there is no mee goreng mamak, no mee rebus, no mee soto.",
  confidence="medium", sources=["johorkaki-hokkien-mee"], flags=["interpretation"])
N("cm-swallow-rempah", "commodity", "Swallow-brand laksa rempah premix",
  period="1960s onward, Kuching",
  blurb="Tan Yong Him, a Kuching fruit seller, developed a laksa rempah premix and became the "
        "first to mass-produce it, under Cap Burung Layang Layang. Hawkers bought his base and "
        "tuned it with fresh spices from the Indian shops on Jalan Gambir. Competitor bird "
        "brands followed - Parrot, Eagle, Double Swallow, Rooster. Tan died in 1993. This is "
        "the best-documented case anywhere in the graph of an industrial spice paste creating "
        "and then freezing a 'traditional' dish.",
  confidence="medium", sources=["johorkaki-sarawak-laksa"])
N("cm-maggi", "commodity", "Nestle Maggi in Malaysia", period="1969 sauces, 1971 noodles",
  blurb="Arrived in 1969 with tomato ketchup and chilli sauce - and only in 1971 with "
        "two-minute noodles, in Kari and Ayam. Worth pausing on: the bottled sauce that "
        "defines mee goreng mamak's colour arrived under the same brand two years before the "
        "noodle that defines Maggi goreng. Maggi goreng cannot predate 1971, which makes it "
        "the only hard chronological anchor in the corpus.",
  confidence="medium", sources=["nestle-maggi-malaysia"])
N("cm-mykuali", "commodity", "MyKuali Penang White Curry Noodles", period="2012 launch",
  blurb="Founded by Penangite Thomas Tang; the instant product launched in 2012 and was ranked "
        "#1 in The Ramen Rater's 'Top 10 Instant Noodles of All Time' in 2014. It is the "
        "mechanism by which a Penang serving convention became a named global dish category.",
  confidence="high", sources=["mykuali", "penang-wikia-white-curry"])
N("cm-condensed-milk", "commodity", "Condensed and evaporated milk", period="colonial onward",
  blurb="Cheap, shelf-stable dairy for a place with no dairy. It made teh tarik possible by "
        "masking the bitterness of sarabat tea dust, and it made 'milk soup' fish bee hoon "
        "possible without boiling bones for hours.",
  confidence="medium", sources=["thesmartlocal-teh-tarik", "wiki-fish-soup-bee-hoon"])


# ============================================================ MEDIA EVENTS
N("m-cnn-2011", "media", "CNN Go, World's 50 Most Delicious Foods", date="21 July 2011",
  blurb="Penang asam laksa at #7 - the only Malaysian entry in the top ten, ahead of tom yum "
        "goong and ice cream. Re-promoted by CNN Travel in 2020, which is why many sources "
        "misdate it. The ranking is a genuine node in Penang's food economy: it appears in "
        "state tourism material, on stall signage, and in instant-noodle marketing.",
  confidence="high", sources=["cnn-go-2011"])
N("m-bourdain-2005", "media", "Bourdain's 'Breakfast of the Gods'", date="2005",
  blurb="Anthony Bourdain ate Sarawak laksa at Choon Hui Cafe, Ban Hock Road, Kuching, on two "
        "consecutive mornings during the Borneo episode of No Reservations. Before that the "
        "dish rarely travelled off the island; his endorsement is the direct cause of its "
        "international profile.", confidence="medium", sources=["bourdain-no-reservations-borneo"])
N("m-ramen-rater-2014", "media", "The Ramen Rater's Top 10 of All Time", date="2014",
  blurb="Ranked MyKuali's Penang white curry noodle #1, which converted a local instant "
        "product into an internationally recognised dish name.",
  confidence="high", sources=["mykuali"])
N("m-michelin-my", "media", "The MICHELIN Guide in Malaysia", date="2022 onward",
  blurb="Bib Gourmand and starred recognition for hawker stalls, including Penang curry mee, "
        "Lum Lai duck koay teow th'ng and a green tom yum noodle on Perak Road. Recognition "
        "changes queues, prices and succession planning - it belongs in the graph as a force, "
        "not a footnote.", confidence="medium", sources=["michelin-ckt", "lum-lai-duck"])
N("m-heritage-2024", "media", "Malaysian Declaration of Heritage Objects", date="2024",
  blurb="Gazetted kolo mee as a heritage food alongside bak kut teh, burasak and nasi ambeng - "
        "the state formally taking a position on culinary genealogy.",
  confidence="high", sources=["heritage-2024-declaration"])


# ================================================================ CONCEPTS
def CON(nid, label, **kw):
    return N(nid, "concept", label, **kw)

CON("x-halal-boundary", "The halal boundary",
    blurb="The single strongest structural force in Penang's noodle culture. It determines who "
          "can sell what to whom, and it generates systematic dish-pairs rather than one "
          "melting pot. It is also why the mamak stall exists: a Tamil Muslim vendor could buy "
          "Chinese wheat noodles and sell cooked food to Malays, holding the one commercial "
          "position neither Chinese nor Malay hawkers could occupy.",
    confidence="high", sources=["wiki-mee-goreng-mamak", "wiki-kolo-mee"])
CON("x-longevity-noodle", "The longevity noodle",
    blurb="Long unbroken strands mean long life; the eater slurps rather than bites, because "
          "cutting the noodle cuts the lifespan. The same idea is expressed through different "
          "noodles by different groups: mee sua for Hokkien, Teochew and Foochow households, "
          "yi mein at Cantonese and Hakka banquets, and lam mee in Penang Nyonya kitchens. "
          "The Emperor Wu of Han legend attached to it - long noodle, long face, long life, "
          "on the homophony of 麵 and 面 - is folk history of great antiquity and zero "
          "verifiability, which is itself a real cultural fact worth recording.",
    confidence="high", sources=["carryitlikeharry-misua", "wiki-yi-mein"])
CON("x-domestic-service", "Domestic service as a transmission channel",
    blurb="Hainanese cooks learned European and Peranakan household cooking in their "
          "employers' kitchens, then took it onto the street when jobs were scarce after 1945. "
          "It explains Hainanese chicken rice, chicken chop, mee Hailam and - on the "
          "documented Singapore case - Katong laksa. As Tony Boey drily notes, no Peranakan "
          "family would have let an heirloom laksa recipe be peddled as street food; the cook "
          "was the leak.", confidence="medium", sources=["johorkaki-katong-laksa", "mothership-hainanese"])
CON("x-northern-triangle", "The Penang-Phuket-Medan triangle",
    blurb="Penang was not a Malaysian city that happened to be near Thailand. It was the "
          "commercial capital of a maritime region whose other corners were southern Siam and "
          "North Sumatra, and whose trade in rice, brown sugar, coconut oil, cloth and salted "
          "vegetables was dominated by the Big Five Hokkien families. Ingredients, cooks, "
          "brides and recipes moved on a north-south Indian Ocean axis, not a Malaysian "
          "national one. This is why Penang food resembles southern Thai and North Sumatran "
          "food more than it resembles Johor food.",
    confidence="high", sources=["wong-big-five", "thai-peranakan-translocal"])
CON("x-kopitiam", "The kopitiam",
    blurb="A Hainanese institution by occupational accident: the last dialect group to arrive "
          "found the trades taken and the kitchens open. Coffee wok-roasted with sugar and "
          "margarine, toast, half-boiled eggs, and a rented stall out front for somebody "
          "else's noodles.", confidence="high", sources=["mothership-hainanese", "kuchler-1965"])
CON("x-mamak-stall", "The mamak stall",
    blurb="An inter-communal institution, open late, halal, and selling Chinese noodle formats "
          "rebuilt with South Indian spice. Its menu adjacencies are a real transmission "
          "mechanism: mee rebus stalls also sell mee goreng because the ingredients overlap; "
          "mee goreng sits beside pasembur and shares its fritters, potato and red sauce.",
    confidence="high", sources=["nlb-mee-rebus", "wiki-pasembur"])
CON("x-hawker-apprenticeship", "Informal apprenticeship and recipe drift",
    blurb="Recipes moved by watching, not by writing. Penang Institute's work on hawker "
          "transmission gives the vocabulary: informal apprenticeship, recipe drift, and air "
          "tangan - the notion that the same recipe in different hands produces a different "
          "bowl. It is the mechanism that makes stall lineages traceable and dish origins not.",
    confidence="medium", sources=["penang-institute-hawkers"])
CON("x-economy-bee-hoon", "The economy bee hoon tray",
    blurb="A tray of fried bee hoon and fried noodles with assorted fried sides, sold by "
          "selection - the Penang Chinese breakfast format, and the everyday home of char bee "
          "hoon.", confidence="high", sources=["wiki-penang-cuisine"])
CON("x-naming-after-cook", "Naming logic: after the cook's ethnicity",
    blurb="Hokkien mee, mee jawa, mee siam, mee goreng mamak, mee Hailam. These names are "
          "usually applied from OUTSIDE the community and are frequently wrong about origin - "
          "nobody in Fujian calls a dish 'Fujian noodles'. Reliable as evidence of the naming "
          "community's perspective; unreliable as evidence of provenance.",
    confidence="high", sources=["johorkaki-hokkien-mee"])
CON("x-naming-after-noodle", "Naming logic: after the noodle",
    blurb="Char kway teow, kolo mee, Maggi goreng, and the curry mee / curry laksa split - "
          "the SAME dish, named 'mee' where yellow noodle or bee hoon is used and 'laksa' "
          "where thick round rice noodle is used. Laksa and mee siam both originally named "
          "noodles rather than dishes.",
    confidence="high", sources=["wiki-laksa", "nlb-mee-siam"])
CON("x-naming-after-process", "Naming logic: after the process",
    blurb="lam mee 'poured', mee rebus 'boiled', lor mee 'braised', char kway teow "
          "'stir-fried', kolo mee 'tossed'. The most honest of the three logics, and the one "
          "that produces the fewest false genealogies.",
    confidence="high", sources=["nlb-mee-rebus", "wiki-lor-mee"])
CON("x-citogenesis", "Citogenesis in food writing",
    blurb="The typical chain: a stall owner tells a journalist a family story, the journalist "
          "prints it, twenty blogs copy the journalist, Wikipedia cites a blog, and everyone "
          "thereafter cites Wikipedia. The char kway teow 'fishermen and farmers' origin is "
          "the textbook case - Wikipedia's footnote points at an NLB article that does not "
          "contain the claim, and at a 2016 newspaper health-scare piece. Modelled here as a "
          "first-class concept because it is the main reason this graph carries confidence "
          "ratings at all.", confidence="high", sources=["wiki-char-kway-teow", "nlb-ckt"])
CON("x-beef-taboo", "The beef question",
    blurb="Chinese beef-noodle stalls are not halal, so Malaysian Muslims eat beef noodles as "
          "soto or sup rather than as ngau yuk. Meanwhile many Chinese Malaysians of Cantonese "
          "and Hakka background avoid beef entirely on Buddhist/Taoist grounds - the taboo on "
          "eating the ox that ploughs the field. Beef noodles are therefore squeezed from both "
          "sides, which is why Penang's beef-noodle scene is thin relative to KL's and "
          "Seremban's.", confidence="medium", sources=["wiki-taiwanese-beef-noodle"])
CON("x-evidence-asymmetry", "Evidence asymmetry between kitchens",
    blurb="Every Chinese dish in this graph has at least a named founder story. Mee udang at "
          "Sungai Dua - a substantial commercial cluster - has none. That is a bias in the "
          "SOURCES, not in the dishes, and a graph built naively on available sources will "
          "inherit it. Recorded here so that it can be corrected for.",
    confidence="high", sources=["penang-traveltips-mee-udang", "wiki-pasembur"])
CON("x-substrate-marker", "The substrate ingredient as naturalisation marker",
    blurb="Anchovy stock in pan mee, sayur manis in Sabah, hae ko in Penang chee cheong fun, "
          "kangkung in Hokkien mee, tomato and lime in mamak bihun, dried flounder across the "
          "north, sambal belacan served with everything. These are the points at which a "
          "Chinese dish becomes a Malaysian one, and they are more reliable evidence of local "
          "adaptation than any origin story.",
    confidence="high", sources=["wiki-banmian", "johorkaki-hokkien-mee"])


# =========================================================== NAME COLLISIONS
N("nm-hokkien-mee", "name", "'Hokkien mee' - three unrelated dishes",
  blurb="Penang: a spicy prawn-head soup noodle. Kuala Lumpur: thick yellow noodles "
        "braise-fried black in dark soy with lard croutons. Singapore: a pale wet fry of mixed "
        "yellow mee and bee hoon moistened with prawn stock. Three dishes, one ethnonym, zero "
        "relationship beyond the makers' shared ancestry - because in each city a Hokkien "
        "hawker named his signature after himself, at roughly the same period, with no "
        "coordination. Penangites resolve it by calling the local fried dish 'Hokkien char'; "
        "KL people call the soup 'prawn mee'.",
  confidence="high", sources=["wiki-hokkien-mee", "johorkaki-kl-sg-hokkien", "kim-lian-kee"])
N("nm-laksa", "name", "'Laksa' - a contested word and a shifting referent",
  blurb="Two live hypotheses. Persian lakhshah, 'slippery noodle', which has real comparative "
        "weight: Russian lapsha, Yiddish lokshen, Uyghur laghman, Afghan lakhchak. And Sinitic "
        "辣沙, 'spicy sand', which is more semantically informative and fits the Peranakan Min-"
        "speaking transmission context. Sanskrit laksa 'one hundred thousand' is a popular but "
        "semantically weak folk etymology, and the 老鼠粉 idea has no support at all. The "
        "decisive evidence is about the REFERENT, not the root: the 1391 Biluluk inscription "
        "glosses hanglaksa as 'vermicelli maker', Wilkinson's 1901 dictionary lists laksa as "
        "'vermicelli', and an 1833 Singapore Chronicle manifest lists 24 baskets of laksa "
        "shipped from Batavia. The word named a noodle for centuries before it named a soup.",
  confidence="disputed", sources=["oxford-companion-laksa", "wilkinson-1901", "biluluk-1391",
                                  "singapore-chronicle-1833", "johorkaki-laksa-word",
                                  "asian-inspirations-laksa"])
N("nm-you-mee", "name", "'You mee' - four referents",
  blurb="幼麵 yau min, the thin round egg noodle, identical to mee kia and to wonton noodle - "
        "this is what a pan mee shop means by it, and it is a noodle option, not a dish. 伊麵 "
        "yee mee, the fried dried e-fu brick. 魚麵, a real Foochow fish-paste noodle from Sibu "
        "and Sitiawan. And 油麵, an alias for ordinary yellow alkaline noodle. Nearly every "
        "English-language food blog that uses the phrase does so without specifying which.",
  confidence="high", sources=["wiki-banmian", "wiki-mee-pok", "wiki-yi-mein"])
N("nm-lam-vs-lor", "name", "Lam mee vs lor mee - a conflation to reject",
  blurb="A widely circulated account has lam mee as loh mee lightened for Cantonese palates "
        "and re-pronounced. It fails four ways: Penang lam mee has a clear broth and loh mee a "
        "thick starchy one, so they are not the same dish lightened; lam mee has a birthday "
        "ritual function loh mee lacks; the phonetic story runs the wrong way geographically, "
        "since Penang is not Cantonese-majority; and 淋 'to pour over' is a perfectly good "
        "independent etymology for a noodle over which broth is poured.",
  confidence="high", sources=["foodpanda-lam-mee", "wiki-lor-mee"])
N("nm-koay-chiap-vs-teow", "name", "Koay chiap vs koay teow",
  blurb="汁 chiap is juice or gravy; 湯 th'ng is soup. Koay teow is a cut ribbon in a clear "
        "broth; koay chiap is a broad folded sheet in a dark braise. They are distinguished at "
        "the level of the NAME, and Penang stalls still sell both from one cart, which is why "
        "the spelling 'koay chiak' floats around menus and blogs.",
  confidence="high", sources=["wiki-kway-chap"])
N("nm-singapore-noodles", "name", "'Singapore noodles' - a fictitious attribution",
  blurb="星洲炒米 is a Hong Kong invention. Cantonese chefs in post-war Hong Kong fried rice "
        "vermicelli with the curry powder that was abundant in the colony through British-"
        "Indian trade, and named it after Singapore for exotic appeal. It is not sold in "
        "Singapore except to tourists, and Singapore's own fried bee hoon uses no curry powder "
        "at all. Useful in the graph precisely because it is a category the model needs to be "
        "able to represent: a place-name that is marketing, not provenance.",
  confidence="high", sources=["wiki-singapore-noodles"])
N("nm-chee-cheong-fun", "name", "'Pig intestine noodle' with no pig in it",
  blurb="豬腸粉 describes the shape of the rolled sheet, nothing else. A folk-descriptive name, "
        "not a documented coinage - and a reminder that Chinese dish names describe what "
        "things look like at least as often as what they contain.",
  confidence="high", sources=["wiki-chee-cheong-fun"])
N("nm-sabah-pan-mee", "name", "'Sabah pan mee' - a name without a dish",
  blurb="No dish by this name is documented. Sabah's real items are sang nyuk mee and the "
        "district-noodle set - Tuaran, Beaufort, Tenom, Tamparuli, Kota Belud. What a Penang "
        "stall selling 'Sabah pan mee' is almost certainly offering is ordinary pan mee made "
        "with sayur manis instead of sweet potato leaves, under a name that borrows Sabah's "
        "Hakka noodle reputation. The name is doing real commercial work even though it "
        "denotes nothing in Sabah.",
  confidence="medium", sources=["wiki-sang-nyuk-mee", "cna-sabah-noodles", "wiki-banmian"])


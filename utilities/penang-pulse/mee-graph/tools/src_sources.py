"""Source register for the Penang noodle culture graph.

Every claim-bearing edge and node in the graph carries one or more source ids
from this register. `tier` records how much weight the source can bear:

  scholarly  - peer-reviewed, academic press, or archival/primary material
  reference  - national library / heritage board / dictionary / museum
  journalism - newspaper or magazine reporting
  specialist - serious food-history writing (researched, not peer-reviewed)
  community  - local heritage sites, clan association pages, wikis
  encyclopedic - Wikipedia and derivatives
  commercial - business or brand's own account of itself
  media      - food blogs, listicles, tourism marketing
"""

SOURCES = {
    # ---------------------------------------------------------------- history
    "kuchler-1965": dict(
        title="Johannes Kuchler, 'Penang's Chinese Population: A Preliminary Account of "
              "its Origin and Social Geographic Pattern', Asian Studies 3(3), 1965",
        url="https://www.asj.upd.edu.ph/mediabox/archive/ASJ-03-03-1965/Kuchler.pdf",
        tier="scholarly",
        note="1957 census dialect counts, Vaughan 1854 occupational survey, street-level "
             "clan mapping. The single most load-bearing source in the graph.",
    ),
    "voon-2024-hakka": dict(
        title="Voon Phin-Keong, 'The Hakkas of Malaysia to 1970: Population, Livelihood, "
              "and Culture', Malaysian Journal of Chinese Studies 13(1), 2024",
        url="https://ejournal.newera.edu.my/mjcs/article/download/23/13",
        tier="scholarly",
        note="Dialect shares by state, Larut shophouse ownership by Hakka sub-group, "
             "dulang washers, pawnbroking.",
    ),
    "muse-emergency-immigration": dict(
        title="'Immigration Control during the Malayan Emergency: Borders, Belonging and "
              "Citizenship, 1948-1960', Project MUSE",
        url="https://muse.jhu.edu/article/622990",
        tier="scholarly",
        note="The 1949 closure of the China pipeline; 1952 citizenship extension.",
    ),
    "wong-big-five": dict(
        title="Wong Yee Tuan, Penang Chinese Commerce in the 19th Century: The Rise and "
              "Fall of the Big Five (ISEAS, 2015)",
        url="https://www.cambridge.org/core/books/penang-chinese-commerce-in-the-19th-century/5985784F383FCC6CBA1D7AB1681557FC",
        tier="scholarly",
        note="Big Five Hokkien families, opium revenue farming, the Penang-Phuket-Deli "
             "commercial region.",
    ),
    "thai-peranakan-translocal": dict(
        title="Scholarship on Thai Peranakan / Phuket Baba translocal identity",
        url="https://en.wikipedia.org/wiki/Thai_Chinese",
        tier="scholarly",
        note="Phuket Baba community sustained a translocal identity oriented on Penang.",
    ),
    "kuroda-samsam": dict(
        title="Kuroda on the Samsam of inland Kedah (Tai-speaking Muslim populations)",
        url="https://en.wikipedia.org/wiki/Samsam",
        tier="scholarly",
        note="The Thai-Malay boundary in the north was gradual, not a line.",
    ),
    "penang-institute-hawkers": dict(
        title="Yvonne Lee & Lim Wei Lee, 'From Means of Survival to Tourism Gems: A Study "
              "of Street Food Prospects in Penang', Penang Institute ISSUES, Nov 2022",
        url="https://penanginstitute.org/publications/issues/from-means-of-survival-to-tourism-gems-a-study-of-street-food-prospects-in-penang/",
        tier="scholarly",
        note="Informal apprenticeship, recipe drift, air tangan as transmission mechanics.",
    ),
    "cambridge-yearning-mamak": dict(
        title="'Mamak and Malaysian: The Indian Muslim Quest for Identity', in Yearning to "
              "Belong (Cambridge University Press)",
        url="https://www.cambridge.org/core/books/abs/yearning-to-belong/mamak-and-malaysian-the-indian-muslim-quest-for-identity/CCAC55B4E549611D5D71E3CF979A199A",
        tier="scholarly",
        note="Mamak as a contested identity term in Malaysian discourse.",
    ),
    "iium-jawi-peranakan": dict(
        title="'The Jawi Peranakan: early popular expressions of Malay identity in the "
              "archipelago', IIUM Repository",
        url="http://irep.iium.edu.my/111470/",
        tier="scholarly",
    ),
    "areca-chulia": dict(
        title="Khoo Salma Nasution, The Chulia in Penang (Areca Books)",
        url="https://arecabooks.com/product/chulia-in-penang/",
        tier="scholarly",
        note="Tamil Muslim traders on the Kedah coast before 1786 and in Penang from 1786.",
    ),
    "peranakan-genetics": dict(
        title="Genetic studies of Peranakan Chinese admixture",
        url="https://en.wikipedia.org/wiki/Peranakan_Chinese",
        tier="scholarly",
        note="Real admixture, not purely cultural creolisation.",
    ),

    # -------------------------------------------------------------- reference
    "nlb-mee-rebus": dict(
        title="'Mee rebus', Singapore NLB Infopedia",
        url="https://eresources.nlb.gov.sg/infopedia/",
        tier="reference",
        note="Mee rebus 'originally peddled by Indian Muslim immigrants'; regional variants; "
             "stalls also sell mee goreng.",
    ),
    "nlb-mee-siam": dict(
        title="'Mee siam', Singapore NLB",
        url="https://www.nlb.gov.sg/main/home",
        tier="reference",
        note="Earliest Singapore newspaper mention 1950 (Esplanade hawkers); Khir Johari on "
             "the Thai-imported vermicelli.",
    ),
    "nlb-mee-jawa": dict(
        title="'Mee Jawa', Singapore NLB Infopedia",
        url="https://eresources.nlb.gov.sg/infopedia/",
        tier="reference",
        note="Johor vs Penang mee Jawa; the Penang gravy's canned-tomato-soup base.",
    ),
    "nlb-ckt": dict(
        title="'Char kway teow', Singapore NLB Infopedia",
        url="https://eresources.nlb.gov.sg/infopedia/",
        tier="reference",
        note="Wartime tapioca noodles and red palm oil (National Archives oral history); the "
             "1950s bean-sprout strike and cai xin substitution. Notably does NOT contain "
             "the 'fishermen and farmers' origin claim Wikipedia attributes to it.",
    ),
    "nlb-hokkien-prawn": dict(
        title="'Hokkien prawn noodle soup', Singapore NLB Infopedia",
        url="https://www.nlb.gov.sg/main/article-detail?cmsuuid=111e806c-bac8-4f6e-88c0-568055f5de19",
        tier="reference",
    ),
    "nlb-jawi-newspaper": dict(
        title="'Jawi Peranakkan - the first Malay newspaper is published', Singapore NLB",
        url="https://www.nlb.gov.sg/main/article-detail?cmsuuid=4942ebac-41d6-4eb8-abcb-cdece539bbea",
        tier="reference",
        note="1876-1895, weekly, Jawi script, editor Munshi Mohamed Said bin Dada Mohyiddin.",
    ),
    "nlb-immigration-1932": dict(
        title="'Immigration Restriction Ordinance is passed', Singapore NLB",
        url="https://eresources.nlb.gov.sg/history/events/ba3578bf-79d5-4e15-8185-30c62d321daa",
        tier="reference",
        note="Male quotas with female exemption; ended the wage-suppression immigration tap.",
    ),
    "nlb-chinese-immigrants-1877": dict(
        title="'Chinese Immigrants Ordinance 1877 is passed', Singapore NLB",
        url="https://eresources.nlb.gov.sg/history/events/dbfed061-8451-42c9-8a5b-5a6c72df1a2c",
        tier="reference",
    ),
    "roots-kway-chap": dict(
        title="Kway chap, Roots.gov.sg (Singapore National Heritage Board)",
        url="https://www.roots.gov.sg/",
        tier="reference",
        note="Teochew intangible heritage; the three-way broth divergence (Chaoshan rice-milk "
             "white / Straits soy-dark / Thai clear).",
    ),
    "oed-mamak": dict(
        title="'mamak, n. & adj.', Oxford English Dictionary",
        url="https://www.oed.com/dictionary/mamak_n",
        tier="reference",
        note="Tamil maamaa 'maternal uncle'; three senses recorded.",
    ),
    "oed-curry": dict(
        title="'curry', Oxford English Dictionary / Oxford Companion to Food",
        url="https://www.oed.com/",
        tier="reference",
        note="Tamil kari; pre-mixed curry powder as a British 18th-century invention.",
    ),
    "oxford-companion-laksa": dict(
        title="Alan Davidson, The Oxford Companion to Food, s.v. laksa",
        url="https://global.oup.com/academic/product/the-oxford-companion-to-food-9780199677337",
        tier="reference",
        note="Derives laksa from Persian lakhshah, 'slippery'.",
    ),
    "wilkinson-1901": dict(
        title="R. J. Wilkinson, A Malay-English Dictionary (1901)",
        url="https://archive.org/details/malayenglishdict01wilk",
        tier="reference",
        note="Lists laksa both as a numeral and as 'vermicelli', ascribing the latter to Persian. "
             "Primary evidence that laksa named a noodle before it named a soup.",
    ),
    "biluluk-1391": dict(
        title="Biluluk copper-plate inscription, East Java, 1391 (Majapahit)",
        url="https://en.wikipedia.org/wiki/Laksa",
        tier="reference",
        note="Contains hanglaksa, glossed in Kawi as 'vermicelli maker'. Pushes the word back "
             "600+ years and decouples it from the Peranakan communities usually credited.",
    ),
    "singapore-chronicle-1833": dict(
        title="Singapore Chronicle cargo manifest, 1833 - '24 baskets of laksa' from Batavia",
        url="https://eresources.nlb.gov.sg/newspapers/",
        tier="reference",
        note="Archival attestation that laksa meant the raw noodle.",
    ),
    "jkkn-culture-mapping": dict(
        title="JKKN Pemetaan Budaya (Malaysian Department of National Culture and Arts)",
        url="https://pemetaanbudaya.jkkn.gov.my/",
        tier="reference",
        note="State culture-mapping entries for mee wantan, nasi kandar and others.",
    ),
    "heritage-2024-declaration": dict(
        title="Malaysian Declaration of Heritage Objects 2024 (kolo mee, bak kut teh, "
              "burasak, nasi ambeng)",
        url="https://en.wikipedia.org/wiki/Kolo_mee",
        tier="reference",
    ),
    "immigration-dept-history": dict(
        title="'Department History', Malaysian Immigration Department",
        url="https://www.imi.gov.my/index.php/en/departments-profile/department-history/",
        tier="reference",
        note="Aliens (Immigration Restriction) Ordinance 1930 quota system.",
    ),
    "sauropus-toxicity": dict(
        title="Medical literature on Sauropus androgynus and bronchiolitis obliterans "
              "(Taiwan epidemic, 1994-95)",
        url="https://en.wikipedia.org/wiki/Sauropus_androgynus",
        tier="reference",
        note="Sayur manis must be cooked; raw/juiced consumption in quantity caused irreversible "
             "obstructive lung disease. Food writing about 'Sabah veg' almost never mentions this.",
    ),

    # ------------------------------------------------------------- journalism
    "malaymail-beyond-hokkien": dict(
        title="Opalyn Mok, 'Beyond Hokkien: The lesser-known communities that shaped George "
              "Town', Malay Mail, 16 Aug 2025",
        url="https://www.malaymail.com/news/life/2025/08/16/beyond-hokkien-the-lesser-known-communities-that-shaped-george-town/184823",
        tier="journalism",
        note="Interviews Penang Heritage Trust president Clement Liang and Kwangtung & "
             "Tengchow Association president Lio Chee Yeong. Source of the enclave map and of "
             "the warning that province does not equal dialect.",
    ),
    "malaymail-loo-pun-hong": dict(
        title="'Inside Penang's Loo Pun Hong, the oldest Cantonese carpentry guild in South "
              "East Asia', Malay Mail, 17 Aug 2025",
        url="https://www.malaymail.com/news/life/2025/08/17/inside-penangs-loo-pun-hong-the-oldest-cantonese-carpentry-guild-in-south-east-asia/186832",
        tier="journalism",
    ),
    "malaymail-mee-jawa": dict(
        title="Opalyn Mok on Penang mee Jawa, Malay Mail",
        url="https://www.malaymail.com/",
        tier="journalism",
        note="'The origin of this hawker fare is unclear but its name suggests that it is linked "
             "back to the heydays of the Java Peranakan.' The honest position.",
    ),
    "ipoh-echo-kai-si-hor-fun": dict(
        title="'Does Kai Si Hor Fun Come From Ipoh?', Ipoh Echo, 16 Feb 2019",
        url="https://www.ipohecho.com.my/2019/02/16/does-kai-si-hor-fun-come-from-ipoh/",
        tier="journalism",
        note="Thean Chun and Loke Wooi Kee founded by Hokkien immigrants from Nan'an, Fujian - "
             "hence the prawn-and-chicken broth. Tanjung Tualang prawn shells as the local "
             "innovation.",
    ),
    "ipoh-echo-foochow-sitiawan": dict(
        title="'The Foochows of Sitiawan', Ipoh Echo, 1 May 2019",
        url="https://www.ipohecho.com.my/2019/05/01/the-foochows-of-sitiawan/",
        tier="journalism",
        note="1903 Methodist Episcopal Mission agricultural colony contracted to feed the "
             "coolie population.",
    ),
    "cgtn-cantonese-ipoh": dict(
        title="'Cantonese Heritage Trail: Cantonese key role in Ipoh's history, development', "
              "CGTN, 18 Jul 2022",
        url="https://news.cgtn.com/news/2022-07-18/VHJhbnNjcmlwdDY3MTUy/index.html",
        tier="journalism",
    ),
    "borneo-post-sarawak-mee": dict(
        title="'The ubiquitous Sarawak mee - kolo, kampua and ketchup', Borneo Post, 17 Dec 2022",
        url="https://www.theborneopost.com/2022/12/17/the-ubiquitous-sarawak-mee-kolo-kampua-and-ketchup/",
        tier="journalism",
        note="Kampua is the Sibu Foochow noodle; kolo is the Kuching one. The distinction most "
             "sources collapse.",
    ),
    "guardian-tuaran-mee": dict(
        title="Guardian street-food coverage of Tuaran mee",
        url="https://www.theguardian.com/",
        tier="journalism",
        note="'Madam Si', 1952; the late-1970s displacement of knife-cut noodles; the retronym "
             "shift from chao men to tao-ah-lan men.",
    ),
    "rakyat-post-kin-kin": dict(
        title="The Rakyat Post interview with Tan Kok Hong of Restoran Kin Kin",
        url="https://www.therakyatpost.com/",
        tier="journalism",
        note="Chilli pan mee, 1985, a stall under a tree in Chow Kit. Customers were already "
             "spooning chilli in; he built a dry version around a proprietary chilli condiment.",
    ),
    "cna-sabah-noodles": dict(
        title="CNA on Sabah's district noodles",
        url="https://www.channelnewsasia.com/",
        tier="journalism",
        note="Sabah's noodle map is organised by district (Tuaran, Beaufort, Tenom, Tamparuli, "
             "Kota Belud) rather than by dialect - a consequence of Hakka majority.",
    ),
    "cj-my-ckt-origins": dict(
        title="Maran Perianen, 'The real story behind Char Kway Teow's Penang origins', "
              "Citizens Journal, 17 Jun 2026",
        url="https://cj.my/157447/the-real-story-behind-char-kway-teows-penang-origins",
        tier="journalism",
        note="Both Hokkien and Teochew dockworkers, fishermen and cockle-gatherers described as "
             "evening hawkers; char koay teow basah at Bukit Mertajam associated with the Malay "
             "community.",
    ),
    "straits-times-bcm": dict(
        title="Straits Times reporting on bak chor mee and kway chap lineages",
        url="https://www.straitstimes.com/",
        tier="journalism",
    ),

    # ------------------------------------------------------------- specialist
    "johorkaki-hokkien-mee": dict(
        title="Tony Boey (Johor Kaki), 'Origin of Hokkien Mee in Penang - Noodles in Prawn "
              "Head Soup from Xiamen', 2022",
        url="https://johorkaki.blogspot.com/2022/06/origin-of-hokkien-mee-in-penang-noodles.html",
        tier="specialist",
        note="Written for the Chinese Cultural Heritage Research Centre. Establishes the surviving "
             "Xiamen parent dish and the documented substitutions (kangkung for coriander, sambal "
             "belacan cooked into the stock replacing raw garlic). Also carries the eyewitness "
             "claim that noodles were unobtainable in occupied Penang.",
    ),
    "johorkaki-laksa-word": dict(
        title="Tony Boey (Johor Kaki) on the history of the word laksa",
        url="https://johorkaki.blogspot.com/",
        tier="specialist",
        note="The 1833 Singapore Chronicle manifest, the 1902 brick advertisement priced per "
             "laksa, and a flat statement that the Chinese folk etymologies are 'not supported "
             "by evidence (so far)'.",
    ),
    "johorkaki-sarawak-laksa": dict(
        title="Tony Boey (Johor Kaki) on Sarawak laksa and the Swallow-brand rempah industry",
        url="https://johorkaki.blogspot.com/",
        tier="specialist",
        note="Goh Lik Teck (Teochew, Carpenter Street, Kuching, 1940s) as credited originator; "
             "Tan Yong Him's Swallow brand premix from the 1960s as the actual standardising "
             "mechanism; the bird-brand competitors; Jalan Gambir Indian spice shops.",
    ),
    "johorkaki-bcm": dict(
        title="Tony Boey (Johor Kaki), 'Origin & Father of Bak Chor Mee', 2020",
        url="https://johorkaki.blogspot.com/2020/10/father-of-singapore-bak-chor-mee-hawker.html",
        tier="specialist",
        note="Chen Lianfu of Zhao'an county, Fujian; learned the trade in Chaozhou; Chai Chee "
             "from the 1920s; 'Hunchback Noodle'; eleven descendant stalls and one shared "
             "noodle supplier. Unusually good provenance for this genre.",
    ),
    "johorkaki-kl-sg-hokkien": dict(
        title="Tony Boey (Johor Kaki), 'Ebony & Ivory - History of KL & Singapore Fried "
              "Hokkien Mee (Rochor Mee)', 2020",
        url="https://johorkaki.blogspot.com/2020/05/ebony-ivory-history-of-kl-singapore.html",
        tier="specialist",
    ),
    "johorkaki-katong-laksa": dict(
        title="Tony Boey (Johor Kaki) on Katong laksa and Hainanese domestic service",
        url="https://johorkaki.blogspot.com/",
        tier="specialist",
        note="Hainanese domestic workers learned Nyonya laksa in Peranakan households and took "
             "it to the street after 1945, 'because no Peranakan will allow their heirloom laksa "
             "recipe to be leaked and peddled as street food'.",
    ),
    "ong-flavours-of-sarawak": dict(
        title="Edgar Ong, 'The Flavours of Sarawak', in Official Guide to Sarawak (Sarawak "
              "state government / Leisure Guide Publishing, 2015)",
        url="https://sarawaktourism.com/",
        tier="specialist",
        note="Sole traceable source for Goh Lik Teck as originator of Sarawak laksa. Gives no "
             "description of what Goh's laksa looked or tasted like, so continuity with today's "
             "dish is unverifiable.",
    ),
    "hutton-nyonya": dict(
        title="Wendy Hutton on Nyonya cooking (quoted for mee siam and asam laksa)",
        url="https://en.wikipedia.org/wiki/Mee_siam",
        tier="specialist",
        note="'A Penang Nonya will follow Thai cooks and make a thin sour fishy gravy' where a "
             "Singapore Nonya uses santan. Also the source of the Penang-origin claim for mee siam.",
    ),
    "khir-johari-malay-food": dict(
        title="Khir Johari, The Food of Singapore Malays (and related interviews)",
        url="https://www.marshallcavendish.com/",
        tier="specialist",
        note="Mee siam as a pre-WWII Singapore creation; the noodle, not the dish, is what is "
             "Thai about mee siam.",
    ),
    "heritasian-jawi": dict(
        title="Heritasian on Jawi Peranakan cuisine",
        url="https://heritasian.com/",
        tier="specialist",
        note="Ghee as primary fat, nut and poppy-seed thickeners, rose water and saffron, the "
             "'four friends' sweet-spice quartet, nasi tomato, nasi lemuni, Jawi bamieh, bubur "
             "Asyura. Well researched but not peer-reviewed and confidently essayistic - the "
             "dish-level claims are flagged in the graph.",
    ),
    "carryitlikeharry-misua": dict(
        title="'Misua - the birthday cake of the Hokkien (Min) people', Carry It Like Harry",
        url="https://carryitlikeharry.com/hokkien-misua-mee-suah-noodles/",
        tier="specialist",
        note="Birthday, confinement and festival usages; red-dyed eggs; the no-biting rule; the "
             "Nyonya birthday-noodle transfer.",
    ),
    "radii-chinese-noodles": dict(
        title="'Mian'splained: An Illustrated Guide to Chinese Noodles, Part Two', RADII",
        url="https://radii.co/article/chinese-noodles-illustrated-guide-2",
        tier="specialist",
        note="Distinguishes Fujian 拌麵 (tossed, peanut) from Hakka 板麵 (board) - a terminological "
             "trap most English sources fall into.",
    ),
    "michelin-ckt": dict(
        title="'Iconic Dishes: Breaking Down Char Koay Teow in Malaysia and in Singapore', "
              "MICHELIN Guide",
        url="https://guide.michelin.com/sg/en/article/features/iconic-dishes-char-koay-teow",
        tier="specialist",
        note="Also the most prominent repetition of the unverified claim that Teochews dominate "
             "Penang's street food trade.",
    ),
    "michelin-yong-tau-foo": dict(
        title="'Iconic Dishes: A Crash Course on Yong Tau Foo, a Dish of Hakka Origins', "
              "MICHELIN Guide",
        url="https://guide.michelin.com/my/en/article/features/what-is-yong-tau-foo",
        tier="specialist",
    ),
    "michelin-hakka-kl": dict(
        title="'Cuisine Without Borders: The Essential Flavors of Hakka Food', MICHELIN Guide",
        url="https://guide.michelin.com/ae-az/en/article/dining-out/hakka-dishes-in-malaysia",
        tier="specialist",
    ),
    "michelin-malaysia-regional": dict(
        title="'A Taste of Malaysia: Exploring the Nation's Diverse Regional Flavors', "
              "MICHELIN Guide",
        url="https://guide.michelin.com/en/article/travel/malaysias-diverse-regional-flavors",
        tier="specialist",
        note="Penang Nyonya sour-and-fiery vs Malacca Nyonya coconut-rich.",
    ),
    "taste-roti-canai": dict(
        title="'The Indian Roti That Became Malaysia's National Bread', TASTE",
        url="https://tastecooking.com/indian-roti-became-malaysias-national-bread/",
        tier="specialist",
    ),
    "adriancheah-nyonya": dict(
        title="Adrian Cheah on Penang Nyonya food",
        url="https://adriancheah.com/",
        tier="specialist",
        note="Rempah pounding, pecah minyak, the Penang sour/herbal register.",
    ),

    # -------------------------------------------------------------- community
    "penang-traveltips-koh-lay-huan": dict(
        title="'Koh Lay Huan', Penang Travel Tips",
        url="https://www.penang-traveltips.com/people/koh-lay-huan.htm",
        tier="community",
        note="Hokkien merchant based at Kuala Muda, Kedah; brought boatloads of Chinese and Malay "
             "settlers from Kedah; first and only Kapitan Cina of George Town, May 1787.",
    ),
    "penang-traveltips-teochew": dict(
        title="'Teochew Association, George Town', Penang Travel Tips",
        url="https://www.penang-traveltips.com/teochew-association.htm",
        tier="community",
        note="Founded 1855, 127 Chulia Street; Hanjiang Teochew Ancestral Temple 1864; 2,316 "
             "registration records from 1919 each listing a Chaoshan district of origin.",
    ),
    "penang-traveltips-hokkien": dict(
        title="'Penang Hokkien People', Penang Travel Tips",
        url="https://www.penang-traveltips.com/penang-hokkien-people.htm",
        tier="community",
    ),
    "penang-traveltips-riots": dict(
        title="'Penang Riots of 1867', Penang Travel Tips",
        url="https://www.penang-traveltips.com/history/penang-riots-1867.htm",
        tier="community",
        note="Also: the riots exposed Kong Hock Keong's failure as a Hokkien-Cantonese mediating "
             "institution, which is why the Penang Chinese Town Hall was later needed.",
    ),
    "penang-traveltips-goddess-mercy": dict(
        title="'Goddess of Mercy Temple (Kuan Im Teng), George Town', Penang Travel Tips",
        url="https://www.penang-traveltips.com/goddess-of-mercy-temple.htm",
        tier="community",
        note="Kong Hock Keong 廣福宮, literally 'Guangdong-Fujian Temple', founded jointly c.1800.",
    ),
    "penang-traveltips-nagore": dict(
        title="'Nagore Durgha Sheriff, George Town', Penang Travel Tips",
        url="https://www.penang-traveltips.com/nagore-shrine.htm",
        tier="community",
    ),
    "penang-traveltips-mee-udang": dict(
        title="Timothy Tye on mee udang, Penang Travel Tips",
        url="https://www.penang-traveltips.com/",
        tier="community",
        note="'Primarily a Malay dish similar to the Jawa Mee sold by Chinese hawkers'; Teluk "
             "Kumbar as the historic cluster and a style name.",
    ),
    "penang-wikia-kuey-teow-thng": dict(
        title="'Kuey teow th'ng', Penang Wikia",
        url="https://penang.fandom.com/wiki/Kuey_teow_th%27ng",
        tier="community",
    ),
    "penang-wikia-ccf": dict(
        title="'Chee cheong fun', Penang Wikia",
        url="https://penang.fandom.com/wiki/Chee_cheong_fun",
        tier="community",
        note="The Penang hae ko + thnee cheo dressing.",
    ),
    "penang-wikia-kwangtung": dict(
        title="'Kwangtung & Tengchow Association', Penang Wikia",
        url="https://penang.fandom.com/wiki/Kwangtung_%26_Tengchow_Association",
        tier="community",
    ),
    "penang-wikia-white-curry": dict(
        title="Penang Wikia on white curry mee",
        url="https://penang.fandom.com/",
        tier="community",
        note="Credits MyKuali with the dish's international recognition.",
    ),
    "khookongsi-official": dict(
        title="'Introduction of Leong San Tong Khoo Kongsi Penang', official site",
        url="https://www.khookongsi.com.my/history/introduction-of-leong-san-tong-khoo-kongsi-penang/",
        tier="community",
        note="Founded 1835, temple completed 1906, Cannon Square; the Khoo from Sin Kang village.",
    ),
    "ccs-city-big-five": dict(
        title="'The Big Five Hokkien Families in Penang, 1830s-1890s', CCS.City",
        url="https://ccs.city/en/past-presend-and-future-in-research/big-five-hokkien-families-in-penang",
        tier="community",
    ),
    "ccs-city-teochew": dict(
        title="'Compatriots: Teochew People's Immigration to Southeast Asia', CCS.City",
        url="https://ccs.city/en/anthology-of-chinese-diasporas/migration-of-the-teochew",
        tier="community",
        note="Gambier and pepper plantations; Kedah and north Perak Teochew fishermen.",
    ),
    "taiwan-panorama-hakka": dict(
        title="'Malaysia's Hakka: Working for Profit, Striving for Knowledge', Taiwan Panorama",
        url="https://www.taiwan-panorama.com/en/Articles/Details?Guid=c26da55f-712c-400b-8af4-d010e8f34bbe",
        tier="community",
    ),
    "mothership-hainanese": dict(
        title="'The Hainanese started S'pore's kopitiam culture & created fusion food', "
              "Mothership.SG, Jul 2019",
        url="https://mothership.sg/2019/07/hainanese-singapore-culture/",
        tier="community",
        note="Late arrival, blocked trades, service work, then conversion of household culinary "
             "skill into hospitality enterprise.",
    ),
    "visitpenang-wanton-mee": dict(
        title="'Wanton Mee (云吞面)', Visit Penang Food Guide",
        url="https://www.visitpenang.com/food/dishes/wanton-mee",
        tier="community",
    ),
    "visitpenang-char-koay-kak": dict(
        title="'Char Koay Kak (炒粿角)', Visit Penang Food Guide",
        url="https://www.visitpenang.com/food/dishes/char-koay-kak",
        tier="community",
    ),
    "streetbite-koay-teow-thng": dict(
        title="'Koay Teow Th'ng - Penang's Comfort in a Bowl', Street Bite Tours",
        url="https://www.streetbitetours.com/koay-teow-thg",
        tier="community",
    ),
    "season-with-spice-asam-laksa": dict(
        title="'Story of Penang Asam Laksa', Season with Spice",
        url="http://blog.seasonwithspice.com/2011/09/what-is-penang-assam-laksa.html",
        tier="community",
    ),
    "hainan-temple-penang": dict(
        title="'Penang Hainan Temple', Malaysia Travel Guide",
        url="https://malaysialife.org/penang-hainan-temple/",
        tier="community",
        note="Penang Kheng Chew Hooi Kuan formed 1925; Loke Thye Kee, Burmah Road, founded 1919 "
             "by two Hainanese brothers.",
    ),

    # ------------------------------------------------------------ commercial
    "nestle-maggi-malaysia": dict(
        title="Nestle Malaysia corporate history of MAGGI in Malaysia",
        url="https://www.nestle.com.my/brands/maggi",
        tier="commercial",
        note="1969 arrival with tomato ketchup and chilli sauce; 1971 two-minute noodles in Kari "
             "and Ayam. The hard chronological anchor of the whole corpus: Maggi goreng cannot "
             "predate 1971.",
    ),
    "kim-lian-kee": dict(
        title="Restaurant Kim Lian Kee's own account of its 1927 founding",
        url="https://malaysiafoodandtravel.com/restaurant-kim-lian-kee-1927-original-hokkien-mee-kl-chinese-noodles/",
        tier="commercial",
        note="Ong Kim Lian from Anxi county, Fujian, arrived c.1905; moved to Petaling Street 1927. "
             "The 1927 date and business continuity are well documented; the invention claim is "
             "family oral history, and at least one retelling calls the founder 'Wong' mid-article.",
    ),
    "mykuali": dict(
        title="MyKuali (Thomas Tang, Penang) Penang White Curry Noodles",
        url="https://www.mykuali.com/",
        tier="commercial",
        note="Instant product launched 2012; ranked #1 in The Ramen Rater's 'Top 10 Instant "
             "Noodles of All Time', 2014. The mechanism by which 'white curry mee' became a "
             "named global category.",
    ),
    "lum-lai-duck": dict(
        title="Lum Lai Duck Meat Koay Teow Th'ng (Cecil Street Market, Michelin Bib Gourmand)",
        url="https://guide.michelin.com/my/en/penang-region/",
        tier="commercial",
        note="Founded late 1970s by Lau Lum Lai, itinerant pushcart hawker in George Town.",
    ),
    "hameed-pata": dict(
        title="Hameed 'Pata' Special Mee Sotong, Kota Selera, Padang Kota Lama",
        url="https://www.penang-traveltips.com/",
        tier="commercial",
        note="Family account: father selling mee rebus and mee goreng from 1942; mee sotong "
             "specialisation from 1978.",
    ),
    "air-itam-curry-mee": dict(
        title="The Lim sisters' Air Itam curry mee stall (Michelin-recognised)",
        url="https://guide.michelin.com/my/en/penang-region/",
        tier="commercial",
        note="Dates a stall to 1946, not the dish. Mdm Lim Kooi Lai died in 2025 aged 91.",
    ),
    "soong-kee": dict(
        title="Soong Kee Beef Noodles (颂记牛肉丸粉), Kuala Lumpur",
        url="https://en.wikipedia.org/wiki/Beef_noodle_soup",
        tier="commercial",
        note="Started 1945 by Hakka hawker-chef Siew Koy Soong; house tradition derives the dish "
             "from Tai Po (Dabu) Hakka noodles, not from Hainanese cooking.",
    ),
    "yean-kee-kluang": dict(
        title="Yean Kee Hainanese Beef Noodles, Kluang, Johor",
        url="https://en.wikipedia.org/wiki/Beef_noodle_soup",
        tier="commercial",
        note="Began as the pushcart 'Tian Le Yuan' in the old Kluang market, 1930, founded by "
             "Goh Hin.",
    ),
    "kin-kin": dict(
        title="Restoran Kin Kin (建記), Kampung Baru, Kuala Lumpur",
        url="https://en.wikipedia.org/wiki/Banmian",
        tier="commercial",
        note="Founded 1985 by Tan Kok Hong. The chilli condiment is not sold separately.",
    ),

    # ------------------------------------------------------------ fieldnote
    "pp-field-mee-sotong": dict(
        title="Penang Pulse field note - 'Jones Road Famous Mee Sotong Sambal', "
              "Mee Myself and I ep.16, 12 Aug 2026",
        url="https://penangpulse.com/guides/jones-road-famous-mee-sotong-sambal/",
        tier="community",
        note="First-hand tasting note. The stall's own account - a Jones Road / Tingkat "
             "Jones T-junction origin in the 1980s, since relocated into Sin Hup Aun Cafe - "
             "is stall-sourced and not independently verified.",
    ),

    # ----------------------------------------------------------------- media
    "cnn-go-2011": dict(
        title="CNN Go, 'World's 50 Most Delicious Foods', 21 July 2011",
        url="https://edition.cnn.com/travel/article/worlds-50-best-foods",
        tier="media",
        note="Penang asam laksa at #7, the only Malaysian entry in the top 10. Re-promoted by CNN "
             "Travel in 2020, which is why many sources misdate it.",
    ),
    "bourdain-no-reservations-borneo": dict(
        title="Anthony Bourdain, No Reservations, Borneo episode (2005) - Sarawak laksa as "
              "'Breakfast of the Gods'",
        url="https://en.wikipedia.org/wiki/Sarawak_laksa",
        tier="media",
        note="Eaten at Choon Hui Cafe, Ban Hock Road, Kuching, on two consecutive mornings. The "
             "direct cause of the dish's international profile.",
    ),
    "asian-inspirations-laksa": dict(
        title="'The History of Laksa', Asian Inspirations",
        url="https://asianinspirations.com.au/food-knowledge/the-history-of-laksa/",
        tier="media",
    ),
    "foodpanda-lam-mee": dict(
        title="foodpanda Malaysia's account of lam mee as a Cantonese re-pronunciation of loh mee",
        url="https://www.foodpanda.my/",
        tier="media",
        note="Assessed in this graph as probably wrong: Penang lam mee has a clear broth and a "
             "birthday ritual function; loh mee has a thick starch gravy and neither.",
    ),
    "tasteasianfood-mee-hailam": dict(
        title="'Mee Hailam recipe - Malaysian noodles with Hainanese influence', Taste of "
              "Asian Food",
        url="https://tasteasianfood.com/mee-hailam/",
        tier="media",
    ),
    "thesmartlocal-teh-tarik": dict(
        title="'The Origins Of Teh Tarik', TheSmartLocal MY",
        url="https://thesmartlocal.my/teh-tarik/",
        tier="media",
    ),
    "danielfooddiary-foochow": dict(
        title="'Seow Choon Hua Restaurant - For Nostalgic Foo Chow Fishballs And Red Wine "
              "Chicken Mee Sua', Daniel Food Diary",
        url="https://danielfooddiary.com/2022/03/27/seowchoonhua/",
        tier="media",
    ),
    "medium-kolo-mee": dict(
        title="Yow Hong Chieh, 'The Origins and History of Kolo Mee', Medium",
        url="https://medium.com/@sixtybolts/the-origins-and-history-of-kolo-mee-91b2b5aa9acd",
        tier="media",
        note="Kiew Shao Nyap of Baihou, Dapu county, Meizhou; Tai Pu / yan mee as the parent dish; "
             "Kuching in the 1920s.",
    ),
    "ummi-laksa-guide": dict(
        title="'A Complete Guide to Malaysian Laksa', Ummi Around Malaysia",
        url="https://ummiaroundmalaysia.com/malaysian-laksa/",
        tier="media",
    ),

    # ---------------------------------------------------------- encyclopedic
    "wiki-penangite-chinese": dict(
        title="'Penangite Chinese', Wikipedia",
        url="https://en.wikipedia.org/wiki/Penangite_Chinese",
        tier="encyclopedic",
    ),
    "wiki-1867-riots": dict(
        title="'1867 Penang riots', Wikipedia",
        url="https://en.wikipedia.org/wiki/1867_Penang_riots",
        tier="encyclopedic",
        note="3-12 Aug 1867; Gee Hin ~20,000 vs Toh Peh Kong ~9,000 led by Khoo Thean Teik; the "
             "rambutan-skin trigger; Suppression of Dangerous Societies Ordinance 1869.",
    ),
    "wiki-larut-wars": dict(
        title="'Larut Wars', Wikipedia",
        url="https://en.wikipedia.org/wiki/Larut_Wars",
        tier="encyclopedic",
    ),
    "wiki-hokkien-mee": dict(
        title="'Hokkien mee', Wikipedia",
        url="https://en.wikipedia.org/wiki/Hokkien_mee",
        tier="encyclopedic",
        note="Asserts without citation that all Hokkien mee variants descend from lor mee. "
             "Treated in this graph as a hypothesis.",
    ),
    "wiki-lor-mee": dict(
        title="'Lor mee', Wikipedia",
        url="https://en.wikipedia.org/wiki/Lor_mee",
        tier="encyclopedic",
        note="Zhangzhou attribution; the Putian lighter seafood form; the Henan 卤面 false friend.",
    ),
    "wiki-char-kway-teow": dict(
        title="'Char kway teow', Wikipedia",
        url="https://en.wikipedia.org/wiki/Char_kway_teow",
        tier="encyclopedic",
        note="Source of the 'fishermen, farmers and cockle-gatherers' origin claim, whose "
             "footnotes do not support it - see nlb-ckt.",
    ),
    "wiki-laksa": dict(
        title="'Laksa', Wikipedia",
        url="https://en.wikipedia.org/wiki/Laksa",
        tier="encyclopedic",
    ),
    "wiki-wonton-noodles": dict(
        title="'Wonton noodles', Wikipedia",
        url="https://en.wikipedia.org/wiki/Wonton_noodles",
        tier="encyclopedic",
        note="Guangzhou origin; the Tongzhi-reign 'Three Chu Noodles Restaurant'; Mak Woon-chi "
             "carrying it to Hong Kong.",
    ),
    "wiki-yi-mein": dict(
        title="'Yi mein', Wikipedia",
        url="https://en.wikipedia.org/wiki/Yi_mein",
        tier="encyclopedic",
        note="Yi Bingshou (1754-1815), prefect of Huizhou; the fry-dry-rehydrate technique; "
             "longevity symbolism.",
    ),
    "wiki-banmian": dict(
        title="'Banmian', Wikipedia",
        url="https://en.wikipedia.org/wiki/Banmian",
        tier="encyclopedic",
        note="The Hakka/Hokkien hybrid; mee hoon kueh, ban mian and youmian as three forms of one "
             "dough; the ikan bilis stock as the Malaysian marker.",
    ),
    "wiki-mee-pok": dict(
        title="'Mee pok', Wikipedia",
        url="https://en.wikipedia.org/wiki/Mee_pok",
        tier="encyclopedic",
        note="Mee pok = flat 'thin in cross-section'; mee kia = 'child noodle', equated with "
             "youmian / wonton noodle.",
    ),
    "wiki-kway-chap": dict(
        title="'Kway chap', Wikipedia",
        url="https://en.wikipedia.org/wiki/Kway_chap",
        tier="encyclopedic",
        note="'In Penang, Malaysia, duck offal and meat make up the sides instead of pork.'",
    ),
    "wiki-tuaran-mee": dict(
        title="'Tuaran mee', Wikipedia",
        url="https://en.wikipedia.org/wiki/Tuaran_mee",
        tier="encyclopedic",
    ),
    "wiki-sang-nyuk-mee": dict(
        title="'Sang nyuk mee', Wikipedia",
        url="https://en.wikipedia.org/wiki/Sang_nyuk_mee",
        tier="encyclopedic",
        note="Reported as invented 1979 by two brothers in Tawau, Sabah.",
    ),
    "wiki-kolo-mee": dict(
        title="'Kolo mee', Wikipedia",
        url="https://en.wikipedia.org/wiki/Kolo_mee",
        tier="encyclopedic",
        note="Iban names mi kering / mi rangkai for the halal version; the white/red/black styles.",
    ),
    "wiki-boat-noodles": dict(
        title="'Boat noodles', Wikipedia",
        url="https://en.wikipedia.org/wiki/Boat_noodles",
        tier="encyclopedic",
        note="Ayutthaya and Rangsit; the small-bowl explanation; fresh pig's or cow's blood as "
             "the thickener.",
    ),
    "wiki-fish-soup-bee-hoon": dict(
        title="'Fish soup bee hoon' / 'Fish head bee hoon', Wikipedia",
        url="https://en.wikipedia.org/wiki/Fish_soup",
        tier="encyclopedic",
    ),
    "wiki-mee-soto": dict(
        title="'Mee soto' / 'Soto (food)', Wikipedia",
        url="https://en.wikipedia.org/wiki/Soto_(food)",
        tier="encyclopedic",
        note="The Lombard-derived caudo/jaoto etymology; Surinamese saoto as a parallel diaspora.",
    ),
    "wiki-jawi-peranakan": dict(
        title="'Jawi Peranakan', Wikipedia",
        url="https://en.wikipedia.org/wiki/Jawi_Peranakan",
        tier="encyclopedic",
        note="Jawi Pekan as the Penang-preferred term; elite mercantile position; the Depression "
             "and the political incentive to register as Malay.",
    ),
    "wiki-nasi-kandar": dict(
        title="'Nasi kandar', Wikipedia",
        url="https://en.wikipedia.org/wiki/Nasi_kandar",
        tier="encyclopedic",
        note="Kandar shoulder pole; Weld Quay dock labour; kuah campur / banjir.",
    ),
    "wiki-pasembur": dict(
        title="'Pasembur', Wikipedia",
        url="https://en.wikipedia.org/wiki/Pasembur",
        tier="encyclopedic",
        note="Three-way disputed origin; the sweet-potato-and-peanut gravy; the rojak mee variant.",
    ),
    "wiki-mee-goreng-mamak": dict(
        title="'Mee goreng mamak', Wikipedia",
        url="https://en.wikipedia.org/wiki/Mee_goreng",
        tier="encyclopedic",
        note="Explicitly: Chinese yellow noodles with Malay and Indian seasoning, sold by "
             "Indian-Muslim hawkers; not found in India.",
    ),
    "wiki-roti-canai": dict(
        title="'Roti canai', Wikipedia",
        url="https://en.wikipedia.org/wiki/Roti_canai",
        tier="encyclopedic",
    ),
    "wiki-murtabak": dict(
        title="'Murtabak', Wikipedia",
        url="https://en.wikipedia.org/wiki/Murtabak",
        tier="encyclopedic",
        note="Arabic mutabbaq 'folded'; the Abbasid mutbaq recipe in al-Baghdadi's Kitab al-Tabikh; "
             "Hadhrami traders as the Java vector.",
    ),
    "wiki-singapore-noodles": dict(
        title="'Singapore-style noodles', Wikipedia",
        url="https://en.wikipedia.org/wiki/Singapore-style_noodles",
        tier="encyclopedic",
        note="A Hong Kong invention using British-Indian curry powder; not sold in Singapore.",
    ),
    "wiki-lanzhou-beef-noodle": dict(
        title="'Lanzhou beef noodles', Wikipedia",
        url="https://en.wikipedia.org/wiki/Lanzhou_beef_noodles",
        tier="encyclopedic",
        note="Ma Baozi, Hui Muslim, 1915; the yi qing er bai san hong si lu wu huang standard. "
             "The best-documented origin claim in the corpus.",
    ),
    "wiki-taiwanese-beef-noodle": dict(
        title="'Beef noodle soup' (Taiwanese red-braised), Wikipedia",
        url="https://en.wikipedia.org/wiki/Beef_noodle_soup",
        tier="encyclopedic",
        note="Created in Taiwan by KMT veterans from Sichuan in Gangshan juancun after 1949.",
    ),
    "wiki-chee-cheong-fun": dict(
        title="'Chee cheong fun' / 'Rice noodle roll', Wikipedia",
        url="https://en.wikipedia.org/wiki/Rice_noodle_roll",
        tier="encyclopedic",
    ),
    "wiki-hainanese-chicken-rice": dict(
        title="'Hainanese chicken rice', Wikipedia",
        url="https://en.wikipedia.org/wiki/Hainanese_chicken_rice",
        tier="encyclopedic",
    ),
    "wiki-wong-nai-siong": dict(
        title="'Wong Nai Siong', Wikipedia",
        url="https://en.wikipedia.org/wiki/Wong_Nai_Siong",
        tier="encyclopedic",
        note="Negotiated with Rajah Charles Brooke; 72 Fuzhou pioneers to Sibu in 1901; "
             "'Sin Hockchew'.",
    ),
    "wiki-kapitan-keling-mosque": dict(
        title="'Kapitan Keling Mosque', Wikipedia",
        url="https://en.wikipedia.org/wiki/Kapitan_Keling_Mosque",
        tier="encyclopedic",
        note="Founded 1801 on land granted by Leith to Cauder Mohudeen, first Kapitan Keling.",
    ),
    "wiki-chulia-street": dict(
        title="'Chulia Street, George Town', Wikipedia",
        url="https://en.wikipedia.org/wiki/Chulia_Street,_George_Town",
        tier="encyclopedic",
        note="Originally Malabar Street; renamed Chulia Street 1798; 1833 census 7,886 Chulias in "
             "Penang.",
    ),
    "wiki-demographics-penang": dict(
        title="'Demographics of Penang', Wikipedia",
        url="https://en.wikipedia.org/wiki/Demographics_of_Penang",
        tier="encyclopedic",
    ),
    "wiki-penang-cuisine": dict(
        title="'Penang cuisine', Wikipedia",
        url="https://en.wikipedia.org/wiki/Penang_cuisine",
        tier="encyclopedic",
    ),
    "wiki-mee-siam": dict(
        title="'Mee siam', Wikipedia",
        url="https://en.wikipedia.org/wiki/Mee_siam",
        tier="encyclopedic",
        note="Hutton, Sylvia Tan, Tan Chee-Beng and Chua Beng Huat as four named disputants; "
             "the Thai mi kathi comparison.",
    ),
    "wiki-teh-tarik": dict(
        title="'Teh tarik', Wikipedia",
        url="https://en.wikipedia.org/wiki/Teh_tarik",
        tier="encyclopedic",
    ),
    "wiki-yusheng": dict(
        title="'Yusheng', Wikipedia",
        url="https://en.wikipedia.org/wiki/Yusheng",
        tier="encyclopedic",
        note="Seremban 1940s (Loke Ching Fatt) vs Singapore 1960s ('Four Heavenly Kings'); both "
             "descend from the Guangdong renri raw-fish custom.",
    ),
}

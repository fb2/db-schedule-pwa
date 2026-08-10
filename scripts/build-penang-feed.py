#!/usr/bin/env python3
"""Build public Penang Pulse feed.json from fetched draft sources."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urljoin


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "scripts" / "penang_sources.json"

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
# Full cross-month/year range: "15 June 2025 - 30 September 2026"
FULL_DATE_RANGE_RE = re.compile(
    r"\b(\d{1,2})\s+([A-Za-z]{3,9})(?:\s*,?\s*(\d{4}))?\s*[–\-]\s*"
    r"(\d{1,2})\s+([A-Za-z]{3,9})(?:\s*,?\s*(\d{4}))?",
    re.I,
)
# Same-month day range: "25–30 Sep". (?<!\d) avoids "2025 - 30 Sep" → 25–30 Sep.
DATE_RANGE_RE = re.compile(
    r"(?<!\d)(\d{1,2})\s*[–\-]\s*(\d{1,2})\s+([A-Za-z]{3,9})(?:\s*,?\s*(\d{4}))?",
    re.I,
)
# "from 1 to 9 August" / "1 to 9 August 2026"
DATE_RANGE_TO_RE = re.compile(
    r"\b(?:from\s+)?(\d{1,2})\s+to\s+(\d{1,2})\s+([A-Za-z]{3,9})(?:\s*,?\s*(\d{4}))?",
    re.I,
)
SINGLE_DATE_RE = re.compile(
    r"\b(\d{1,2})\s+([A-Za-z]{3,9})(?:\s*,?\s*(\d{4}))?\b",
    re.I,
)
# Past-tense / after-the-fact event write-ups (especially undated RSS recaps).
PAST_EVENT_RECAP_RE = re.compile(
    r"\b("
    r"was held|were held|was staged|were staged|"
    r"took place|has concluded|have concluded|concluded|"
    r"last night|last (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"yesterday|over the weekend|"
    r"drew crowds|drew locals|drew thousands|drew revellers|"
    r"attracted (?:crowds|thousands|locals|visitors)|"
    r"descended on|packed the|filled the|"
    r"wrapped up|came to a close|kicked off yesterday|"
    r"earlier today|earlier this (?:week|month)"
    r")\b",
    re.I,
)
# Future/upcoming language that should keep an item despite weak past-ish verbs.
FUTURE_EVENT_HINT_RE = re.compile(
    r"\b("
    r"will be held|will take place|is scheduled|are scheduled|"
    r"to be held|set to|slated to|coming soon|"
    r"this (?:weekend|coming)|next (?:week|month)|"
    r"tickets? (?:are )?now|register (?:now|here)|"
    r"will (?:bring|feature|host|run|open)|opens? on|starts? on"
    r")\b",
    re.I,
)
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
FOOD_HINTS = re.compile(
    r"\b(cafe|café|restaurant|bakery|hawker|stall|popup|pop-up|buffet|eatery|bistro|opening|opened)\b",
    re.I,
)
OPENING_HINTS = re.compile(
    r"\b(open(?:ed|ing)|now open|new cafe|new restaurant|launches?|first store|grand opening)\b|"
    r"(开幕|新开|开张)",
    re.I,
)
REVIEW_HINTS = re.compile(
    r"\b(best|must[- ]try|must[- ]visit|review|guide|spots?|edition|worth|favourite|favorite)\b|"
    r"(必比登|米其林|推荐|必吃|推介|值得)",
    re.I,
)
NOISE_FOOD = re.compile(
    r"\b(closure|hygiene|violation|gazettes|tourism chief|missing|4d|magnum|grant|privacy policy|"
    r"itinerary|shenzhen|massage chair)\b",
    re.I,
)
EVENT_HINTS = re.compile(
    r"\b(festival|event|parade|fair|exhibition|concert|workshop|market|celebration|programme|program)\b|"
    r"(嘉年华|活动|展览|市集)",
    re.I,
)
OUTSIDE_PENANG_EVENT_RE = re.compile(
    r"\b(kuala lumpur|petaling jaya|putrajaya|shah alam|mitec)\b",
    re.I,
)
HIN_JUNK_RE = re.compile(
    r"^(subscribe to our mailing list|this website uses cookies\.?)$",
    re.I,
)
# Corporate / institutional PR with no planning value: MoUs and partnership
# announcements, executive appointments, policy programmes, industry
# symposiums, property launches. Applies to every kind, not just events.
PROMO_NOISE_RE = re.compile(
    r"\bmemorandum of understanding\b|\bmou\b|"
    r"\bthrough (?:a )?new partnership\b|"
    r"\btalent (?:pilot )?(?:programme|program|scheme)\b|"
    r"\bfood safety (?:symposium|day|ministry)\b|"
    r"\b\d+ industry leaders\b|\bindustry leaders gather\b|"
    r"\bappoints?\b[^.]{0,60}\bchef\b|\bnew executive chef\b|"
    r"\bfreehold\b|\bleasehold\b|\bserviced apartments?\b|\bcondominium\b|"
    r"\bproperty launch\b|"
    r"(人才计划|人才培育|谅解备忘录)",
    re.I,
)
EVENT_NEWS_NOISE_RE = re.compile(
    r"\b("
    r"deploys gps tracking|scales up .*training|wedding venue guide|"
    r"on track for .*completion|proposed acquisition|launches? .*campaign"
    r")\b",
    re.I,
)
# Consumer-facing interests to surface near the top of Happening soon.
# Each rule: (topic id, keyword regex, score boost).
INTEREST_RULES: list[tuple[str, re.Pattern[str], int]] = [
    (
        "family",
        re.compile(
            r"\b(family|kids?|children|child[- ]friendly|all ages|toddler|亲子|家庭|"
            r"keluarga|kanak[- ]kanak)\b",
            re.I,
        ),
        22,
    ),
    (
        "festival",
        re.compile(
            r"\b(festival|fiesta|carnival|嘉年华|节|pesta|perayaan)\b",
            re.I,
        ),
        28,
    ),
    (
        "fair",
        re.compile(
            r"\b(fair|bazaar|pasar malam|night market|flea|craft fair|travel fair|"
            r"市集|夜市|bazaar)\b",
            re.I,
        ),
        20,
    ),
    (
        "literary",
        re.compile(
            r"\b(literary|literature|book\s*fair|bookstore|poetry|poet|author talk|"
            r"reading\b|writers?|novel|书展|文学|buku|sastera)\b",
            re.I,
        ),
        24,
    ),
    (
        "food",
        re.compile(
            r"\b(food|culinary|gastronom|hawker|street food|makan|foodie|taste of|"
            r"美食|小吃|makanan|jualan makanan)\b",
            re.I,
        ),
        18,
    ),
    (
        "music",
        re.compile(
            r"\b(music|concert|gig|orchestra|choir|jazz|live band|open mic|"
            r"音乐会|演唱会|muzik|konsert)\b",
            re.I,
        ),
        22,
    ),
    (
        "culture",
        re.compile(
            r"\b(culture|cultural|heritage|museum|art\b|arts\b|theatre|theater|"
            r"dance|exhibition|gallery|wayang|传统文化|文化|展览|budaya|warisan)\b",
            re.I,
        ),
        18,
    ),
    (
        "movies",
        re.compile(
            r"\b(movie|film|cinema|screening|film fest|电影|影展|filem|pameran filem)\b",
            re.I,
        ),
        20,
    ),
    (
        "books",
        re.compile(
            r"\b(books?|bookstore|bookshop|library|reading club|书|书局|perpustakaan)\b",
            re.I,
        ),
        18,
    ),
    (
        "gaming",
        re.compile(
            r"\b(gaming|game\s*night|board\s*game|tabletop|esports?|video\s*game|"
            r"游戏|permainan)\b",
            re.I,
        ),
        16,
    ),
]
# Industry / trade / B2B — demote heavily or drop from consumer "Happening soon".
INDUSTRY_HARD_RE = re.compile(
    r"\b("
    r"halal\s+industry|mihas|pharma(?:ceutical)?\s+expo|medical\s+device\s+expo|"
    r"b2b|business[- ]to[- ]business|trade\s+only|trade\s+visitors?\s+only|"
    r"industry\s+expo|industrial\s+expo|manufactur(?:ing|ers?)\s+expo|"
    r"procurement\s+(?:forum|expo|summit)|supply\s+chain\s+(?:expo|summit)|"
    r"investor\s+(?:forum|summit)|property\s+investment\s+(?:expo|fair)|"
    r"conference\s+for\s+professionals|professional\s+conference|"
    r"corporate\s+(?:summit|expo|convention)|"
    r"pihex|penang\s+international\s+halal"
    r")\b|"
    r"(清真工业|工业展|贸易展)",
    re.I,
)
INDUSTRY_FORM_RE = re.compile(
    r"\b(expo|exhibition|convention|symposium|summit|trade\s+show|trade\s+fair|"
    r"congress|business\s+forum)\b",
    re.I,
)
INDUSTRY_CONTEXT_RE = re.compile(
    r"\b(industry|industrial|trade|corporate|business|b2b|professional|"
    r"manufactur|procurement|investor|halal\s+hub|export|wholesale|"
    r"会议|峰会|展会)\b",
    re.I,
)
JUNK_TITLES = {
    "cafe",
    "café",
    "penang",
    "food",
    "restaurant",
    "home",
    "more",
    "read more",
    "learn more",
}
GTF_JUNK_TITLES = {
    "download now",
    "explore more",
    "learn more",
    "click to explore the full programme",
    "get tickets",
    "buy tickets",
}
MYPENANG_EVENT_RE = re.compile(
    r'<div class="row event-item">(.*?)</div>\s*<div class="row event-item">|'
    r'<div class="row event-item">(.*?)</div>\s*</div>\s*</div>',
    re.I | re.S,
)
CHINAPRESS_LINK_RE = re.compile(
    r'<a[^>]+href="(https://penang\.chinapress\.com\.my/(\d{8})/[^"]+)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
FOODIE_LINK_RE = re.compile(
    r'<a[^>]+href="(https://penangfoodie\.com/([^"#?]+)/?)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
OG_IMAGE_RE = re.compile(
    r'<meta\s+(?:property|name)=["\']og:image(?::secure_url)?["\']\s+content=["\']([^"\']+)["\']|'
    r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image(?::secure_url)?["\']',
    re.I,
)
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
# Lazy-loading builders (GoDaddy/wsimg, WordPress plugins) keep the real poster in a
# data attribute and ship a 1x1 placeholder in src.
LAZY_IMG_ATTR_RE = re.compile(
    r'\b(?:data-srclazy|data-lazy-src|data-original|data-src)=["\']([^"\']+)["\']',
    re.I,
)
LAZY_SRCSET_ATTR_RE = re.compile(
    r'\b(?:data-srcsetlazy|data-lazy-srcset|srcset)=["\']([^"\']+)["\']',
    re.I,
)
# Site chrome that must never become an item card image.
LOGO_IMAGE_RE = re.compile(
    r"(logo|favicon|apple-touch-icon|site-?icon|brandmark|sprite|"
    r"transparent_placeholder|placeholder|spacer\.gif|/wp-includes/)",
    re.I,
)
WSIMG_WIDTH_RE = re.compile(r"(rs=w:)(\d+)", re.I)
# PenangToday RSS often embeds /wp-content/uploads/ URLs that soft-404 to the homepage.
# Prefer /ipsostuh/ CDN paths from article og:image instead.
BROKEN_IMAGE_RE = re.compile(
    r"https?://penangtoday\.my/wp-content/uploads/",
    re.I,
)
HIN_BLOCK_RE = re.compile(
    r"<h4[^>]*>\s*(.*?)\s*</h4>\s*(.*?)(?=<h4|SUBSCRIBE|$)",
    re.I | re.S,
)
# Each Hin event is a builder "ContentCard": poster image, duplicated h4 title
# (mobile + desktop), description block, then an optional CTA link.
HIN_CARD_SPLIT_RE = re.compile(r'(?=<div\s[^>]*data-ux="ContentCard")', re.I)
HIN_CARD_TITLE_RE = re.compile(r"<h4[^>]*>(.*?)</h4>", re.I | re.S)
HIN_CARD_TEXT_RE = re.compile(
    r'<div[^>]+data-ux="ContentCardText"[^>]*>(.*?)</div>', re.I | re.S
)
HIN_CARD_LINK_RE = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.I)
# CTA links that say nothing about the event itself; keep the events page instead.
HIN_GENERIC_LINK_RE = re.compile(
    r"(instagram\.com/hinbusdepot/?(?:\?|$)|list-manage\.com|facebook\.com/hinbusdepot/?(?:\?|$))",
    re.I,
)
SMARTLOCAL_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.I | re.S)
SMARTLOCAL_MONTH_RE = re.compile(
    r"^[–\-—]?\s*(january|february|march|april|may|june|july|august|september|october|november|december)\s*[–\-—]?$",
    re.I,
)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def title_from_slug(slug: str) -> str:
    """Humanize a URL slug when link text is nav chrome (Cafe / Penang)."""
    raw = (slug or "").strip("/")
    if "/" in raw:
        raw = raw.rsplit("/", 1)[-1]
    raw = re.sub(r"-\d+$", "", raw)
    words = [w for w in raw.replace("-", " ").split() if w]
    if len(words) < 3:
        return ""
    return " ".join(w.capitalize() for w in words)


def is_junk_title(title: str) -> bool:
    t = (title or "").strip().lower()
    if not t or len(t) < 8:
        return True
    if t in JUNK_TITLES:
        return True
    return False


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(TAG_RE.sub(" ", value))
    return WS_RE.sub(" ", text).strip()


def normalize_image_url(url: str | None, base: str = "") -> str:
    if not url:
        return ""
    cleaned = html.unescape(url.strip())
    if not cleaned or cleaned.startswith("data:"):
        return ""
    if BROKEN_IMAGE_RE.search(cleaned):
        return ""
    if base and cleaned.startswith("/"):
        cleaned = urljoin(base, cleaned)
    if cleaned.startswith("//"):
        cleaned = "https:" + cleaned
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        return ""
    return cleaned


def classify_food_kind(title: str, summary: str = "", default_kind: str = "revisit") -> str:
    blob = f"{title} {summary}"
    if OPENING_HINTS.search(blob):
        return "food"
    if REVIEW_HINTS.search(blob):
        return "revisit"
    return default_kind


def is_logo_image(url: str | None) -> bool:
    """True for site chrome (brand logo, favicon, placeholder) rather than content."""
    return bool(url) and bool(LOGO_IMAGE_RE.search(url))


def upgrade_wsimg_width(url: str, target: int = 1095) -> str:
    """Request a poster-sized render from the wsimg CDN instead of the 365px thumbnail."""
    if "wsimg.com" not in url:
        return url

    def bump(match: re.Match[str]) -> str:
        width = int(match.group(2))
        return f"{match.group(1)}{target}" if width < target else match.group(0)

    return WSIMG_WIDTH_RE.sub(bump, url)


def largest_srcset_url(srcset: str, base: str = "") -> str:
    """Pick the highest-density/width candidate from a srcset attribute."""
    best_url = ""
    best_weight = -1.0
    for candidate in srcset.split(","):
        parts = candidate.strip().split()
        if not parts:
            continue
        url = normalize_image_url(parts[0], base)
        if not url or is_logo_image(url):
            continue
        weight = 1.0
        if len(parts) > 1:
            descriptor = parts[1].lower()
            try:
                weight = float(descriptor[:-1])
            except ValueError:
                weight = 1.0
        if weight > best_weight:
            best_weight = weight
            best_url = url
    return best_url


def first_content_img(raw_html: str | None, base: str = "") -> str:
    """Best content image from a block, tolerating lazy-loaded builder markup."""
    if not raw_html:
        return ""
    for match in LAZY_IMG_ATTR_RE.finditer(raw_html):
        url = normalize_image_url(match.group(1), base)
        if url and not is_logo_image(url):
            return url
    for match in LAZY_SRCSET_ATTR_RE.finditer(raw_html):
        url = largest_srcset_url(match.group(1), base)
        if url:
            return url
    for match in IMG_SRC_RE.finditer(raw_html):
        url = normalize_image_url(match.group(1), base)
        if url and not is_logo_image(url):
            return url
    return ""


def first_img_src(raw_html: str | None, base: str = "") -> str:
    if not raw_html:
        return ""
    match = IMG_SRC_RE.search(raw_html)
    if not match:
        return ""
    return normalize_image_url(match.group(1), base)


def extract_og_image(page_html: str, base: str = "") -> str:
    match = OG_IMAGE_RE.search(page_html or "")
    if not match:
        return ""
    return normalize_image_url(match.group(1) or match.group(2), base)


def fetch_url_text(url: str, timeout: int, user_agent: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-MY,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            # Cap body read so a slow host cannot stall publish for minutes.
            return response.read(400_000).decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return ""


# Hosts that often hang or soft-block automated GETs during og:image enrichment.
SLOW_ENRICH_HOST_RE = re.compile(
    r"(chinapress\.com\.my|buletinmutiara\.com|penanghyperlocal\.com|smartdory\.com)",
    re.I,
)


def enrich_missing_images(
    items: list[dict[str, Any]],
    *,
    user_agent: str,
    timeout: int = 6,
    sleep: float = 0.12,
    limit: int = 12,
    deadline_sec: float = 75.0,
) -> int:
    """Fill empty imageUrl from article og:image (needed for PenangToday).

    Bounded by request timeout, item limit, and a hard wall-clock deadline so
    --publish finishes in minutes even when remote hosts stall.
    """
    filled = 0
    attempted = 0
    started = time.monotonic()
    priority_ids = {
        "penangtoday_events",
        "penangtoday_food",
        "penang_foodie",
        "hin_bus_depot",
    }
    candidates = [
        i
        for i in items
        if not i.get("imageUrl") and (i.get("sourceUrl") or "").startswith("http")
    ]
    candidates.sort(key=lambda i: 0 if (i.get("sourceId") or "") in priority_ids else 1)
    for item in candidates:
        if filled >= limit or attempted >= limit * 2:
            break
        if time.monotonic() - started > deadline_sec:
            print(
                f"Stopping image enrichment after {deadline_sec:.0f}s "
                f"({filled} filled, {attempted} attempted)"
            )
            break
        source_url = item.get("sourceUrl") or ""
        source_id = item.get("sourceId") or ""
        if source_id not in priority_ids:
            continue
        if SLOW_ENRICH_HOST_RE.search(source_url):
            continue
        attempted += 1
        html_text = fetch_url_text(source_url, timeout, user_agent)
        image = extract_og_image(html_text, source_url)
        if is_logo_image(image):
            # Builder sites set og:image to the brand logo on listing pages.
            image = ""
        if not image:
            image = first_content_img(html_text, source_url)
        if image:
            item["imageUrl"] = image
            filled += 1
        time.sleep(sleep)
    return filled


def slug_id(kind: str, title: str, start: str | None) -> str:
    basis = f"{kind}|{title.strip().lower()}|{start or ''}"
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "item"
    return f"{kind}-{slug}-{digest}"


def month_num(name: str) -> int | None:
    return MONTHS.get(name.lower())


def coerce_year(year: str | None, default_year: int) -> int:
    return int(year) if year else default_year


def _fmt_day_month(day: int, month: int, year: int | None = None) -> str:
    month_name = dt.date(2000, month, 1).strftime("%b")
    if year is None:
        return f"{day} {month_name}"
    return f"{day} {month_name} {year}"


def parse_dates_from_text(text: str, default_year: int) -> tuple[str | None, str | None, str]:
    text = clean_text(text)
    full = FULL_DATE_RANGE_RE.search(text)
    if full:
        d1, m1, y1, d2, m2, y2 = full.groups()
        month1, month2 = month_num(m1), month_num(m2)
        if month1 and month2:
            year2 = coerce_year(y2, default_year)
            if y1:
                year1 = int(y1)
            else:
                year1 = year2
                if month1 > month2 or (month1 == month2 and int(d1) > int(d2)):
                    year1 = year2 - 1
            start = f"{year1:04d}-{month1:02d}-{int(d1):02d}"
            end = f"{year2:04d}-{month2:02d}-{int(d2):02d}"
            if year1 != year2:
                label = f"{_fmt_day_month(int(d1), month1, year1)} – {_fmt_day_month(int(d2), month2, year2)}"
            elif month1 != month2:
                label = f"{_fmt_day_month(int(d1), month1)} – {_fmt_day_month(int(d2), month2)}"
            else:
                label = f"{int(d1)}–{int(d2)} {m2[:3].title()}"
            return start, end, label
    for pattern in (DATE_RANGE_RE, DATE_RANGE_TO_RE):
        range_match = pattern.search(text)
        if not range_match:
            continue
        d1, d2, month, year = range_match.groups()
        m = month_num(month)
        if m:
            y = coerce_year(year, default_year)
            start = f"{y:04d}-{m:02d}-{int(d1):02d}"
            end = f"{y:04d}-{m:02d}-{int(d2):02d}"
            label = f"{int(d1)}–{int(d2)} {month[:3].title()}"
            return start, end, label
    single = SINGLE_DATE_RE.search(text)
    if single:
        d, month, year = single.groups()
        m = month_num(month)
        if m:
            y = coerce_year(year, default_year)
            start = f"{y:04d}-{m:02d}-{int(d):02d}"
            label = f"{int(d)} {month[:3].title()}"
            return start, start, label
    return None, None, ""


def newest_draft_dir(draft_root: pathlib.Path) -> pathlib.Path | None:
    if not draft_root.exists():
        return None
    dirs = sorted([p for p in draft_root.iterdir() if p.is_dir()], reverse=True)
    return dirs[0] if dirs else None


def load_manifest(draft_dir: pathlib.Path) -> dict[str, Any]:
    path = draft_dir / "fetch-manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def read_source_text(draft_dir: pathlib.Path, entry: dict[str, Any]) -> str:
    rel = entry.get("path")
    if not rel:
        return ""
    path = draft_dir / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_rss_items(
    text: str,
    *,
    kind: str,
    source_name: str,
    source_id: str,
    default_year: int,
    limit: int = 12,
) -> list[dict[str, Any]]:
    if not text.strip():
        return []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    channel = root.find("channel")
    if channel is None:
        return []
    items: list[dict[str, Any]] = []
    for node in channel.findall("item")[:limit]:
        title = clean_text(node.findtext("title"))
        link = clean_text(node.findtext("link"))
        raw_encoded = node.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or ""
        raw_description = node.findtext("description") or ""
        description = clean_text(raw_description or raw_encoded)
        pub = clean_text(node.findtext("pubDate"))
        if not title or not link:
            continue
        item_kind = kind
        blob = f"{title} {description}"
        if kind == "food":
            if NOISE_FOOD.search(blob) and not FOOD_HINTS.search(blob):
                continue
            item_kind = classify_food_kind(title, description, default_kind="food")
        elif kind == "revisit":
            if NOISE_FOOD.search(blob) and not (FOOD_HINTS.search(blob) or REVIEW_HINTS.search(blob)):
                continue
            item_kind = classify_food_kind(title, description, default_kind="revisit")
        elif kind == "event" and source_id in {"penang_hyperlocal", "buletin_mutiara"}:
            if not EVENT_HINTS.search(blob) or OUTSIDE_PENANG_EVENT_RE.search(blob):
                continue
        if item_kind == "event" and EVENT_NEWS_NOISE_RE.search(blob):
            continue
        # Prefer dates mentioned in the article text. RSS pubDate is article
        # publish time, not the event/opening date — do not treat it as startDate.
        start, end, label = parse_dates_from_text(blob, default_year)
        image_url = ""
        enclosure = node.find("enclosure")
        if enclosure is not None:
            image_url = normalize_image_url(enclosure.attrib.get("url", ""), link)
        media = node.find("{http://search.yahoo.com/mrss/}content")
        if media is not None and not image_url:
            image_url = normalize_image_url(media.attrib.get("url", ""), link)
        if not image_url:
            image_url = first_img_src(raw_encoded, link) or first_img_src(raw_description, link)
        summary = description[:220] + ("…" if len(description) > 220 else "")
        if item_kind == "food":
            date_label = label or "Recently · Penang"
        elif item_kind == "revisit":
            date_label = label or "Worth a revisit · Penang"
        else:
            date_label = label or "Date TBA · Penang"
        items.append(
            {
                "id": slug_id(item_kind, title, start),
                "kind": item_kind,
                "title": title,
                "summary": summary,
                "detail": description[:800],
                "startDate": start,
                "endDate": end,
                "dateLabel": date_label,
                "area": "Penang",
                "imageUrl": image_url,
                "sourceUrl": link,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Food" if item_kind in {"food", "revisit"} else "Events",
                "publishedAt": pub or None,
            }
        )
    return items


def _hin_card_body(card: str) -> str:
    match = HIN_CARD_TEXT_RE.search(card)
    if match:
        text = clean_text(match.group(1))
        if text:
            return text
    return clean_text(HIN_CARD_TITLE_RE.sub(" ", card))


def hin_event_blocks(text: str) -> list[tuple[str, str, str, str]]:
    """Yield (title, body, imageUrl, href) per event card.

    Falls back to the older heading-split scan if the builder markup changes, so a
    layout change degrades to text-only items instead of dropping the source.
    """
    blocks: list[tuple[str, str, str, str]] = []
    for card in HIN_CARD_SPLIT_RE.split(text):
        if 'data-ux="ContentCard"' not in card:
            continue
        title_match = HIN_CARD_TITLE_RE.search(card)
        if not title_match:
            continue
        image = first_content_img(card, "https://hinbusdepot.com/")
        href = ""
        for link_match in HIN_CARD_LINK_RE.finditer(card):
            candidate = link_match.group(1)
            if not HIN_GENERIC_LINK_RE.search(candidate):
                href = candidate
                break
        blocks.append(
            (
                clean_text(title_match.group(1)),
                _hin_card_body(card),
                upgrade_wsimg_width(image) if image else "",
                href,
            )
        )
    if blocks:
        return blocks
    for match in HIN_BLOCK_RE.finditer(text):
        link_match = re.search(r'href=["\']([^"\']+)["\']', match.group(2), re.I)
        blocks.append(
            (
                clean_text(match.group(1)),
                clean_text(match.group(2)),
                "",
                link_match.group(1) if link_match else "",
            )
        )
    return blocks


def parse_hin_events(text: str, source_name: str, source_id: str, default_year: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for title, body, image_url, href in hin_event_blocks(text):
        if not title or title.lower() in seen or is_junk_title(title) or HIN_JUNK_RE.search(title):
            continue
        seen.add(title.lower())
        start, end, label = parse_dates_from_text(body, default_year)
        if not start:
            start, end, label = parse_dates_from_text(title, default_year)
        source_url = urljoin("https://hinbusdepot.com/", href or "https://hinbusdepot.com/events")
        kind = "food" if re.search(r"market|pasar|popup|pop-up", title, re.I) else "event"
        date_label = " · ".join(part for part in [label or "Ongoing", "Hin Bus Depot"] if part)
        items.append(
            {
                "id": slug_id(kind, title, start),
                "kind": kind,
                "title": title,
                "summary": body[:220] + ("…" if len(body) > 220 else ""),
                "detail": body[:800],
                "startDate": start,
                "endDate": end,
                "dateLabel": date_label,
                "area": "George Town",
                "imageUrl": image_url,
                "sourceUrl": source_url,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Markets" if kind == "food" else "Arts",
            }
        )
    return items[:16]


def parse_smartlocal_cafes(text: str, source_name: str, source_id: str, page_url: str) -> list[dict[str, Any]]:
    """Parse numbered cafe headings; keep only the newest month section on the page."""
    items: list[dict[str, Any]] = []
    page_image = extract_og_image(text, page_url) or first_img_src(text, page_url)
    current_month: str | None = None
    newest_month: str | None = None
    for raw in SMARTLOCAL_H3_RE.findall(text):
        cleaned = clean_text(raw)
        if not cleaned:
            continue
        month_match = SMARTLOCAL_MONTH_RE.match(cleaned)
        if month_match:
            current_month = month_match.group(1).title()
            if newest_month is None:
                newest_month = current_month
            continue
        if newest_month and current_month and current_month != newest_month:
            # Older month sections further down the evergreen article.
            continue
        # "1. Hearty Cafe" / nested <strong> already stripped by clean_text.
        numbered = re.match(r"^(\d+)\.\s+(.+)$", cleaned)
        if not numbered:
            continue
        title = numbered.group(2).strip()
        if len(title) < 3 or title.lower().startswith("new cafes"):
            continue
        label = f"New opening · {newest_month}" if newest_month else "New opening · Penang"
        items.append(
            {
                "id": slug_id("food", title, None),
                "kind": "food",
                "title": title,
                "summary": "New cafe or restaurant opening highlighted in The Smart Local Penang roundup.",
                "detail": "",
                "startDate": None,
                "endDate": None,
                "dateLabel": label,
                "area": "Penang",
                "imageUrl": page_image,
                "sourceUrl": page_url,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Food",
            }
        )
        if len(items) >= 10:
            break
    return items


def parse_gtf(text: str, source_name: str, source_id: str, page_url: str, default_year: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    hero = extract_og_image(text, page_url)
    for match in re.finditer(
        r'<a[^>]+href="(https://georgetownfestival\.com/programme/[^"]+)"[^>]*>\s*([^<]{3,120})\s*</a>',
        text,
        re.I,
    ):
        href, title = match.group(1), clean_text(match.group(2))
        if not title or title.lower() in GTF_JUNK_TITLES:
            continue
        start, end, label = parse_dates_from_text(title, default_year)
        items.append(
            {
                "id": slug_id("event", title, start),
                "kind": "event",
                "title": title,
                "summary": "George Town Festival programme highlight.",
                "detail": "",
                "startDate": start,
                "endDate": end,
                "dateLabel": (label + " · George Town") if label else "George Town Festival",
                "area": "George Town",
                "imageUrl": hero,
                "sourceUrl": href,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Arts",
            }
        )
        if len(items) >= 12:
            break
    if not items and "George Town Festival" in text:
        items.append(
            {
                "id": slug_id("event", "George Town Festival", f"{default_year}-08-01"),
                "kind": "event",
                "title": "George Town Festival",
                "summary": "Annual arts festival across George Town heritage venues.",
                "detail": "",
                "startDate": f"{default_year}-08-01",
                "endDate": f"{default_year}-08-09",
                "dateLabel": f"Aug {default_year} · George Town",
                "area": "George Town",
                "imageUrl": hero,
                "sourceUrl": page_url,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Arts",
            }
        )
    return items


def parse_smartdory_home(text: str, source_name: str, source_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for match in re.finditer(
        r'<a[^>]+href="(https://smartdory\.com/\d{4}/\d{2}/[^"]+)"[^>]*>([^<]{8,140})</a>',
        text,
        re.I,
    ):
        href, title = match.group(1), clean_text(match.group(2))
        if len(title) < 18:
            continue
        if not FOOD_HINTS.search(title) and "penang" not in title.lower():
            continue
        if title.lower() in {"penang", "cafe", "food", "restaurant"}:
            continue
        kind = classify_food_kind(title, default_kind="revisit")
        items.append(
            {
                "id": slug_id(kind, title, None),
                "kind": kind,
                "title": title,
                "summary": "Local food write-up from SmartDory.",
                "detail": "",
                "startDate": None,
                "endDate": None,
                "dateLabel": "New opening · Penang" if kind == "food" else "Worth a revisit · Penang",
                "area": "Penang",
                "imageUrl": "",
                "sourceUrl": href,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Food",
            }
        )
        if len(items) >= 6:
            break
    return items


def parse_mypenang_events(
    text: str, source_name: str, source_id: str, page_url: str, default_year: int
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    blocks = re.findall(r'<div class="row event-item">(.*?)</div>\s*(?=<div class="row event-item"|$)', text, re.I | re.S)
    for block in blocks:
        link_match = re.search(
            r'<div class="title">\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            block,
            re.I | re.S,
        )
        if not link_match:
            continue
        href = urljoin(page_url, link_match.group(1))
        title = clean_text(link_match.group(2))
        if not title:
            continue
        subtitle = clean_text(
            re.search(r'<div class="subtitle">(.*?)</div>', block, re.I | re.S).group(1)
            if re.search(r'<div class="subtitle">(.*?)</div>', block, re.I | re.S)
            else ""
        )
        summary = clean_text(
            re.search(r'<div class="summary">(.*?)</div>', block, re.I | re.S).group(1)
            if re.search(r'<div class="summary">(.*?)</div>', block, re.I | re.S)
            else ""
        )
        img_match = re.search(r'<img[^>]+src="([^"]+)"', block, re.I)
        image_url = normalize_image_url(img_match.group(1) if img_match else "", page_url)
        start, end, label = parse_dates_from_text(
            subtitle.replace("Event Date:", "") if subtitle else (summary or title),
            default_year,
        )
        items.append(
            {
                "id": slug_id("event", title, start),
                "kind": "event",
                "title": title,
                "summary": (summary or subtitle)[:220],
                "detail": summary[:800],
                "startDate": start,
                "endDate": end,
                "dateLabel": (label + " · myPenang") if label else "myPenang",
                "area": "Penang",
                "imageUrl": image_url,
                "sourceUrl": href,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Events",
            }
        )
        if len(items) >= 16:
            break
    return items


def parse_chinapress_category(
    text: str, source_name: str, source_id: str, page_url: str, default_year: int
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    # Prefer in-category cards; homepage chrome often injects unrelated dated headlines.
    scoped = "\n".join(
        re.findall(
            r'<(?:div|a)[^>]*class="[^"]*(?:vertical-post|horizontal-post|title)[^"]*"[^>]*>.*?(?=<div class="(?:vertical-post|horizontal-post|page-section)|$)',
            text,
            re.I | re.S,
        )
    ) or text
    for match in CHINAPRESS_LINK_RE.finditer(scoped):
        href, ymd, inner = match.group(1), match.group(2), match.group(3)
        title = clean_text(inner)
        if len(title) < 6:
            alt = re.search(r'alt="([^"]+)"', inner, re.I)
            title = clean_text(alt.group(1) if alt else "")
        if len(title) < 6 or href in seen:
            continue
        seen.add(href)
        kind = classify_food_kind(title, default_kind="revisit")
        published = None
        if len(ymd) == 8 and ymd.isdigit():
            published = f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}"
        items.append(
            {
                "id": slug_id(kind, title, published),
                "kind": kind,
                "title": title,
                "summary": "China Press Penang food & lifestyle highlight.",
                "detail": "",
                "startDate": None,
                "endDate": None,
                "dateLabel": "New opening · Penang" if kind == "food" else "Worth a revisit · Penang",
                "area": "Penang",
                "imageUrl": "",
                "sourceUrl": href,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Food",
                "publishedAt": published,
            }
        )
        if len(items) >= 10:
            break
    return items


def parse_penangfoodie_home(text: str, source_name: str, source_id: str, page_url: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in FOODIE_LINK_RE.finditer(text):
        href, slug, inner = match.group(1), match.group(2), match.group(3)
        title = clean_text(inner)
        if is_junk_title(title) or title.lower().startswith("read more"):
            title = title_from_slug(slug)
        if is_junk_title(title):
            continue
        if any(part in slug.lower() for part in ("privacy", "tag/", "category/", "author/", "about")):
            continue
        if NOISE_FOOD.search(title):
            continue
        if href.rstrip("/") in seen or title.lower() in seen:
            continue
        if not (
            FOOD_HINTS.search(title)
            or REVIEW_HINTS.search(title)
            or OPENING_HINTS.search(title)
            or "penang" in title.lower()
        ):
            continue
        seen.add(href.rstrip("/"))
        seen.add(title.lower())
        kind = classify_food_kind(title, default_kind="revisit")
        items.append(
            {
                "id": slug_id(kind, title, None),
                "kind": kind,
                "title": title,
                "summary": "Penang Foodie roundup or review.",
                "detail": "",
                "startDate": None,
                "endDate": None,
                "dateLabel": "New opening · Penang" if kind == "food" else "Worth a revisit · Penang",
                "area": "Penang",
                "imageUrl": "",
                "sourceUrl": href,
                "sourceName": source_name,
                "sourceId": source_id,
                "category": "Food",
            }
        )
        if len(items) >= 10:
            break
    return items


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        title = item.get("title") or ""
        if is_junk_title(title):
            continue
        key = re.sub(r"[^a-z0-9]+", "", title.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def item_anchor_date(item: dict[str, Any]) -> dt.date | None:
    """Best available calendar date for freshness (startDate, then publishedAt)."""
    for key in ("startDate", "endDate"):
        value = item.get(key)
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                return dt.date.fromisoformat(value)
            except ValueError:
                pass
    published = item.get("publishedAt")
    if isinstance(published, str) and published.strip():
        raw = published.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            try:
                return dt.date.fromisoformat(raw)
            except ValueError:
                pass
        try:
            # RSS pubDate e.g. "Sat, 18 Jul 2026 15:45:25 +0000"
            parsed = dt.datetime.strptime(raw[:31], "%a, %d %b %Y %H:%M:%S")
            return parsed.date()
        except ValueError:
            pass
        match = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", raw)
        if match:
            day, month, year = match.groups()
            m = month_num(month)
            if m:
                return dt.date(int(year), m, int(day))
    # Last resort: dates mentioned in title/label (catches "Labour Day" season pieces).
    for key in ("dateLabel", "title", "summary"):
        start, _, _ = parse_dates_from_text(item.get(key) or "", utc_now().year)
        if start:
            try:
                return dt.date.fromisoformat(start)
            except ValueError:
                pass
    return None


def filter_stale_food_openings(
    items: list[dict[str, Any]], *, max_age_days: int = 62
) -> tuple[list[dict[str, Any]], int]:
    """Drop kind=food openings older than ~2 months. Revisits keep older reviews."""
    today = utc_now().date()
    cutoff = today - dt.timedelta(days=max_age_days)
    kept: list[dict[str, Any]] = []
    dropped = 0
    for item in items:
        if item.get("kind") != "food":
            kept.append(item)
            continue
        anchor = item_anchor_date(item)
        if anchor is not None and anchor < cutoff:
            dropped += 1
            continue
        kept.append(item)
    return kept, dropped


def filter_promo_noise(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Drop corporate/institutional PR that readers cannot act on this week."""
    kept: list[dict[str, Any]] = []
    dropped = 0
    for item in items:
        if PROMO_NOISE_RE.search(item_text_blob(item)):
            dropped += 1
            continue
        kept.append(item)
    return kept, dropped


def _iso_date(value: Any) -> dt.date | None:
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def is_past_event_recap(item: dict[str, Any]) -> bool:
    """True for after-the-fact event write-ups that should not appear as upcoming.

    Heuristic: past-tense cues ("was held", "last night", "drew crowds", …) and
    no future-facing language. Undated (Date TBA) recaps always drop; dated
    items drop only when the event window has already ended.
    """
    if item.get("kind") != "event":
        return False
    blob = item_text_blob(item)
    if not PAST_EVENT_RECAP_RE.search(blob):
        return False
    if FUTURE_EVENT_HINT_RE.search(blob):
        return False
    start = _iso_date(item.get("startDate"))
    end = _iso_date(item.get("endDate")) or start
    if start is None:
        return True
    today = utc_now().date()
    return end is not None and end < today


def filter_event_window(
    items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    """Drop ended dated items + past-tense event recaps; relabel ongoing shows.

    Returns (items, ended_dropped, recap_dropped).
    """
    today = utc_now().date()
    kept: list[dict[str, Any]] = []
    ended_dropped = 0
    recap_dropped = 0
    for item in items:
        if item.get("kind") == "food":
            food_end = _iso_date(item.get("endDate"))
            if food_end is not None and food_end < today:
                ended_dropped += 1
                continue
        if item.get("kind") != "event":
            kept.append(item)
            continue
        if is_past_event_recap(item):
            recap_dropped += 1
            continue
        start = _iso_date(item.get("startDate"))
        end = _iso_date(item.get("endDate")) or start
        if end is not None and end < today:
            ended_dropped += 1
            continue
        if start is not None and end is not None and start < today <= end:
            # Ongoing exhibition/run — prefer clear label over a wrong end fragment.
            until = _fmt_day_month(end.day, end.month)
            source_bit = ""
            label = item.get("dateLabel") or ""
            if "·" in label:
                source_bit = " ·" + label.split("·", 1)[1]
            elif label and not re.search(r"\d", label):
                source_bit = f" · {label}"
            item["dateLabel"] = f"Ongoing · until {until}{source_bit}"
        kept.append(item)
    return kept, ended_dropped, recap_dropped


def item_text_blob(item: dict[str, Any]) -> str:
    return " ".join(
        part
        for part in (
            item.get("title") or "",
            item.get("summary") or "",
            item.get("detail") or "",
            item.get("category") or "",
        )
        if part
    )


def classify_interests(blob: str) -> list[str]:
    """Topic tags from title/summary keywords (EN + common MS/ZH)."""
    topics: list[str] = []
    for topic, pattern, _boost in INTEREST_RULES:
        if pattern.search(blob) and topic not in topics:
            topics.append(topic)
    return topics


def industry_demote_level(blob: str, topics: list[str]) -> str:
    """Return 'hard', 'soft', or '' for industry/trade/B2B demotion."""
    if INDUSTRY_HARD_RE.search(blob):
        return "hard"
    if not (INDUSTRY_FORM_RE.search(blob) and INDUSTRY_CONTEXT_RE.search(blob)):
        return ""
    # Consumer fairs/festivals (travel fair, food fest, art expo) stay promoted.
    consumer_topics = {
        "festival",
        "fair",
        "food",
        "music",
        "culture",
        "family",
        "literary",
        "movies",
        "books",
        "gaming",
    }
    if set(topics) & consumer_topics and not re.search(
        r"\b(food|halal)\s+industry\b", blob, re.I
    ):
        return ""
    return "soft"


def score_event_item(item: dict[str, Any]) -> tuple[int, list[str], str]:
    """Score an event for Happening soon ranking. Higher = nearer the top."""
    blob = item_text_blob(item)
    topics = classify_interests(blob)
    demote = industry_demote_level(blob, topics)
    score = 40
    for topic, _pattern, boost in INTEREST_RULES:
        if topic in topics:
            score += boost
    if item.get("imageUrl"):
        score += 4
    if item.get("startDate"):
        score += 6
    if demote == "hard":
        score -= 90
    elif demote == "soft":
        score -= 45
    # Cap so boosts stay readable in draft inspection.
    score = max(0, min(score, 100))
    return score, topics, demote


def annotate_event_ranking(
    items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Add interest/topics + interestScore; drop hard industry trade shows."""
    kept: list[dict[str, Any]] = []
    dropped = 0
    for item in items:
        if item.get("kind") != "event":
            kept.append(item)
            continue
        score, topics, demote = score_event_item(item)
        if demote == "hard":
            dropped += 1
            continue
        item["topics"] = topics
        item["interest"] = topics[:]  # alias for clients/docs
        item["interestScore"] = score
        if demote:
            item["demote"] = demote
        kept.append(item)
    return kept, dropped


def format_week_label(run_date: str) -> str:
    """Human week label, e.g. 'Week of 19 Jul'."""
    try:
        day = dt.date.fromisoformat(run_date)
    except ValueError:
        return f"Week of {run_date}"
    return f"Week of {day.day} {day.strftime('%b')}"


def build_intro(items: list[dict[str, Any]]) -> str:
    """Short lede without repeating the week label."""
    events = sum(1 for i in items if i.get("kind") == "event")
    food = sum(1 for i in items if i.get("kind") == "food")
    revisits = sum(1 for i in items if i.get("kind") == "revisit")
    bits: list[str] = []
    if events:
        bits.append(f"{events} event{'s' if events != 1 else ''}")
    if food:
        bits.append(f"{food} food pick{'s' if food != 1 else ''}")
    if revisits:
        bits.append(f"{revisits} worth revisiting")
    if not bits:
        return "What’s on in Penang — events and new food this week."
    if len(bits) == 1:
        return f"{bits[0]}."
    if len(bits) == 2:
        return f"{bits[0]} and {bits[1]}."
    return f"{bits[0]}, {bits[1]}, and {bits[2]}."


def validate_feed(feed: dict[str, Any], sanity: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    items = feed.get("items") or []
    if len(items) < int(sanity.get("minTotalItems", 1)):
        errors.append(f"need >= {sanity['minTotalItems']} items, got {len(items)}")
    events = sum(1 for i in items if i.get("kind") == "event")
    foodish = sum(1 for i in items if i.get("kind") in {"food", "revisit"})
    if events < int(sanity.get("minEvents", 0)):
        errors.append(f"need >= {sanity['minEvents']} events, got {events}")
    if foodish < int(sanity.get("minFood", 0)):
        errors.append(f"need >= {sanity['minFood']} food/revisit items, got {foodish}")
    for item in items:
        if not item.get("title") or not item.get("id"):
            errors.append("item missing title/id")
            break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--date", help="Draft date folder.")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--force-publish", action="store_true")
    args = parser.parse_args()

    config = json.loads(pathlib.Path(args.config).read_text(encoding="utf-8"))
    draft_root = ROOT / config.get("draftRoot", "private/penang-pulse")
    draft_dir = draft_root / args.date if args.date else newest_draft_dir(draft_root)
    if not draft_dir or not (draft_dir / "fetch-manifest.json").is_file():
        print("No draft fetch-manifest found. Run fetch-penang-sources.py first.", file=sys.stderr)
        return 1

    manifest = load_manifest(draft_dir)
    source_config = {s["id"]: s for s in config.get("sources", [])}
    default_year = utc_now().year
    items: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    warnings: list[str] = []

    for entry in manifest.get("sources", []):
        source_id = entry["id"]
        meta = source_config.get(source_id, {})
        parser_name = entry.get("parser") or meta.get("parser")
        kind = entry.get("kind") or meta.get("kind") or "event"
        name = entry.get("name") or meta.get("name") or source_id
        text = read_source_text(draft_dir, entry) if entry.get("ok") else ""
        parsed: list[dict[str, Any]] = []
        if entry.get("ok") and text:
            if parser_name == "rss_items":
                parsed = parse_rss_items(
                    text,
                    kind=kind,
                    source_name=name,
                    source_id=source_id,
                    default_year=default_year,
                )
            elif parser_name == "hin_events_html":
                parsed = parse_hin_events(text, name, source_id, default_year)
            elif parser_name == "smartlocal_cafes_html":
                parsed = parse_smartlocal_cafes(text, name, source_id, entry.get("url") or meta.get("url", ""))
            elif parser_name == "gtf_html":
                parsed = parse_gtf(
                    text,
                    name,
                    source_id,
                    entry.get("url") or meta.get("url", ""),
                    default_year,
                )
            elif parser_name == "wordpress_home_html":
                parsed = parse_smartdory_home(text, name, source_id)
            elif parser_name == "mypenang_events_html":
                parsed = parse_mypenang_events(
                    text,
                    name,
                    source_id,
                    entry.get("url") or meta.get("url", ""),
                    default_year,
                )
            elif parser_name == "chinapress_category_html":
                parsed = parse_chinapress_category(
                    text,
                    name,
                    source_id,
                    entry.get("url") or meta.get("url", ""),
                    default_year,
                )
            elif parser_name == "penangfoodie_home_html":
                parsed = parse_penangfoodie_home(
                    text,
                    name,
                    source_id,
                    entry.get("url") or meta.get("url", ""),
                )
            else:
                warnings.append(f"unknown parser for {source_id}: {parser_name}")
        elif not entry.get("ok"):
            warnings.append(f"fetch failed for {source_id} (status={entry.get('status')})")

        items.extend(parsed)
        source_summaries.append(
            {
                "id": source_id,
                "name": name,
                "tier": entry.get("tier") or meta.get("tier"),
                "kind": kind,
                "url": entry.get("url") or meta.get("url"),
                "ok": bool(entry.get("ok")),
                "status": entry.get("status"),
                "bytes": entry.get("bytes"),
                "itemCount": len(parsed),
                "parser": parser_name,
            }
        )

    items = dedupe_items(items)
    items, promo_dropped = filter_promo_noise(items)
    if promo_dropped:
        warnings.append(f"dropped {promo_dropped} corporate/institutional PR item(s)")
        print(f"Dropped {promo_dropped} corporate/institutional PR item(s)")
    items, stale_food_dropped = filter_stale_food_openings(items, max_age_days=62)
    if stale_food_dropped:
        warnings.append(f"dropped {stale_food_dropped} food opening(s) older than ~2 months")
        print(f"Dropped {stale_food_dropped} stale food opening(s) (>~2 months)")
    items, ended_dropped, recap_dropped = filter_event_window(items)
    if recap_dropped:
        warnings.append(f"dropped {recap_dropped} past-tense event recap(s)")
        print(f"Dropped {recap_dropped} past-tense event recap(s)")
    if ended_dropped:
        warnings.append(f"dropped {ended_dropped} ended dated item(s) (endDate before today)")
        print(f"Dropped {ended_dropped} ended dated item(s)")
    user_agent = config.get(
        "userAgent",
        "PenangPulse/0.1 (+https://fb2.github.io/db-schedule-pwa/utilities/penang-pulse/)",
    )
    filled = enrich_missing_images(items, user_agent=user_agent)
    if filled:
        print(f"Enriched {filled} item image(s) from article og:image")
    items, industry_dropped = annotate_event_ranking(items)
    if industry_dropped:
        warnings.append(
            f"dropped {industry_dropped} industry/trade event(s) from consumer feed"
        )
        print(f"Dropped {industry_dropped} industry/trade event(s)")

    def sort_key(item: dict[str, Any]) -> tuple:
        start = item.get("startDate") or "9999-99-99"
        kind = item.get("kind") or "event"
        kind_rank = {"event": 0, "food": 1, "revisit": 2}.get(kind, 3)
        # Events: interest score desc, then soonest date, then title.
        score = int(item.get("interestScore") or 0)
        return (kind_rank, -score, start, item.get("title") or "")

    items.sort(key=sort_key)
    run_date = manifest.get("runDate") or draft_dir.name
    week_label = format_week_label(run_date)
    feed = {
        "schemaVersion": 1,
        "generatedAt": utc_now().isoformat(),
        "weekLabel": week_label,
        "intro": build_intro(items),
        "sources": source_summaries,
        "items": items,
        "warnings": warnings,
    }

    draft_path = draft_dir / "feed.draft.json"
    draft_path.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Draft: {draft_path} ({len(items)} items)")
    for warning in warnings:
        print(f"warning: {warning}")

    errors = validate_feed(feed, config.get("feedSanity") or {})
    public_path = ROOT / config.get("publicFeed", "utilities/penang-pulse/feed.json")
    if errors:
        print("Sanity check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        if args.publish and not args.force_publish:
            if public_path.is_file():
                print(f"Keeping previous public feed: {public_path}", file=sys.stderr)
            return 1

    if args.publish:
        if errors and not args.force_publish:
            return 1
        tmp_path = public_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp_path.replace(public_path)
        with_images = sum(1 for i in items if i.get("imageUrl"))
        print(f"Published {public_path} ({with_images}/{len(items)} with images)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

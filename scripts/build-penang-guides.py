#!/usr/bin/env python3
"""Build Penang Pulse editorial guides into static HTML + index.json.

Reads source posts under utilities/penang-pulse/guides/posts/<slug>/post.md
and the series registry guides/posts/_series.json, resizes media/orig images
to web JPEGs, and emits:

  utilities/penang-pulse/guides/index.json
  utilities/penang-pulse/guides/<slug>/index.html
  utilities/penang-pulse/guides/<slug>/media/*.jpg
  utilities/penang-pulse/guides/series/<series-slug>/index.html
  utilities/penang-pulse/guides/series/mee-myself-and-i/mee-search/index.html
    (when registry entry has "meeSearch": true)

Registered series get index pages even with 0–1 posts.

Requires Pillow. Optional pillow-heif for HEIC/HEIF originals.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import sys
import urllib.parse
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
PULSE_DIR = ROOT / "utilities" / "penang-pulse"
GUIDES_DIR = PULSE_DIR / "guides"
POSTS_DIR = GUIDES_DIR / "posts"
SERIES_REGISTRY = POSTS_DIR / "_series.json"
SERIES_DIR = GUIDES_DIR / "series"
ARTICLE_CSS = "article.css"
ARTICLE_CSS_VER = "23"  # bump when article.css layout changes (cache bust)
MARKS_DIR = GUIDES_DIR / "marks"
GRAPH_STATS = PULSE_DIR / "mee-graph" / "data" / "graph-stats.json"
MEE_SEARCH_SERIES = "mee-myself-and-i"
SITE_ORIGIN = "https://penangpulse.com"
SITE_NAME = "Penang Pulse"
SITE_AUTHOR = "Balazs Fejes"
OG_DEFAULT_PATH = "/og-default.jpg"
APPLE_TOUCH = "apple-touch-icon.png"
OG_DEFAULT_FILE = "og-default.jpg"


def copyright_year() -> int:
    """Calendar year for soft © chrome (build date)."""
    return dt.date.today().year


def author_byline(*, series_hub: bool = False) -> str:
    """Quiet authorship chrome — brand first, name as support."""
    if series_hub:
        return f"By {SITE_AUTHOR} · Field notes from Penang"
    return f"By {SITE_AUTHOR}"


def author_footer() -> str:
    return f"By {SITE_AUTHOR} · © {copyright_year()}"


def series_date_span(posts: list[dict[str, Any]]) -> str:
    """Compact month/year span from published post dates, e.g. Jul–Aug 2026."""
    dates: list[dt.date] = []
    for post in posts:
        raw = str(post.get("updated") or "").strip()
        if not raw:
            continue
        try:
            dates.append(dt.date.fromisoformat(raw[:10]))
        except ValueError:
            continue
    if not dates:
        return ""
    start, end = min(dates), max(dates)
    if start.year == end.year and start.month == end.month:
        return f"{start.strftime('%b')} {start.year}"
    if start.year == end.year:
        return f"{start.strftime('%b')}–{end.strftime('%b')} {start.year}"
    return f"{start.strftime('%b')} {start.year}–{end.strftime('%b')} {end.year}"


def series_meta_label(count: int, *, template: str) -> str:
    """Episode count phrase; Mee uses bowls, others use episodes."""
    if (template or "").strip().lower() == "mee":
        unit = "bowl" if count == 1 else "bowls"
    else:
        unit = "episode" if count == 1 else "episodes"
    return f"{count} {unit}"


_FIELDNOTE_DAY_RE = re.compile(
    r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b",
    re.I,
)
_FIELDNOTE_MON_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b",
    re.I,
)
_MONTH_NUM = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def parse_series_cal(post: dict[str, Any]) -> tuple[dt.date | None, bool]:
    """Return (date, month_only) for the series calendar chip."""
    for key in ("tasted", "updated"):
        raw = str(post.get(key) or "").strip()
        if not raw:
            continue
        try:
            return dt.date.fromisoformat(raw[:10]), False
        except ValueError:
            pass
    note = str(post.get("fieldNote") or "")
    day_m = _FIELDNOTE_DAY_RE.search(note)
    if day_m:
        mon = _MONTH_NUM.get(day_m.group(2).lower())
        if mon:
            try:
                return dt.date(int(day_m.group(3)), mon, int(day_m.group(1))), False
            except ValueError:
                pass
    mon_m = _FIELDNOTE_MON_RE.search(note)
    if mon_m:
        mon = _MONTH_NUM.get(mon_m.group(1).lower())
        if mon:
            try:
                return dt.date(int(mon_m.group(2)), mon, 1), True
            except ValueError:
                pass
    return None, False


def series_note_place(post: dict[str, Any]) -> str:
    """Neighbourhood line for the hub list (date lives on the calendar chip)."""
    place = str(post.get("neighbourhood") or "").strip()
    if place:
        return place
    note = str(post.get("fieldNote") or "").strip()
    if not note:
        return ""
    # "Field note · Pulau Tikus · 20 Jul 2026" → Pulau Tikus
    parts = [p.strip() for p in note.split("·")]
    if len(parts) >= 2:
        mid = parts[1]
        if mid and not _FIELDNOTE_MON_RE.search(mid) and not _FIELDNOTE_DAY_RE.search(mid):
            return mid
    cleaned = _FIELDNOTE_DAY_RE.sub("", note)
    cleaned = _FIELDNOTE_MON_RE.sub("", cleaned)
    cleaned = re.sub(r"\s*·\s*", " · ", cleaned).strip(" ·")
    return cleaned


def render_series_cal(when: dt.date | None, *, month_only: bool = False) -> str:
    """Quiet calendar square: month + day + year (month + year when day unknown)."""
    if when is None:
        return ""
    mon = when.strftime("%b")
    year = str(when.year)
    if month_only:
        label = when.strftime("%B %Y")
        iso = when.strftime("%Y-%m")
        cls = "series-cal series-cal--month"
        day_html = ""
    else:
        label = f"{when.day} {mon} {when.year}"
        iso = when.isoformat()
        cls = "series-cal"
        day_html = f'<span class="series-cal-day">{when.day}</span>'
    return (
        f'<time class="{cls}" datetime="{html.escape(iso, quote=True)}" '
        f'title="{html.escape(label)}">'
        f'<span class="series-cal-mon">{html.escape(mon)}</span>'
        f"{day_html}"
        f'<span class="series-cal-year">{html.escape(year)}</span>'
        f"</time>"
    )

MAX_WIDTH = 1400
JPEG_QUALITY = 82

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)
IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_MD_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
# Capture full basename (spaces allowed); rewrite_media_src strips the match.
ORIG_MEDIA_RE = re.compile(
    r"(?:\./)?media/orig/([^)\"']+)",
    re.I,
)
PLACE_PATH_RE = re.compile(r"/place/([^/@]+)", re.I)
COORDS_AT_RE = re.compile(r"@(-?\d+\.?\d*),\s*(-?\d+\.?\d*)")
COORDS_QUERY_RE = re.compile(r"^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp"}
HEIC_EXTS = {".heic", ".heif"}

TYPE_LABELS = {
    "text": "Text",
    "photo": "Photos",
    "photos": "Photos",
    "video": "Video",
    "series-mee": "Mee",
    "mee": "Mee",
}

NESTED_KEYS = {"location"}


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_pillow() -> Any:
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        die(
            "Pillow is required. Create a venv and install it, e.g.\n"
            "  python3 -m venv scripts/penang-guides-editor/.venv\n"
            "  scripts/penang-guides-editor/.venv/bin/pip install Pillow\n"
            "  scripts/penang-guides-editor/.venv/bin/python scripts/build-penang-guides.py"
        )
    return Image


def try_register_heif() -> bool:
    try:
        from pillow_heif import register_heif_opener  # type: ignore

        register_heif_opener()
        return True
    except ImportError:
        return False


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse simple YAML front matter, including one-level nested maps (location)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, Any] = {}
    current_nested: str | None = None
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indented = bool(re.match(r"^[ \t]+", raw_line))
        line = raw_line.strip()
        if indented and current_nested:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            nested = meta.setdefault(current_nested, {})
            if not isinstance(nested, dict):
                nested = {}
                meta[current_nested] = nested
            nested[key.strip().lower()] = value.strip().strip('"').strip("'")
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        if key in NESTED_KEYS and not value:
            current_nested = key
            meta[key] = {}
            continue
        current_nested = None
        meta[key] = value
    return meta, match.group(2).lstrip("\n")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "guide"


def type_label(raw: str) -> str:
    key = (raw or "text").strip().lower()
    return TYPE_LABELS.get(key, raw.strip().title() or "Text")


def location_from_meta(meta: dict[str, Any]) -> dict[str, str]:
    loc = meta.get("location")
    out: dict[str, str] = {
        "name": "",
        "mapsurl": "",
        "address": "",
        "lat": "",
        "lng": "",
    }
    if isinstance(loc, dict):
        out["name"] = str(loc.get("name") or "").strip()
        # Front matter lowercases mapsUrl → mapsurl
        out["mapsurl"] = str(
            loc.get("mapsurl") or loc.get("url") or ""
        ).strip()
        out["address"] = str(loc.get("address") or "").strip()
        out["lat"] = str(loc.get("lat") or "").strip()
        out["lng"] = str(loc.get("lng") or "").strip()
    # Flat aliases from editor / older posts
    if not out["name"]:
        out["name"] = str(meta.get("locationname") or meta.get("location_name") or "").strip()
    if not out["mapsurl"]:
        out["mapsurl"] = str(
            meta.get("mapsurl")
            or meta.get("maps_url")
            or meta.get("locationurl")
            or ""
        ).strip()
    if not out["address"]:
        out["address"] = str(meta.get("locationaddress") or meta.get("address") or "").strip()
    return out


def parse_maps_url(url: str) -> dict[str, str]:
    """Client-side-style parse of Google Maps URLs (no network / API keys).

    Short links (maps.app.goo.gl, goo.gl/maps) are kept as-is with no name/coords.
    Full google.com/maps URLs may yield place name and/or lat/lng.
    """
    result = {
        "mapsUrl": (url or "").strip(),
        "name": "",
        "lat": "",
        "lng": "",
        "address": "",
    }
    raw = result["mapsUrl"]
    if not raw:
        return result

    lower = raw.lower()
    if "maps.app.goo.gl" in lower or "goo.gl/maps" in lower:
        return result

    try:
        parsed = urllib.parse.urlparse(raw)
    except ValueError:
        return result

    host = (parsed.netloc or "").lower()
    if "google." not in host and not host.endswith("maps.google.com"):
        # Still store URL; only extract from known Google Maps hosts
        if "maps" not in lower:
            return result

    path = urllib.parse.unquote(parsed.path or "")
    place = PLACE_PATH_RE.search(path)
    if place:
        name = place.group(1).replace("+", " ").strip()
        name = re.sub(r"\s+", " ", name)
        if name and not COORDS_QUERY_RE.match(name.replace(" ", "")):
            result["name"] = name

    coords = COORDS_AT_RE.search(raw)
    if coords:
        result["lat"] = coords.group(1)
        result["lng"] = coords.group(2)

    qs = urllib.parse.parse_qs(parsed.query)
    for key in ("query", "q", "destination"):
        if key not in qs or not qs[key]:
            continue
        q = urllib.parse.unquote(qs[key][0]).strip()
        coord_m = COORDS_QUERY_RE.match(q)
        if coord_m:
            result["lat"] = result["lat"] or coord_m.group(1)
            result["lng"] = result["lng"] or coord_m.group(2)
        elif q and not result["name"]:
            result["name"] = q.replace("+", " ")
        break

    return result


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    text = LINK_MD_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" '
        f'rel="noopener noreferrer">{m.group(1)}</a>',
        text,
    )
    return text


def rewrite_media_src(src: str, media_map: dict[str, str]) -> str:
    src = src.strip()
    match = ORIG_MEDIA_RE.search(src)
    if match:
        name = match.group(1).strip()
        if name in media_map:
            return f"./media/{media_map[name]}"
        stem = pathlib.Path(name).stem
        return f"./media/{web_stem(name)}.jpg"
    if src.startswith("./media/") or src.startswith("media/"):
        name = pathlib.Path(src).name
        if name in media_map.values():
            return f"./media/{name}"
        stem = pathlib.Path(name).stem
        if f"{stem}.jpg" in media_map.values():
            return f"./media/{stem}.jpg"
    return src


def md_to_html(body: str, media_map: dict[str, str]) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        img = IMG_MD_RE.fullmatch(stripped)
        if img:
            alt = html.escape(img.group(1))
            src = html.escape(rewrite_media_src(img.group(2), media_map), quote=True)
            caption = ""
            # Allow a blank line between image and _caption_ (CMS-friendly).
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                cap = lines[j].strip()
                if len(cap) > 2 and cap.startswith("_") and cap.endswith("_"):
                    caption = inline_md(cap[1:-1])
                    i = j
            out.append('<figure class="photo-block">')
            out.append(
                f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async" '
                f'referrerpolicy="no-referrer" />'
            )
            if caption:
                out.append(f"<figcaption>{caption}</figcaption>")
            out.append("</figure>")
            i += 1
            continue

        if stripped.startswith("### "):
            out.append(f"<h3>{inline_md(stripped[4:])}</h3>")
            i += 1
            continue
        if stripped.startswith("## "):
            out.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            i += 1
            continue
        if stripped.startswith("# "):
            out.append(f"<h2>{inline_md(stripped[2:])}</h2>")
            i += 1
            continue

        if stripped in {"---", "***", "___"}:
            out.append('<p class="tip"></p>')
            i += 1
            continue

        if stripped.startswith(("- ", "* ")):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{inline_md(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>")
            out.extend(items)
            out.append("</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(f"<li>{inline_md(item_text)}</li>")
                i += 1
            out.append("<ol>")
            out.extend(items)
            out.append("</ol>")
            continue

        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith("#")
                or nxt.startswith(("- ", "* "))
                or re.match(r"^\d+\.\s+", nxt)
                or IMG_MD_RE.fullmatch(nxt)
                or nxt in {"---", "***", "___"}
            ):
                break
            para.append(nxt)
            i += 1
        joined = " ".join(para)
        if joined.startswith("> "):
            out.append(f'<p class="tip">{inline_md(joined[2:])}</p>')
        else:
            out.append(f"<p>{inline_md(joined)}</p>")

    return "\n".join(out)


def web_stem(filename: str) -> str:
    return slugify(pathlib.Path(filename).stem) or "image"


def process_images(
    post_dir: pathlib.Path,
    public_media: pathlib.Path,
    Image: Any,
    heif_ok: bool,
) -> dict[str, str]:
    """Return map of original basename -> web filename (e.g. lunch.jpg)."""
    orig_dir = post_dir / "media" / "orig"
    work_media = post_dir / "media"
    work_media.mkdir(parents=True, exist_ok=True)
    public_media.mkdir(parents=True, exist_ok=True)

    media_map: dict[str, str] = {}
    if not orig_dir.is_dir():
        return media_map

    for path in sorted(orig_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        ext = path.suffix.lower()
        if ext in HEIC_EXTS and not heif_ok:
            print(
                f"warning: skipping HEIC/HEIF (install pillow-heif): {path.relative_to(ROOT)}",
                file=sys.stderr,
            )
            continue
        if ext not in IMAGE_EXTS | HEIC_EXTS:
            print(f"warning: skipping unsupported media: {path.name}", file=sys.stderr)
            continue

        out_name = f"{web_stem(path.name)}.jpg"
        work_out = work_media / out_name
        public_out = public_media / out_name

        try:
            with Image.open(path) as img:
                img = img.convert("RGB") if img.mode not in ("RGB", "L") else img.convert("RGB")
                w, h = img.size
                if w > MAX_WIDTH:
                    new_h = max(1, round(h * (MAX_WIDTH / w)))
                    img = img.resize((MAX_WIDTH, new_h), Image.Resampling.LANCZOS)
                img.save(work_out, "JPEG", quality=JPEG_QUALITY, optimize=True)
        except Exception as exc:  # noqa: BLE001 — surface per-file failures
            print(f"warning: failed to process {path.name}: {exc}", file=sys.stderr)
            continue

        shutil.copy2(work_out, public_out)
        media_map[path.name] = out_name
        media_map[path.name.lower()] = out_name

    return media_map


def render_spot_widget(location: dict[str, str]) -> str:
    name = (location.get("name") or "").strip()
    maps_url = (location.get("mapsurl") or "").strip()
    address = (location.get("address") or "").strip()
    if not name and not maps_url:
        return ""

    name_html = html.escape(name) if name else "Location"
    address_html = (
        f'<p class="spot-address">{html.escape(address)}</p>' if address else ""
    )
    maps_html = ""
    if maps_url:
        maps_html = (
            f'<a class="spot-maps" href="{html.escape(maps_url, quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">Open in Google Maps</a>'
        )
    return (
        '<aside class="spot-widget">\n'
        '  <p class="spot-label">Spot</p>\n'
        f'  <p class="spot-name">{name_html}</p>\n'
        f"  {address_html}\n"
        f"  {maps_html}\n"
        "</aside>"
    )


def insert_spot_widget(body_html: str, spot_html: str) -> str:
    if not spot_html:
        return body_html
    if not body_html.strip():
        return spot_html
    idx = body_html.find("</p>")
    if idx != -1:
        return body_html[: idx + 4] + "\n" + spot_html + body_html[idx + 4 :]
    return spot_html + "\n" + body_html


def absolute_url(path: str) -> str:
    """Build a canonical absolute HTTPS URL for share previews."""
    if path.startswith("https://") or path.startswith("http://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{SITE_ORIGIN}{path}"


def ensure_share_assets(Image: Any) -> None:
    """Ensure raster share/home icons exist (WhatsApp needs JPEG/PNG, not SVG)."""
    apple = PULSE_DIR / APPLE_TOUCH
    og = PULSE_DIR / OG_DEFAULT_FILE
    if apple.is_file() and og.is_file():
        return

    try:
        from PIL import ImageDraw, ImageFont  # type: ignore
    except ImportError:
        die("Pillow ImageDraw required to generate share assets")

    if not apple.is_file():
        size = 180
        icon = Image.new("RGB", (size, size), "#0f6e6e")
        draw = ImageDraw.Draw(icon)
        cx = cy = size // 2
        r_outer = int(size * 34 / 128)
        r_inner = int(size * 12 / 128)
        sw = max(4, int(size * 8 / 128))
        cross = max(3, int(size * 6 / 128))
        draw.ellipse(
            [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
            outline="#fafaf8",
            width=sw,
        )
        draw.ellipse(
            [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
            fill="#fafaf8",
        )
        outer = int(size * 42 / 128)
        inner = int(size * 28 / 128)
        for x1, y1, x2, y2 in [
            (cx, cy - outer, cx, cy - inner),
            (cx, cy + inner, cx, cy + outer),
            (cx - outer, cy, cx - inner, cy),
            (cx + inner, cy, cx + outer, cy),
        ]:
            draw.line([(x1, y1), (x2, y2)], fill="#fafaf8", width=cross)
        icon.save(apple, "PNG", optimize=True)
        print(f"wrote {apple.relative_to(ROOT)}")

    if not og.is_file():
        w, h = 1200, 630
        canvas = Image.new("RGB", (w, h), "#0f6e6e")
        draw = ImageDraw.Draw(canvas)
        for i in range(h):
            t = i / h
            draw.line(
                [(0, i), (w, i)],
                fill=(int(15 + t * 8), int(110 + t * 12), int(110 + t * 8)),
            )
        cx, cy = w // 2, h // 2 - 40
        draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], outline="#fafaf8", width=14)
        draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill="#fafaf8")
        for x1, y1, x2, y2 in [
            (cx, cy - 110, cx, cy - 72),
            (cx, cy + 72, cx, cy + 110),
            (cx - 110, cy, cx - 72, cy),
            (cx + 72, cy, cx + 110, cy),
        ]:
            draw.line([(x1, y1), (x2, y2)], fill="#fafaf8", width=10)
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Supplemental/Georgia.ttf", 72
            )
            small = ImageFont.truetype(
                "/System/Library/Fonts/Supplemental/Georgia.ttf", 36
            )
        except OSError:
            font = ImageFont.load_default()
            small = font
        title = SITE_NAME
        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, cy + 130), title, fill="#fafaf8", font=font)
        sub = "Local guides & weekly happenings"
        bbox = draw.textbbox((0, 0), sub, font=small)
        sw_ = bbox[2] - bbox[0]
        draw.text(((w - sw_) // 2, cy + 210), sub, fill="#d7ebea", font=small)
        canvas.save(og, "JPEG", quality=88, optimize=True)
        print(f"wrote {og.relative_to(ROOT)}")


def social_head_tags(
    *,
    title: str,
    description: str,
    canonical_path: str,
    image_url: str,
    og_type: str = "article",
    icon_href: str,
    apple_touch_href: str,
) -> str:
    """Open Graph + Twitter Card tags for WhatsApp / Messenger share previews."""
    canon = absolute_url(canonical_path)
    desc = description or title
    img = absolute_url(image_url) if image_url else absolute_url(OG_DEFAULT_PATH)
    card = "summary_large_image"
    return f"""    <link rel="canonical" href="{html.escape(canon, quote=True)}" />
    <meta property="og:title" content="{html.escape(title)}" />
    <meta property="og:description" content="{html.escape(desc)}" />
    <meta property="og:url" content="{html.escape(canon, quote=True)}" />
    <meta property="og:type" content="{html.escape(og_type)}" />
    <meta property="og:site_name" content="{html.escape(SITE_NAME)}" />
    <meta property="og:image" content="{html.escape(img, quote=True)}" />
    <meta name="twitter:card" content="{card}" />
    <meta name="twitter:title" content="{html.escape(title)}" />
    <meta name="twitter:description" content="{html.escape(desc)}" />
    <meta name="twitter:image" content="{html.escape(img, quote=True)}" />
    <link rel="icon" href="{html.escape(icon_href, quote=True)}" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="{html.escape(apple_touch_href, quote=True)}" />"""


def cover_path_for_guide(slug: str, hero_src: str | None, media_map: dict[str, str]) -> str:
    """Site-absolute path to a raster cover image for OG previews."""
    if hero_src:
        name = pathlib.Path(hero_src).name
        if name:
            return f"/guides/{slug}/media/{name}"
    if media_map:
        first = next(iter(media_map.values()))
        return f"/guides/{slug}/media/{first}"
    return OG_DEFAULT_PATH


def render_article(
    *,
    title: str,
    dek: str,
    type_name: str,
    neighbourhood: str,
    field_note: str,
    series_slug: str,
    series_title: str,
    body_html: str,
    hero_src: str | None,
    series_mark: str = "",
    home_href: str = "../../",
    css_href: str = f"../{ARTICLE_CSS}?v={ARTICLE_CSS_VER}",
    icon_href: str = "../../icon.svg",
    apple_touch_href: str = "../../apple-touch-icon.png",
    canonical_path: str = "/",
    og_image: str = OG_DEFAULT_PATH,
) -> str:
    meta_bits = []
    if neighbourhood:
        meta_bits.append(f"Neighbourhood · {html.escape(neighbourhood)}")
    meta_html = (
        f'<p class="guide-meta">{meta_bits[0]}</p>' if meta_bits else ""
    )
    dek_html = f'<p class="guide-dek">{html.escape(dek)}</p>' if dek else ""
    field_html = (
        f'<p class="guide-field-note">{html.escape(field_note)}</p>'
        if field_note
        else ""
    )

    mark_html = series_mark_img(series_mark, prefix="../") if series_mark else ""

    series_html = ""
    if series_slug and series_title:
        series_href = f"../series/{html.escape(series_slug, quote=True)}/"
        series_html = (
            f'<p class="guide-series">'
            f"{mark_html}"
            f'<a href="{series_href}">{html.escape(series_title)}</a>'
            f"</p>"
        )
    elif series_title:
        series_html = (
            f'<p class="guide-series">{mark_html}'
            f"<span>{html.escape(series_title)}</span></p>"
        )

    hero_html = ""
    if hero_src:
        hero_html = (
            f'<img class="guide-hero" src="{html.escape(hero_src, quote=True)}" alt="" '
            f'loading="eager" decoding="async" referrerpolicy="no-referrer" />\n'
        )

    # Calm format-agnostic kicker; field note + series carry the voice.
    kicker = "Field guide"
    byline_html = f'<p class="guide-byline">{html.escape(author_byline())}</p>'
    footer_html = f'<p class="guide-footer">{html.escape(author_footer())}</p>'
    social = social_head_tags(
        title=f"{title} — {SITE_NAME}",
        description=dek or title,
        canonical_path=canonical_path,
        image_url=og_image,
        og_type="article",
        icon_href=icon_href,
        apple_touch_href=apple_touch_href,
    )
    author_meta = (
        f'    <meta property="article:author" content="{html.escape(SITE_AUTHOR)}" />'
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta name="description" content="{html.escape(dek or title)}" />
    <title>{html.escape(title)} — Penang Pulse</title>
{social}
{author_meta}
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="{html.escape(css_href, quote=True)}" />
  </head>
  <body>
    <div class="guide-topbar">
      <a class="back" href="{html.escape(home_href, quote=True)}">← Home</a>
      <a class="brand-mini" href="{html.escape(home_href, quote=True)}">Penang Pulse</a>
    </div>
{hero_html}
    <article class="guide-article">
      <p class="guide-kicker">{kicker}</p>
      {series_html}
      {field_html}
      <h1>{html.escape(title)}</h1>
      {dek_html}
      {byline_html}
      {meta_html}
      <div class="guide-body">
{body_html}
      </div>
      {footer_html}
    </article>
  </body>
</html>
"""


def load_mee_search_counts() -> dict[str, int]:
    """Literal counts for Mee-Search teaser/landing — kept in step with graph-stats.json."""
    defaults = {"dish": 75, "culture": 26, "region": 62, "sources": 137}
    if not GRAPH_STATS.is_file():
        print(f"warning: missing {GRAPH_STATS.relative_to(ROOT)}; using defaults", file=sys.stderr)
        return defaults
    try:
        data = json.loads(GRAPH_STATS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: could not read graph-stats: {exc}", file=sys.stderr)
        return defaults
    by_type = data.get("nodesByType") or {}
    return {
        "dish": int(by_type.get("dish", defaults["dish"])),
        "culture": int(by_type.get("culture", defaults["culture"])),
        "region": int(by_type.get("region", defaults["region"])),
        "sources": int(data.get("sources", defaults["sources"])),
    }


def render_mee_search_teaser(counts: dict[str, int]) -> str:
    """Series-hub intro strip linking into the Mee-Search landing."""
    return f"""      <a class="ms-teaser" href="./mee-search/">
        <img class="cmeepo-peek" src="../../marks/c-mee-po.svg" alt="" width="40" height="64" decoding="async" />
        <p class="ms-teaser-kicker">Research companion</p>
        <h2>Mee-Search</h2>
        <p class="ms-teaser-tag">Where Penang&apos;s noodles come from</p>
        <p class="ms-teaser-dek">The graph underneath the diary — communities, towns, and sources behind the bowls. Four ways in; start with Bowl Orbit.</p>
        <ul class="ms-teaser-counts">
          <li>{counts["dish"]} dishes</li>
          <li>{counts["culture"]} communities</li>
          <li>{counts["region"]} regions</li>
          <li>{counts["sources"]} sources</li>
        </ul>
        <span class="ms-teaser-more">Explore Mee-Search →</span>
      </a>"""


def render_mee_search_landing(
    *,
    series_title: str,
    og_image: str,
    counts: dict[str, int],
) -> str:
    """Port of mee-graph/viz/mee-search.html into series chrome; viz cards link to /mee-graph/viz/."""
    social = social_head_tags(
        title=f"Mee-Search — where Penang's noodles come from · {SITE_NAME}",
        description=(
            "Where Penang's noodles come from. "
            f"{counts['dish']} noodle dishes traced to the communities and towns that brought them, "
            "across four interactive views."
        ),
        canonical_path=f"/guides/series/{MEE_SEARCH_SERIES}/mee-search/",
        image_url=og_image,
        og_type="website",
        icon_href="../../../../icon.svg",
        apple_touch_href="../../../../apple-touch-icon.png",
    )
    viz = "../../../../mee-graph/viz"
    d = counts["dish"]
    c = counts["culture"]
    r = counts["region"]
    s = counts["sources"]
    series_href = "../"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta
      name="description"
      content="Where Penang's noodles come from. {d} noodle dishes traced to the communities and towns that brought them, across four interactive views."
    />
    <title>Mee-Search — where Penang's noodles come from · {html.escape(SITE_NAME)}</title>
{social}
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../{ARTICLE_CSS}?v={ARTICLE_CSS_VER}" />
  </head>
  <body>
    <div class="guide-topbar">
      <a class="back" href="{series_href}">← {html.escape(series_title)}</a>
      <a class="brand-mini" href="../../../../">Penang Pulse</a>
    </div>

    <main class="ms-wrap">
      <header class="ms-head">
        <h1>Mee-Search</h1>
        <p class="ms-tagline">Where Penang's noodles come from</p>
        <p class="ms-dek">
          Every noodle dish in Penang arrived from somewhere, carried by someone, and changed on
          the way. This is the graph underneath
          <a href="{series_href}">the diary</a> — four ways in.
        </p>
      </header>

      <div class="ms-counts">
        <div class="ms-count"><b data-count="dish">{d}</b><span>noodle dishes</span></div>
        <div class="ms-count"><b data-count="culture">{c}</b><span>communities</span></div>
        <div class="ms-count"><b data-count="region">{r}</b><span>towns and regions</span></div>
        <div class="ms-count"><b data-count="sources">{s}</b><span>cited sources</span></div>
      </div>
      <p class="ms-promise">
        Every connection traced to a source, and the shaky ones say so.
      </p>

      <div class="ms-grid">
        <a class="ms-card" href="{viz}/02-origin-drill.html">
          <span class="ms-thumb" data-ms-thumb="origin" aria-hidden="true"></span>
          <span class="ms-flag ms-flag--alpha">Alpha</span>
          <h2>Origin drill</h2>
          <p>
            “Chinese” covers a dozen different kitchens, and “Indian” covers several more. Drill
            through the rings and each one gets more specific — from a broad thread, to the
            community that carried it, to the town the recipe left: Zhangzhou, Dabu, Nagore.
          </p>
          <span class="ms-more">Start drilling</span>
        </a>

        <a class="ms-card ms-card--first" href="{viz}/04-bowl-orbit.html">
          <span class="ms-flag">Start here</span>
          <span class="ms-thumb" data-ms-thumb="orbit" aria-hidden="true"></span>
          <h2>Bowl orbit</h2>
          <p>
            One bowl, taken apart. The noodle, every ingredient, every technique — each coloured by
            the community that contributed it. Most bowls turn out to hold five or six kitchens at
            once.
          </p>
          <span class="ms-more">Open a bowl</span>
        </a>

        <a class="ms-card" href="{viz}/03-thread-flow.html">
          <span class="ms-thumb" data-ms-thumb="flow" aria-hidden="true"></span>
          <span class="ms-flag ms-flag--alpha">Alpha</span>
          <h2>Thread flow</h2>
          <p>
            Pick a kitchen or a noodle and follow it across the island. Some stayed put; yellow
            alkaline noodles ended up in nearly every stall, regardless of whose stall it was.
          </p>
          <span class="ms-more">Follow a thread</span>
        </a>

        <div class="ms-card ms-card--disabled" aria-disabled="true">
          <span class="ms-thumb" data-ms-thumb="timeline" aria-hidden="true"></span>
          <span class="ms-flag ms-flag--alpha">Coming later</span>
          <h2>Arrivals</h2>
          <p>
            When the kitchens got here — Hokkien, Hakka, Cantonese, Tamil Muslim, and the rest —
            mapped onto ports, migrations and ordinances.
          </p>
          <span class="ms-more">Not open yet</span>
        </div>
      </div>

      <p class="ms-foot">
        Drawn from census records, food writing, academic work on the Straits Chinese and the
        Hadhrami diaspora, and stallholders' own accounts. Where the record runs out, it says so:
        every dish carries a confidence level, and contested claims name what is disputed and by
        whom. Origin drill and Thread flow are early alphas — Bowl Orbit is the place to start.
      </p>
    </main>
    <script src="{viz}/d3.v7.min.js"></script>
    <script src="{viz}/graph-data.js"></script>
    <script src="{viz}/mee-viz.js"></script>
    <script src="{viz}/mee-search-thumbs.js"></script>
    <script>
      (async function () {{
        try {{
          const g = await MEE.load();
          MEE_THUMBS.mountLanding(document, g);
        }} catch (err) {{
          console.warn("Mee-Search thumbs:", err);
        }}
      }})();
    </script>
  </body>
</html>
"""


def series_mark_img(mark: str, *, prefix: str) -> str:
    """Return <img> for a guides/marks filename, or empty if missing/unsafe."""
    name = pathlib.Path(str(mark or "").strip()).name
    if not name or name != mark.strip() or not name.endswith(".svg"):
        return ""
    if not (MARKS_DIR / name).is_file():
        return ""
    src = f"{prefix}marks/{html.escape(name, quote=True)}"
    return (
        f'<img class="series-mark" src="{src}" alt="" width="52" height="52" '
        f'decoding="async" />'
    )


def render_series_index(
    *,
    series_slug: str,
    series_title: str,
    series_dek: str,
    posts: list[dict[str, Any]],
    series_mark: str = "",
    series_intro: str = "",
    series_template: str = "",
    og_image: str = OG_DEFAULT_PATH,
    mee_search: bool = False,
) -> str:
    items = []
    for post in posts:
        href = f"../../{html.escape(post['slug'], quote=True)}/"
        when, month_only = parse_series_cal(post)
        cal_html = render_series_cal(when, month_only=month_only)
        place = series_note_place(post)
        note_html = f'<span class="series-note">{html.escape(place)}</span>' if place else ""
        items.append(
            "<li>"
            f'<a href="{href}">'
            f"{cal_html}"
            f'<span class="series-list-copy">'
            f'<span class="g-title">{html.escape(post["title"])}</span>'
            f"{note_html}"
            f"</span>"
            f"</a>"
            "</li>"
        )
    list_html = (
        "\n".join(items)
        if items
        else '<li class="muted">No episodes yet — check back after the next field note.</li>'
    )
    list_heading = "Field notes" if posts else "Episodes"
    dek = series_dek or f"Episodes in {series_title}."
    mark_html = series_mark_img(series_mark, prefix="../../")
    if mark_html:
        heading_html = (
            f'<div class="series-mast">\n'
            f"        {mark_html}\n"
            f'        <div class="series-mast-stack">\n'
            f"          <h1>{html.escape(series_title)}</h1>\n"
            f"        </div>\n"
            f"      </div>"
        )
    else:
        heading_html = f"<h1>{html.escape(series_title)}</h1>"
    # Dek lives in the lead row so it can sit beside Mee-Search on wide hubs.
    dek_html = f'<p class="guide-dek">{html.escape(dek)}</p>'
    byline_html = (
        f'<p class="guide-byline">{html.escape(author_byline(series_hub=True))}</p>'
    )
    intro_html = (
        f'\n      <p class="series-intro">{html.escape(series_intro)}</p>'
        if series_intro
        else ""
    )
    count_label = series_meta_label(len(posts), template=series_template)
    span = series_date_span(posts)
    meta_text = f"{count_label} · {span}" if span else count_label
    meta_strip_html = f'<p class="series-meta-strip">{html.escape(meta_text)}</p>'
    teaser_html = (
        "\n" + render_mee_search_teaser(load_mee_search_counts())
        if mee_search
        else ""
    )
    peek_html = (
        """
          <div class="cmeepo-rail" aria-hidden="true">
            <span class="cmeepo-rail-line"></span>
          </div>"""
        if mee_search
        else ""
    )
    footer_html = f'<p class="guide-footer">{html.escape(author_footer())}</p>'
    social = social_head_tags(
        title=f"{series_title} — {SITE_NAME}",
        description=dek,
        canonical_path=f"/guides/series/{series_slug}/",
        image_url=og_image,
        og_type="website",
        icon_href="../../../icon.svg",
        apple_touch_href="../../../apple-touch-icon.png",
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta name="description" content="{html.escape(dek)}" />
    <title>{html.escape(series_title)} — Penang Pulse</title>
{social}
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../{ARTICLE_CSS}?v={ARTICLE_CSS_VER}" />
  </head>
  <body>
    <div class="guide-topbar">
      <a class="back" href="../../../">← Home</a>
      <a class="brand-mini" href="../../../">Penang Pulse</a>
    </div>
    <article class="guide-article guide-article--hub">
      <div class="series-hub-top">
        <div class="series-hub-mast">
      {heading_html}
        </div>
        <div class="series-hub-lead">
          <div class="series-hub-copy">
      {dek_html}
      {byline_html}{intro_html}
      {meta_strip_html}
          </div>{peek_html}
{teaser_html}
        </div>
      </div>
      <h2 class="series-list-label">{html.escape(list_heading)}</h2>
      <ul class="series-list series-list--hub">
{list_html}
      </ul>
      {footer_html}
    </article>
  </body>
</html>
"""


def load_series_registry(path: pathlib.Path = SERIES_REGISTRY) -> list[dict[str, Any]]:
    """Load known series from guides/posts/_series.json (empty list if missing)."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: could not read series registry: {exc}", file=sys.stderr)
        return []
    raw = data.get("series") if isinstance(data, dict) else data
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or "").strip()
        if not slug:
            continue
        entry: dict[str, Any] = {
            "slug": slug,
            "title": str(item.get("title") or slug.replace("-", " ").title()).strip(),
            "dek": str(item.get("dek") or "").strip(),
            "status": str(item.get("status") or "active").strip() or "active",
            "defaultType": str(item.get("defaultType") or item.get("default_type") or "text").strip(),
            "template": str(item.get("template") or "blank").strip() or "blank",
        }
        intro = str(item.get("intro") or "").strip()
        if intro:
            entry["intro"] = intro
        mark = str(item.get("mark") or item.get("icon") or "").strip()
        if mark:
            entry["mark"] = pathlib.Path(mark).name
        if item.get("meeSearch") is True or str(item.get("meeSearch") or "").strip().lower() in {
            "1",
            "true",
            "yes",
        }:
            entry["meeSearch"] = True
        out.append(entry)
    return out


def collect_posts(posts_dir: pathlib.Path) -> list[pathlib.Path]:
    if not posts_dir.is_dir():
        return []
    posts = []
    for path in sorted(posts_dir.iterdir()):
        if path.is_dir() and (path / "post.md").is_file():
            posts.append(path)
    return posts


def build_one(
    post_dir: pathlib.Path,
    Image: Any,
    heif_ok: bool,
    series_marks: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    slug = post_dir.name
    text = (post_dir / "post.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    if meta.get("draft", "").lower() in {"1", "true", "yes"}:
        print(f"skip draft: {slug}")
        return None

    title = meta.get("title") or slug.replace("-", " ").title()
    dek = meta.get("dek") or meta.get("description") or ""
    type_raw = str(meta.get("type") or "text")
    type_name = type_label(type_raw)
    neighbourhood = meta.get("neighbourhood") or meta.get("area") or ""
    field_note = str(meta.get("fieldnote") or meta.get("field_note") or "").strip()
    updated = meta.get("updated") or meta.get("date") or dt.date.today().isoformat()
    tasted = str(meta.get("tasted") or "").strip()
    hero = meta.get("hero") or ""
    # cover / ogImage: share preview only — does not render the in-page 16:9 hero banner
    cover = meta.get("cover") or meta.get("ogimage") or meta.get("og_image") or ""

    series_slug = str(meta.get("series") or "").strip()
    series_title = str(meta.get("seriestitle") or meta.get("series_title") or "").strip()
    series_order_raw = str(meta.get("seriesorder") or meta.get("series_order") or "").strip()
    series_order: int | None = None
    if series_order_raw.isdigit():
        series_order = int(series_order_raw)
    if series_slug and not series_title:
        series_title = series_slug.replace("-", " ").title()
    series_mark = ""
    if series_slug and series_marks:
        series_mark = series_marks.get(series_slug) or ""

    location = location_from_meta(meta)
    # Fill name/coords from maps URL when present and fields empty
    if location["mapsurl"]:
        parsed = parse_maps_url(location["mapsurl"])
        if not location["name"] and parsed["name"]:
            location["name"] = parsed["name"]
        if not location["lat"] and parsed["lat"]:
            location["lat"] = parsed["lat"]
        if not location["lng"] and parsed["lng"]:
            location["lng"] = parsed["lng"]

    public_dir = GUIDES_DIR / slug
    public_media = public_dir / "media"
    if public_dir.exists():
        shutil.rmtree(public_dir)
    public_dir.mkdir(parents=True)

    media_map = process_images(post_dir, public_media, Image, heif_ok)
    body_html = md_to_html(body, media_map)
    spot_html = render_spot_widget(location)
    body_html = insert_spot_widget(body_html, spot_html)

    hero_src = None
    if hero:
        hero_src = rewrite_media_src(hero, media_map)
    elif type_name == "Photos" and media_map:
        first = next(iter(media_map.values()))
        hero_src = f"./media/{first}"

    cover_src = rewrite_media_src(cover, media_map) if cover else None
    og_image = cover_path_for_guide(slug, cover_src or hero_src, media_map)
    # Prefer first web photo for OG even when there is no in-page hero / cover
    if og_image == OG_DEFAULT_PATH and media_map:
        og_image = cover_path_for_guide(slug, None, media_map)

    html_out = render_article(
        title=title,
        dek=dek,
        type_name=type_name,
        neighbourhood=neighbourhood,
        field_note=field_note,
        series_slug=series_slug,
        series_title=series_title,
        body_html=body_html,
        hero_src=hero_src,
        series_mark=series_mark,
        canonical_path=f"/guides/{slug}/",
        og_image=og_image,
    )
    (public_dir / "index.html").write_text(html_out, encoding="utf-8")

    if public_media.is_dir() and not any(public_media.iterdir()):
        public_media.rmdir()

    entry: dict[str, Any] = {
        "slug": slug,
        "title": title,
        "dek": dek,
        "type": type_name,
        "href": f"./guides/{slug}/",
        "updated": updated,
        "cover": og_image,
    }
    if field_note:
        entry["fieldNote"] = field_note
    if tasted:
        entry["tasted"] = tasted
    if neighbourhood:
        entry["neighbourhood"] = neighbourhood
    if series_slug:
        entry["series"] = series_slug
        entry["seriesTitle"] = series_title
        entry["seriesHref"] = f"./guides/series/{series_slug}/"
        if series_order is not None:
            entry["seriesOrder"] = series_order
    if location["name"] or location["mapsurl"]:
        entry["location"] = {
            k: v
            for k, v in {
                "name": location["name"],
                "mapsUrl": location["mapsurl"],
                "address": location["address"],
                "lat": location["lat"],
                "lng": location["lng"],
            }.items()
            if v
        }
    return entry


def ensure_article_css() -> None:
    css_path = GUIDES_DIR / ARTICLE_CSS
    if not css_path.is_file():
        die(f"missing {css_path.relative_to(ROOT)} — commit guides/{ARTICLE_CSS}")


def clean_stale_public(active_slugs: set[str], active_series: set[str]) -> None:
    if not GUIDES_DIR.is_dir():
        return
    reserved = {"posts", "series", "marks", ARTICLE_CSS, "index.json"}
    for path in GUIDES_DIR.iterdir():
        if not path.is_dir():
            continue
        if path.name in reserved or path.name in active_slugs:
            continue
        if path.name.startswith("."):
            continue
        shutil.rmtree(path)
        print(f"removed stale guide output: {path.name}")

    if SERIES_DIR.is_dir():
        for path in list(SERIES_DIR.iterdir()):
            if not path.is_dir():
                continue
            if path.name in active_series:
                continue
            shutil.rmtree(path)
            print(f"removed stale series output: {path.name}")
        if not active_series and SERIES_DIR.is_dir():
            # Keep empty series dir only if we have no series; remove orphans above
            if not any(SERIES_DIR.iterdir()):
                SERIES_DIR.rmdir()


def build_series_pages(
    guides: list[dict[str, Any]],
    registry: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Emit series index pages from registry + posts (0–N episodes OK)."""
    registry = registry if registry is not None else load_series_registry()
    by_series: dict[str, list[dict[str, Any]]] = {}
    titles: dict[str, str] = {}
    deks: dict[str, str] = {}
    intros: dict[str, str] = {}
    templates: dict[str, str] = {}
    statuses: dict[str, str] = {}
    marks: dict[str, str] = {}
    mee_search_flags: dict[str, bool] = {}

    for entry in registry:
        slug = entry["slug"]
        by_series.setdefault(slug, [])
        titles[slug] = entry["title"]
        deks[slug] = entry.get("dek") or ""
        intros[slug] = entry.get("intro") or ""
        templates[slug] = entry.get("template") or ""
        statuses[slug] = entry.get("status") or "active"
        mee_search_flags[slug] = bool(entry.get("meeSearch"))
        if entry.get("mark"):
            marks[slug] = str(entry["mark"])

    for guide in guides:
        series = guide.get("series")
        if not series:
            continue
        by_series.setdefault(series, []).append(guide)
        # Post title wins only when series is not in the registry
        if series not in titles:
            titles[series] = guide.get("seriesTitle") or series.replace("-", " ").title()
        elif guide.get("seriesTitle") and not deks.get(series):
            # Keep registry title; ignore post override for registered series
            pass
        statuses.setdefault(series, "active")

    series_index: list[dict[str, Any]] = []
    if SERIES_DIR.exists():
        shutil.rmtree(SERIES_DIR)

    for series_slug in sorted(by_series.keys(), key=lambda s: titles.get(s, s).lower()):
        posts = by_series[series_slug]
        posts_sorted = sorted(
            posts,
            key=lambda g: (
                g.get("seriesOrder") is None,
                g.get("seriesOrder") if g.get("seriesOrder") is not None else 0,
                g.get("updated") or "",
            ),
        )
        series_title = titles.get(series_slug) or series_slug.replace("-", " ").title()
        series_dek = deks.get(series_slug) or ""
        series_intro = intros.get(series_slug) or ""
        series_template = templates.get(series_slug) or ""
        series_mark = marks.get(series_slug) or ""
        mee_search = bool(mee_search_flags.get(series_slug))
        og_image = OG_DEFAULT_PATH
        for post in posts_sorted:
            cover = str(post.get("cover") or "").strip()
            if cover and cover != OG_DEFAULT_PATH:
                og_image = cover
                break
        out_dir = SERIES_DIR / series_slug
        out_dir.mkdir(parents=True)
        html_out = render_series_index(
            series_slug=series_slug,
            series_title=series_title,
            series_dek=series_dek,
            posts=posts_sorted,
            series_mark=series_mark,
            series_intro=series_intro,
            series_template=series_template,
            og_image=og_image,
            mee_search=mee_search,
        )
        (out_dir / "index.html").write_text(html_out, encoding="utf-8")
        if mee_search:
            landing_dir = out_dir / "mee-search"
            landing_dir.mkdir(parents=True, exist_ok=True)
            landing = render_mee_search_landing(
                series_title=series_title,
                og_image=og_image,
                counts=load_mee_search_counts(),
            )
            (landing_dir / "index.html").write_text(landing, encoding="utf-8")
            print(f"built series/{series_slug}/mee-search")
        entry: dict[str, Any] = {
            "slug": series_slug,
            "title": series_title,
            "href": f"./guides/series/{series_slug}/",
            "count": len(posts_sorted),
            "status": statuses.get(series_slug) or "active",
            "cover": og_image,
        }
        if series_dek:
            entry["dek"] = series_dek
        if series_intro:
            entry["intro"] = series_intro
        if series_mark:
            entry["mark"] = f"./guides/marks/{series_mark}"
        if mee_search:
            entry["meeSearch"] = True
            entry["meeSearchHref"] = f"./guides/series/{series_slug}/mee-search/"
        series_index.append(entry)
        print(f"built series/{series_slug} ({len(posts_sorted)} post(s))")

    return series_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--posts",
        type=pathlib.Path,
        default=POSTS_DIR,
        help="Posts directory (default: utilities/penang-pulse/guides/posts)",
    )
    args = parser.parse_args()
    posts_dir = args.posts.resolve()

    Image = require_pillow()
    heif_ok = try_register_heif()
    if not heif_ok:
        print("note: pillow-heif not installed; HEIC/HEIF originals will be skipped")

    GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    ensure_article_css()
    ensure_share_assets(Image)

    registry = load_series_registry(
        posts_dir / "_series.json" if posts_dir != POSTS_DIR else SERIES_REGISTRY
    )
    series_marks = {
        e["slug"]: str(e["mark"])
        for e in registry
        if e.get("mark")
    }
    posts = collect_posts(posts_dir)

    guides: list[dict[str, Any]] = []
    if not posts:
        print(f"no posts found under {posts_dir.relative_to(ROOT)}")
    else:
        for post_dir in posts:
            entry = build_one(post_dir, Image, heif_ok, series_marks)
            if entry:
                guides.append(entry)
                print(f"built {entry['slug']}")

    guides.sort(key=lambda g: g.get("updated") or "", reverse=True)
    series_list = build_series_pages(guides, registry)
    clean_stale_public(
        {g["slug"] for g in guides},
        {s["slug"] for s in series_list},
    )

    index = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "guides": guides,
        "series": series_list,
    }
    (GUIDES_DIR / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {len(guides)} guide(s), {len(series_list)} series → "
        f"{GUIDES_DIR.relative_to(ROOT)}/index.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

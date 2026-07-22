#!/usr/bin/env python3
"""Build Penang Pulse editorial guides into static HTML + index.json.

Reads source posts under utilities/penang-pulse/guides/posts/<slug>/post.md
and the series registry guides/posts/_series.json, resizes media/orig images
to web JPEGs, and emits:

  utilities/penang-pulse/guides/index.json
  utilities/penang-pulse/guides/<slug>/index.html
  utilities/penang-pulse/guides/<slug>/media/*.jpg
  utilities/penang-pulse/guides/series/<series-slug>/index.html

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
GUIDES_DIR = ROOT / "utilities" / "penang-pulse" / "guides"
POSTS_DIR = GUIDES_DIR / "posts"
SERIES_REGISTRY = POSTS_DIR / "_series.json"
SERIES_DIR = GUIDES_DIR / "series"
ARTICLE_CSS = "article.css"
ARTICLE_CSS_VER = "2"  # bump when article.css layout changes (cache bust)

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
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("_") and lines[i + 1].strip().endswith("_"):
                caption = inline_md(lines[i + 1].strip()[1:-1])
                i += 1
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
    home_href: str = "../../",
    css_href: str = f"../{ARTICLE_CSS}?v={ARTICLE_CSS_VER}",
    icon_href: str = "../../icon.svg",
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

    series_html = ""
    if series_slug and series_title:
        series_href = f"../series/{html.escape(series_slug, quote=True)}/"
        series_html = (
            f'<p class="guide-series">'
            f'<a href="{series_href}">{html.escape(series_title)}</a>'
            f"</p>"
        )
    elif series_title:
        series_html = f'<p class="guide-series"><span>{html.escape(series_title)}</span></p>'

    hero_html = ""
    if hero_src:
        hero_html = (
            f'<img class="guide-hero" src="{html.escape(hero_src, quote=True)}" alt="" '
            f'loading="eager" decoding="async" referrerpolicy="no-referrer" />\n'
        )

    # Calm format-agnostic kicker; field note + series carry the voice.
    kicker = "Field guide"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta name="description" content="{html.escape(dek or title)}" />
    <title>{html.escape(title)} — Penang Pulse</title>
    <link rel="icon" href="{html.escape(icon_href, quote=True)}" type="image/svg+xml" />
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
      {meta_html}
      <div class="guide-body">
{body_html}
      </div>
    </article>
  </body>
</html>
"""


def render_series_index(
    *,
    series_slug: str,
    series_title: str,
    series_dek: str,
    posts: list[dict[str, Any]],
) -> str:
    items = []
    for post in posts:
        href = f"../../{html.escape(post['slug'], quote=True)}/"
        note = html.escape(post.get("fieldNote") or "")
        note_html = f'<span class="series-note">{note}</span>' if note else ""
        items.append(
            "<li>"
            f'<a href="{href}">'
            f'<span class="g-title">{html.escape(post["title"])}</span>'
            f'<span class="g-type">Field guide</span>'
            f"</a>"
            f"{note_html}"
            "</li>"
        )
    list_html = (
        "\n".join(items)
        if items
        else '<li class="muted">No episodes yet — check back after the next field note.</li>'
    )
    dek = series_dek or f"Episodes in {series_title}."
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta name="description" content="{html.escape(dek)}" />
    <title>{html.escape(series_title)} — Penang Pulse</title>
    <link rel="icon" href="../../../icon.svg" type="image/svg+xml" />
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
    <article class="guide-article">
      <p class="guide-kicker">Series</p>
      <h1>{html.escape(series_title)}</h1>
      <p class="guide-dek">{html.escape(dek)}</p>
      <ul class="series-list">
{list_html}
      </ul>
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
        out.append(
            {
                "slug": slug,
                "title": str(item.get("title") or slug.replace("-", " ").title()).strip(),
                "dek": str(item.get("dek") or "").strip(),
                "status": str(item.get("status") or "active").strip() or "active",
                "defaultType": str(item.get("defaultType") or item.get("default_type") or "text").strip(),
                "template": str(item.get("template") or "blank").strip() or "blank",
            }
        )
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
    hero = meta.get("hero") or ""

    series_slug = str(meta.get("series") or "").strip()
    series_title = str(meta.get("seriestitle") or meta.get("series_title") or "").strip()
    series_order_raw = str(meta.get("seriesorder") or meta.get("series_order") or "").strip()
    series_order: int | None = None
    if series_order_raw.isdigit():
        series_order = int(series_order_raw)
    if series_slug and not series_title:
        series_title = series_slug.replace("-", " ").title()

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
    }
    if field_note:
        entry["fieldNote"] = field_note
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
    reserved = {"posts", "series", ARTICLE_CSS, "index.json"}
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
    statuses: dict[str, str] = {}

    for entry in registry:
        slug = entry["slug"]
        by_series.setdefault(slug, [])
        titles[slug] = entry["title"]
        deks[slug] = entry.get("dek") or ""
        statuses[slug] = entry.get("status") or "active"

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
        out_dir = SERIES_DIR / series_slug
        out_dir.mkdir(parents=True)
        html_out = render_series_index(
            series_slug=series_slug,
            series_title=series_title,
            series_dek=series_dek,
            posts=posts_sorted,
        )
        (out_dir / "index.html").write_text(html_out, encoding="utf-8")
        entry: dict[str, Any] = {
            "slug": series_slug,
            "title": series_title,
            "href": f"./guides/series/{series_slug}/",
            "count": len(posts_sorted),
            "status": statuses.get(series_slug) or "active",
        }
        if series_dek:
            entry["dek"] = series_dek
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

    registry = load_series_registry(
        posts_dir / "_series.json" if posts_dir != POSTS_DIR else SERIES_REGISTRY
    )
    posts = collect_posts(posts_dir)

    guides: list[dict[str, Any]] = []
    if not posts:
        print(f"no posts found under {posts_dir.relative_to(ROOT)}")
    else:
        for post_dir in posts:
            entry = build_one(post_dir, Image, heif_ok)
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

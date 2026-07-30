#!/usr/bin/env python3
"""Local-only Penang Pulse guides editor (not deployed).

Series-aware mini CMS: dashboard → series detail → episode editor.

Run from repo root or this folder:

  python3 scripts/penang-guides-editor/server.py

Then open http://127.0.0.1:8765/
"""

from __future__ import annotations

import datetime as dt
import email
import email.policy
import html
import json
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[2]
EDITOR_DIR = pathlib.Path(__file__).resolve().parent
GUIDES_DIR = ROOT / "utilities" / "penang-pulse" / "guides"
POSTS_DIR = GUIDES_DIR / "posts"
SERIES_REGISTRY = POSTS_DIR / "_series.json"
BUILD_SCRIPT = ROOT / "scripts" / "build-penang-guides.py"
VENV_PYTHON = EDITOR_DIR / ".venv" / "bin" / "python"
HOST = "127.0.0.1"
PORT = 8765

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)
PLACE_PATH_RE = re.compile(r"/place/([^/@]+)", re.I)
COORDS_AT_RE = re.compile(r"@(-?\d+\.?\d*),\s*(-?\d+\.?\d*)")
COORDS_QUERY_RE = re.compile(r"^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$")

NESTED_KEYS = {"location"}

GIT_AUTHOR_NAME = "Balazs Fejes"
GIT_AUTHOR_EMAIL = "fbalazs@gmail.com"
LIVE_HOST = "https://penangpulse.com"

MONTH_NAMES = {
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
FIELD_NOTE_DAY_RE = re.compile(
    r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b",
    re.I,
)
FIELD_NOTE_MONTH_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b",
    re.I,
)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Canonical filename role → editorial sort rank (seller/hawker first, then dish/bowl, author, other)
PHOTO_ROLE_RANK = {
    "seller": 0,
    "hawker": 0,
    "bowl": 1,
    "dish": 1,
    "author": 2,
}
PHOTO_ROLE_ALT = {
    "seller": "Hawker",
    "hawker": "Hawker",
    "bowl": "Bowl",
    "dish": "Dish",
    "author": "Author",
}
PHOTO_ROLE_CANONICAL = {
    "seller": "seller",
    "hawker": "seller",
    "bowl": "bowl",
    "dish": "bowl",
    "author": "author",
}


def python_for_build() -> str:
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "guide"


def safe_upload_name(filename: str) -> str:
    """Basename with spaces/odd chars collapsed so markdown media links stay reliable."""
    raw = pathlib.Path(filename).name
    if not raw or raw.startswith("."):
        return ""
    stem = slugify(pathlib.Path(raw).stem) or "image"
    ext = pathlib.Path(raw).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".heic", ".heif"}:
        ext = ".jpg"
    return f"{stem}{ext}"


def is_valid_slug(value: str) -> bool:
    return bool(value) and bool(SLUG_RE.match(value))


def remove_public_slug(slug: str) -> None:
    """Remove built guides/<slug>/ if present (posts/ is source of truth)."""
    public = GUIDES_DIR / slug
    if public.is_dir() and public.resolve().parent == GUIDES_DIR.resolve():
        shutil.rmtree(public)


def rename_post(old_slug: str, new_slug: str) -> str | None:
    """Move posts/<old>/ → posts/<new>/. Returns error message or None on success."""
    if not is_valid_slug(old_slug) or not is_valid_slug(new_slug):
        return "Slug must be lowercase kebab-case (a-z, 0-9, hyphens)."
    if old_slug == new_slug:
        return None
    old_dir = POSTS_DIR / old_slug
    new_dir = POSTS_DIR / new_slug
    if not old_dir.is_dir() or not (old_dir / "post.md").is_file():
        return f"Unknown episode: {old_slug}"
    if new_dir.exists():
        return f"Slug already exists: {new_slug}"
    old_dir.rename(new_dir)
    remove_public_slug(old_slug)
    return None


def delete_post(slug: str) -> str | None:
    """Remove posts/<slug>/ folder. Returns error message or None on success."""
    if not is_valid_slug(slug):
        return "Invalid slug."
    post_dir = POSTS_DIR / slug
    if not post_dir.is_dir() or not (post_dir / "post.md").is_file():
        return f"Unknown episode: {slug}"
    shutil.rmtree(post_dir)
    remove_public_slug(slug)
    return None


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
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


def parse_maps_url(url: str) -> dict[str, str]:
    """Parse Google Maps URL string only (no network, no API keys)."""
    result = {
        "mapsUrl": (url or "").strip(),
        "name": "",
        "lat": "",
        "lng": "",
        "address": "",
        "shortLink": False,
        "hint": "",
    }
    raw = result["mapsUrl"]
    if not raw:
        return result

    lower = raw.lower()
    if "maps.app.goo.gl" in lower or "goo.gl/maps" in lower:
        result["shortLink"] = True
        result["hint"] = "Short link kept as-is — fill the venue name manually."
        return result

    try:
        parsed = urllib.parse.urlparse(raw)
    except ValueError:
        result["hint"] = "Could not parse URL."
        return result

    host = (parsed.netloc or "").lower()
    if host and "google." not in host and "maps.google." not in host:
        if "maps" not in lower:
            result["hint"] = "Not a recognised Google Maps URL — stored as-is."
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

    if result["name"] or result["lat"]:
        bits = []
        if result["name"]:
            bits.append(f"name “{result['name']}”")
        if result["lat"] and result["lng"]:
            bits.append(f"coords {result['lat']},{result['lng']}")
        result["hint"] = "Parsed " + ", ".join(bits) + "."
    else:
        result["hint"] = "URL stored — no place name/coords found in the string."
    return result


def yaml_quote(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if any(c in value for c in (":", "#", '"', "'", "\n")) or value != value.strip():
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def is_draft_value(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def parse_iso_date(value: str) -> dt.date | None:
    raw = (value or "").strip()
    if not ISO_DATE_RE.match(raw):
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        return None


def format_field_note_date(day: dt.date) -> str:
    return f"{day.day} {day.strftime('%b %Y')}"


def build_field_note(neighbourhood: str, tasted: dt.date | None) -> str:
    if tasted:
        date_part = format_field_note_date(tasted)
    else:
        date_part = dt.date.today().strftime("%b %Y")
    neighbourhood = (neighbourhood or "").strip()
    if neighbourhood:
        return f"Field note · {neighbourhood} · {date_part}"
    return f"Field note · {date_part}"


def parse_tasted_from_field_note(field_note: str) -> str:
    """Infer YYYY-MM-DD from fieldNote. Day+month preferred; month-only → day 1."""
    note = field_note or ""
    day_m = FIELD_NOTE_DAY_RE.search(note)
    if day_m:
        day = int(day_m.group(1))
        month = MONTH_NAMES[day_m.group(2).lower()[:3]]
        year = int(day_m.group(3))
        try:
            return dt.date(year, month, day).isoformat()
        except ValueError:
            pass
    month_m = FIELD_NOTE_MONTH_RE.search(note)
    if month_m:
        month = MONTH_NAMES[month_m.group(1).lower()[:3]]
        year = int(month_m.group(2))
        try:
            return dt.date(year, month, 1).isoformat()
        except ValueError:
            pass
    return ""


def infer_tasted(fields: dict[str, str]) -> str:
    """Prefer tasted → day-precise fieldNote → updated → month-only fieldNote."""
    tasted = (fields.get("tasted") or "").strip()
    if parse_iso_date(tasted):
        return tasted
    note = fields.get("fieldNote") or ""
    day_m = FIELD_NOTE_DAY_RE.search(note)
    if day_m:
        inferred = parse_tasted_from_field_note(note)
        if inferred:
            return inferred
    updated = (fields.get("updated") or "").strip()
    if parse_iso_date(updated):
        return updated
    return parse_tasted_from_field_note(note)


def apply_tasting_fields(fields: dict[str, str]) -> None:
    """Sync tasted / fieldNote / updated from the tasting date control."""
    tasted_raw = (fields.get("tasted") or "").strip()
    tasted_date = parse_iso_date(tasted_raw)
    if not tasted_date:
        inferred = infer_tasted(fields)
        tasted_date = parse_iso_date(inferred)
        if tasted_date:
            fields["tasted"] = tasted_date.isoformat()
    else:
        fields["tasted"] = tasted_date.isoformat()
    if tasted_date:
        fields["updated"] = tasted_date.isoformat()
        fields["fieldNote"] = build_field_note(
            fields.get("neighbourhood", ""), tasted_date
        )
    elif not (fields.get("fieldNote") or "").strip():
        fields["fieldNote"] = build_field_note(fields.get("neighbourhood", ""), None)
    if not (fields.get("updated") or "").strip():
        fields["updated"] = dt.date.today().isoformat()


def write_post_fields(slug: str, fields: dict[str, str], body: str) -> None:
    post_dir = POSTS_DIR / slug
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / "post.md").write_text(
        compose_post_md(fields, body),
        encoding="utf-8",
    )


def recompute_series_orders(series_slug: str) -> list[str]:
    """Dense seriesOrder by tasting date ASC for all episodes in series.

    Same-day tie-break: existing seriesOrder, then slug.
    Returns slugs that were rewritten.
    """
    series_slug = (series_slug or "").strip()
    if not series_slug or not POSTS_DIR.is_dir():
        return []

    episodes: list[dict[str, Any]] = []
    for path in sorted(POSTS_DIR.iterdir()):
        post = path / "post.md"
        if not (path.is_dir() and post.is_file()):
            continue
        text = post.read_text(encoding="utf-8")
        fields, body = fields_from_post(text)
        if (fields.get("series") or "").strip() != series_slug:
            continue
        tasted = infer_tasted(fields)
        if tasted and not (fields.get("tasted") or "").strip():
            fields["tasted"] = tasted
        order_raw = (fields.get("seriesOrder") or "").strip()
        order = int(order_raw) if order_raw.isdigit() else 10**9
        episodes.append(
            {
                "slug": path.name,
                "fields": fields,
                "body": body,
                "tasted": tasted or "9999-99-99",
                "order": order,
            }
        )

    episodes.sort(key=lambda e: (e["tasted"], e["order"], e["slug"]))
    changed: list[str] = []
    for idx, ep in enumerate(episodes, start=1):
        fields = ep["fields"]
        new_order = str(idx)
        prev_order = (fields.get("seriesOrder") or "").strip()
        prev_tasted = (fields.get("tasted") or "").strip()
        fields["seriesOrder"] = new_order
        if not prev_tasted and ep["tasted"] != "9999-99-99":
            fields["tasted"] = ep["tasted"]
        if prev_order != new_order or prev_tasted != (fields.get("tasted") or "").strip():
            write_post_fields(ep["slug"], fields, ep["body"])
            changed.append(ep["slug"])
    return changed


def media_role_filename(slug: str, role: str, other_label: str, ext: str) -> str:
    role = (role or "other").strip().lower()
    if role == "other":
        label = slugify(other_label) or "photo"
        stem = f"{slug}-{label}"
    else:
        canon = PHOTO_ROLE_CANONICAL.get(role, slugify(role) or "photo")
        stem = f"{slug}-{canon}"
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".heic", ".heif"}:
        ext = ".jpeg"
    return f"{stem}{ext}"


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif"}


def list_orig_images(slug: str) -> list[pathlib.Path]:
    """Sorted image files under posts/<slug>/media/orig/."""
    if not is_valid_slug(slug):
        return []
    orig = POSTS_DIR / slug / "media" / "orig"
    if not orig.is_dir():
        return []
    files: list[pathlib.Path] = []
    for path in sorted(orig.iterdir()):
        if (
            path.is_file()
            and not path.name.startswith(".")
            and path.suffix.lower() in IMAGE_SUFFIXES
        ):
            files.append(path)
    return files


def resolve_orig_media(slug: str, filename: str) -> pathlib.Path | None:
    """Safe resolve of a basename under posts/<slug>/media/orig/."""
    if not is_valid_slug(slug) or not filename or "/" in filename or "\\" in filename:
        return None
    if filename.startswith(".") or filename != pathlib.Path(filename).name:
        return None
    path = (POSTS_DIR / slug / "media" / "orig" / filename).resolve()
    root = (POSTS_DIR / slug / "media" / "orig").resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def cover_picker_html(slug: str, current_cover: str) -> str:
    """Radio grid to pick og:image cover from uploaded originals."""
    current = (current_cover or "").strip()
    files = list_orig_images(slug)
    matched_links = {f"./media/orig/{path.name}" for path in files}
    current_matched = current in matched_links or any(
        current.endswith("/" + path.name) for path in files
    )
    none_checked = " checked" if not current or not current_matched else ""
    cards = [
        f"""
        <label class="cover-card">
          <input type="radio" name="cover" value=""{none_checked} />
          <span class="cover-thumb cover-none">Default</span>
          <span class="cover-name">Alphabetical first</span>
        </label>
        """
    ]
    for path in files:
        link = f"./media/orig/{path.name}"
        checked = (
            " checked"
            if current_matched and (current == link or current.endswith("/" + path.name))
            else ""
        )
        thumb = (
            f"/media-orig?slug={urllib.parse.quote(slug)}"
            f"&file={urllib.parse.quote(path.name)}"
        )
        role = "photo"
        stem = path.stem.lower()
        if stem.endswith("-seller") or "-seller-" in stem:
            role = "seller"
        elif stem.endswith("-bowl") or "-bowl-" in stem:
            role = "bowl"
        elif stem.endswith("-author") or "-author-" in stem:
            role = "author"
        cards.append(
            f"""
        <label class="cover-card">
          <input type="radio" name="cover" value="{html.escape(link, quote=True)}"{checked} />
          <img class="cover-thumb" src="{html.escape(thumb, quote=True)}" alt="" loading="lazy" />
          <span class="cover-name"><code>{html.escape(path.name)}</code>
          <span class="cover-role">{html.escape(role)}</span></span>
        </label>
        """
        )
    if not files:
        return (
            '<p class="muted">No originals yet — upload photos first, then pick a share image.</p>'
            f'<input type="hidden" name="cover" value="{html.escape(current, quote=True)}" />'
        )
    return (
        '<div class="cover-picker" role="radiogroup" aria-label="Share / OG image">'
        + "".join(cards)
        + "</div>"
    )


def unique_media_path(orig_dir: pathlib.Path, name: str) -> pathlib.Path:
    dest = orig_dir / name
    if not dest.exists():
        return dest
    stem = pathlib.Path(name).stem
    suffix = pathlib.Path(name).suffix
    n = 2
    while dest.exists():
        dest = orig_dir / f"{stem}-{n}{suffix}"
        n += 1
    return dest


def append_photos_markdown(
    body: str,
    additions: list[tuple[str, str, str]],
) -> str:
    """Append photo blocks into ## Photos (or end). Skip if path already in body.

    additions: list of (filename, role, alt) in desired editorial order.
    """
    if not additions:
        return body
    body = body.replace("\r\n", "\n")
    blocks: list[str] = []
    for filename, role, alt in additions:
        link = f"./media/orig/{filename}"
        if link in body:
            continue
        alt_text = alt or PHOTO_ROLE_ALT.get(role, "Photo")
        blocks.append(f"![{alt_text}]({link})\n\n_Caption._\n")
    if not blocks:
        return body

    insert = "\n".join(blocks)
    photos_re = re.compile(r"(^## Photos[^\n]*\n)", re.M)
    match = photos_re.search(body)
    if match:
        # Insert after heading, before next ## heading or EOF — append at end of section
        start = match.end()
        next_h = re.search(r"^## ", body[start:], re.M)
        end = start + next_h.start() if next_h else len(body)
        section = body[start:end]
        # Trim trailing whitespace in section; keep one blank line before insert
        section_core = section.rstrip()
        spacer = "\n\n" if section_core else "\n"
        new_section = section_core + spacer + insert
        if not new_section.endswith("\n"):
            new_section += "\n"
        if next_h and not new_section.endswith("\n\n"):
            new_section += "\n"
        return body[:start] + new_section + body[end:]

    # No Photos section — append one
    body = body.rstrip() + "\n\n## Photos\n\n" + insert
    if not body.endswith("\n"):
        body += "\n"
    return body


def run_subprocess(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> tuple[int, str]:
    merged = {**os.environ, **(env or {})}
    # Avoid hangs when a tool prompts on a TTY while stdout/stderr are captured.
    merged.setdefault("CI", "1")
    merged.setdefault("npm_config_yes", "true")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
            env=merged,
            timeout=timeout,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        return 124, (out or "") + "\n(timeout)"
    except OSError as exc:
        return 1, str(exc)


def firebase_cmd() -> list[str]:
    """Prefer a local firebase binary over npx (avoids npm-exec install hangs)."""
    local = shutil.which("firebase")
    if local:
        return [local]
    return ["npx", "--yes", "firebase-tools"]


def publish_paths_for_slug(slug: str, series_slug: str, touched_slugs: list[str]) -> list[str]:
    """Relative paths under repo root to stage for a guide publish."""
    paths: list[str] = []
    slugs = {slug, *touched_slugs}
    for s in sorted(slugs):
        if not is_valid_slug(s):
            continue
        paths.append(f"utilities/penang-pulse/guides/posts/{s}")
        built = GUIDES_DIR / s
        if built.is_dir():
            paths.append(f"utilities/penang-pulse/guides/{s}")
    paths.append("utilities/penang-pulse/guides/index.json")
    if series_slug and is_valid_slug(series_slug):
        series_dir = GUIDES_DIR / "series" / series_slug
        if series_dir.is_dir():
            paths.append(f"utilities/penang-pulse/guides/series/{series_slug}")
    # Also stage any other series indexes that exist (cheap; avoids stale siblings)
    series_root = GUIDES_DIR / "series"
    if series_root.is_dir():
        for path in series_root.iterdir():
            if path.is_dir():
                rel = f"utilities/penang-pulse/guides/series/{path.name}"
                if rel not in paths:
                    paths.append(rel)
    return paths


def compose_post_md(fields: dict[str, str], body: str) -> str:
    """Compose post.md from structured editor fields + markdown body."""
    title = fields.get("title", "").strip() or "Untitled"
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"dek: {yaml_quote(fields.get('dek', '').strip())}",
        f"type: {yaml_quote(fields.get('type', 'text').strip() or 'text')}",
    ]
    if is_draft_value(fields.get("draft", "")):
        lines.append("draft: true")
    neighbourhood = fields.get("neighbourhood", "").strip()
    if neighbourhood:
        lines.append(f"neighbourhood: {yaml_quote(neighbourhood)}")
    tasted = fields.get("tasted", "").strip()
    if tasted:
        lines.append(f"tasted: {yaml_quote(tasted)}")
    field_note = fields.get("fieldNote", "").strip()
    if field_note:
        lines.append(f"fieldNote: {yaml_quote(field_note)}")
    updated = fields.get("updated", "").strip() or dt.date.today().isoformat()
    lines.append(f"updated: {yaml_quote(updated)}")

    series = fields.get("series", "").strip()
    series_title = fields.get("seriesTitle", "").strip()
    series_order = fields.get("seriesOrder", "").strip()
    if series:
        lines.append(f"series: {yaml_quote(series)}")
    if series_title:
        lines.append(f"seriesTitle: {yaml_quote(series_title)}")
    if series_order:
        lines.append(f"seriesOrder: {yaml_quote(series_order)}")

    loc_name = fields.get("locationName", "").strip()
    maps_url = fields.get("mapsUrl", "").strip()
    loc_address = fields.get("locationAddress", "").strip()
    loc_lat = fields.get("locationLat", "").strip()
    loc_lng = fields.get("locationLng", "").strip()
    if loc_name or maps_url or loc_address or loc_lat or loc_lng:
        lines.append("location:")
        if loc_name:
            lines.append(f"  name: {yaml_quote(loc_name)}")
        if maps_url:
            lines.append(f"  mapsUrl: {yaml_quote(maps_url)}")
        if loc_address:
            lines.append(f"  address: {yaml_quote(loc_address)}")
        if loc_lat:
            lines.append(f"  lat: {yaml_quote(loc_lat)}")
        if loc_lng:
            lines.append(f"  lng: {yaml_quote(loc_lng)}")

    cover = fields.get("cover", "").strip()
    if cover:
        lines.append(f"cover: {yaml_quote(cover)}")
    hero = fields.get("hero", "").strip()
    if hero:
        lines.append(f"hero: {yaml_quote(hero)}")

    lines.append("---")
    lines.append("")
    body = body.replace("\r\n", "\n").lstrip("\n")
    if body and not body.endswith("\n"):
        body += "\n"
    return "\n".join(lines) + "\n" + body


def fields_from_post(text: str) -> tuple[dict[str, str], str]:
    meta, body = parse_frontmatter(text)
    loc = meta.get("location") if isinstance(meta.get("location"), dict) else {}
    draft_raw = str(meta.get("draft") or meta.get("status") or "")
    fields = {
        "title": str(meta.get("title") or ""),
        "dek": str(meta.get("dek") or meta.get("description") or ""),
        "type": str(meta.get("type") or "text"),
        "draft": "true" if is_draft_value(draft_raw) or draft_raw.lower() == "draft" else "",
        "neighbourhood": str(meta.get("neighbourhood") or meta.get("area") or ""),
        "tasted": str(meta.get("tasted") or ""),
        "fieldNote": str(meta.get("fieldnote") or meta.get("field_note") or ""),
        "updated": str(meta.get("updated") or meta.get("date") or ""),
        "series": str(meta.get("series") or ""),
        "seriesTitle": str(meta.get("seriestitle") or meta.get("series_title") or ""),
        "seriesOrder": str(meta.get("seriesorder") or meta.get("series_order") or ""),
        "locationName": str(loc.get("name") or meta.get("locationname") or ""),
        "mapsUrl": str(loc.get("mapsurl") or meta.get("mapsurl") or ""),
        "locationAddress": str(loc.get("address") or ""),
        "locationLat": str(loc.get("lat") or ""),
        "locationLng": str(loc.get("lng") or ""),
        "cover": str(meta.get("cover") or meta.get("ogimage") or meta.get("og_image") or ""),
        "hero": str(meta.get("hero") or ""),
    }
    if not fields["tasted"]:
        fields["tasted"] = infer_tasted(fields)
    return fields, body


def load_series_registry() -> list[dict[str, Any]]:
    if not SERIES_REGISTRY.is_file():
        return []
    try:
        data = json.loads(SERIES_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
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
                "defaultType": str(
                    item.get("defaultType") or item.get("default_type") or "text"
                ).strip(),
                "template": str(item.get("template") or "blank").strip() or "blank",
            }
        )
    return out


def series_by_slug(slug: str) -> dict[str, Any] | None:
    for entry in load_series_registry():
        if entry["slug"] == slug:
            return entry
    return None


def list_posts_detailed() -> list[dict[str, Any]]:
    if not POSTS_DIR.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(POSTS_DIR.iterdir()):
        post = path / "post.md"
        if not (path.is_dir() and post.is_file()):
            continue
        text = post.read_text(encoding="utf-8")
        fields, _ = fields_from_post(text)
        order_raw = fields.get("seriesOrder") or ""
        order: int | None = int(order_raw) if order_raw.isdigit() else None
        items.append(
            {
                "slug": path.name,
                "title": fields.get("title") or path.name,
                "series": fields.get("series") or "",
                "seriesTitle": fields.get("seriesTitle") or "",
                "seriesOrder": order,
                "tasted": fields.get("tasted") or "",
                "fieldNote": fields.get("fieldNote") or "",
                "updated": fields.get("updated") or "",
                "type": fields.get("type") or "text",
                "draft": is_draft_value(fields.get("draft", "")),
                "dek": fields.get("dek") or "",
            }
        )
    return items


def episodes_for_series(series_slug: str) -> list[dict[str, Any]]:
    eps = [p for p in list_posts_detailed() if p.get("series") == series_slug]
    eps.sort(
        key=lambda p: (
            p.get("seriesOrder") is None,
            p.get("seriesOrder") if p.get("seriesOrder") is not None else 0,
            p.get("tasted") or p.get("updated") or "",
            p.get("slug") or "",
        )
    )
    return eps


def next_series_order(series_slug: str) -> str:
    """Hint only — real order is recomputed from tasting dates on save."""
    orders = [
        p["seriesOrder"]
        for p in episodes_for_series(series_slug)
        if isinstance(p.get("seriesOrder"), int)
    ]
    if not orders:
        return "1"
    return str(max(orders) + 1)


def default_post_fields(
    title: str,
    template: str = "blank",
    series_entry: dict[str, Any] | None = None,
    tasted: str = "",
) -> tuple[dict[str, str], str]:
    today = dt.date.today().isoformat()
    tasted_date = parse_iso_date(tasted) or dt.date.today()
    tasted_iso = tasted_date.isoformat()

    series_slug = ""
    series_title = ""
    series_order = ""
    type_val = "text"
    if series_entry:
        series_slug = series_entry["slug"]
        series_title = series_entry["title"]
        series_order = next_series_order(series_slug)
        type_val = series_entry.get("defaultType") or "text"
        if not template or template == "blank":
            template = series_entry.get("template") or "blank"

    if template == "mee" or (series_entry and series_entry.get("template") == "mee"):
        fields = {
            "title": title,
            "dek": "",
            "type": type_val or "series-mee",
            "neighbourhood": "",
            "tasted": tasted_iso,
            "fieldNote": build_field_note("", tasted_date),
            "updated": tasted_iso,
            "series": series_slug or "mee-myself-and-i",
            "seriesTitle": series_title or "Mee Myself and I",
            "seriesOrder": series_order or next_series_order(series_slug or "mee-myself-and-i"),
            "locationName": "",
            "mapsUrl": "",
            "locationAddress": "",
            "locationLat": "",
            "locationLng": "",
            "cover": "",
            "hero": "",
        }
        body = (
            "Intro paragraph — why this bowl, where you were coming from.\n\n"
            "## Tasting notes\n\n"
            "- **Broth** — \n"
            "- **Noodles** — \n"
            "- **Toppings** — \n"
            "- **Timing / queue** — \n\n"
            "## Photos\n\n"
            "> Optional tip or caveat.\n"
        )
        return fields, body

    if template == "family" or (series_entry and series_entry.get("template") == "family"):
        fields = {
            "title": title,
            "dek": "",
            "type": type_val or "text",
            "neighbourhood": "",
            "tasted": tasted_iso,
            "fieldNote": build_field_note("", tasted_date),
            "updated": tasted_iso,
            "series": series_slug or "family-matters",
            "seriesTitle": series_title or "Family Matters",
            "seriesOrder": series_order or next_series_order(series_slug or "family-matters"),
            "locationName": "",
            "mapsUrl": "",
            "locationAddress": "",
            "locationLat": "",
            "locationLng": "",
            "cover": "",
            "hero": "",
        }
        body = (
            "Why this outing works for a family evening or weekend — ages, energy, rain plan.\n\n"
            "## What we did\n\n"
            "- \n\n"
            "## Logistics\n\n"
            "- **When** — \n"
            "- **Where / parking** — \n"
            "- **Food nearby** — \n"
            "- **Kid friction** — \n\n"
            "## Photos\n\n"
            "> Tip or caveat.\n"
        )
        return fields, body

    fields = {
        "title": title,
        "dek": "",
        "type": type_val or "text",
        "neighbourhood": "",
        "tasted": tasted_iso if (series_slug or tasted) else "",
        "fieldNote": (
            build_field_note("", tasted_date) if (series_slug or tasted) else ""
        ),
        "updated": tasted_iso if (series_slug or tasted) else today,
        "series": series_slug,
        "seriesTitle": series_title,
        "seriesOrder": series_order,
        "locationName": "",
        "mapsUrl": "",
        "locationAddress": "",
        "locationLat": "",
        "locationLng": "",
        "cover": "",
        "hero": "",
    }
    body = (
        "Write the guide here. Use `##` headings and lists.\n\n"
        "Images: upload below with a role (seller / bowl / author); "
        "they land as `./media/orig/{slug}-{role}.jpeg` under ## Photos.\n"
    )
    return fields, body


def parse_multipart(
    content_type: str, body: bytes
) -> tuple[dict[str, str], list[tuple[str, bytes]], dict[str, list[str]]]:
    """Return (fields, files, multi) where files are (filename, data) tuples.

    `multi` keeps all values for repeated field names (e.g. media_role).
    """
    msg = email.message_from_bytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body,
        policy=email.policy.default,
    )
    fields: dict[str, str] = {}
    multi: dict[str, list[str]] = {}
    files: list[tuple[str, bytes]] = []
    if not msg.is_multipart():
        return fields, files, multi
    for part in msg.iter_parts():
        disposition = part.get_content_disposition()
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if disposition == "attachment" or filename:
            if filename:
                files.append((filename, payload))
            continue
        value = payload.decode("utf-8", errors="replace")
        fields[name] = value
        multi.setdefault(name, []).append(value)
    return fields, files, multi


SLUGIFY_JS = r"""
  function slugify(value) {
    return (value || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "guide";
  }
  function isValidSlug(value) {
    return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value || "");
  }
"""

NEW_PAGE_JS = (
    "(function () {\n"
    + SLUGIFY_JS
    + r"""
  const titleInput = document.getElementById("title");
  const slugInput = document.getElementById("slug");
  const preview = document.getElementById("slugPreview");
  const previewWarn = document.getElementById("slugPreviewWarn");
  let slugTouched = false;

  function updateSlugPreview() {
    const derived = slugify(titleInput ? titleInput.value : "");
    if (slugInput && !slugTouched) {
      slugInput.value = derived;
    }
    const slug = (slugInput && slugInput.value.trim()) || derived || "…";
    if (preview) {
      preview.textContent = "guides/posts/" + slug + "/ → live /guides/" + slug + "/";
    }
    if (previewWarn) {
      const ok = !slug || isValidSlug(slug);
      previewWarn.hidden = ok;
      previewWarn.textContent = ok
        ? ""
        : "Slug must be lowercase kebab-case (a-z, 0-9, hyphens).";
    }
  }

  if (titleInput) {
    titleInput.addEventListener("input", updateSlugPreview);
  }
  if (slugInput) {
    slugInput.addEventListener("input", function () {
      slugTouched = slugInput.value.trim().length > 0;
      updateSlugPreview();
    });
  }
  updateSlugPreview();
})();
"""
)

BUSY_JS = r"""
(function () {
  const overlay = document.getElementById("busyOverlay");
  const titleEl = document.getElementById("busyTitle");
  const detailEl = document.getElementById("busyDetail");
  const stepsEl = document.getElementById("busySteps");
  if (!overlay) return;

  function showBusy(opts) {
    const title = (opts && opts.title) || "Working…";
    const detail = (opts && opts.detail) || "Please leave this tab open.";
    const steps = (opts && opts.steps) || [];
    if (titleEl) titleEl.textContent = title;
    if (detailEl) detailEl.textContent = detail;
    if (stepsEl) {
      stepsEl.innerHTML = "";
      if (steps.length) {
        steps.forEach(function (s) {
          const li = document.createElement("li");
          li.textContent = s;
          stepsEl.appendChild(li);
        });
        stepsEl.hidden = false;
      } else {
        stepsEl.hidden = true;
      }
    }
    overlay.hidden = false;
    overlay.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  window.__penangShowBusy = showBusy;

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (!form.hasAttribute("data-busy")) return;
    if (event.defaultPrevented) return;

    const confirmMsg = form.getAttribute("data-busy-confirm");
    if (confirmMsg && !window.confirm(confirmMsg)) {
      event.preventDefault();
      return;
    }

    const stepsAttr = form.getAttribute("data-busy-steps") || "";
    const steps = stepsAttr
      ? stepsAttr.split("|").map(function (s) { return s.trim(); }).filter(Boolean)
      : [];
    showBusy({
      title: form.getAttribute("data-busy-title") || "Working…",
      detail: form.getAttribute("data-busy-detail") || "Please leave this tab open.",
      steps: steps,
    });
  }, true);
})();
"""

EDITOR_JS = (
    "(function () {\n"
    + SLUGIFY_JS
    + r"""
  const mapsInput = document.getElementById("mapsUrl");
  const nameInput = document.getElementById("locationName");
  const latInput = document.getElementById("locationLat");
  const lngInput = document.getElementById("locationLng");
  const addressInput = document.getElementById("locationAddress");
  const hint = document.getElementById("mapsHint");
  const spotName = document.getElementById("spotPreviewName");
  const spotAddr = document.getElementById("spotPreviewAddr");
  const spotMaps = document.getElementById("spotPreviewMaps");
  const spotEmpty = document.getElementById("spotPreviewEmpty");
  const seriesSelect = document.getElementById("seriesPick");
  const seriesSlug = document.getElementById("series");
  const seriesTitle = document.getElementById("seriesTitle");
  const typeSelect = document.getElementById("type");
  const slugInput = document.getElementById("slug");
  const slugHint = document.getElementById("slugRenameHint");
  const tastedInput = document.getElementById("tasted");
  const neighbourhoodInput = document.getElementById("neighbourhood");
  const fieldNotePreview = document.getElementById("fieldNotePreview");
  const uploadList = document.getElementById("uploadRoleList");
  const filesInput = document.getElementById("files");

  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

  function formatFieldNoteDate(iso) {
    if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return "";
    const parts = iso.split("-");
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    const d = parseInt(parts[2], 10);
    if (!y || !m || !d) return "";
    return d + " " + MONTHS[m - 1] + " " + y;
  }

  function updateFieldNotePreview() {
    if (!fieldNotePreview) return;
    const tasted = tastedInput ? tastedInput.value : "";
    const neigh = neighbourhoodInput ? neighbourhoodInput.value.trim() : "";
    const datePart = formatFieldNoteDate(tasted);
    if (!datePart) {
      fieldNotePreview.textContent = "Set a tasting date to sync field note + updated.";
      return;
    }
    fieldNotePreview.textContent = neigh
      ? ("Field note · " + neigh + " · " + datePart)
      : ("Field note · " + datePart);
  }

  if (tastedInput) tastedInput.addEventListener("input", updateFieldNotePreview);
  if (neighbourhoodInput) neighbourhoodInput.addEventListener("input", updateFieldNotePreview);
  updateFieldNotePreview();

  function roleRowHtml(index, fileName) {
    return (
      '<div class="upload-role-row" data-idx="' + index + '">' +
        '<span class="upload-file-name">' + (fileName || "file") + "</span>" +
        '<select name="media_role" class="media-role">' +
          '<option value="seller">Hawker / seller</option>' +
          '<option value="bowl" selected>Dish / bowl</option>' +
          '<option value="author">Author</option>' +
          '<option value="other">Other (freeform)</option>' +
        "</select>" +
        '<input type="text" name="media_role_label" class="media-role-label" ' +
          'placeholder="Label for Other" hidden />' +
      "</div>"
    );
  }

  function bindRoleRow(row) {
    const sel = row.querySelector(".media-role");
    const label = row.querySelector(".media-role-label");
    if (!sel || !label) return;
    function sync() {
      const other = sel.value === "other";
      label.hidden = !other;
      if (other) label.required = true;
      else { label.required = false; label.value = ""; }
    }
    sel.addEventListener("change", sync);
    sync();
  }

  if (filesInput && uploadList) {
    filesInput.addEventListener("change", function () {
      uploadList.innerHTML = "";
      const list = filesInput.files || [];
      for (let i = 0; i < list.length; i++) {
        uploadList.insertAdjacentHTML("beforeend", roleRowHtml(i, list[i].name));
      }
      uploadList.querySelectorAll(".upload-role-row").forEach(bindRoleRow);
    });
  }

  function parseMapsUrl(url) {
    const result = { mapsUrl: (url || "").trim(), name: "", lat: "", lng: "", shortLink: false, hint: "" };
    const raw = result.mapsUrl;
    if (!raw) return result;
    const lower = raw.toLowerCase();
    if (lower.includes("maps.app.goo.gl") || lower.includes("goo.gl/maps")) {
      result.shortLink = true;
      result.hint = "Short link kept as-is — fill the venue name manually.";
      return result;
    }
    let parsed;
    try { parsed = new URL(raw); } catch (e) {
      result.hint = "Could not parse URL.";
      return result;
    }
    const host = (parsed.hostname || "").toLowerCase();
    if (host && !host.includes("google.") && !host.includes("maps.google.")) {
      if (!lower.includes("maps")) {
        result.hint = "Not a recognised Google Maps URL — stored as-is.";
        return result;
      }
    }
    const path = decodeURIComponent(parsed.pathname || "");
    const placeMatch = path.match(/\/place\/([^/@]+)/i);
    if (placeMatch) {
      let name = placeMatch[1].replace(/\+/g, " ").replace(/\s+/g, " ").trim();
      if (name && !/^-?\d+\.?\d*,\s*-?\d+\.?\d*$/.test(name)) result.name = name;
    }
    const at = raw.match(/@(-?\d+\.?\d*),\s*(-?\d+\.?\d*)/);
    if (at) { result.lat = at[1]; result.lng = at[2]; }
    for (const key of ["query", "q", "destination"]) {
      const q = parsed.searchParams.get(key);
      if (!q) continue;
      const decoded = decodeURIComponent(q).trim();
      const coord = decoded.match(/^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$/);
      if (coord) {
        result.lat = result.lat || coord[1];
        result.lng = result.lng || coord[2];
      } else if (decoded && !result.name) {
        result.name = decoded.replace(/\+/g, " ");
      }
      break;
    }
    if (result.name || result.lat) {
      const bits = [];
      if (result.name) bits.push('name “' + result.name + '”');
      if (result.lat && result.lng) bits.push("coords " + result.lat + "," + result.lng);
      result.hint = "Parsed " + bits.join(", ") + ".";
    } else {
      result.hint = "URL stored — no place name/coords found in the string.";
    }
    return result;
  }

  function updateSpotPreview() {
    if (!spotName) return;
    const name = (nameInput && nameInput.value.trim()) || "";
    const addr = (addressInput && addressInput.value.trim()) || "";
    const maps = (mapsInput && mapsInput.value.trim()) || "";
    const has = !!(name || maps);
    if (spotEmpty) spotEmpty.hidden = has;
    spotName.textContent = name || (maps ? "Location" : "—");
    if (spotAddr) {
      spotAddr.textContent = addr;
      spotAddr.hidden = !addr;
    }
    if (spotMaps) {
      if (maps) {
        spotMaps.href = maps;
        spotMaps.hidden = false;
      } else {
        spotMaps.hidden = true;
      }
    }
  }

  function applyParse() {
    if (!mapsInput) return;
    const parsed = parseMapsUrl(mapsInput.value);
    if (hint) hint.textContent = parsed.hint || "";
    if (parsed.name && nameInput && !nameInput.value.trim()) {
      nameInput.value = parsed.name;
    }
    if (parsed.lat && latInput && !latInput.value.trim()) latInput.value = parsed.lat;
    if (parsed.lng && lngInput && !lngInput.value.trim()) lngInput.value = parsed.lng;
    updateSpotPreview();
  }

  if (mapsInput) {
    mapsInput.addEventListener("paste", function () { setTimeout(applyParse, 0); });
    mapsInput.addEventListener("blur", applyParse);
    mapsInput.addEventListener("input", updateSpotPreview);
  }
  if (nameInput) nameInput.addEventListener("input", updateSpotPreview);
  if (addressInput) addressInput.addEventListener("input", updateSpotPreview);

  if (seriesSelect && seriesSlug && seriesTitle) {
    seriesSelect.addEventListener("change", function () {
      const opt = seriesSelect.options[seriesSelect.selectedIndex];
      const slug = seriesSelect.value;
      if (!slug) {
        seriesSlug.value = "";
        seriesTitle.value = "";
        return;
      }
      seriesSlug.value = slug;
      seriesTitle.value = opt.getAttribute("data-title") || opt.textContent || "";
      const defType = opt.getAttribute("data-type") || "";
      if (defType && typeSelect) {
        for (const o of typeSelect.options) {
          if (o.value === defType) { typeSelect.value = defType; break; }
        }
      }
    });
  }

  if (slugInput && slugHint) {
    const original = slugInput.getAttribute("data-original") || slugInput.value;
    function updateSlugHint() {
      const next = (slugInput.value || "").trim();
      if (!next || next === original) {
        slugHint.textContent = "Changing the slug renames the posts folder on save. Lowercase kebab only.";
        return;
      }
      if (!isValidSlug(next)) {
        slugHint.textContent = "Invalid slug — use lowercase a-z, 0-9, hyphens.";
        return;
      }
      slugHint.textContent =
        "Will rename posts/" + original + "/ → posts/" + next + "/ on save. Run build to refresh live URLs.";
    }
    slugInput.addEventListener("input", updateSlugHint);
    updateSlugHint();
  }

  updateSpotPreview();
})();
""")


def page_shell(
    title: str,
    body: str,
    flash: str = "",
    extra_js: str = "",
    wide: bool = False,
) -> bytes:
    flash_html = f'<p class="flash">{html.escape(flash)}</p>' if flash else ""
    js_html = f"<script>{extra_js}</script>" if extra_js else ""
    width = "72rem" if wide else "44rem"
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)} — Penang Guides Editor</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;500;600&display=swap"
    rel="stylesheet"
  />
  <style>
    :root {{
      --bg: #fafaf8; --text: #1c1c1a; --muted: #6b6b66;
      --line: #e6e6e2; --accent: #0f6e6e; --accent-soft: rgba(15, 110, 110, 0.12);
      --card: #fff; --band: #eef6f5;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Source Sans 3", system-ui, sans-serif;
      background:
        radial-gradient(ellipse 80% 40% at 10% 0%, var(--accent-soft), transparent 55%),
        var(--bg);
      color: var(--text); line-height: 1.45;
      min-height: 100vh;
    }}
    .topbar {{
      display: flex; align-items: center; justify-content: space-between;
      gap: 12px; padding: 12px 20px; border-bottom: 1px solid var(--line);
      background: rgba(250, 250, 248, 0.92); backdrop-filter: blur(8px);
      position: sticky; top: 0; z-index: 2;
    }}
    .brand {{
      font-family: Fraunces, Georgia, serif; font-weight: 650;
      font-size: 1.05rem; color: var(--accent); text-decoration: none;
    }}
    .topbar .meta {{ color: var(--muted); font-size: 0.85rem; }}
    main {{ max-width: {width}; margin: 0 auto; padding: 28px 16px 72px; }}
    h1 {{
      font-family: Fraunces, Georgia, serif; font-weight: 650;
      font-size: 1.65rem; margin: 0 0 6px; letter-spacing: -0.02em;
    }}
    h2 {{
      font-family: Fraunces, Georgia, serif; font-weight: 560;
      font-size: 1.15rem; margin: 28px 0 10px;
    }}
    .lede {{ color: var(--muted); margin: 0 0 20px; max-width: 40rem; }}
    .muted {{ color: var(--muted); font-size: 0.92rem; }}
    .flash {{
      margin: 0 0 18px; padding: 10px 12px; background: var(--band);
      border: 1px solid #b7dede; border-radius: 10px;
    }}
    a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .series-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px; margin: 16px 0 8px;
    }}
    .series-card {{
      display: block; padding: 16px 16px 14px; background: var(--card);
      border: 1px solid var(--line); border-radius: 12px;
      text-decoration: none; color: inherit; transition: border-color .15s, box-shadow .15s;
    }}
    .series-card:hover {{
      border-color: #9bc8c8; box-shadow: 0 4px 18px rgba(15, 110, 110, 0.08);
      text-decoration: none;
    }}
    .series-card .kicker {{
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em;
      text-transform: uppercase; color: var(--accent); margin: 0 0 6px;
    }}
    .series-card h3 {{
      font-family: Fraunces, Georgia, serif; font-size: 1.15rem;
      margin: 0 0 6px; font-weight: 560;
    }}
    .series-card .dek {{ color: var(--muted); font-size: 0.9rem; margin: 0 0 12px; }}
    .badge {{
      display: inline-block; font-size: 0.78rem; font-weight: 600;
      padding: 3px 8px; border-radius: 999px; background: var(--accent-soft);
      color: var(--accent);
    }}
    .badge.quiet {{ background: #eee; color: var(--muted); }}
    .badge.draft {{ background: #f3e6c8; color: #7a5a12; }}
    ul.posts, ul.episodes {{ list-style: none; margin: 12px 0; padding: 0; }}
    ul.posts li, ul.episodes li {{
      display: flex; justify-content: space-between; align-items: flex-start;
      gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--line);
    }}
    ul.posts li > span, ul.episodes li > .ep-main {{
      min-width: 0; flex: 1;
    }}
    ul.posts li > a, ul.episodes li > a.ep-edit {{
      flex: 0 0 auto; margin-top: 2px; white-space: nowrap;
      font-weight: 600; font-size: 0.9rem;
    }}
    .ep-main .ep-title {{ line-height: 1.35; }}
    .ep-meta {{
      display: block; margin-top: 4px;
      color: var(--muted); font-size: 0.85rem; line-height: 1.4;
      overflow-wrap: anywhere;
    }}
    form.card, .card, .panel {{
      margin-top: 16px; padding: 16px 18px; background: var(--card);
      border: 1px solid var(--line); border-radius: 12px;
    }}
    .layout {{
      display: grid; grid-template-columns: minmax(0, 1fr) 240px; gap: 18px;
      align-items: start;
    }}
    @media (max-width: 860px) {{
      .layout {{ grid-template-columns: 1fr; }}
    }}
    .sidebar .panel {{ position: sticky; top: 68px; }}
    .sidebar h3 {{
      font-family: Fraunces, Georgia, serif; font-size: 1rem;
      margin: 0 0 8px; font-weight: 560;
    }}
    .sidebar ol {{ margin: 0; padding-left: 1.1rem; font-size: 0.9rem; }}
    .sidebar li {{ margin: 6px 0; }}
    .sidebar li.current a {{ color: var(--text); }}
    label {{ display: block; font-weight: 600; margin: 12px 0 6px; font-size: 0.9rem; }}
    input[type=text], textarea, select {{
      width: 100%; padding: 10px 12px; border: 1px solid var(--line);
      border-radius: 8px; font: inherit; background: #fff;
    }}
    textarea {{ min-height: 20rem; font-family: ui-monospace, Menlo, monospace; font-size: 0.88rem; }}
    .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }}
    @media (max-width: 640px) {{ .grid2 {{ grid-template-columns: 1fr; }} }}
    .row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    button, .btn {{
      appearance: none; border: 0; border-radius: 8px; padding: 10px 14px;
      background: var(--accent); color: #fff; font: inherit; font-weight: 600;
      cursor: pointer; display: inline-block; text-decoration: none;
    }}
    button:hover, .btn:hover {{ filter: brightness(1.05); text-decoration: none; }}
    button.secondary, a.btn.secondary {{
      background: #fff; color: var(--text); border: 1px solid var(--line);
    }}
    button.danger, a.btn.danger {{
      background: #8b2e2e; color: #fff;
    }}
    button.publish, a.btn.publish {{
      background: #fff; color: var(--accent);
      border: 1px solid var(--accent);
      font-weight: 600;
    }}
    button.publish:hover, a.btn.publish:hover {{
      background: var(--band); filter: none;
    }}
    .danger-zone {{
      margin-top: 22px; padding: 14px 16px; border: 1px dashed #d4a8a8;
      border-radius: 12px; background: #fff8f8;
    }}
    .danger-zone h2 {{ margin-top: 0; color: #8b2e2e; font-size: 1.05rem; }}
    .publish-zone {{
      margin-top: 18px; padding: 12px 14px; border: 1px solid var(--line);
      border-radius: 12px; background: #fff;
    }}
    .publish-zone h2 {{
      margin: 0 0 6px; font-size: 0.95rem; font-family: inherit; font-weight: 600;
      color: var(--muted);
    }}
    .actions-bar form {{ margin: 0; display: inline; }}
    .slug-preview {{
      margin: 8px 0 0; padding: 10px 12px; border-radius: 8px;
      background: var(--band); border: 1px solid #c5e0df; font-size: 0.9rem;
    }}
    .slug-preview code {{ font-size: 0.92em; }}
    .media {{ margin-top: 10px; font-size: 0.9rem; }}
    .media li {{ margin: 4px 0; }}
    .cover-picker {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 10px; margin: 10px 0 0;
    }}
    .cover-card {{
      display: flex; flex-direction: column; gap: 6px; margin: 0;
      padding: 8px; border: 1px solid var(--line); border-radius: 10px;
      background: #fff; cursor: pointer; font-weight: 500;
    }}
    .cover-card:has(input:checked) {{
      border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-soft);
    }}
    .cover-card input {{ position: absolute; opacity: 0; pointer-events: none; }}
    .cover-thumb {{
      display: block; width: 100%; aspect-ratio: 1; object-fit: cover;
      border-radius: 8px; background: #eee;
    }}
    .cover-none {{
      display: grid; place-items: center; color: var(--muted);
      font-size: 0.85rem; font-weight: 600;
    }}
    .cover-name {{
      font-size: 0.78rem; color: var(--muted); line-height: 1.3;
      overflow-wrap: anywhere;
    }}
    .cover-name code {{ font-size: 0.72rem; color: var(--text); }}
    .cover-role {{
      display: inline-block; margin-left: 4px; padding: 1px 6px;
      border-radius: 999px; background: var(--accent-soft); color: var(--accent);
      font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .upload-role-list {{ margin: 10px 0 0; display: grid; gap: 8px; }}
    .upload-role-row {{
      display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr);
      gap: 8px; align-items: center; padding: 8px 10px;
      border: 1px solid var(--line); border-radius: 8px; background: #fff;
    }}
    @media (max-width: 640px) {{
      .upload-role-row {{ grid-template-columns: 1fr; }}
    }}
    .upload-file-name {{
      font-size: 0.85rem; color: var(--muted); overflow: hidden;
      text-overflow: ellipsis; white-space: nowrap;
    }}
    .upload-role-row select, .upload-role-row input[type=text] {{
      margin: 0; padding: 8px 10px;
    }}
    pre.build {{
      margin-top: 12px; padding: 12px; background: #1c1c1a; color: #eee;
      border-radius: 8px; overflow: auto; font-size: 0.82rem; white-space: pre-wrap;
    }}
    .hint {{ margin: 6px 0 0; font-size: 0.85rem; color: var(--muted); }}
    .soft-warn {{ color: #7a5a12; }}
    fieldset {{
      margin: 16px 0 0; padding: 12px 14px 14px; border: 1px solid var(--line);
      border-radius: 10px; background: #fcfcfa;
    }}
    legend {{ font-weight: 600; padding: 0 6px; color: var(--accent); font-size: 0.88rem; }}
    .spot-preview {{
      margin-top: 12px; padding: 12px 14px; border-radius: 10px;
      background: var(--band); border: 1px solid #c5e0df;
    }}
    .spot-preview .spot-label {{
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em;
      text-transform: uppercase; color: var(--accent); margin: 0 0 4px;
    }}
    .spot-preview .spot-name {{
      font-family: Fraunces, Georgia, serif; font-size: 1.1rem;
      margin: 0 0 4px; font-weight: 560;
    }}
    .spot-preview .spot-addr {{ margin: 0 0 6px; color: var(--muted); font-size: 0.9rem; }}
    .spot-preview a {{ font-size: 0.9rem; }}
    .actions-bar {{
      display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
      margin: 8px 0 18px;
    }}
    .save-bar {{
      display: flex; flex-wrap: wrap; gap: 12px 16px; align-items: center;
      margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--line);
    }}
    .save-bar .row {{ margin-top: 0; }}
    .draft-toggle {{
      display: inline-flex; align-items: center; gap: 8px;
      font-weight: 600; margin: 0; cursor: pointer; user-select: none;
    }}
    .draft-toggle input {{ width: auto; margin: 0; }}
    .draft-toggle .draft-hint {{
      font-weight: 500; font-size: 0.85rem; color: var(--muted);
    }}
    .busy-overlay {{
      position: fixed; inset: 0; z-index: 100;
      display: none; align-items: center; justify-content: center;
      padding: 24px; background: rgba(28, 28, 26, 0.45);
      backdrop-filter: blur(3px);
    }}
    .busy-overlay[open], .busy-overlay.is-open {{ display: flex; }}
    .busy-card {{
      width: min(26rem, 100%); padding: 22px 22px 18px;
      background: var(--card); border-radius: 14px;
      border: 1px solid var(--line);
      box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
    }}
    .busy-card h2 {{
      margin: 0 0 8px; font-size: 1.15rem; color: var(--text);
    }}
    .busy-card p {{
      margin: 0; color: var(--muted); font-size: 0.92rem; line-height: 1.45;
    }}
    .busy-steps {{
      margin: 14px 0 0; padding: 0; list-style: none;
      font-size: 0.88rem; color: var(--muted);
    }}
    .busy-steps li {{
      display: flex; gap: 8px; align-items: baseline;
      padding: 4px 0;
    }}
    .busy-steps li::before {{
      content: "·"; color: var(--accent); font-weight: 700;
    }}
    .busy-spinner {{
      width: 28px; height: 28px; margin: 16px auto 0;
      border: 3px solid var(--line); border-top-color: var(--accent);
      border-radius: 50%; animation: busy-spin 0.8s linear infinite;
    }}
    @keyframes busy-spin {{ to {{ transform: rotate(360deg); }} }}
    input[type=date] {{
      width: 100%; padding: 10px 12px; border: 1px solid var(--line);
      border-radius: 8px; font: inherit; background: #fff;
    }}
    code {{ font-size: 0.88em; }}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="/">Penang Pulse · Guides</a>
    <span class="meta">local only · not deployed</span>
  </div>
  <main>
    <h1>{html.escape(title)}</h1>
    {flash_html}
    {body}
  </main>
  <div id="busyOverlay" class="busy-overlay" hidden aria-live="polite" aria-busy="true">
    <div class="busy-card" role="dialog" aria-modal="true" aria-labelledby="busyTitle">
      <h2 id="busyTitle">Working…</h2>
      <p id="busyDetail">Please leave this tab open.</p>
      <ul class="busy-steps" id="busySteps" hidden></ul>
      <div class="busy-spinner" aria-hidden="true"></div>
    </div>
  </div>
  <script>{BUSY_JS}</script>
  {js_html}
</body>
</html>
"""
    return doc.encode("utf-8")


def _input(
    name: str,
    label: str,
    value: str,
    placeholder: str = "",
    input_id: str | None = None,
) -> str:
    eid = input_id or name
    return (
        f'<label for="{html.escape(eid)}">{html.escape(label)}</label>'
        f'<input id="{html.escape(eid)}" name="{html.escape(name)}" type="text" '
        f'value="{html.escape(value)}" placeholder="{html.escape(placeholder)}" />'
    )


def index_page(flash: str = "") -> bytes:
    registry = load_series_registry()
    posts = list_posts_detailed()
    by_series: dict[str, list[dict[str, Any]]] = {}
    for p in posts:
        if p.get("series"):
            by_series.setdefault(p["series"], []).append(p)

    # Ensure registered series appear even with 0 posts; also surface orphan series
    known_slugs = {s["slug"] for s in registry}
    cards = []
    for s in registry:
        count = len(by_series.get(s["slug"], []))
        status = s.get("status") or "active"
        cards.append(
            f'<a class="series-card" href="/series?slug={urllib.parse.quote(s["slug"])}">'
            f'<p class="kicker">Series · {html.escape(status)}</p>'
            f'<h3>{html.escape(s["title"])}</h3>'
            f'<p class="dek">{html.escape(s.get("dek") or "No dek yet.")}</p>'
            f'<span class="badge">{count} episode{"s" if count != 1 else ""}</span>'
            f"</a>"
        )
    for slug, eps in sorted(by_series.items()):
        if slug in known_slugs:
            continue
        title = eps[0].get("seriesTitle") or slug.replace("-", " ").title()
        cards.append(
            f'<a class="series-card" href="/series?slug={urllib.parse.quote(slug)}">'
            f'<p class="kicker">Series · unregistered</p>'
            f"<h3>{html.escape(title)}</h3>"
            f'<p class="dek">Found on posts — add to <code>_series.json</code> to register.</p>'
            f'<span class="badge">{len(eps)} episode{"s" if len(eps) != 1 else ""}</span>'
            f"</a>"
        )
    series_html = (
        f'<div class="series-grid">{"".join(cards)}</div>'
        if cards
        else '<p class="muted">No series registered yet. Edit <code>guides/posts/_series.json</code>.</p>'
    )

    standalone = [p for p in posts if not p.get("series")]
    stand_items = "".join(
        f'<li><span>{html.escape(p["title"])} '
        f'<span class="muted">({html.escape(p["slug"])})</span>'
        f'{" <span class=\"badge draft\">draft</span>" if p.get("draft") else ""}'
        f"</span>"
        f'<a href="/edit?slug={urllib.parse.quote(p["slug"])}">Edit</a></li>'
        for p in standalone
    ) or '<li class="muted">No standalone guides.</li>'

    body = f"""
    <p class="lede">Editorial desk for owned Guides. Series first — open a spine,
    then add episodes. Charter: <code>utilities/penang-pulse/EDITORIAL.md</code>.</p>
    <p class="hint">Save &amp; build is local · Publish deploys all of penangpulse.com</p>
    <div class="actions-bar">
      <a class="btn" href="/new">New standalone guide</a>
      <a class="btn secondary" href="/build">Run build</a>
    </div>

    <h2>Series</h2>
    {series_html}

    <h2>Standalone guides</h2>
    <ul class="posts">{stand_items}</ul>
    """
    return page_shell("Guides desk", body, flash)


def series_page(slug: str, flash: str = "") -> bytes:
    entry = series_by_slug(slug)
    episodes = episodes_for_series(slug)
    if entry:
        title = entry["title"]
        dek = entry.get("dek") or ""
        status = entry.get("status") or "active"
    elif episodes:
        title = episodes[0].get("seriesTitle") or slug.replace("-", " ").title()
        dek = "Unregistered series (present on posts only)."
        status = "unregistered"
    else:
        return page_shell(
            "Series not found",
            f"<p>Unknown series <code>{html.escape(slug)}</code>.</p>"
            f'<p><a href="/">← Desk</a></p>',
            flash,
        )

    items = []
    publish_anchor = ""
    for ep in episodes:
        order = ep.get("seriesOrder")
        order_label = f"#{order}" if order is not None else "—"
        tasted = ep.get("tasted") or ""
        note = html.escape(ep.get("fieldNote") or "")
        draft_badge = (
            ' <span class="badge draft">draft</span>' if ep.get("draft") else ""
        )
        if not publish_anchor and not ep.get("draft"):
            publish_anchor = ep["slug"]
        items.append(
            "<li>"
            f'<div class="ep-main">'
            f'<span class="ep-title"><strong>{html.escape(ep["title"])}</strong>'
            f"{draft_badge}</span>"
            f'<span class="ep-meta">{html.escape(order_label)} · '
            f'tasted {html.escape(tasted or "—")} · '
            f'{html.escape(ep["slug"])}'
            f'{(" · " + note) if note else ""}</span>'
            f"</div>"
            f'<a class="ep-edit" href="/edit?slug={urllib.parse.quote(ep["slug"])}">Edit</a>'
            "</li>"
        )
    list_html = "".join(items) or '<li class="muted">No episodes yet — create the first one.</li>'

    if publish_anchor:
        series_publish = (
            f'<form method="post" action="/publish" data-busy '
            f'data-busy-title="Publishing…" '
            f'data-busy-detail="Leave this tab open — Firebase deploy often takes several minutes." '
            f'data-busy-steps="Build all guides|git commit|git push (best-effort)|Firebase deploy" '
            f'data-busy-confirm="Publish pending guide changes to penangpulse.com? '
            f'Commits guide paths and deploys the whole site.">'
            f'<input type="hidden" name="slug" value="{html.escape(publish_anchor)}" />'
            f'<input type="hidden" name="intent" value="series" />'
            f'<button class="publish" type="submit">Publish to penangpulse.com</button>'
            f"</form>"
        )
    else:
        series_publish = (
            '<span class="muted" style="font-size:0.9rem">'
            "Publish available after a non-draft episode is saved."
            "</span>"
        )

    body = f"""
    <p class="lede">{html.escape(dek)}</p>
    <p class="muted">
      <span class="badge">{html.escape(status)}</span>
      <span class="badge quiet">{len(episodes)} episode{"s" if len(episodes) != 1 else ""}</span>
      · slug <code>{html.escape(slug)}</code>
      · live <a href="{LIVE_HOST}/guides/series/{html.escape(slug, quote=True)}/"
        target="_blank" rel="noopener">penangpulse.com/…</a>
    </p>
    <div class="actions-bar">
      <a class="btn" href="/new?series={urllib.parse.quote(slug)}">New episode in this series</a>
      {series_publish}
      <a class="btn secondary" href="/">← Desk</a>
      <a class="btn secondary" href="/build">Run build</a>
    </div>
    <div class="card">
      <h2 style="margin-top:0">Episodes</h2>
      <p class="hint">Save &amp; build is local · Publish deploys all of penangpulse.com
      <span title="seriesOrder is recomputed on save from tasting date (oldest = #1). Same-day tie-break: previous order, then slug.">· order from tasting date</span></p>
      <ul class="episodes">{list_html}</ul>
    </div>
    """
    return page_shell(title, body, flash)


def new_page(series_slug: str = "", flash: str = "") -> bytes:
    registry = load_series_registry()
    series_entry = series_by_slug(series_slug) if series_slug else None
    options = ['<option value="">None (standalone)</option>']
    for s in registry:
        selected = " selected" if series_entry and s["slug"] == series_entry["slug"] else ""
        options.append(
            f'<option value="{html.escape(s["slug"])}"{selected}>'
            f'{html.escape(s["title"])}</option>'
        )
    default_title = ""
    heading = "New guide"
    if series_entry:
        heading = f"New episode · {series_entry['title']}"
        default_title = ""

    today = dt.date.today().isoformat()
    body = f"""
    <p class="lede">Creates <code>guides/posts/&lt;slug&gt;/post.md</code> with a template skeleton.
    Edit the slug before create — it becomes the live URL.</p>
    <form class="card" method="post" action="/create">
      <label for="series">Series</label>
      <select id="series" name="series">{"".join(options)}</select>
      <p class="hint">Choosing a series pre-fills series fields, template, and tasting-date order.</p>
      <label for="title">Title</label>
      <input id="title" name="title" type="text" required
        value="{html.escape(default_title)}"
        placeholder="Sister’s Curry Mee" autocomplete="off" />
      <label for="slug">Slug</label>
      <input id="slug" name="slug" type="text"
        placeholder="sisters-curry-mee" autocomplete="off"
        pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
        title="Lowercase kebab-case: a-z, 0-9, hyphens" />
      <p class="slug-preview"><code id="slugPreview">guides/posts/…/</code></p>
      <p class="hint" id="slugPreviewWarn" hidden></p>
      <p class="hint">Derived from the title as you type; edit freely before Create.
      Must be lowercase kebab-case. Live path: <code>/guides/&lt;slug&gt;/</code>.</p>
      <label for="tasted">Tasting date</label>
      <input id="tasted" name="tasted" type="date" value="{html.escape(today)}" required />
      <p class="hint">Sets <code>tasted</code>, syncs <code>fieldNote</code> / <code>updated</code>,
      and places the episode in series order (oldest first).</p>
      <div class="row">
        <button type="submit">Create</button>
        <a class="btn secondary" href="{
            f'/series?slug={urllib.parse.quote(series_slug)}' if series_slug else '/'
        }">Cancel</a>
      </div>
    </form>
    """
    return page_shell(heading, body, flash, NEW_PAGE_JS)


def edit_page(slug: str, flash: str = "") -> bytes:
    post_path = POSTS_DIR / slug / "post.md"
    if not post_path.is_file():
        return page_shell(
            "Not found",
            f"<p>Unknown slug <code>{html.escape(slug)}</code>.</p>",
            flash,
        )
    content = post_path.read_text(encoding="utf-8")
    fields, body_md = fields_from_post(content)
    media_files = list_orig_images(slug)
    media_items = [
        f"<li><code>./media/orig/{html.escape(path.name)}</code></li>"
        for path in media_files
    ]
    media_html = (
        f'<ul class="media">{"".join(media_items)}</ul>'
        if media_items
        else '<p class="muted">No originals uploaded yet.</p>'
    )
    cover_html = cover_picker_html(slug, fields.get("cover", ""))

    type_val = fields.get("type") or "text"
    type_options = [
        ("text", "Text"),
        ("photo", "Photos"),
        ("video", "Video"),
        ("series-mee", "Mee (series episode)"),
    ]
    type_html = "".join(
        f'<option value="{html.escape(v)}"'
        f'{" selected" if type_val == v else ""}>{html.escape(label)}</option>'
        for v, label in type_options
    )

    registry = load_series_registry()
    current_series = fields.get("series") or ""
    pick_options = ['<option value="">None</option>']
    for s in registry:
        selected = " selected" if s["slug"] == current_series else ""
        next_ord = next_series_order(s["slug"])
        pick_options.append(
            f'<option value="{html.escape(s["slug"])}"{selected} '
            f'data-title="{html.escape(s["title"], quote=True)}" '
            f'data-type="{html.escape(s.get("defaultType") or "text", quote=True)}" '
            f'data-next-order="{html.escape(next_ord)}">'
            f'{html.escape(s["title"])}</option>'
        )
    # If post has a series not in registry, keep it selectable
    if current_series and not any(s["slug"] == current_series for s in registry):
        pick_options.append(
            f'<option value="{html.escape(current_series)}" selected '
            f'data-title="{html.escape(fields.get("seriesTitle") or current_series, quote=True)}">'
            f'{html.escape(fields.get("seriesTitle") or current_series)} (unregistered)</option>'
        )

    siblings = episodes_for_series(current_series) if current_series else []
    sib_items = []
    for ep in siblings:
        order = ep.get("seriesOrder")
        label = f'{order}. {ep["title"]}' if order is not None else ep["title"]
        if ep.get("draft"):
            label = f"{label} (draft)"
        if ep["slug"] == slug:
            sib_items.append(
                f'<li class="current"><strong>{html.escape(label)}</strong></li>'
            )
        else:
            sib_items.append(
                f'<li><a href="/edit?slug={urllib.parse.quote(ep["slug"])}">'
                f"{html.escape(label)}</a></li>"
            )
    sidebar = ""
    if current_series:
        series_title = fields.get("seriesTitle") or current_series
        sidebar = f"""
        <aside class="sidebar">
          <div class="panel">
            <h3>{html.escape(series_title)}</h3>
            <p class="muted" style="margin:0 0 10px">Sibling episodes</p>
            <ol>{"".join(sib_items) or "<li class='muted'>Only this episode.</li>"}</ol>
            <div class="row" style="margin-top:14px">
              <a class="btn secondary" href="/series?slug={urllib.parse.quote(current_series)}">Series page</a>
            </div>
            <div class="row">
              <a class="btn" href="/new?series={urllib.parse.quote(current_series)}">New episode</a>
            </div>
          </div>
        </aside>
        """

    loc_name = fields.get("locationName", "")
    maps_url = fields.get("mapsUrl", "")
    loc_addr = fields.get("locationAddress", "")
    has_spot = bool(loc_name or maps_url)

    is_draft = is_draft_value(fields.get("draft", ""))
    draft_checked = " checked" if is_draft else ""
    draft_badge = (
        ' <span class="badge draft">draft — not published</span>' if is_draft else ""
    )
    tasted_val = fields.get("tasted") or ""
    order_val = fields.get("seriesOrder") or "—"
    dek_hint = ""
    if not (fields.get("dek") or "").strip():
        dek_hint = (
            '<p class="hint soft-warn">Dek is empty — fine for drafts; '
            "worth filling before Publish (not blocked).</p>"
        )
    publish_block = ""
    if is_draft:
        publish_block = """
        <div class="publish-zone">
          <h2>Publish</h2>
          <p class="hint">Uncheck Draft, Save, then Publish. Drafts cannot go live.</p>
        </div>
        """
    else:
        publish_block = f"""
        <div class="publish-zone">
          <h2>Publish</h2>
          <p class="hint">Save &amp; build is local (rebuilds all guides) ·
          Publish commits guide paths and deploys all of penangpulse.com</p>
          <form method="post" action="/publish" data-busy
            data-busy-title="Publishing…"
            data-busy-detail="Leave this tab open — Firebase deploy often takes several minutes."
            data-busy-steps="Build all guides|git commit|git push (best-effort)|Firebase deploy"
            data-busy-confirm="Publish to penangpulse.com? Commits guide paths and deploys the whole site.">
            <input type="hidden" name="slug" value="{html.escape(slug)}" />
            <div class="row">
              <button class="publish" type="submit">Publish to penangpulse.com</button>
              <a class="btn secondary" href="{LIVE_HOST}/guides/{html.escape(slug, quote=True)}/"
                 target="_blank" rel="noopener">Open live</a>
            </div>
          </form>
        </div>
        """

    form = f"""
    <form class="card" method="post" action="/save" enctype="multipart/form-data">
      <input type="hidden" name="old_slug" value="{html.escape(slug)}" />
      {_input("title", "Title", fields.get("title", ""))}
      {_input("dek", "Dek", fields.get("dek", ""), "One-line summary — answer-shaped if you can")}
      {dek_hint}
      <label for="slug">Slug</label>
      <input id="slug" name="slug" type="text" required
        value="{html.escape(slug)}" data-original="{html.escape(slug)}"
        pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
        title="Lowercase kebab-case: a-z, 0-9, hyphens" autocomplete="off" />
      <p class="hint" id="slugRenameHint">Changing the slug renames the posts folder on save. Lowercase kebab only.</p>
      <div class="grid2">
        <div>
          <label for="type">Type</label>
          <select id="type" name="type">{type_html}</select>
        </div>
        <div>
          <label for="tasted">Tasting date</label>
          <input id="tasted" name="tasted" type="date" value="{html.escape(tasted_val)}" />
          <p class="hint" id="fieldNotePreview">Field note syncs from tasting date + neighbourhood.</p>
        </div>
      </div>
      <input type="hidden" name="updated" value="{html.escape(fields.get("updated", ""))}" />
      <input type="hidden" name="fieldNote" value="{html.escape(fields.get("fieldNote", ""))}" />
      {_input("neighbourhood", "Neighbourhood", fields.get("neighbourhood", ""), "Pulau Tikus")}

      <fieldset>
        <legend>Series</legend>
        <label for="seriesPick">Series</label>
        <select id="seriesPick" name="seriesPick">{"".join(pick_options)}</select>
        <input type="hidden" id="series" name="series" value="{html.escape(fields.get("series", ""))}" />
        <input type="hidden" id="seriesTitle" name="seriesTitle" value="{html.escape(fields.get("seriesTitle", ""))}" />
        <input type="hidden" id="seriesOrder" name="seriesOrder" value="{html.escape(fields.get("seriesOrder", ""))}" />
        <p class="hint">Computed order: <strong>#{html.escape(str(order_val))}</strong>
        (auto from tasting date on save; oldest = 1). Same-day: keep prior order, then slug.</p>
      </fieldset>

      <fieldset>
        <legend>Spot / Google Maps</legend>
        {_input("locationName", "Venue name", loc_name, "Venue name", "locationName")}
        {_input("mapsUrl", "Maps URL", maps_url, "https://maps.app.goo.gl/… or google.com/maps/place/…", "mapsUrl")}
        <p class="hint" id="mapsHint">Paste a Maps link — short links stay as-is; full URLs may fill name/coords.</p>
        {_input("locationAddress", "Address (optional)", loc_addr, "", "locationAddress")}
        <div class="grid2">
          <div>{_input("locationLat", "Lat (optional)", fields.get("locationLat", ""), "", "locationLat")}</div>
          <div>{_input("locationLng", "Lng (optional)", fields.get("locationLng", ""), "", "locationLng")}</div>
        </div>
        <div class="spot-preview" id="spotPreview">
          <p class="spot-label">Spot preview</p>
          <p class="spot-name" id="spotPreviewName">{html.escape(loc_name or ("Location" if maps_url else "—"))}</p>
          <p class="spot-addr" id="spotPreviewAddr" {"hidden" if not loc_addr else ""}>{html.escape(loc_addr)}</p>
          <a class="spot-maps" id="spotPreviewMaps" href="{html.escape(maps_url, quote=True)}"
             target="_blank" rel="noopener" {"hidden" if not maps_url else ""}>Open in Google Maps</a>
          <p class="muted" id="spotPreviewEmpty" {"hidden" if has_spot else ""}>Paste a Maps URL or venue name to preview.</p>
        </div>
      </fieldset>

      <label for="body">Body (markdown)</label>
      <textarea id="body" name="body" required>{html.escape(body_md)}</textarea>
      <fieldset>
        <legend>Photo intake</legend>
        <label for="files">Upload to media/orig/</label>
        <input id="files" name="files" type="file" multiple accept="image/*,.heic,.heif" />
        <p class="hint">Pick a role per file — renamed to
        <code>{{slug}}-seller.jpeg</code> / <code>-bowl</code> / <code>-author</code>
        (or freeform). Appends into <code>## Photos</code> in editorial order if missing.</p>
        <div id="uploadRoleList" class="upload-role-list"></div>
        {media_html}
        <label>Share / OG image</label>
        {cover_html}
        <p class="hint">Optional. Click a photo for WhatsApp / social preview
        (<code>cover</code> → <code>og:image</code>). No in-page banner.
        Default = alphabetically first processed photo.</p>
        <input type="hidden" name="hero" value="{html.escape(fields.get("hero", ""))}" />
      </fieldset>
      <div class="save-bar">
        <label class="draft-toggle">
          <input type="checkbox" name="draft" value="true"{draft_checked} />
          Draft
          <span class="draft-hint">skip public build</span>
        </label>
        <div class="row">
          <button type="submit">Save</button>
          <button class="secondary" type="submit" name="and_build" value="1">Save &amp; build</button>
          <a class="btn secondary" href="/">Desk</a>
        </div>
      </div>
    </form>

    {publish_block}

    <div class="danger-zone">
      <h2>Delete episode</h2>
      <p class="hint">Removes <code>guides/posts/{html.escape(slug)}/</code> permanently
      (and any built <code>guides/{html.escape(slug)}/</code>). This cannot be undone.</p>
      <form method="post" action="/delete"
        onsubmit="return confirm('Delete this episode permanently? This cannot be undone.');">
        <input type="hidden" name="slug" value="{html.escape(slug)}" />
        <div class="row">
          <button class="danger" type="submit">Delete episode</button>
        </div>
      </form>
    </div>
    """

    body = f"""
    <p class="muted">Editing <code>{html.escape(slug)}</code>{draft_badge}</p>
    <div class="layout">
      <div>{form}</div>
      {sidebar}
    </div>
    """
    return page_shell(f"Edit · {slug}", body, flash, EDITOR_JS, wide=True)


def build_page() -> bytes:
    code, output = run_subprocess([python_for_build(), str(BUILD_SCRIPT)])
    flash = f"Build {'ok' if code == 0 else 'failed'} (exit {code})"
    body = f"""
    <p class="muted">Command: <code>{html.escape(python_for_build() + " " + str(BUILD_SCRIPT))}</code></p>
    <pre class="build">{html.escape(output or "(no output)")}</pre>
    <div class="row"><a class="btn" href="/">Desk</a></div>
    """
    return page_shell("Build", body, flash)


def publish_page(slug: str, result: dict[str, Any]) -> bytes:
    live = f"{LIVE_HOST}/guides/{slug}/"
    steps_html = []
    for step in result.get("steps") or []:
        name = html.escape(str(step.get("name") or ""))
        ok = step.get("ok")
        badge = "ok" if ok else ("skipped" if step.get("skipped") else "failed")
        detail = html.escape(str(step.get("detail") or ""))
        log = step.get("log") or ""
        steps_html.append(
            f"<h2>{name} · {badge}</h2>"
            f'<p class="muted">{detail}</p>'
            + (f'<pre class="build">{html.escape(log)}</pre>' if log else "")
        )
    flash = str(result.get("flash") or "")
    body = f"""
    <p class="lede">Publish handoff for <code>{html.escape(slug)}</code>.</p>
    <p class="hint">Build rebuilt all guides · deploy covers all of penangpulse.com</p>
    <p><a href="{html.escape(live)}" target="_blank" rel="noopener">{html.escape(live)}</a></p>
    {"".join(steps_html) or '<p class="muted">No steps ran.</p>'}
    <div class="row">
      <a class="btn" href="/edit?slug={urllib.parse.quote(slug)}">← Editor</a>
      <a class="btn secondary" href="/">Desk</a>
    </div>
    """
    return page_shell(f"Publish · {slug}", body, flash)


def run_publish(slug: str, intent: str = "") -> dict[str, Any]:
    """Build all guides → git add/commit → push (best-effort) → firebase deploy.

    Build always runs the full guides builder. Deploy always targets the entire
    hosting:penang-pulse surface (penangpulse.com), not a single article CDN path.
    """
    result: dict[str, Any] = {"steps": [], "flash": ""}
    if not is_valid_slug(slug):
        result["flash"] = "Invalid slug."
        return result
    post_path = POSTS_DIR / slug / "post.md"
    if not post_path.is_file():
        result["flash"] = f"Unknown episode: {slug}"
        return result

    fields, _ = fields_from_post(post_path.read_text(encoding="utf-8"))
    if is_draft_value(fields.get("draft", "")):
        result["flash"] = "Refused: draft:true — uncheck Draft and Save before Publish."
        result["steps"].append(
            {
                "name": "Guard",
                "ok": False,
                "detail": "Publish blocked while draft is set.",
            }
        )
        return result

    title = (fields.get("title") or slug).strip()
    series_slug = (fields.get("series") or "").strip()
    series_title = (fields.get("seriesTitle") or series_slug).strip()

    # Ensure tasting/order sync before build
    apply_tasting_fields(fields)
    body_md = fields_from_post(post_path.read_text(encoding="utf-8"))[1]
    write_post_fields(slug, fields, body_md)
    touched = [slug]
    if series_slug:
        touched = list({*touched, *recompute_series_orders(series_slug)})

    code, log = run_subprocess([python_for_build(), str(BUILD_SCRIPT)], timeout=180)
    result["steps"].append(
        {
            "name": "Build",
            "ok": code == 0,
            "detail": f"full guides builder · exit {code}",
            "log": log,
        }
    )
    if code != 0:
        result["flash"] = "Publish stopped — build failed."
        return result

    paths = publish_paths_for_slug(slug, series_slug, touched)
    existing = [p for p in paths if (ROOT / p).exists()]
    if not existing:
        result["flash"] = "Nothing to stage."
        return result

    add_code, add_log = run_subprocess(["git", "add", "--", *existing])
    result["steps"].append(
        {
            "name": "git add",
            "ok": add_code == 0,
            "detail": ", ".join(existing),
            "log": add_log,
        }
    )
    if add_code != 0:
        result["flash"] = "Publish stopped — git add failed."
        return result

    cached_code, cached_out = run_subprocess(
        ["git", "diff", "--cached", "--name-only", "--", *existing]
    )
    has_cached = bool((cached_out or "").strip()) and cached_code == 0

    commit_env = {
        "GIT_AUTHOR_NAME": GIT_AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": GIT_AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME": GIT_AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": GIT_AUTHOR_EMAIL,
    }
    if has_cached:
        if intent == "series" and series_title:
            msg = f"Publish {series_title} series guides."
        else:
            msg = f"Publish {title} guide."
        commit_code, commit_log = run_subprocess(
            ["git", "commit", "-m", msg],
            env=commit_env,
        )
        result["steps"].append(
            {
                "name": "git commit",
                "ok": commit_code == 0,
                "detail": msg,
                "log": commit_log,
            }
        )
        if commit_code != 0:
            result["flash"] = "Publish stopped — commit failed."
            return result
    else:
        result["steps"].append(
            {
                "name": "git commit",
                "ok": True,
                "skipped": True,
                "detail": "Nothing new to commit (working tree already clean for these paths).",
                "log": cached_out,
            }
        )

    push_code, push_log = run_subprocess(
        ["git", "push", "origin", "main"],
        timeout=120,
    )
    push_ok = push_code == 0
    result["steps"].append(
        {
            "name": "git push",
            "ok": push_ok,
            "skipped": not push_ok,
            "detail": "origin main" if push_ok else "PUSH_SKIPPED — continuing to deploy",
            "log": push_log,
        }
    )

    deploy_code, deploy_log = run_subprocess(
        [
            *firebase_cmd(),
            "deploy",
            "--only",
            "hosting:penang-pulse",
            "--non-interactive",
        ],
        timeout=600,
    )
    result["steps"].append(
        {
            "name": "firebase deploy",
            "ok": deploy_code == 0,
            "detail": "hosting:penang-pulse (entire penangpulse.com)",
            "log": deploy_log,
        }
    )

    live = f"{LIVE_HOST}/guides/{slug}/"
    if deploy_code == 0:
        bits = [f"Published → {live}"]
        if not push_ok:
            bits.append("PUSH_SKIPPED")
        result["flash"] = " · ".join(bits)
    else:
        result["flash"] = "Deploy failed — see log below."
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = "PenangGuidesEditor/3.0"

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        if path in {"/", "/index.html"}:
            self._send(200, index_page())
            return
        if path == "/series":
            slug = (qs.get("slug") or [""])[0]
            self._send(200, series_page(slug))
            return
        if path == "/new":
            series = (qs.get("series") or [""])[0]
            self._send(200, new_page(series))
            return
        if path == "/edit":
            slug = (qs.get("slug") or [""])[0]
            self._send(200, edit_page(slug))
            return
        if path == "/build":
            self._send(200, build_page())
            return
        if path == "/api/parse-maps":
            url = (qs.get("url") or [""])[0]
            payload = json.dumps(parse_maps_url(url), ensure_ascii=False).encode("utf-8")
            self._send(200, payload, "application/json; charset=utf-8")
            return
        if path == "/media-orig":
            slug = (qs.get("slug") or [""])[0]
            filename = (qs.get("file") or [""])[0]
            media_path = resolve_orig_media(slug, filename)
            if media_path is None:
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            data = media_path.read_bytes()
            ctype = mimetypes.guess_type(media_path.name)[0] or "application/octet-stream"
            self._send(200, data, ctype)
            return
        self._send(404, page_shell("Not found", "<p>Not found.</p>"))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        ctype = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)

        if path == "/create":
            data = urllib.parse.parse_qs(body.decode("utf-8"))
            title = (data.get("title") or [""])[0].strip()
            slug = (data.get("slug") or [""])[0].strip() or slugify(title)
            series_slug = (data.get("series") or [""])[0].strip()
            tasted = (data.get("tasted") or [""])[0].strip()
            series_entry = series_by_slug(series_slug) if series_slug else None
            template = "blank"
            if series_entry:
                template = series_entry.get("template") or "blank"
            if not title or not SLUG_RE.match(slug):
                self._send(
                    400,
                    new_page(series_slug, "Need a title and a simple slug (a-z, 0-9, hyphens)."),
                )
                return
            if tasted and not parse_iso_date(tasted):
                self._send(400, new_page(series_slug, "Tasting date must be YYYY-MM-DD."))
                return
            post_dir = POSTS_DIR / slug
            if post_dir.exists():
                self._send(400, new_page(series_slug, f"Slug already exists: {slug}"))
                return
            (post_dir / "media" / "orig").mkdir(parents=True)
            fields, body_md = default_post_fields(
                title,
                template=template,
                series_entry=series_entry,
                tasted=tasted,
            )
            # Orphan series slug from form when not in registry
            if series_slug and not series_entry:
                fields["series"] = series_slug
                fields["seriesTitle"] = series_slug.replace("-", " ").title()
                fields["seriesOrder"] = next_series_order(series_slug)
            apply_tasting_fields(fields)
            write_post_fields(slug, fields, body_md)
            if fields.get("series"):
                recompute_series_orders(fields["series"])
            self._redirect(f"/edit?slug={urllib.parse.quote(slug)}")
            return

        if path == "/save":
            fields, files, multi = parse_multipart(ctype, body)
            old_slug = fields.get("old_slug", "").strip() or fields.get("slug", "").strip()
            slug = fields.get("slug", "").strip()
            body_md = fields.get("body", "")
            if not is_valid_slug(slug) or not body_md.strip():
                self._send(
                    400,
                    edit_page(old_slug, "Need a valid kebab slug and a non-empty body.")
                    if is_valid_slug(old_slug)
                    else page_shell("Error", "<p>Invalid save request.</p>"),
                )
                return

            if old_slug and old_slug != slug:
                err = rename_post(old_slug, slug)
                if err:
                    self._send(400, edit_page(old_slug, err))
                    return

            # Series picker → hidden fields (JS usually syncs; enforce server-side)
            pick = fields.get("seriesPick", "").strip()
            if pick:
                entry = series_by_slug(pick)
                fields["series"] = pick
                if entry:
                    fields["seriesTitle"] = entry["title"]
                elif not fields.get("seriesTitle", "").strip():
                    fields["seriesTitle"] = pick.replace("-", " ").title()
            else:
                fields["series"] = ""
                fields["seriesTitle"] = ""
                fields["seriesOrder"] = ""

            # Checkbox omitted from multipart when unchecked
            fields["draft"] = "true" if is_draft_value(fields.get("draft", "")) else ""

            maps_url = fields.get("mapsUrl", "").strip()
            if maps_url:
                parsed_maps = parse_maps_url(maps_url)
                if not fields.get("locationName", "").strip() and parsed_maps["name"]:
                    fields["locationName"] = parsed_maps["name"]
                if not fields.get("locationLat", "").strip() and parsed_maps["lat"]:
                    fields["locationLat"] = parsed_maps["lat"]
                if not fields.get("locationLng", "").strip() and parsed_maps["lng"]:
                    fields["locationLng"] = parsed_maps["lng"]

            apply_tasting_fields(fields)

            post_dir = POSTS_DIR / slug
            if not (post_dir / "post.md").is_file() and old_slug == slug:
                self._send(400, page_shell("Error", f"<p>Unknown episode: {html.escape(slug)}</p>"))
                return
            post_dir.mkdir(parents=True, exist_ok=True)
            orig = post_dir / "media" / "orig"
            orig.mkdir(parents=True, exist_ok=True)

            roles = multi.get("media_role") or []
            labels = multi.get("media_role_label") or []
            saved = 0
            photo_additions: list[tuple[str, str, str, int]] = []
            for i, (filename, data) in enumerate(files):
                if not data:
                    continue
                role = (roles[i] if i < len(roles) else "bowl").strip().lower() or "bowl"
                other_label = labels[i] if i < len(labels) else ""
                if role == "other" and not slugify(other_label):
                    other_label = pathlib.Path(filename).stem
                ext = pathlib.Path(filename).suffix.lower() or ".jpeg"
                name = media_role_filename(slug, role, other_label, ext)
                dest = unique_media_path(orig, name)
                dest.write_bytes(data)
                saved += 1
                canon = PHOTO_ROLE_CANONICAL.get(role, role)
                if role == "other":
                    canon = slugify(other_label) or "photo"
                alt = PHOTO_ROLE_ALT.get(role) or (other_label.strip() or "Photo")
                rank = PHOTO_ROLE_RANK.get(role, 50)
                photo_additions.append((dest.name, canon, alt, rank))

            photo_additions.sort(key=lambda item: (item[3], item[0]))
            if photo_additions:
                body_md = append_photos_markdown(
                    body_md,
                    [(name, role, alt) for name, role, alt, _ in photo_additions],
                )

            write_post_fields(slug, fields, body_md)

            order_note = ""
            if fields.get("series"):
                changed = recompute_series_orders(fields["series"])
                # Refresh seriesOrder display from recomputed file
                refreshed, _ = fields_from_post(
                    (POSTS_DIR / slug / "post.md").read_text(encoding="utf-8")
                )
                fields["seriesOrder"] = refreshed.get("seriesOrder", "")
                if changed:
                    order_note = f" Reordered series ({len(changed)} file(s))."

            flash = "Saved."
            if old_slug and old_slug != slug:
                flash = f"Renamed to {slug}. Saved."
            if saved:
                flash += f" Uploaded {saved} file(s)."
            flash += order_note
            if is_draft_value(fields.get("draft", "")):
                flash += " Draft — skipped on public build."
            if fields.get("and_build"):
                self._redirect("/build")
                return
            if old_slug and old_slug != slug:
                self._redirect(f"/edit?slug={urllib.parse.quote(slug)}")
                return
            self._send(200, edit_page(slug, flash))
            return

        if path == "/publish":
            data = urllib.parse.parse_qs(body.decode("utf-8"))
            slug = (data.get("slug") or [""])[0].strip()
            intent = (data.get("intent") or [""])[0].strip()
            result = run_publish(slug, intent=intent)
            self._send(200, publish_page(slug if is_valid_slug(slug) else "?", result))
            return

        if path == "/delete":
            data = urllib.parse.parse_qs(body.decode("utf-8"))
            slug = (data.get("slug") or [""])[0].strip()
            err = delete_post(slug)
            if err:
                if is_valid_slug(slug) and (POSTS_DIR / slug / "post.md").is_file():
                    self._send(400, edit_page(slug, err))
                else:
                    self._send(400, index_page(err))
                return
            self._send(
                200,
                index_page(
                    f"Deleted {slug}. Run build to refresh public series/index output."
                ),
            )
            return

        self._send(404, page_shell("Not found", "<p>Not found.</p>"))


def main() -> int:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Penang Guides editor: http://{HOST}:{PORT}/")
    print(f"Posts: {POSTS_DIR}")
    print(f"Series registry: {SERIES_REGISTRY}")
    print(f"Build python: {python_for_build()}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

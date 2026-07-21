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
import pathlib
import re
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


def python_for_build() -> str:
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "guide"


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


def compose_post_md(fields: dict[str, str], body: str) -> str:
    """Compose post.md from structured editor fields + markdown body."""
    title = fields.get("title", "").strip() or "Untitled"
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"dek: {yaml_quote(fields.get('dek', '').strip())}",
        f"type: {yaml_quote(fields.get('type', 'text').strip() or 'text')}",
    ]
    neighbourhood = fields.get("neighbourhood", "").strip()
    if neighbourhood:
        lines.append(f"neighbourhood: {yaml_quote(neighbourhood)}")
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

    lines.append("---")
    lines.append("")
    body = body.replace("\r\n", "\n").lstrip("\n")
    if body and not body.endswith("\n"):
        body += "\n"
    return "\n".join(lines) + "\n" + body


def fields_from_post(text: str) -> tuple[dict[str, str], str]:
    meta, body = parse_frontmatter(text)
    loc = meta.get("location") if isinstance(meta.get("location"), dict) else {}
    fields = {
        "title": str(meta.get("title") or ""),
        "dek": str(meta.get("dek") or meta.get("description") or ""),
        "type": str(meta.get("type") or "text"),
        "neighbourhood": str(meta.get("neighbourhood") or meta.get("area") or ""),
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
    }
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
                "fieldNote": fields.get("fieldNote") or "",
                "updated": fields.get("updated") or "",
                "type": fields.get("type") or "text",
            }
        )
    return items


def episodes_for_series(series_slug: str) -> list[dict[str, Any]]:
    eps = [p for p in list_posts_detailed() if p.get("series") == series_slug]
    eps.sort(
        key=lambda p: (
            p.get("seriesOrder") is None,
            p.get("seriesOrder") if p.get("seriesOrder") is not None else 0,
            p.get("updated") or "",
        )
    )
    return eps


def next_series_order(series_slug: str) -> str:
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
) -> tuple[dict[str, str], str]:
    today = dt.date.today().isoformat()
    month = dt.date.today().strftime("%b %Y")

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
            "fieldNote": f"Field note · George Town · {month}",
            "updated": today,
            "series": series_slug or "mee-myself-and-i",
            "seriesTitle": series_title or "Mee Myself and I",
            "seriesOrder": series_order or next_series_order(series_slug or "mee-myself-and-i"),
            "locationName": "",
            "mapsUrl": "",
            "locationAddress": "",
            "locationLat": "",
            "locationLng": "",
        }
        body = (
            "Intro paragraph — why this bowl, where you were coming from.\n\n"
            "## Tasting notes\n\n"
            "- **Broth** — \n"
            "- **Noodles** — \n"
            "- **Toppings** — \n"
            "- **Timing / queue** — \n\n"
            "## Photos\n\n"
            "![Bowl](./media/orig/bowl.jpg)\n\n"
            "_Caption_\n\n"
            "![Context](./media/orig/context.jpg)\n\n"
            "_Caption_\n\n"
            "> Optional tip or caveat.\n"
        )
        return fields, body

    if template == "family" or (series_entry and series_entry.get("template") == "family"):
        fields = {
            "title": title,
            "dek": "",
            "type": type_val or "text",
            "neighbourhood": "",
            "fieldNote": f"Field note · Penang · {month}",
            "updated": today,
            "series": series_slug or "family-matters",
            "seriesTitle": series_title or "Family Matters",
            "seriesOrder": series_order or next_series_order(series_slug or "family-matters"),
            "locationName": "",
            "mapsUrl": "",
            "locationAddress": "",
            "locationLat": "",
            "locationLng": "",
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
            "![Moment](./media/orig/moment.jpg)\n\n"
            "_Caption_\n\n"
            "> Tip or caveat.\n"
        )
        return fields, body

    fields = {
        "title": title,
        "dek": "",
        "type": type_val or "text",
        "neighbourhood": "",
        "fieldNote": f"Field note · Penang · {month}" if series_slug else "",
        "updated": today,
        "series": series_slug,
        "seriesTitle": series_title,
        "seriesOrder": series_order,
        "locationName": "",
        "mapsUrl": "",
        "locationAddress": "",
        "locationLat": "",
        "locationLng": "",
    }
    body = (
        "Write the guide here. Use `##` headings and lists.\n\n"
        "Images: upload below, then reference as "
        "`![caption](./media/orig/filename.jpg)`.\n"
    )
    return fields, body


def parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], list[tuple[str, bytes]]]:
    """Return (fields, files) where files are (filename, data) tuples."""
    msg = email.message_from_bytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body,
        policy=email.policy.default,
    )
    fields: dict[str, str] = {}
    files: list[tuple[str, bytes]] = []
    if not msg.is_multipart():
        return fields, files
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
        fields[name] = payload.decode("utf-8", errors="replace")
    return fields, files


EDITOR_JS = r"""
(function () {
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
  const seriesOrder = document.getElementById("seriesOrder");
  const typeSelect = document.getElementById("type");

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
      if (seriesOrder && !seriesOrder.value.trim()) {
        const next = opt.getAttribute("data-next-order") || "";
        if (next) seriesOrder.value = next;
      }
    });
  }

  updateSpotPreview();
})();
"""


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
    ul.posts, ul.episodes {{ list-style: none; margin: 12px 0; padding: 0; }}
    ul.posts li, ul.episodes li {{
      display: flex; justify-content: space-between; align-items: baseline;
      gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line);
    }}
    ul.episodes li {{
      flex-wrap: wrap;
    }}
    .ep-meta {{ color: var(--muted); font-size: 0.85rem; }}
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
    .media {{ margin-top: 10px; font-size: 0.9rem; }}
    .media li {{ margin: 4px 0; }}
    pre.build {{
      margin-top: 12px; padding: 12px; background: #1c1c1a; color: #eee;
      border-radius: 8px; overflow: auto; font-size: 0.82rem; white-space: pre-wrap;
    }}
    .hint {{ margin: 6px 0 0; font-size: 0.85rem; color: var(--muted); }}
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
        f'<span class="muted">({html.escape(p["slug"])})</span></span>'
        f'<a href="/edit?slug={urllib.parse.quote(p["slug"])}">Edit</a></li>'
        for p in standalone
    ) or '<li class="muted">No standalone guides.</li>'

    body = f"""
    <p class="lede">Editorial desk for owned Guides. Series first — open a spine,
    then add episodes. Charter: <code>utilities/penang-pulse/EDITORIAL.md</code>.</p>
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
    for ep in episodes:
        order = ep.get("seriesOrder")
        order_label = f"#{order}" if order is not None else "—"
        note = html.escape(ep.get("fieldNote") or "")
        items.append(
            "<li>"
            f'<span><strong>{html.escape(ep["title"])}</strong> '
            f'<span class="ep-meta">{html.escape(order_label)} · '
            f'{html.escape(ep["slug"])}'
            f'{(" · " + note) if note else ""}</span></span>'
            f'<a href="/edit?slug={urllib.parse.quote(ep["slug"])}">Edit</a>'
            "</li>"
        )
    list_html = "".join(items) or '<li class="muted">No episodes yet — create the first one.</li>'

    body = f"""
    <p class="lede">{html.escape(dek)}</p>
    <p class="muted">
      <span class="badge">{html.escape(status)}</span>
      <span class="badge quiet">{len(episodes)} episode{"s" if len(episodes) != 1 else ""}</span>
      · slug <code>{html.escape(slug)}</code>
      · live <a href="https://penangpulse.com/guides/series/{html.escape(slug, quote=True)}/"
        target="_blank" rel="noopener">penangpulse.com/…</a>
    </p>
    <div class="actions-bar">
      <a class="btn" href="/new?series={urllib.parse.quote(slug)}">New episode in this series</a>
      <a class="btn secondary" href="/">← Desk</a>
      <a class="btn secondary" href="/build">Run build</a>
    </div>
    <div class="card">
      <h2 style="margin-top:0">Episodes</h2>
      <p class="hint">Order via each post’s <code>seriesOrder</code> field (lower first).
      Reorder by editing that number, then Save &amp; build.</p>
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

    body = f"""
    <p class="lede">Creates <code>guides/posts/&lt;slug&gt;/post.md</code> with a template skeleton.</p>
    <form class="card" method="post" action="/create">
      <label for="series">Series</label>
      <select id="series" name="series">{"".join(options)}</select>
      <p class="hint">Choosing a series pre-fills series fields, order, and template.</p>
      <label for="title">Title</label>
      <input id="title" name="title" type="text" required
        value="{html.escape(default_title)}"
        placeholder="Lean Huat Hokkien Mee" />
      <label for="slug">Slug (optional)</label>
      <input id="slug" name="slug" type="text" placeholder="lean-huat-hokkien-mee" />
      <div class="row">
        <button type="submit">Create</button>
        <a class="btn secondary" href="{
            f'/series?slug={urllib.parse.quote(series_slug)}' if series_slug else '/'
        }">Cancel</a>
      </div>
    </form>
    """
    return page_shell(heading, body, flash)


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
    orig = POSTS_DIR / slug / "media" / "orig"
    media_items = []
    if orig.is_dir():
        for path in sorted(orig.iterdir()):
            if path.is_file() and not path.name.startswith("."):
                media_items.append(
                    f"<li><code>./media/orig/{html.escape(path.name)}</code></li>"
                )
    media_html = (
        f'<ul class="media">{"".join(media_items)}</ul>'
        if media_items
        else '<p class="muted">No originals uploaded yet.</p>'
    )

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

    form = f"""
    <form class="card" method="post" action="/save" enctype="multipart/form-data">
      <input type="hidden" name="slug" value="{html.escape(slug)}" />
      {_input("title", "Title", fields.get("title", ""))}
      {_input("dek", "Dek", fields.get("dek", ""), "One-line summary — answer-shaped if you can")}
      <div class="grid2">
        <div>
          <label for="type">Type</label>
          <select id="type" name="type">{type_html}</select>
        </div>
        <div>
          {_input("updated", "Updated (YYYY-MM-DD)", fields.get("updated", ""))}
        </div>
      </div>
      {_input("neighbourhood", "Neighbourhood", fields.get("neighbourhood", ""), "Pulau Tikus")}
      {_input("fieldNote", "Field note", fields.get("fieldNote", ""), "Field note · George Town · Jul 2026")}

      <fieldset>
        <legend>Series</legend>
        <label for="seriesPick">Series</label>
        <select id="seriesPick" name="seriesPick">{"".join(pick_options)}</select>
        <input type="hidden" id="series" name="series" value="{html.escape(fields.get("series", ""))}" />
        <input type="hidden" id="seriesTitle" name="seriesTitle" value="{html.escape(fields.get("seriesTitle", ""))}" />
        {_input("seriesOrder", "Series order", fields.get("seriesOrder", ""), "1")}
        <p class="hint">Lower numbers first on the series page. Leave empty for standalone.</p>
      </fieldset>

      <fieldset>
        <legend>Spot / Google Maps</legend>
        {_input("locationName", "Venue name", loc_name, "Lean Huat Hokkien Mee", "locationName")}
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
      <label for="files">Upload to media/orig/</label>
      <input id="files" name="files" type="file" multiple accept="image/*,.heic,.heif" />
      {media_html}
      <div class="row">
        <button type="submit">Save</button>
        <button class="secondary" type="submit" name="and_build" value="1">Save &amp; build</button>
        <a class="btn secondary" href="/">Desk</a>
      </div>
    </form>
    """

    body = f"""
    <p class="muted">Editing <code>{html.escape(slug)}</code></p>
    <div class="layout">
      <div>{form}</div>
      {sidebar}
    </div>
    """
    return page_shell(f"Edit · {slug}", body, flash, EDITOR_JS, wide=True)


def build_page() -> bytes:
    cmd = [python_for_build(), str(BUILD_SCRIPT)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        status = "ok" if proc.returncode == 0 else "failed"
        flash = f"Build {status} (exit {proc.returncode})"
    except OSError as exc:
        output = str(exc)
        flash = "Build failed to start"
    body = f"""
    <p class="muted">Command: <code>{html.escape(" ".join(cmd))}</code></p>
    <pre class="build">{html.escape(output or "(no output)")}</pre>
    <div class="row"><a class="btn" href="/">Desk</a></div>
    """
    return page_shell("Build", body, flash)


class Handler(BaseHTTPRequestHandler):
    server_version = "PenangGuidesEditor/2.0"

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
            post_dir = POSTS_DIR / slug
            if post_dir.exists():
                self._send(400, new_page(series_slug, f"Slug already exists: {slug}"))
                return
            (post_dir / "media" / "orig").mkdir(parents=True)
            fields, body_md = default_post_fields(
                title, template=template, series_entry=series_entry
            )
            # Orphan series slug from form when not in registry
            if series_slug and not series_entry:
                fields["series"] = series_slug
                fields["seriesTitle"] = series_slug.replace("-", " ").title()
                fields["seriesOrder"] = next_series_order(series_slug)
            (post_dir / "post.md").write_text(
                compose_post_md(fields, body_md),
                encoding="utf-8",
            )
            self._redirect(f"/edit?slug={urllib.parse.quote(slug)}")
            return

        if path == "/save":
            fields, files = parse_multipart(ctype, body)
            slug = fields.get("slug", "").strip()
            body_md = fields.get("body", "")
            if not SLUG_RE.match(slug) or not body_md.strip():
                self._send(400, page_shell("Error", "<p>Invalid save request.</p>"))
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

            maps_url = fields.get("mapsUrl", "").strip()
            if maps_url:
                parsed_maps = parse_maps_url(maps_url)
                if not fields.get("locationName", "").strip() and parsed_maps["name"]:
                    fields["locationName"] = parsed_maps["name"]
                if not fields.get("locationLat", "").strip() and parsed_maps["lat"]:
                    fields["locationLat"] = parsed_maps["lat"]
                if not fields.get("locationLng", "").strip() and parsed_maps["lng"]:
                    fields["locationLng"] = parsed_maps["lng"]

            post_dir = POSTS_DIR / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            (post_dir / "post.md").write_text(
                compose_post_md(fields, body_md),
                encoding="utf-8",
            )
            orig = post_dir / "media" / "orig"
            orig.mkdir(parents=True, exist_ok=True)

            saved = 0
            for filename, data in files:
                name = pathlib.Path(filename).name
                if not name or name.startswith("."):
                    continue
                (orig / name).write_bytes(data)
                saved += 1

            flash = "Saved."
            if saved:
                flash += f" Uploaded {saved} file(s)."
            if fields.get("and_build"):
                self._redirect("/build")
                return
            self._send(200, edit_page(slug, flash))
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

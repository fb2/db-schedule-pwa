#!/usr/bin/env python3
"""Build Penang Pulse editorial guides into static HTML + index.json.

Reads source posts under utilities/penang-pulse/guides/posts/<slug>/post.md,
resizes media/orig images to web JPEGs, and emits:

  utilities/penang-pulse/guides/index.json
  utilities/penang-pulse/guides/<slug>/index.html
  utilities/penang-pulse/guides/<slug>/media/*.jpg

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
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "utilities" / "penang-pulse" / "guides"
POSTS_DIR = GUIDES_DIR / "posts"
ARTICLE_CSS = "article.css"

MAX_WIDTH = 1400
JPEG_QUALITY = 82

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)
IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_MD_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
ORIG_MEDIA_RE = re.compile(
    r"(?:\./)?media/orig/([^)\s\"']+)",
    re.I,
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp"}
HEIC_EXTS = {".heic", ".heif"}

TYPE_LABELS = {
    "text": "Text",
    "photo": "Photos",
    "photos": "Photos",
    "video": "Video",
}


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


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"').strip("'")
    return meta, match.group(2).lstrip("\n")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "guide"


def type_label(raw: str) -> str:
    key = (raw or "text").strip().lower()
    return TYPE_LABELS.get(key, raw.strip().title() or "Text")


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
        name = match.group(1)
        if name in media_map:
            return f"./media/{media_map[name]}"
        stem = pathlib.Path(name).stem
        return f"./media/{stem}.jpg"
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
        # Also allow lookups without worrying about case
        media_map[path.name.lower()] = out_name

    return media_map


def render_article(
    *,
    title: str,
    dek: str,
    type_name: str,
    neighbourhood: str,
    body_html: str,
    hero_src: str | None,
) -> str:
    meta_bits = []
    if neighbourhood:
        meta_bits.append(f"Neighbourhood · {html.escape(neighbourhood)}")
    meta_html = (
        f'<p class="guide-meta">{meta_bits[0]}</p>' if meta_bits else ""
    )
    dek_html = f'<p class="guide-dek">{html.escape(dek)}</p>' if dek else ""
    hero_html = ""
    if hero_src:
        hero_html = (
            f'<img class="guide-hero" src="{html.escape(hero_src, quote=True)}" alt="" '
            f'loading="eager" decoding="async" referrerpolicy="no-referrer" />\n'
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0f6e6e" />
    <meta name="description" content="{html.escape(dek or title)}" />
    <title>{html.escape(title)} — Penang Pulse</title>
    <link rel="icon" href="../../icon.svg" type="image/svg+xml" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../{ARTICLE_CSS}" />
  </head>
  <body>
    <div class="guide-topbar">
      <a class="back" href="../../">← Home</a>
      <a class="brand-mini" href="../../">Penang Pulse</a>
    </div>
{hero_html}
    <article class="guide-article">
      <p class="guide-kicker">Guide · {html.escape(type_name)}</p>
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
    type_name = type_label(meta.get("type", "text"))
    neighbourhood = meta.get("neighbourhood") or meta.get("area") or ""
    updated = meta.get("updated") or meta.get("date") or dt.date.today().isoformat()
    hero = meta.get("hero") or ""

    public_dir = GUIDES_DIR / slug
    public_media = public_dir / "media"
    if public_dir.exists():
        shutil.rmtree(public_dir)
    public_dir.mkdir(parents=True)

    media_map = process_images(post_dir, public_media, Image, heif_ok)
    body_html = md_to_html(body, media_map)

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
        body_html=body_html,
        hero_src=hero_src,
    )
    (public_dir / "index.html").write_text(html_out, encoding="utf-8")

    # Drop empty media dir
    if public_media.is_dir() and not any(public_media.iterdir()):
        public_media.rmdir()

    return {
        "slug": slug,
        "title": title,
        "dek": dek,
        "type": type_name,
        "href": f"./guides/{slug}/",
        "updated": updated,
    }


def ensure_article_css() -> None:
    css_path = GUIDES_DIR / ARTICLE_CSS
    if not css_path.is_file():
        die(f"missing {css_path.relative_to(ROOT)} — commit guides/{ARTICLE_CSS}")


def clean_stale_public(active_slugs: set[str]) -> None:
    if not GUIDES_DIR.is_dir():
        return
    reserved = {"posts", ARTICLE_CSS, "index.json"}
    for path in GUIDES_DIR.iterdir():
        if not path.is_dir():
            continue
        if path.name in reserved or path.name in active_slugs:
            continue
        if path.name.startswith("."):
            continue
        shutil.rmtree(path)
        print(f"removed stale guide output: {path.name}")


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

    posts = collect_posts(posts_dir)
    if not posts:
        print(f"no posts found under {posts_dir.relative_to(ROOT)}")
        index = {"generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "guides": []}
        (GUIDES_DIR / "index.json").write_text(
            json.dumps(index, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return 0

    guides: list[dict[str, Any]] = []
    for post_dir in posts:
        entry = build_one(post_dir, Image, heif_ok)
        if entry:
            guides.append(entry)
            print(f"built {entry['slug']}")

    guides.sort(key=lambda g: g.get("updated") or "", reverse=True)
    clean_stale_public({g["slug"] for g in guides})

    index = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "guides": guides,
    }
    (GUIDES_DIR / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(guides)} guide(s) → {GUIDES_DIR.relative_to(ROOT)}/index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Local-only Penang Pulse guides editor (not deployed).

Run from repo root or this folder:

  python3 scripts/penang-guides-editor/server.py

Then open http://127.0.0.1:8765/
"""

from __future__ import annotations

import datetime as dt
import email
import email.policy
import html
import pathlib
import re
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


ROOT = pathlib.Path(__file__).resolve().parents[2]
EDITOR_DIR = pathlib.Path(__file__).resolve().parent
POSTS_DIR = ROOT / "utilities" / "penang-pulse" / "guides" / "posts"
BUILD_SCRIPT = ROOT / "scripts" / "build-penang-guides.py"
VENV_PYTHON = EDITOR_DIR / ".venv" / "bin" / "python"
HOST = "127.0.0.1"
PORT = 8765

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def python_for_build() -> str:
    if VENV_PYTHON.is_file():
        return str(VENV_PYTHON)
    return sys.executable


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "guide"


def list_posts() -> list[dict[str, str]]:
    if not POSTS_DIR.is_dir():
        return []
    items = []
    for path in sorted(POSTS_DIR.iterdir()):
        post = path / "post.md"
        if path.is_dir() and post.is_file():
            title = path.name
            text = post.read_text(encoding="utf-8")
            for line in text.splitlines()[:20]:
                if line.lower().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                    break
            items.append({"slug": path.name, "title": title})
    return items


def default_post_md(title: str) -> str:
    today = dt.date.today().isoformat()
    return (
        f"---\n"
        f"title: {title}\n"
        f"dek: \n"
        f"type: text\n"
        f"neighbourhood: \n"
        f"updated: {today}\n"
        f"---\n\n"
        f"Write the guide here. Use `##` headings and lists.\n\n"
        f"Images: upload below, then reference as "
        f"`![caption](./media/orig/filename.jpg)`.\n"
    )


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


def page_shell(title: str, body: str, flash: str = "") -> bytes:
    flash_html = f'<p class="flash">{html.escape(flash)}</p>' if flash else ""
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)} — Penang Guides Editor</title>
  <style>
    :root {{
      --bg: #f7f6f2; --text: #1c1c1a; --muted: #6b6b66;
      --line: #ddd9d0; --accent: #0f6e6e; --card: #fff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: ui-sans-serif, system-ui, sans-serif;
      background: var(--bg); color: var(--text); line-height: 1.45;
    }}
    main {{ max-width: 52rem; margin: 0 auto; padding: 24px 16px 64px; }}
    h1 {{ font-size: 1.5rem; margin: 0 0 8px; }}
    .muted {{ color: var(--muted); font-size: 0.92rem; }}
    .flash {{
      margin: 16px 0; padding: 10px 12px; background: #e8f5f5;
      border: 1px solid #b7dede; border-radius: 8px;
    }}
    ul.posts {{ list-style: none; margin: 20px 0; padding: 0; }}
    ul.posts li {{
      display: flex; justify-content: space-between; gap: 12px;
      padding: 12px 0; border-bottom: 1px solid var(--line);
    }}
    a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
    form.card, .card {{
      margin-top: 20px; padding: 16px; background: var(--card);
      border: 1px solid var(--line); border-radius: 10px;
    }}
    label {{ display: block; font-weight: 600; margin: 12px 0 6px; font-size: 0.9rem; }}
    input[type=text], textarea, select {{
      width: 100%; padding: 10px 12px; border: 1px solid var(--line);
      border-radius: 8px; font: inherit; background: #fff;
    }}
    textarea {{ min-height: 28rem; font-family: ui-monospace, Menlo, monospace; font-size: 0.88rem; }}
    .row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    button, .btn {{
      appearance: none; border: 0; border-radius: 8px; padding: 10px 14px;
      background: var(--accent); color: #fff; font: inherit; font-weight: 600;
      cursor: pointer; display: inline-block;
    }}
    button.secondary, a.btn.secondary {{
      background: #fff; color: var(--text); border: 1px solid var(--line);
    }}
    .media {{ margin-top: 10px; font-size: 0.9rem; }}
    .media li {{ margin: 4px 0; }}
    pre.build {{
      margin-top: 12px; padding: 12px; background: #1c1c1a; color: #eee;
      border-radius: 8px; overflow: auto; font-size: 0.82rem; white-space: pre-wrap;
    }}
  </style>
</head>
<body>
  <main>
    <p class="muted"><a href="/">Guides editor</a> · local only · not deployed</p>
    <h1>{html.escape(title)}</h1>
    {flash_html}
    {body}
  </main>
</body>
</html>
"""
    return doc.encode("utf-8")


def index_page(flash: str = "") -> bytes:
    posts = list_posts()
    items = "".join(
        f'<li><span>{html.escape(p["title"])} '
        f'<span class="muted">({html.escape(p["slug"])})</span></span>'
        f'<a href="/edit?slug={urllib.parse.quote(p["slug"])}">Edit</a></li>'
        for p in posts
    ) or '<li class="muted">No posts yet.</li>'
    body = f"""
    <p class="muted">Source posts live under <code>utilities/penang-pulse/guides/posts/</code>.
    Upload originals to <code>media/orig/</code>, then run Build.</p>
    <ul class="posts">{items}</ul>
    <form class="card" method="post" action="/create">
      <strong>New guide</strong>
      <label for="title">Title</label>
      <input id="title" name="title" type="text" required placeholder="Morning at Pulau Tikus Market" />
      <label for="slug">Slug (optional)</label>
      <input id="slug" name="slug" type="text" placeholder="morning-pulau-tikus-market" />
      <div class="row">
        <button type="submit">Create</button>
        <a class="btn secondary" href="/build">Run build</a>
      </div>
    </form>
    """
    return page_shell("Penang Pulse Guides", body, flash)


def edit_page(slug: str, flash: str = "") -> bytes:
    post_path = POSTS_DIR / slug / "post.md"
    if not post_path.is_file():
        return page_shell("Not found", f"<p>Unknown slug <code>{html.escape(slug)}</code>.</p>", flash)
    content = post_path.read_text(encoding="utf-8")
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
    body = f"""
    <p class="muted">Editing <code>{html.escape(slug)}</code></p>
    <form class="card" method="post" action="/save" enctype="multipart/form-data">
      <input type="hidden" name="slug" value="{html.escape(slug)}" />
      <label for="content">post.md</label>
      <textarea id="content" name="content" required>{html.escape(content)}</textarea>
      <label for="files">Upload to media/orig/</label>
      <input id="files" name="files" type="file" multiple accept="image/*,.heic,.heif" />
      {media_html}
      <div class="row">
        <button type="submit">Save</button>
        <button class="secondary" type="submit" name="and_build" value="1">Save &amp; build</button>
        <a class="btn secondary" href="/">Back</a>
      </div>
    </form>
    """
    return page_shell(f"Edit · {slug}", body, flash)


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
    <div class="row"><a class="btn" href="/">Back</a></div>
    """
    return page_shell("Build", body, flash)


class Handler(BaseHTTPRequestHandler):
    server_version = "PenangGuidesEditor/1.0"

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
        if path == "/edit":
            slug = (qs.get("slug") or [""])[0]
            self._send(200, edit_page(slug))
            return
        if path == "/build":
            self._send(200, build_page())
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
            if not title or not SLUG_RE.match(slug):
                self._send(
                    400,
                    index_page("Need a title and a simple slug (a-z, 0-9, hyphens)."),
                )
                return
            post_dir = POSTS_DIR / slug
            if post_dir.exists():
                self._send(400, index_page(f"Slug already exists: {slug}"))
                return
            (post_dir / "media" / "orig").mkdir(parents=True)
            (post_dir / "post.md").write_text(default_post_md(title), encoding="utf-8")
            self._redirect(f"/edit?slug={urllib.parse.quote(slug)}")
            return

        if path == "/save":
            fields, files = parse_multipart(ctype, body)
            slug = fields.get("slug", "").strip()
            content = fields.get("content", "")
            if not SLUG_RE.match(slug) or not content.strip():
                self._send(400, page_shell("Error", "<p>Invalid save request.</p>"))
                return
            post_dir = POSTS_DIR / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            (post_dir / "post.md").write_text(content.replace("\r\n", "\n"), encoding="utf-8")
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
    print(f"Build python: {python_for_build()}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

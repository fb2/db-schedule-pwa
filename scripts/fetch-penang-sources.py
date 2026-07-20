#!/usr/bin/env python3
"""Fetch Penang Pulse source pages/feeds into an ignored draft folder."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "scripts" / "penang_sources.json"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def fetch(url: str, timeout: int, user_agent: str) -> tuple[int | None, str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/rss+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-MY,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            content_type = response.headers.get("content-type", "")
            return status, content_type, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("content-type", ""), error.read()
    except urllib.error.URLError as error:
        return None, str(error.reason), b""


def extension_for(url: str, content_type: str) -> str:
    lowered = (content_type or "").lower()
    if "xml" in lowered or "rss" in lowered or url.rstrip("/").endswith("feed"):
        return ".xml"
    return ".html"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--date", help="Draft date folder, default UTC today.")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--sleep", type=float, default=0.6)
    args = parser.parse_args()

    config = json.loads(pathlib.Path(args.config).read_text(encoding="utf-8"))
    run_date = args.date or utc_now().date().isoformat()
    draft_dir = ROOT / config.get("draftRoot", "private/penang-pulse") / run_date
    raw_dir = draft_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    user_agent = config.get(
        "userAgent",
        "PenangPulse/0.1 (+https://fb2.github.io/db-schedule-pwa/utilities/penang-pulse/)",
    )
    manifest = {
        "generatedAt": utc_now().isoformat(),
        "runDate": run_date,
        "sources": [],
    }

    for index, source in enumerate(config.get("sources", [])):
        if index:
            time.sleep(args.sleep)
        source_id = source["id"]
        url = source["url"]
        status, content_type, body = fetch(url, args.timeout, user_agent)
        ok = status is not None and 200 <= status < 400 and bool(body)
        ext = extension_for(url, content_type)
        relative = f"raw/{source_id}{ext}"
        path = draft_dir / relative
        if body:
            path.write_bytes(body)
        entry = {
            "id": source_id,
            "name": source.get("name"),
            "tier": source.get("tier"),
            "kind": source.get("kind"),
            "parser": source.get("parser"),
            "optional": bool(source.get("optional")),
            "url": url,
            "ok": ok,
            "status": status,
            "contentType": content_type,
            "bytes": len(body),
            "path": relative if body else None,
        }
        manifest["sources"].append(entry)
        label = "ok" if ok else "FAIL"
        print(f"[{label}] {source_id}: status={status} bytes={len(body)}")

    (draft_dir / "fetch-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {draft_dir / 'fetch-manifest.json'}")
    failed_required = [
        s for s in manifest["sources"] if not s["ok"] and not s.get("optional")
    ]
    failed_optional = [
        s for s in manifest["sources"] if not s["ok"] and s.get("optional")
    ]
    if failed_optional:
        print(f"Optional source failures (non-blocking): {len(failed_optional)}")
    if failed_required:
        print(
            f"Required source failures: {len(failed_required)} "
            "(build may still publish if sanity passes / previous feed kept)",
            file=sys.stderr,
        )
        # Soft-fail: do not block the weekly pipeline; build/publish gates decide.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

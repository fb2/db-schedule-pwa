#!/usr/bin/env python3
"""Fetch Konbini Radar source pages into an ignored draft folder."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import time
import urllib.error
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "scripts" / "konbini_sources.json"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def fetch(url: str, timeout: int) -> tuple[int | None, str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "KonbiniRadar/0.1 (+https://fb2.github.io/db-schedule-pwa/)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to source config JSON.")
    parser.add_argument("--date", help="Draft date folder, default is today's UTC date.")
    parser.add_argument("--timeout", type=int, default=25, help="Fetch timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.75, help="Delay between source requests.")
    args = parser.parse_args()

    config_path = pathlib.Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_date = args.date or utc_now().date().isoformat()
    draft_dir = ROOT / config.get("draftRoot", "private/konbini-radar") / run_date
    raw_dir = draft_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schemaVersion": 1,
        "fetchedAt": utc_now().isoformat(),
        "configPath": str(config_path.relative_to(ROOT)),
        "draftDir": str(draft_dir.relative_to(ROOT)),
        "sources": [],
    }

    for index, source in enumerate(config["sources"]):
        if index:
            time.sleep(args.sleep)

        source_id = source["id"]
        raw_path = raw_dir / f"{source_id}.html"
        status, content_type, body = fetch(source["url"], args.timeout)
        raw_path.write_bytes(body)

        ok = bool(status and 200 <= status < 400 and body)
        manifest["sources"].append(
            {
                "id": source_id,
                "name": source["name"],
                "tier": source["tier"],
                "chain": source.get("chain"),
                "url": source["url"],
                "parser": source["parser"],
                "language": source.get("language", "ja"),
                "status": status,
                "ok": ok,
                "contentType": content_type,
                "bytes": len(body),
                "rawPath": str(raw_path.relative_to(ROOT)),
            }
        )

        state = "ok" if ok else "warning"
        print(f"{state}: {source_id} status={status} bytes={len(body)}")

    (draft_dir / "fetch-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {draft_dir.relative_to(ROOT)}/fetch-manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

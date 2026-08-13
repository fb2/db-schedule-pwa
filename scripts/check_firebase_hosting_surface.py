#!/usr/bin/env python3
"""Fail Firebase Hosting deploys if required static apps are missing.

Firebase Hosting releases are complete snapshots. If a utility app directory is
missing from the checkout used for deploy, the release can silently remove that
URL. Keep this check narrow and explicit so private utilities do not undeploy
each other.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = {
    "DB Ferry root app": [
        "index.html",
        "app.js",
        "styles.css",
        "sw.js",
        "manifest.webmanifest",
        "icon.svg",
    ],
    "Utilities index": [
        "utilities/index.html",
    ],
    "Travel Plans": [
        "travel/index.html",
        "travel/app.js",
        "travel/styles.css",
        "travel/sw.js",
        "travel/manifest.webmanifest",
        "travel/icon.svg",
    ],
    "Recipe Book": [
        "utilities/recipe-book/index.html",
        "utilities/recipe-book/app.js",
        "utilities/recipe-book/styles.css",
        "utilities/recipe-book/manifest.webmanifest",
    ],
    "KCRW Tracklists": [
        "utilities/kcrw-tracklists/index.html",
        "utilities/kcrw-tracklists/app.js",
        "utilities/kcrw-tracklists/styles.css",
        "utilities/kcrw-tracklists/sw.js",
        "utilities/kcrw-tracklists/manifest.webmanifest",
        "utilities/kcrw-tracklists/icon.svg",
    ],
    "Expense Helper": [
        "utilities/expense-helper/index.html",
        "utilities/expense-helper/app.js",
        "utilities/expense-helper/styles.css",
        "utilities/expense-helper/sw.js",
        "utilities/expense-helper/manifest.webmanifest",
        "utilities/expense-helper/icon.svg",
    ],
    "Reciprocity Timer": [
        "utilities/reciprocity-timer/index.html",
        "utilities/reciprocity-timer/app.js",
        "utilities/reciprocity-timer/styles.css",
        "utilities/reciprocity-timer/sw.js",
        "utilities/reciprocity-timer/manifest.webmanifest",
        "utilities/reciprocity-timer/icon.svg",
    ],
    "Movie Shelf": [
        "utilities/movie-shelf/index.html",
        "utilities/movie-shelf/app.js",
        "utilities/movie-shelf/styles.css",
        "utilities/movie-shelf/sw.js",
        "utilities/movie-shelf/manifest.webmanifest",
        "utilities/movie-shelf/icon.svg",
        "utilities/movie-shelf/movies.js",
        "utilities/movie-shelf/trivia.js",
        "utilities/movie-shelf/quiz.js",
        "utilities/movie-shelf/collection.json",
    ],
    "Konbini Radar": [
        "utilities/konbini-radar/index.html",
        "utilities/konbini-radar/app.js",
        "utilities/konbini-radar/styles.css",
        "utilities/konbini-radar/sw.js",
        "utilities/konbini-radar/manifest.webmanifest",
        "utilities/konbini-radar/icon.svg",
        "utilities/konbini-radar/feed.json",
    ],
    "Penang Pulse": [
        "utilities/penang-pulse/index.html",
        "utilities/penang-pulse/app.js",
        "utilities/penang-pulse/styles.css",
        "utilities/penang-pulse/sw.js",
        "utilities/penang-pulse/manifest.webmanifest",
        "utilities/penang-pulse/icon.svg",
        "utilities/penang-pulse/feed.json",
        "utilities/penang-pulse/guides/index.json",
        "utilities/penang-pulse/guides/article.css",
        "utilities/penang-pulse/guides/series/mee-myself-and-i/index.html",
        "utilities/penang-pulse/guides/series/mee-myself-and-i/mee-search/index.html",
        "utilities/penang-pulse/mee-graph/viz/04-bowl-orbit.html",
        "utilities/penang-pulse/mee-graph/viz/d3.v7.min.js",
        "utilities/penang-pulse/mee-graph/viz/mee-search-thumbs.js",
    ],
}


def main() -> int:
    errors: list[str] = []
    firebase_json = read_json(ROOT / "firebase.json", errors)
    firebaserc = read_json(ROOT / ".firebaserc", errors)

    for app_name, paths in REQUIRED_PATHS.items():
        for relative_path in paths:
            path = ROOT / relative_path
            if not path.is_file():
                errors.append(f"{app_name}: missing {relative_path}")

    check_hosting_config(firebase_json, errors)
    check_targets(firebaserc, errors)

    if errors:
        print("Firebase Hosting surface check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Firebase Hosting surface check passed.")
    return 0


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")
    return {}


def check_hosting_config(firebase_json: dict, errors: list[str]) -> None:
    hosting = firebase_json.get("hosting")
    if not isinstance(hosting, list):
        errors.append(
            "firebase.json: hosting must be a list with main, konbini-radar, and penang-pulse targets"
        )
        return

    targets = {entry.get("target"): entry for entry in hosting if isinstance(entry, dict)}
    main = targets.get("main")
    konbini = targets.get("konbini-radar")
    penang = targets.get("penang-pulse")

    if not main:
        errors.append("firebase.json: missing hosting target 'main'")
    elif main.get("public") != ".":
        errors.append("firebase.json: hosting target 'main' must publish '.'")
    else:
        ignored = main.get("ignore", [])
        blocked = {
            "travel",
            "travel/",
            "travel/**",
            "utilities",
            "utilities/",
            "utilities/**",
        }
        if any(pattern in blocked for pattern in ignored):
            errors.append(
                "firebase.json: main hosting ignore list must not exclude travel/ or utilities/ wholesale"
            )

    if not konbini:
        errors.append("firebase.json: missing hosting target 'konbini-radar'")
    elif konbini.get("public") != "utilities/konbini-radar":
        errors.append("firebase.json: konbini-radar target must publish utilities/konbini-radar")

    if not penang:
        errors.append("firebase.json: missing hosting target 'penang-pulse'")
    elif penang.get("public") != "utilities/penang-pulse":
        errors.append("firebase.json: penang-pulse target must publish utilities/penang-pulse")


def check_targets(firebaserc: dict, errors: list[str]) -> None:
    hosting = (
        firebaserc.get("targets", {})
        .get("fb-personal-utilities", {})
        .get("hosting", {})
    )
    if hosting.get("main") != ["fb-personal-utilities"]:
        errors.append(".firebaserc: target 'main' must map to fb-personal-utilities")
    if hosting.get("konbini-radar") != ["fb-konbini-radar"]:
        errors.append(".firebaserc: target 'konbini-radar' must map to fb-konbini-radar")
    if hosting.get("penang-pulse") != ["fb-penang-pulse"]:
        errors.append(".firebaserc: target 'penang-pulse' must map to fb-penang-pulse")


if __name__ == "__main__":
    raise SystemExit(main())

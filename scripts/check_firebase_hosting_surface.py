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
    "Konbini Radar": [
        "utilities/konbini-radar/index.html",
        "utilities/konbini-radar/app.js",
        "utilities/konbini-radar/styles.css",
        "utilities/konbini-radar/sw.js",
        "utilities/konbini-radar/manifest.webmanifest",
        "utilities/konbini-radar/icon.svg",
        "utilities/konbini-radar/feed.json",
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
        errors.append("firebase.json: hosting must be a list with main and konbini-radar targets")
        return

    targets = {entry.get("target"): entry for entry in hosting if isinstance(entry, dict)}
    main = targets.get("main")
    konbini = targets.get("konbini-radar")

    if not main:
        errors.append("firebase.json: missing hosting target 'main'")
    elif main.get("public") != ".":
        errors.append("firebase.json: hosting target 'main' must publish '.'")
    else:
        ignored = main.get("ignore", [])
        if any(pattern.startswith("travel") or pattern.startswith("utilities") for pattern in ignored):
            errors.append("firebase.json: main hosting ignore list must not exclude travel/ or utilities/")

    if not konbini:
        errors.append("firebase.json: missing hosting target 'konbini-radar'")
    elif konbini.get("public") != "utilities/konbini-radar":
        errors.append("firebase.json: konbini-radar target must publish utilities/konbini-radar")


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


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Create a private Firestore import file for the recipe utility.

The generated JSON is intentionally written under private/ and excluded from
Firebase Hosting. Import it from the hosted recipe app after signing in.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_RECIPES_DIR = Path("/Users/fbalazs/Library/CloudStorage/Dropbox/Claude/Personal/Recipes/recipes_data")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "private" / "recipe-import.private.json"


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def ingredient_text(item: dict) -> str:
    quantity = clean_text(item.get("quantity"))
    text = clean_text(item.get("text"))
    if quantity and text:
        return f"{quantity} {text}"
    return text or quantity


def make_thumbnail_data_url(image_path: Path, size: int, quality: int) -> str:
    if not image_path.exists():
        return ""

    with tempfile.TemporaryDirectory() as tmpdir:
        thumb_path = Path(tmpdir) / image_path.name
        command = [
            "sips",
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(quality),
            "-Z",
            str(size),
            str(image_path),
            "--out",
            str(thumb_path),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        encoded = base64.b64encode(thumb_path.read_bytes()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"


def load_recipes(recipes_dir: Path, size: int, quality: int) -> list[dict]:
    recipes_by_id: dict[str, dict] = {}

    for path in sorted(recipes_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        recipe_id = clean_text(raw.get("id")) or path.stem
        if recipe_id in recipes_by_id:
            continue

        ingredients = [
            {
                "section": clean_text(item.get("section")),
                "text": ingredient_text(item),
            }
            for item in raw.get("ingredients") or []
            if ingredient_text(item)
        ]
        instructions = [
            {
                "section": clean_text(step.get("section")),
                "number": step.get("number"),
                "description": clean_text(step.get("description")),
            }
            for step in raw.get("instructions") or []
            if clean_text(step.get("description"))
        ]
        tips = [clean_text(tip) for tip in raw.get("tips") or [] if clean_text(tip)]
        tags = [clean_text(tag) for tag in raw.get("tags") or [] if clean_text(tag)]
        rating = raw.get("rating") or {}
        image_file = clean_text(raw.get("image_file"))

        recipes_by_id[recipe_id] = {
            "id": recipe_id,
            "title": clean_text(raw.get("title")),
            "url": clean_text(raw.get("url")),
            "description": clean_text(raw.get("description")),
            "author": clean_text(raw.get("author")),
            "yield": clean_text(raw.get("yield")),
            "times": raw.get("times") or {},
            "ingredients": ingredients,
            "instructions": instructions,
            "tips": tips,
            "tags": tags,
            "rating": {
                "average": rating.get("average"),
                "count": rating.get("count"),
            },
            "image": make_thumbnail_data_url(recipes_dir / image_file, size=size, quality=quality),
            "imageCredit": clean_text(raw.get("image_credit")),
        }

    return sorted(recipes_by_id.values(), key=lambda item: item["title"].casefold())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the private recipe Firestore import JSON.")
    parser.add_argument("--recipes-dir", type=Path, default=DEFAULT_RECIPES_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--thumb-size", type=int, default=360)
    parser.add_argument("--quality", type=int, default=58)
    args = parser.parse_args()

    if not shutil.which("sips"):
        raise SystemExit("This exporter requires macOS 'sips' for thumbnail generation.")
    if not args.recipes_dir.exists():
        raise SystemExit(f"Recipe data directory not found: {args.recipes_dir}")

    recipes = load_recipes(args.recipes_dir, size=args.thumb_size, quality=args.quality)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(recipes, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {args.output}")
    print(f"Recipes: {len(recipes)}")
    print(f"Size: {args.output.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()

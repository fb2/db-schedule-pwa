#!/usr/bin/env python3
"""
Clean generated KCRW downloader sidecars after offline files are prepared.

The final keepers are the listening/import artifacts:
- *.mp3
- *.tracklist.txt
- *.show.json

By default this is a dry run. Pass --apply to delete files.
"""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "private" / "kcrw-downloads"
KEEP_SUFFIXES = (".chaptered.mp3", ".mp3", ".tracklist.txt", ".show.json")
DELETE_SUFFIXES = (".episode.json", ".tracklist.json", ".ffmetadata", ".part")


def is_keeper(path: Path) -> bool:
    return any(path.name.endswith(suffix) for suffix in KEEP_SUFFIXES)


def is_cleanup_candidate(path: Path, delete_show_json: bool) -> bool:
    delete_suffixes = DELETE_SUFFIXES + ((".show.json",) if delete_show_json else ())
    return any(path.name.endswith(suffix) for suffix in delete_suffixes)


def final_stem(path: Path) -> str:
    name = path.name
    for suffix in KEEP_SUFFIXES + DELETE_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"KCRW download directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("--apply", action="store_true", help="delete cleanup candidates; default is dry-run")
    parser.add_argument(
        "--delete-show-json",
        action="store_true",
        help="also delete PWA import bundles; by default *.show.json is kept",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.output_dir.exists():
        print(f"Missing output directory: {args.output_dir}")
        return 1

    files = sorted(path for path in args.output_dir.iterdir() if path.is_file())
    keepers = [path for path in files if is_keeper(path) and not (args.delete_show_json and path.name.endswith(".show.json"))]
    candidates = [path for path in files if is_cleanup_candidate(path, args.delete_show_json)]
    ignored = [path for path in files if path not in keepers and path not in candidates]

    stems = sorted({final_stem(path) for path in files})
    missing_pairs = []
    for stem in stems:
        has_txt = any(path.name == f"{stem}.tracklist.txt" for path in files)
        has_mp3 = any(path.name == f"{stem}.mp3" or path.name == f"{stem}.chaptered.mp3" for path in files)
        if has_txt and not has_mp3:
            missing_pairs.append(f"{stem}: missing mp3")
        elif has_mp3 and not has_txt:
            missing_pairs.append(f"{stem}: missing tracklist txt")

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"{mode}: {args.output_dir}")
    print(f"Keeping {len(keepers)} file(s).")
    print(f"Deleting {len(candidates)} generated sidecar file(s).")
    if ignored:
        print(f"Ignoring {len(ignored)} unrecognized file(s).")

    if missing_pairs:
        print("\nFinal artifact warnings:")
        for warning in missing_pairs:
            print(f"  - {warning}")

    if candidates:
        print("\nCleanup candidates:")
        for path in candidates:
            print(f"  - {path.name}")

    if args.apply:
        for path in candidates:
            path.unlink()
        print(f"\nDeleted {len(candidates)} file(s).")
    else:
        print("\nNo files deleted. Re-run with --apply to clean up.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

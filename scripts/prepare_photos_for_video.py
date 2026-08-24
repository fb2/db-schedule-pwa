#!/usr/bin/env python3
"""
Prepare photos for video editing by letterboxing/pillarboxing to an exact frame size.

Creates non-destructive copies in a subfolder (default: video-prep). Originals are
never modified. Each output image is exactly the target width x height with white
borders on all four sides so the full photo is visible (no cropping).

Dependency (one-time setup, from the scripts folder):
    python3 -m venv .venv && .venv/bin/pip install Pillow

Run (from repo root or from scripts/):
    ./scripts/prepare_photos_for_video.py "/path/to/photos"
    cd scripts && ./prepare_photos_for_video.py "/path/to/photos"

The script auto-uses scripts/.venv when present.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _bootstrap_venv() -> None:
    """Re-exec with the local .venv Python when Pillow is not on system Python."""
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass

    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / ".venv"
    venv_python = venv_dir / "bin" / "python"
    if not venv_python.is_file():
        return
    if Path(sys.prefix).resolve() == venv_dir.resolve():
        return

    os.execv(str(venv_python), [str(venv_python), *sys.argv])


_bootstrap_venv()

try:
    from PIL import Image, ImageOps
except ImportError:
    script_dir = Path(__file__).resolve().parent
    print(
        "Error: Pillow is required.\n\n"
        "One-time setup:\n"
        f"    cd {script_dir} && python3 -m venv .venv && .venv/bin/pip install Pillow\n\n"
        "Then run:\n"
        f"    {script_dir}/prepare_photos_for_video.py \"/path/to/photos\"\n",
        file=sys.stderr,
    )
    raise SystemExit(1)


PRESETS = {
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic", ".heif"}


@dataclass
class FrameLayout:
    target_size: tuple[int, int]
    inner_size: tuple[int, int]
    margin_x: int
    margin_y: int


@dataclass
class ProcessResult:
    source: Path
    output: Path
    source_size: tuple[int, int]
    scaled_size: tuple[int, int]
    offset: tuple[int, int]
    ok: bool
    skipped: bool = False
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Letterbox photos to an exact video frame size (non-destructive)."
    )
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Folder containing source photos",
    )
    parser.add_argument(
        "--output-subdir",
        default="video-prep",
        help="Subfolder name for processed copies (default: video-prep)",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        help="Target resolution preset (1080p or 4k)",
    )
    parser.add_argument("--width", type=int, help="Target frame width in pixels")
    parser.add_argument("--height", type=int, help="Target frame height in pixels")
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="JPEG output quality 1-100 (default: 95)",
    )
    parser.add_argument(
        "--border-color",
        default="#FFFFFF",
        help="Border color as #RRGGBB (default: white)",
    )
    parser.add_argument(
        "--margin-pct",
        type=float,
        default=5.0,
        help="Uniform border on all four sides, as %% of frame width/height (default: 5)",
    )
    parser.add_argument(
        "--no-upscale",
        action="store_true",
        help="Do not enlarge photos smaller than the target frame",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess even if output file already exists",
    )
    parser.add_argument(
        "--format",
        choices=("jpeg", "png"),
        default="jpeg",
        help="Output image format (default: jpeg)",
    )
    return parser.parse_args()


def resolve_target_size(args: argparse.Namespace) -> tuple[int, int]:
    if args.preset:
        if args.width or args.height:
            raise SystemExit("Use either --preset or --width/--height, not both.")
        return PRESETS[args.preset]

    if args.width and args.height:
        return args.width, args.height

    if args.preset is None and args.width is None and args.height is None:
        return PRESETS["1080p"]

    raise SystemExit("Provide --preset or both --width and --height.")


def resolve_frame_layout(target_size: tuple[int, int], margin_pct: float) -> FrameLayout:
    if margin_pct < 0 or margin_pct >= 50:
        raise SystemExit("--margin-pct must be between 0 and 50.")

    tgt_w, tgt_h = target_size
    margin_x = round(tgt_w * margin_pct / 100)
    margin_y = round(tgt_h * margin_pct / 100)
    inner_w = max(1, tgt_w - 2 * margin_x)
    inner_h = max(1, tgt_h - 2 * margin_y)
    return FrameLayout(
        target_size=target_size,
        inner_size=(inner_w, inner_h),
        margin_x=margin_x,
        margin_y=margin_y,
    )


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.strip()
    if not value.startswith("#") or len(value) != 7:
        raise SystemExit(f"Invalid color {value!r}; use #RRGGBB.")
    try:
        return (
            int(value[1:3], 16),
            int(value[3:5], 16),
            int(value[5:7], 16),
        )
    except ValueError as exc:
        raise SystemExit(f"Invalid color {value!r}; use #RRGGBB.") from exc


def list_source_images(source_dir: Path) -> list[Path]:
    files = [
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    return sorted(files, key=lambda path: path.name.lower())


def output_path_for(source: Path, output_dir: Path, output_format: str) -> Path:
    suffix = ".png" if output_format == "png" else ".jpg"
    return output_dir / f"{source.stem}{suffix}"


def compute_scaled_size(
    source_size: tuple[int, int],
    target_size: tuple[int, int],
    *,
    no_upscale: bool,
) -> tuple[int, int]:
    src_w, src_h = source_size
    tgt_w, tgt_h = target_size
    if src_w <= 0 or src_h <= 0:
        raise ValueError(f"Invalid source dimensions: {source_size}")

    scale = min(tgt_w / src_w, tgt_h / src_h)
    if no_upscale:
        scale = min(scale, 1.0)

    scaled_w = max(1, round(src_w * scale))
    scaled_h = max(1, round(src_h * scale))

    # Guard against rounding pushing past the frame by a pixel.
    if scaled_w > tgt_w:
        scaled_w = tgt_w
    if scaled_h > tgt_h:
        scaled_h = tgt_h

    return scaled_w, scaled_h


def letterbox_image(
    image: Image.Image,
    layout: FrameLayout,
    border_rgb: tuple[int, int, int],
    *,
    no_upscale: bool,
) -> tuple[Image.Image, tuple[int, int], tuple[int, int]]:
    source_size = image.size
    scaled_size = compute_scaled_size(
        source_size,
        layout.inner_size,
        no_upscale=no_upscale,
    )
    resized = image.resize(scaled_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", layout.target_size, border_rgb)
    offset_x = (layout.target_size[0] - scaled_size[0]) // 2
    offset_y = (layout.target_size[1] - scaled_size[1]) // 2
    canvas.paste(resized, (offset_x, offset_y))
    return canvas, scaled_size, (offset_x, offset_y)


def save_image(image: Image.Image, path: Path, output_format: str, quality: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "png":
        image.save(path, format="PNG", optimize=True)
        return

    image.save(
        path,
        format="JPEG",
        quality=quality,
        subsampling=0,
        optimize=True,
    )


def process_one(
    source: Path,
    output_dir: Path,
    layout: FrameLayout,
    border_rgb: tuple[int, int, int],
    *,
    output_format: str,
    quality: int,
    no_upscale: bool,
    force: bool,
) -> ProcessResult:
    output = output_path_for(source, output_dir, output_format)

    if output.exists() and not force:
        return ProcessResult(
            source=source,
            output=output,
            source_size=(0, 0),
            scaled_size=(0, 0),
            offset=(0, 0),
            ok=True,
            skipped=True,
        )

    try:
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            elif image.mode == "RGBA":
                background = Image.new("RGB", image.size, border_rgb)
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert("RGB")

            source_size = image.size
            framed, scaled_size, offset = letterbox_image(
                image,
                layout,
                border_rgb,
                no_upscale=no_upscale,
            )
            save_image(framed, output, output_format, quality)

        return ProcessResult(
            source=source,
            output=output,
            source_size=source_size,
            scaled_size=scaled_size,
            offset=offset,
            ok=True,
        )
    except Exception as exc:  # noqa: BLE001 - report and continue
        return ProcessResult(
            source=source,
            output=output,
            source_size=(0, 0),
            scaled_size=(0, 0),
            offset=(0, 0),
            ok=False,
            error=str(exc),
        )


def aspect_ratio(size: tuple[int, int]) -> float:
    width, height = size
    return width / height


def verify_result(
    result: ProcessResult,
    layout: FrameLayout,
    *,
    aspect_ratio_tolerance: float = 0.02,
) -> list[str]:
    issues: list[str] = []

    if result.skipped:
        if not result.output.exists():
            issues.append("skipped output is missing")
            return issues
        if result.output.stat().st_size == 0:
            issues.append("skipped output is 0 bytes")
        return issues

    if not result.ok:
        issues.append(result.error or "processing failed")
        return issues

    if not result.output.exists():
        issues.append("output file missing")
        return issues

    size_bytes = result.output.stat().st_size
    if size_bytes == 0:
        issues.append("output is 0 bytes")
        return issues

    scaled_w, scaled_h = result.scaled_size
    tgt_w, tgt_h = layout.target_size
    inner_w, inner_h = layout.inner_size
    if scaled_w > inner_w or scaled_h > inner_h:
        issues.append(
            f"scaled content {scaled_w}x{scaled_h} exceeds inner area "
            f"{inner_w}x{inner_h} (cropped)"
        )

    off_x, off_y = result.offset
    if off_x < 0 or off_y < 0:
        issues.append(f"negative paste offset ({off_x}, {off_y})")
    if off_x + scaled_w > tgt_w or off_y + scaled_h > tgt_h:
        issues.append("paste region extends outside frame (cropped)")

    if layout.margin_x > 0 and off_y < layout.margin_y - 1:
        issues.append(
            f"top border {off_y}px is less than margin {layout.margin_y}px"
        )
    if layout.margin_y > 0 and off_x < layout.margin_x - 1:
        issues.append(
            f"left border {off_x}px is less than margin {layout.margin_x}px"
        )
    right_border = tgt_w - (off_x + scaled_w)
    bottom_border = tgt_h - (off_y + scaled_h)
    if layout.margin_x > 0 and right_border < layout.margin_x - 1:
        issues.append(
            f"right border {right_border}px is less than margin {layout.margin_x}px"
        )
    if layout.margin_y > 0 and bottom_border < layout.margin_y - 1:
        issues.append(
            f"bottom border {bottom_border}px is less than margin {layout.margin_y}px"
        )

    src_w, src_h = result.source_size
    if src_w > 0 and src_h > 0:
        src_ratio = aspect_ratio(result.source_size)
        out_ratio = aspect_ratio(result.scaled_size)
        if abs(src_ratio - out_ratio) > aspect_ratio_tolerance:
            issues.append(
                f"aspect ratio changed ({src_ratio:.4f} -> {out_ratio:.4f})"
            )

    try:
        with Image.open(result.output) as saved:
            if saved.size != layout.target_size:
                issues.append(
                    f"output size {saved.size[0]}x{saved.size[1]} != "
                    f"target {tgt_w}x{tgt_h}"
                )
    except Exception as exc:  # noqa: BLE001
        issues.append(f"cannot reopen output: {exc}")

    return issues


def print_progress(index: int, total: int, result: ProcessResult) -> None:
    prefix = f"[{index}/{total}]"
    if result.skipped:
        print(f"{prefix} skip  {result.source.name} (already exists)")
        return
    if not result.ok:
        print(f"{prefix} FAIL  {result.source.name}: {result.error}")
        return

    src_w, src_h = result.source_size
    sc_w, sc_h = result.scaled_size
    off_x, off_y = result.offset
    print(
        f"{prefix} ok    {result.source.name}: "
        f"{src_w}x{src_h} -> {sc_w}x{sc_h} @ ({off_x},{off_y})"
    )


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.expanduser().resolve()

    if not source_dir.is_dir():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return 1

    if args.quality < 1 or args.quality > 100:
        print("Error: --quality must be between 1 and 100.", file=sys.stderr)
        return 1

    target_size = resolve_target_size(args)
    layout = resolve_frame_layout(target_size, args.margin_pct)
    border_rgb = parse_color(args.border_color)
    output_dir = source_dir / args.output_subdir

    sources = list_source_images(source_dir)
    if not sources:
        print(f"No images found in {source_dir}")
        return 1

    tgt_w, tgt_h = target_size
    inner_w, inner_h = layout.inner_size
    print(f"Source:  {source_dir}")
    print(f"Output:  {output_dir}")
    print(f"Frame:   {tgt_w}x{tgt_h}")
    print(
        f"Margin:  {args.margin_pct:g}% "
        f"({layout.margin_x}px sides, {layout.margin_y}px top/bottom) "
        f"-> inner {inner_w}x{inner_h}"
    )
    print(f"Format:  {args.format}  quality={args.quality}  no_upscale={args.no_upscale}")
    print(f"Found {len(sources)} image(s)\n")

    results: list[ProcessResult] = []
    for index, source in enumerate(sources, start=1):
        result = process_one(
            source,
            output_dir,
            layout,
            border_rgb,
            output_format=args.format,
            quality=args.quality,
            no_upscale=args.no_upscale,
            force=args.force,
        )
        results.append(result)
        print_progress(index, len(sources), result)

    converted = sum(1 for item in results if item.ok and not item.skipped)
    skipped = sum(1 for item in results if item.skipped)
    failed = sum(1 for item in results if not item.ok)

    print("\nSanity check")
    issues_by_file: dict[str, list[str]] = {}
    for result in results:
        if not result.ok:
            continue
        file_issues = verify_result(result, layout)
        if file_issues:
            issues_by_file[result.source.name] = file_issues

    if issues_by_file:
        print("Issues found:")
        for name, file_issues in issues_by_file.items():
            for issue in file_issues:
                print(f"  - {name}: {issue}")
    else:
        checked = converted + skipped
        print(f"All {checked} output file(s) passed checks.")

    print("\nSummary")
    print(f"  converted: {converted}")
    print(f"  skipped:   {skipped}")
    print(f"  failed:    {failed}")
    print(f"  total:     {len(results)}")

    return 1 if failed or issues_by_file else 0


if __name__ == "__main__":
    raise SystemExit(main())

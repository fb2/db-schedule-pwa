#!/usr/bin/env python3
"""
Download a public KCRW episode MP3 and its accompanying track list.

By default this targets the Chris Douridas episode from Apr 26, 2026. Pass a
different KCRW episode URL to reuse the same discovery flow.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_EPISODE_URL = (
    "https://www.kcrw.com/shows/chris-douridas/stories/"
    "new-mia-doi-todd-a-return-to-form-for-jack-white-and-a-touch-of-turkish-culture"
)
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "private" / "kcrw-downloads"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def request(url: str) -> Request:
    return Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.kcrw.com/",
        },
    )


def fetch_text(url: str) -> str:
    with urlopen(request(url), timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def fetch_json(url: str) -> object:
    with urlopen(request(url), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = re.sub(r"<[^>]+>", "", str(value))
    return html.unescape(text).strip()


def slugify(value: str, fallback: str = "kcrw-episode") -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug[:120] or fallback


def extract_page_title(page_html: str) -> str:
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", page_html, flags=re.S)
    if h1_match:
        return clean_text(h1_match.group(1))

    title_match = re.search(r"<title[^>]*>(.*?)</title>", page_html, flags=re.S)
    if title_match:
        return clean_text(title_match.group(1)).removesuffix("| KCRW").strip()

    return "KCRW Episode"


def extract_byline_date(page_html: str) -> str:
    match = re.search(r'dateTime="(\d{4}-\d{2}-\d{2})T', page_html)
    return match.group(1) if match else ""


def extract_meta_image(page_html: str) -> str:
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html, flags=re.I)
        if match:
            return html.unescape(match.group(1))
    return ""


def date_token(byline_date: str) -> str:
    if not byline_date:
        return ""
    year, month, day = byline_date.split("-")
    return f"{int(month)}_{int(day)}_{year}"


def escaped_json_key_pattern(key: str) -> str:
    return rf'\\?"{re.escape(key)}\\?"\s*:\s*\\?"'


def iter_key_values(page_html: str, key: str) -> list[tuple[int, str]]:
    pattern = escaped_json_key_pattern(key) + r'([^"\\]+)'
    return [(match.start(), match.group(1)) for match in re.finditer(pattern, page_html)]


def nearby_float(page_html: str, start: int, key: str, limit: int = 700) -> float | None:
    window = page_html[start : start + limit]
    match = re.search(escaped_json_key_pattern(key).removesuffix(r'\\?"') + r"([0-9.]+)", window)
    if not match:
        match = re.search(rf'\\?"{re.escape(key)}\\?"\s*:\s*([0-9.]+)', window)
    return float(match.group(1)) if match else None


def discover_episode(page_html: str) -> dict[str, object]:
    title = extract_page_title(page_html)
    byline_date = extract_byline_date(page_html)
    media_matches = [(pos, url) for pos, url in iter_key_values(page_html, "mediaUrl") if url.lower().endswith(".mp3")]
    playlist_matches = iter_key_values(page_html, "apiUrl")

    if not media_matches:
        raise ValueError("Could not find a public MP3 mediaUrl in the episode page.")
    if not playlist_matches:
        raise ValueError("Could not find a public tracklist apiUrl in the episode page.")

    token = date_token(byline_date)
    chosen_media = next(((pos, url) for pos, url in media_matches if token and token in url), media_matches[-1])
    media_pos, media_url = chosen_media

    later_playlists = [(pos, url) for pos, url in playlist_matches if pos > media_pos]
    playlist_pos, playlist_url = min(
        later_playlists or playlist_matches,
        key=lambda item: abs(item[0] - media_pos),
    )

    return {
        "title": title,
        "date": byline_date,
        "media_url": media_url,
        "duration": nearby_float(page_html, media_pos, "duration"),
        "playlist_url": playlist_url,
        "playlist_id": playlist_url.rstrip("/").rsplit("/", 1)[-1],
        "playlist_position": playlist_pos,
        "image_url": extract_meta_image(page_html),
    }


def normalize_tracks(raw_tracks: list[dict]) -> list[dict]:
    tracks = sorted(raw_tracks, key=lambda item: int(item.get("offset") or 0))
    return [
        {
            "offset": int(track.get("offset") or 0),
            "time": clean_text(track.get("time")),
            "host": clean_text(track.get("host")),
            "artist": clean_text(track.get("artist")),
            "title": clean_text(track.get("title")),
            "album": clean_text(track.get("album")),
            "label": clean_text(track.get("label")),
            "year": clean_text(track.get("year")),
            "comments": clean_text(track.get("comments")),
            "play_id": track.get("play_id"),
        }
        for track in tracks
    ]


def format_timestamp(seconds: float) -> str:
    whole_seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def track_display_title(track: dict) -> str:
    artist = clean_text(track.get("artist"))
    title = clean_text(track.get("title"))
    if artist == "[BREAK]":
        return "[BREAK]"
    if artist and title:
        return f"{artist} - {title}"
    return title or artist or "Untitled"


def make_track_id(track: dict, index: int) -> str:
    play_id = clean_text(track.get("play_id"))
    parts = [str(index + 1).zfill(3), clean_text(track.get("artist")), clean_text(track.get("title")), play_id]
    return slugify("-".join(part for part in parts if part), fallback=f"track-{index + 1:03d}")


def make_show_bundle(source_url: str, episode: dict[str, object], tracks: list[dict]) -> dict:
    show_id = slugify(f"{episode.get('date') or 'kcrw'}-{episode['title']}")
    host = next((track.get("host") for track in tracks if track.get("host")), "")
    bundled_tracks = []
    for index, track in enumerate(tracks):
        bundled_tracks.append(
            {
                "id": make_track_id(track, index),
                "offset": track["offset"],
                "time": track["time"],
                "artist": track["artist"],
                "title": track["title"],
                "album": track["album"],
                "label": track["label"],
                "year": track["year"],
                "comments": track["comments"],
                "playId": track["play_id"],
                "ordinal": index,
            }
        )

    return {
        "schema": "kcrw-show-bundle-v1",
        "show": {
            "id": show_id,
            "title": episode["title"],
            "date": episode.get("date") or "",
            "host": host,
            "sourceUrl": source_url,
            "mediaUrl": episode["media_url"],
            "playlistUrl": episode["playlist_url"],
            "playlistId": episode["playlist_id"],
            "duration": episode.get("duration"),
            "imageUrl": episode.get("image_url") or "",
            "trackCount": len(bundled_tracks),
        },
        "tracks": bundled_tracks,
    }


def write_tracklists(base_path: Path, tracks: list[dict], episode: dict[str, object]) -> tuple[Path, Path]:
    json_path = base_path.with_suffix(".tracklist.json")
    txt_path = base_path.with_suffix(".tracklist.txt")

    json_path.write_text(json.dumps(tracks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        str(episode["title"]),
        f"Date: {episode.get('date') or 'unknown'}",
        f"Playlist: {episode['playlist_url']}",
        "",
    ]
    for track in tracks:
        details = [format_timestamp(track["offset"]), track_display_title(track)]
        if track.get("album"):
            details.append(f"album: {track['album']}")
        if track.get("label"):
            details.append(f"label: {track['label']}")
        lines.append(" | ".join(details))

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".part")

    with urlopen(request(url), timeout=60) as response, tmp_path.open("wb") as output:
        total = int(response.headers.get("Content-Length") or 0)
        downloaded = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\rDownloading audio: {pct:5.1f}%", end="", file=sys.stderr)
        if total:
            print(file=sys.stderr)

    tmp_path.replace(output_path)


def ffmetadata_escape(value: object) -> str:
    text = clean_text(value)
    return text.replace("\\", "\\\\").replace("=", r"\=").replace(";", r"\;").replace("#", r"\#").replace("\n", r"\n")


def chapter_tracks(
    tracks: list[dict],
    duration_seconds: float | None,
    include_breaks: bool,
    offset_seconds: float | None,
) -> tuple[list[tuple[int, str]], float]:
    usable = [track for track in tracks if include_breaks or track.get("artist") != "[BREAK]"]
    if not usable:
        return [], 0.0

    if offset_seconds is None:
        if duration_seconds and max(track["offset"] for track in usable) > duration_seconds:
            offset_seconds = max(track["offset"] for track in usable) - duration_seconds
        else:
            offset_seconds = 0.0

    chapters = []
    for track in usable:
        start = int(round((track["offset"] - offset_seconds) * 1000))
        if start < 0:
            continue
        if duration_seconds and start >= int(duration_seconds * 1000):
            continue
        chapters.append((start, track_display_title(track)))

    unique_chapters = []
    seen_starts = set()
    for start, title in sorted(chapters):
        if start in seen_starts:
            continue
        seen_starts.add(start)
        unique_chapters.append((start, title))

    return unique_chapters, offset_seconds


def write_ffmetadata(
    metadata_path: Path,
    episode: dict[str, object],
    tracks: list[dict],
    duration_seconds: float | None,
    include_breaks: bool,
    offset_seconds: float | None,
) -> tuple[int, float]:
    chapters, applied_offset = chapter_tracks(tracks, duration_seconds, include_breaks, offset_seconds)
    duration_ms = int((duration_seconds or 0) * 1000)

    lines = [
        ";FFMETADATA1",
        f"title={ffmetadata_escape(episode['title'])}",
        "artist=KCRW",
        "album=Chris Douridas",
    ]
    if episode.get("date"):
        lines.append(f"date={ffmetadata_escape(episode['date'])}")

    for index, (start, title) in enumerate(chapters):
        if index + 1 < len(chapters):
            end = chapters[index + 1][0]
        elif duration_ms:
            end = duration_ms
        else:
            end = start + 1
        if end <= start:
            continue
        lines.extend(
            [
                "",
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={start}",
                f"END={end}",
                f"title={ffmetadata_escape(title)}",
            ]
        )

    metadata_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(chapters), applied_offset


def add_chapters(mp3_path: Path, metadata_path: Path, chaptered_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is not installed or not on PATH; install it to write MP3 chapters.")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(mp3_path),
        "-i",
        str(metadata_path),
        "-map_metadata",
        "1",
        "-codec",
        "copy",
        "-id3v2_version",
        "3",
        str(chaptered_path),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=DEFAULT_EPISODE_URL, help="KCRW episode URL")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"directory for downloads (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("--skip-audio", action="store_true", help="only write episode metadata and track lists")
    parser.add_argument("--chapters", action="store_true", help="write a chaptered MP3 with ffmpeg")
    parser.add_argument("--include-breaks", action="store_true", help="include [BREAK] entries as chapters")
    parser.add_argument(
        "--chapter-offset-seconds",
        type=float,
        default=None,
        help="subtract this many seconds from playlist offsets; default auto-fits to archived audio length",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        page_html = fetch_text(args.url)
        episode = discover_episode(page_html)
        raw_tracks = fetch_json(str(episode["playlist_url"]))
        if not isinstance(raw_tracks, list):
            raise ValueError("Tracklist API did not return a list.")
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    tracks = normalize_tracks(raw_tracks)
    base_name = f"{episode.get('date') or 'kcrw'}-{slugify(str(episode['title']))}"
    base_path = args.output_dir / base_name
    metadata_path = base_path.with_suffix(".episode.json")
    bundle_path = base_path.with_suffix(".show.json")
    mp3_path = base_path.with_suffix(".mp3")

    metadata_path.write_text(json.dumps(episode, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bundle_path.write_text(json.dumps(make_show_bundle(args.url, episode, tracks), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tracklist_json, tracklist_txt = write_tracklists(base_path, tracks, episode)

    print(f"Episode: {episode['title']}")
    print(f"Audio URL: {episode['media_url']}")
    print(f"Tracklist API: {episode['playlist_url']}")
    print(f"Wrote: {metadata_path}")
    print(f"Wrote: {bundle_path}")
    print(f"Wrote: {tracklist_json}")
    print(f"Wrote: {tracklist_txt}")

    if not args.skip_audio:
        if mp3_path.exists():
            print(f"Audio already exists: {mp3_path}")
        else:
            download_file(str(episode["media_url"]), mp3_path)
            print(f"Wrote: {mp3_path}")

    if args.chapters:
        ffmetadata_path = base_path.with_suffix(".ffmetadata")
        chaptered_path = base_path.with_name(base_path.name + ".chaptered.mp3")
        chapter_count, applied_offset = write_ffmetadata(
            ffmetadata_path,
            episode,
            tracks,
            float(episode["duration"]) if episode.get("duration") else None,
            args.include_breaks,
            args.chapter_offset_seconds,
        )
        print(f"Wrote: {ffmetadata_path}")
        print(f"Chapter offset: {applied_offset:.1f}s; chapters: {chapter_count}")
        if not mp3_path.exists():
            print("Error: cannot write chapters because the MP3 was not downloaded.", file=sys.stderr)
            return 1
        try:
            add_chapters(mp3_path, ffmetadata_path, chaptered_path)
        except (RuntimeError, subprocess.CalledProcessError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(f"Wrote: {chaptered_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

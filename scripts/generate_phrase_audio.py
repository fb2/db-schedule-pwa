#!/usr/bin/env python3
"""Generate Malay MP3s for Phrase Cards and optionally upload them to Storage.

Uses Application Default Credentials. Enable Cloud Text-to-Speech on the
Firebase project first:

  gcloud services enable texttospeech.googleapis.com --project fb-personal-utilities

Audio stays under private/phrase-audio/ and is not hosted as public files.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LESSONS = ROOT / "utilities" / "phrase-cards" / "lessons.json"
DEFAULT_OUT = ROOT / "private" / "phrase-audio"
PROJECT_ID = "fb-personal-utilities"
DEFAULT_BUCKET = "fb-personal-utilities.firebasestorage.app"
TTS_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Phrase Cards TTS clips.")
    parser.add_argument("--lessons", type=Path, default=DEFAULT_LESSONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--voice", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    pack = json.loads(args.lessons.read_text(encoding="utf-8"))
    language = pack.get("language") or "ms"
    voice = args.voice or pack.get("voice") or "ms-MY-Wavenet-A"
    locale = pack.get("locale") or "ms-MY"
    lines = [
        line
        for day in pack.get("days", [])
        for line in day.get("lines", [])
    ]
    if args.limit:
        lines = lines[: args.limit]

    token = access_token()
    out_dir = args.out / language
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for index, line in enumerate(lines, start=1):
        line_id = line["id"]
        path = out_dir / f"{line_id}.mp3"
        if path.exists() and not args.force:
            skipped += 1
            if args.upload:
                upload_object(token, args.bucket, f"phraseAudio/{language}/{line_id}.mp3", path)
            continue
        text = (line.get("speak") or line.get("text") or "").strip()
        if not text:
            print(f"skip empty {line_id}")
            continue
        print(f"[{index}/{len(lines)}] {line_id}: {text}")
        audio = synthesize(token, text, locale, voice)
        path.write_bytes(audio)
        created += 1
        if args.upload:
            upload_object(token, args.bucket, f"phraseAudio/{language}/{line_id}.mp3", path)
        time.sleep(0.05)

    print(f"Created {created}, skipped {skipped}, total {len(lines)}.")
    return 0


def access_token() -> str:
    for command in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        result = subprocess.run(command, capture_output=True, text=True)
        token = result.stdout.strip()
        if result.returncode == 0 and token:
            return token
    raise RuntimeError("Could not get a gcloud access token. Run `gcloud auth login`.")


def synthesize(token: str, text: str, locale: str, voice: str) -> bytes:
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": locale, "name": voice},
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 0.9,
        },
    }
    request = urllib.request.Request(
        TTS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": PROJECT_ID,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"TTS failed: {error.read().decode('utf-8', errors='replace')}") from error
    audio = body.get("audioContent")
    if not audio:
        raise RuntimeError("TTS response had no audioContent.")
    return base64.b64decode(audio)


def upload_object(token: str, bucket: str, name: str, path: Path) -> None:
    query = urllib.parse.urlencode({"uploadType": "media", "name": name})
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o?{query}"
    request = urllib.request.Request(
        url,
        data=path.read_bytes(),
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": PROJECT_ID,
            "Content-Type": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Upload failed for {name}: {error.read().decode('utf-8', errors='replace')}") from error


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Headless smoke test for the unlisted EPAM workshop landing page.

Spawns `python3 -m http.server` against utilities/penang-pulse, then drives the
workshop page in Chromium (desktop) and WebKit + Chromium (mobile) to check that
the page renders, the illustrated map is interactive, and the key content blocks
are present.

Run:
    cd scripts/workshop-page-smoke
    ./run.sh

or directly:
    PLAYWRIGHT_BROWSERS_PATH="$PWD/.browsers" .venv/bin/python smoke.py

Options:
    --keep-screenshots   write PNGs of each viewport into ./screenshots/
    --port N             serve on a specific port (default: an ephemeral free port)
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "utilities" / "penang-pulse"
PAGE_PATH = "/workshops/epam-apac-pods-2026/"
MDAC_URL = "https://imigresen-online.imi.gov.my/mdac/main"
MEE_SERIES_HREF = "../../guides/series/mee-myself-and-i/"

# Every pin key must be reachable from both the map and the side list.
PIN_KEYS = ["airport", "hotel", "balihai", "ferringhi", "fort", "georgetown", "hill"]

VIEWPORTS = [
    # label, browser, viewport, is_mobile
    ("desktop-chromium", "chromium", {"width": 1280, "height": 800}, False),
    ("mobile-chromium", "chromium", {"width": 390, "height": 844}, True),
    ("mobile-webkit", "webkit", {"width": 390, "height": 844}, True),
]


@dataclass
class Results:
    passed: int = 0
    failures: list[str] = field(default_factory=list)

    def check(self, label: str, ok: bool, detail: str = "") -> bool:
        if ok:
            self.passed += 1
            print(f"  ok   {label}")
        else:
            self.failures.append(f"{label}{f' — {detail}' if detail else ''}")
            print(f"  FAIL {label}{f' — {detail}' if detail else ''}")
        return ok


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=SITE_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            with urllib.request.urlopen(base + PAGE_PATH, timeout=1) as response:
                if response.status == 200:
                    return proc
        except (urllib.error.URLError, OSError):
            time.sleep(0.1)
    proc.terminate()
    raise RuntimeError(f"local server did not come up on {base}")


def http_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def run_viewport(playwright, label, browser_name, viewport, is_mobile, base_url, results, shots_dir):
    print(f"\n[{label}] {browser_name} {viewport['width']}x{viewport['height']}")
    browser = getattr(playwright, browser_name).launch()
    context_args = {"viewport": viewport}
    if is_mobile:
        context_args["is_mobile"] = True
        context_args["has_touch"] = True
        context_args["device_scale_factor"] = 3
    if browser_name == "webkit":
        # WebKit rejects the Chromium-only is_mobile flag.
        context_args.pop("is_mobile", None)
    context = browser.new_context(**context_args)
    page = context.new_page()

    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: console_errors.append(str(exc)))
    failed_requests: list[str] = []
    page.on(
        "requestfailed",
        lambda request: failed_requests.append(f"{request.url} ({request.failure})"),
    )

    response = page.goto(base_url + PAGE_PATH, wait_until="load")
    results.check(f"{label}: page returns 200", response is not None and response.status == 200,
                  f"status={response.status if response else 'none'}")

    # --- chrome / brand ---
    results.check(f"{label}: unlisted (noindex,nofollow)",
                  "noindex" in (page.locator('meta[name="robots"]').get_attribute("content") or ""))
    results.check(f"{label}: Penang Pulse brand links home",
                  page.locator('.hero-brand[href="../../"]').first.is_visible())
    results.check(f"{label}: workshop sub-head visible",
                  "EPAM APAC Business Pods Workshop" in (page.locator("h1").first.inner_text()))
    results.check(f"{label}: hero photo loaded",
                  page.evaluate("() => { const i = document.querySelector('.hero-img');"
                                " return !!i && i.complete && i.naturalWidth > 0; }"))
    results.check(f"{label}: EPAM logo rendered",
                  page.evaluate("() => { const i = document.querySelector('.epam-mark img');"
                                " return !!i && i.complete && i.naturalWidth > 0; }"))

    # --- key sections ---
    for section_label, selector in [
        ("welcome", "#welcome-title"),
        ("map", "#map-title"),
        ("tips", "#tips-title"),
        ("what to see", "#see-title"),
        ("food", "#food-title"),
        ("team moments", "#team-title"),
        ("events", "#events-title"),
    ]:
        locator = page.locator(selector).first
        locator.scroll_into_view_if_needed()
        results.check(f"{label}: section visible — {section_label}", locator.is_visible())

    # --- links ---
    mdac = page.locator("#mdacLink").first
    mdac.scroll_into_view_if_needed()
    results.check(f"{label}: MDAC link visible", mdac.is_visible())
    results.check(f"{label}: MDAC href is the official Imigresen page",
                  mdac.get_attribute("href") == MDAC_URL, mdac.get_attribute("href") or "")
    results.check(f"{label}: auto gates tip present",
                  page.get_by_text("auto gates", exact=False).first.is_visible())
    mee = page.locator(f'a[href="{MEE_SERIES_HREF}"]').first
    mee.scroll_into_view_if_needed()
    results.check(f"{label}: Mee Myself and I link present", mee.is_visible())
    results.check(f"{label}: no link to the guides index JSON or feed",
                  page.locator('a[href*="index.json"], a[href*="feed.json"]').count() == 0)

    # --- map structure ---
    page.locator("#mapStage").scroll_into_view_if_needed()
    results.check(f"{label}: map SVG present", page.locator("#mapStage svg.map-svg").is_visible())
    results.check(f"{label}: all {len(PIN_KEYS)} pins rendered",
                  page.locator("#mapStage .pin").count() == len(PIN_KEYS),
                  f"found {page.locator('#mapStage .pin').count()}")
    results.check(f"{label}: POI list mirrors the pins",
                  page.locator(".poi-item").count() == len(PIN_KEYS),
                  f"found {page.locator('.poi-item').count()}")
    results.check(f"{label}: legend visible", page.locator(".legend").first.is_visible())
    results.check(f"{label}: hotel popover open by default",
                  page.locator("#pop-hotel").evaluate("el => el.classList.contains('is-open')"))

    # --- map interaction: pins ---
    for key in PIN_KEYS:
        pin = page.locator(f'#mapStage .pin[data-pin="{key}"]')
        popover_id = pin.get_attribute("aria-controls")
        pin.click()
        opened = page.locator(f"#{popover_id}")
        results.check(
            f"{label}: pin click opens popover — {key}",
            opened.evaluate("el => el.classList.contains('is-open')")
            and pin.get_attribute("aria-expanded") == "true",
        )
        results.check(
            f"{label}: only one popover open — {key}",
            page.locator(".popover.is-open").count() == 1,
            f"open={page.locator('.popover.is-open').count()}",
        )
        page.keyboard.press("Escape")

    # --- map interaction: side list opens the matching popover ---
    for key in PIN_KEYS:
        item = page.locator(f'.poi-item[data-pin="{key}"]')
        item.scroll_into_view_if_needed()
        item.click()
        expected_id = page.locator(f'#mapStage .pin[data-pin="{key}"]').get_attribute("aria-controls")
        open_ids = page.locator(".popover.is-open").evaluate_all("els => els.map(el => el.id)")
        results.check(
            f"{label}: POI list opens matching popover — {key}",
            open_ids == [expected_id],
            f"open={open_ids} expected=[{expected_id}]",
        )
        results.check(
            f"{label}: POI item marked current — {key}",
            item.get_attribute("aria-current") == "true",
        )
        page.keyboard.press("Escape")

    results.check(f"{label}: Escape closes popovers", page.locator(".popover.is-open").count() == 0)

    # --- close button ---
    page.locator('.poi-item[data-pin="hotel"]').click()
    page.locator("#pop-hotel .popover-close").click()
    results.check(f"{label}: close button dismisses popover",
                  page.locator(".popover.is-open").count() == 0)

    # --- layout sanity: no horizontal overflow on mobile ---
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    results.check(f"{label}: no horizontal overflow", overflow <= 2, f"{overflow}px")

    # --- images and console ---
    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1200)
    broken = page.evaluate(
        "() => Array.from(document.images)"
        ".filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.src)"
    )
    results.check(f"{label}: no broken images", not broken, ", ".join(broken))
    results.check(f"{label}: no failed requests", not failed_requests, "; ".join(failed_requests))
    results.check(f"{label}: no console errors", not console_errors, "; ".join(console_errors))

    if shots_dir:
        shots_dir.mkdir(parents=True, exist_ok=True)
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        page.screenshot(path=str(shots_dir / f"{label}-full.png"), full_page=True)

    context.close()
    browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-screenshots", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    os.environ.setdefault(
        "PLAYWRIGHT_BROWSERS_PATH", str(Path(__file__).resolve().parent / ".browsers")
    )

    port = args.port or free_port()
    print(f"serving {SITE_ROOT} on http://127.0.0.1:{port}")
    server = start_server(port)
    base_url = f"http://127.0.0.1:{port}"
    shots_dir = Path(__file__).resolve().parent / "screenshots" if args.keep_screenshots else None
    results = Results()

    try:
        print("\n[http]")
        results.check("workshop page returns 200", http_status(base_url + PAGE_PATH) == 200)
        results.check("site root still returns 200", http_status(base_url + "/") == 200)

        with sync_playwright() as playwright:
            for label, browser_name, viewport, is_mobile in VIEWPORTS:
                try:
                    run_viewport(playwright, label, browser_name, viewport, is_mobile,
                                 base_url, results, shots_dir)
                except PlaywrightError as exc:
                    results.check(f"{label}: run completed", False, str(exc).splitlines()[0])
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        print("\nlocal server stopped")

    total = results.passed + len(results.failures)
    print(f"\n{results.passed}/{total} checks passed")
    if results.failures:
        print("\nfailures:")
        for failure in results.failures:
            print(f"  - {failure}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

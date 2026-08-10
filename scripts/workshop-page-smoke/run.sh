#!/usr/bin/env bash
# Headless smoke test for the unlisted EPAM workshop landing page.
# Spawns its own http.server against utilities/penang-pulse and tears it down again.
#
#   ./run.sh                      # desktop + mobile checks
#   ./run.sh --keep-screenshots   # also write screenshots/
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -x .venv/bin/python ]]; then
  echo "Setting up venv…"
  python3 -m venv .venv
  .venv/bin/pip -q install -r requirements.txt
fi

export PLAYWRIGHT_BROWSERS_PATH="$PWD/.browsers"

if [[ ! -d .browsers ]]; then
  echo "Downloading Playwright browsers (~850 MB, one time)…"
  .venv/bin/python -m playwright install chromium webkit
fi

exec .venv/bin/python smoke.py "$@"

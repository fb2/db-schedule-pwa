# Konbini Radar Weekly Agent

Use this runbook in Cursor once a week to refresh the public Konbini Radar feed. The fetch/build scripts are deterministic; the agentic part is limited to source-grounded editorial review and final publication.

## Goal

Create `utilities/konbini-radar/feed.json` from current Japanese convenience-store product sources, with an English weekly intro and concise context for English readers.

Follow `scripts/konbini_translation_guidance.md` when adjusting glossary tables or editorial English.

## Constraints

- No login, API keys, Firebase, or database.
- Do not publish raw scrape artifacts. They belong under `private/konbini-radar/`, which is ignored.
- Do not copy full Japanese article text or full translations into the feed.
- Public feed content should be English-first. Keep Japanese source text only in trace fields such as `nameJa`, `regionsJa`, `titleJa`, or `snippetJa`.
- Keep editorial claims source-grounded. Do not describe taste unless a review source actually tried the item.
- Treat official chain pages as availability sources. Treat blogs, media, PR, and rankings as context or hotness signals.

## Recommended Schedule

- Mon 11:30 JST: primary weekly source fetch, draft review, and publish if sanity checks pass.
- Tue 09:30 JST: sanity rerun to catch late official page updates or parser drift.
- Fri 11:30 JST: optional deal/campaign refresh for short-window promotions.

## Weekly Steps

1. Fetch configured sources:

   ```sh
   python3 scripts/fetch-konbini-sources.py
   ```

2. Build a draft feed:

   ```sh
   python3 scripts/build-konbini-feed.py
   ```

3. Review the generated draft under the newest `private/konbini-radar/YYYY-MM-DD/` folder:

   - Check `fetch-manifest.json` for failed or unexpectedly tiny source fetches.
   - Check `feed.draft.json` warnings.
   - Confirm the top items have visible `scoreReasons`.
   - Confirm short-window or regional items have `timeGate` where appropriate.
   - Confirm `intro` summarizes the week without inventing claims.
   - Confirm UI-facing fields such as `name`, `category`, `regions`, `summary`, `englishContext`, and local signal display text are English.

4. If needed, adjust parsers or source config and rebuild the draft. Prefer parser/config fixes over manual feed edits.

5. Publish the reviewed feed:

   ```sh
   python3 scripts/build-konbini-feed.py --publish
   ```

   `--publish` is fail-closed: the script builds `private/konbini-radar/YYYY-MM-DD/feed.draft.json`, runs required source and feed sanity checks, then atomically replaces `utilities/konbini-radar/feed.json` only if validation passes. If validation fails, the public feed is not modified and the error output includes the 7-Eleven, FamilyMart, Lawson, and total product counts against their thresholds.

   Emergency override:

   ```sh
   python3 scripts/build-konbini-feed.py --publish --force-publish
   ```

   Use `--force-publish` only after manually inspecting the fetched raw HTML and draft feed. Do not use older bypass flags to publish a broken weekly feed unless paired with this explicit emergency override.

6. Test locally:

   ```sh
   python3 -m http.server 5173
   ```

   Open `http://localhost:5173/utilities/konbini-radar/`.

7. Commit/upload only the public app/feed and script changes. Do not commit `private/`.

   Do not commit, push, or deploy a weekly refresh unless `--publish` succeeds and the major-three sanity checks pass. No Firebase deploy is needed for ordinary Konbini Radar static feed/script changes.

## Editorial Checklist

- Weekly intro mentions the strongest visible themes: collabs, limited items, seasonal flavors, regional finds, or standout secondary-store items.
- English context explains Japanese terms like:
  - `監修`: chef, restaurant, or brand-supervised item.
  - `数量限定`: limited quantity.
  - `期間限定`: available for a limited period.
  - `地域限定`: regional-only availability.
  - `増量`: larger portion or bonus-size campaign.
- Local Japanese sources are used as context, not as proof of official availability.
- Product cards link back to original Japanese sources so readers can verify details.

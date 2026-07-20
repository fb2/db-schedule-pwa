# Konbini Radar — English copy guidance

These rules apply to **machine-assisted glossary output** in `scripts/build-konbini-feed.py` and any weekly editorial pass.

## Goals

- English readers should understand **what the product is** (format, chain, cold/hot, coffee vs tea when ambiguous).
- Avoid **misleading or offensive English cognates** even when they resemble Japanese loanwords.
- Prefer **literal food descriptions** over trendy slang.
- Always link to **Japanese official pages** so readers can verify names and allergens.

## Forbidden / high-risk wording

- **Never** render ぶっかけうどん / ぶっかけ（麺） as the English homograph that suggests sexual content. Use phrases such as **“broth-poured udon”**, **“udon with chilled dashi poured on top”**, or **“broth-poured soba”** depending on the noodle type.
- Avoid bare **“bukkake”** in any English consumer-facing field.

## Café drinks

- Treat **ラテ** as **café latte-style chilled dairy coffee** unless the Japanese copy explicitly names tea (e.g. matcha latte with 抹茶).
- Keep **CAFÉ LATTE** branding where it is literally Latin letters on pack shots.
- Preserve **milliliters** (e.g. `240ml`) from Japanese labeling when present.

## Proper nouns

- Leave recognized brands as proper nouns: GODIVA, mofusand, Lawson Lab feature names, etc.
- Transliterate known Japanese brands consistently (example: 森半 → Morihan, 八天堂 → Hattendo) when they appear in glossary tables.

## When glossary output looks wrong

1. Add or extend a **long Japanese phrase** entry in `PRIORITY_JP_PHRASES` (preferred for multi-word product titles).
2. Add missing ingredients or formats to `PHRASE_TRANSLATIONS`.
3. Extend `SANITIZE_ENGLISH_PATTERNS` only for **post-fixes** that catch systematic mistakes.
4. Re-run `python3 scripts/build-konbini-feed.py --publish` and skim high-visibility chains first.

## Images

- Thumbnails are **hotlinked from retailer CDNs** when the listing HTML exposes them. Some browsers or ad blockers may hide third-party images.
- Images are illustrative only; **availability and packaging** remain authoritative on the linked official page.

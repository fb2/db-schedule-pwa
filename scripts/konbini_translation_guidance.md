# Konbini Radar — English copy guidance

These rules apply to **machine-assisted glossary output** in `scripts/build-konbini-feed.py` and any weekly editorial pass.

## Goals

- English readers should understand **what the product is** (format, chain, cold/hot, coffee vs tea when ambiguous).
- Avoid **misleading or offensive English cognates** even when they resemble Japanese loanwords.
- Prefer **literal food descriptions** over trendy slang.
- Always link to **Japanese official pages** so readers can verify names and allergens.

## Card copy policy

Product cards should explain the product, not the translation pipeline.

- Leave `englishContext` empty unless there is a useful, product-specific note. Empty is the correct default.
- Never repeat generic card copy about automated glossaries, wording safeguards, exact naming, or allergens.
- Keep translation and allergen caveats once at page level. Do not imply that Konbini Radar verified allergens.
- Use `englishContext` for concrete help: unfamiliar formats, meaningful ingredients, collaboration context, regional limits, or a Japanese term whose literal rendering could mislead.
- Prefer one short sentence. Do not repeat the title, price, chain, badges, or region list unless the restriction itself needs explanation.
- Do not describe flavor, texture, or quality beyond what the official title or source explicitly states.
- The UI labels non-empty context as **Good to know** and removes the row entirely when context is empty.

Good:

- `A cold ramen from LabQ built around dried-sardine shoyu broth; sold only in Hokkaido, Tohoku and Kanto.`
- `A large soft-chewy daifuku filled with strawberry whipped cream and condensed milk.`
- `Bukkake udon means chilled udon served with savory broth poured over.`

Not useful:

- `supervised by a named restaurant, chef, or brand`
- `Milliliters on pack shots reflect Japanese retail labeling`
- `English names use a glossary; verify wording on the Japanese official source link`

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
2. For a high-ranking current product, add an exact entry to `PRODUCT_SPECIFIC_TITLES` and, only when useful, `PRODUCT_SPECIFIC_NOTES`.
3. Add missing reusable ingredients or formats to `PHRASE_TRANSLATIONS`.
4. Extend `SANITIZE_ENGLISH_PATTERNS` only for **post-fixes** that catch systematic mistakes.
5. Re-run `python3 scripts/build-konbini-feed.py --publish` and skim high-visibility chains first.

Exact weekly mappings are editorial overrides, not a quota. Prioritize the chain leaders and malformed or ambiguous titles; ordinary products do not need extra context merely to fill the card.

## Images

- Thumbnails are **hotlinked from retailer CDNs** when the listing HTML exposes them. Some browsers or ad blockers may hide third-party images.
- Images are illustrative only; **availability and packaging** remain authoritative on the linked official page.

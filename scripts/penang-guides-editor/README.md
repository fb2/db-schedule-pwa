# Penang Pulse Guides Editor (local only)

Small HTTP UI for editing editorial guides. **Not deployed** to Firebase or GitHub Pages.

## Setup (once)

Pillow is required for the image build step:

```sh
python3 -m venv scripts/penang-guides-editor/.venv
scripts/penang-guides-editor/.venv/bin/pip install Pillow
# optional HEIC support:
# scripts/penang-guides-editor/.venv/bin/pip install pillow-heif
```

## Run

From the repo root:

```sh
python3 scripts/penang-guides-editor/server.py
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

## Workflow

1. Create or open a guide (writes `utilities/penang-pulse/guides/posts/<slug>/post.md`).
2. Upload photos into that post’s `media/orig/` (gitignored).
3. In markdown, reference them as `![alt](./media/orig/filename.heic)` (or `.jpg` / `.png`).
4. Click **Save & build** (or **Run build** on the home page).
5. Preview locally: `python3 -m http.server 5173` → `/utilities/penang-pulse/`.
6. Deploy production:

   ```sh
   npx firebase-tools deploy --only hosting:penang-pulse
   ```

Built output (safe to commit): `guides/index.json`, `guides/<slug>/`, `guides/article.css`.

Source posts under `guides/posts/` are ignored by Firebase Hosting.

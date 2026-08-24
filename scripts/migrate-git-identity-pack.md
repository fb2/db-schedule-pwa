# Cursor prompt: pack Git + SSH identity for laptop migration

Run this on your **old laptop** in Cursor (Agent mode). Goal: create a **single encrypted-ready archive** with the files needed to restore personal + EPAM Git identities on the new machine.

Copy this entire file into a new Cursor chat on the old laptop, or open this file and say: **"Follow this runbook."**

---

## Prompt (paste into Cursor on old laptop)

You are helping migrate Git and SSH identity from this old laptop to a new one. The user has **two identities**:

- **Personal** — GitHub `fb2`, email `fbalazs@gmail.com`, repos often under `~/Projects/Personal/`
- **Work / EPAM** — corporate email and host (GitHub Enterprise, Azure DevOps, etc.), repos under a work folder

### Constraints

- **Do not** push, commit, or change any repo code.
- **Do not** print private key contents in chat.
- **Do not** upload the archive anywhere. Keep it local until the user transfers it manually (AirDrop, USB, secure copy).
- Prefer **copying existing keys** over generating new ones unless keys are missing or the user asks to rotate.
- If `~/.ssh` or `~/.gitconfig` is missing, report what you found and stop.

### Step 1 — Inventory

Inspect and summarize (paths only, not secret contents):

1. `~/.ssh/` — list files: private keys, `.pub`, `config`, `known_hosts`, `allowed_signers`
2. `~/.gitconfig` and any `[includeIf]` targets (e.g. `~/.gitconfig-personal`, `~/.gitconfig-work`)
3. `gh auth status` — note which GitHub hostnames are logged in (do **not** export gh token stores; user will `gh auth login` on new laptop)
4. Optional: `gpg --list-secret-keys --keyid-format=long` if commit signing was used
5. Scan common roots for repo layout (adjust paths to what exists on this machine):
   - `~/Projects/Personal/`
   - `~/Projects/Work/` or `~/Projects/EPAM/` or `~/epam/`
   For up to 5 repos per root, record: path, `git remote -v`, `git config user.email`, `git config --local --list | grep user`

Output a short table: **what exists / what is missing / recommended to pack**.

### Step 2 — Build pack folder

Create a timestamped pack directory:

```sh
PACK=~/Desktop/git-identity-pack-$(date +%Y%m%d-%H%M%S)
mkdir -p "$PACK/ssh" "$PACK/git" "$PACK/notes"
```

Copy only what exists:

```sh
# SSH
[ -d ~/.ssh ] && rsync -a \
  --include='config' \
  --include='id_*' \
  --include='known_hosts' \
  --include='allowed_signers' \
  --exclude='*' \
  ~/.ssh/ "$PACK/ssh/"

# Git global config + conditional includes
[ -f ~/.gitconfig ] && cp ~/.gitconfig "$PACK/git/"
for f in ~/.gitconfig-*; do
  [ -f "$f" ] && cp "$f" "$PACK/git/"
done

# Optional: GPG public key export only (secret key export only if user explicitly confirms signing migration)
# gpg --armor --export YOUR_KEY_ID > "$PACK/git/gpg-public.asc"
```

Write `$PACK/notes/inventory.txt` with:

- hostname, username, date
- output of `ls -la ~/.ssh` (filenames only)
- `gh auth status` summary
- list of Host aliases from `~/.ssh/config` (grep `^Host ` lines only)
- personal vs work folder paths discovered
- **reminder:** user must run `gh auth login` on new laptop; do not rely on copied gh credentials

Write `$PACK/notes/restore-on-new-laptop.md` with these restore steps:

```md
# Restore on new laptop

1. mkdir -p ~/.ssh && chmod 700 ~/.ssh
2. cp pack/ssh/* ~/.ssh/
3. chmod 600 ~/.ssh/id_* ; chmod 644 ~/.ssh/*.pub ; chmod 600 ~/.ssh/config
4. cp pack/git/.gitconfig ~/.gitconfig
5. cp pack/git/.gitconfig-* ~/   (if any)
6. Test: ssh -T git@github.com   (or your Host alias from config)
7. gh auth login                 (personal; re-login, do not copy old gh tokens)
8. Verify in a personal repo:
     git config user.email
     git remote -v
     git push --dry-run
```

### Step 3 — Archive

```sh
( cd "$(dirname "$PACK")" && tar czf "$(basename "$PACK").tar.gz" "$(basename "$PACK")" )
shasum -a 256 "$(dirname "$PACK")/$(basename "$PACK").tar.gz" > "$(dirname "$PACK")/$(basename "$PACK").tar.gz.sha256"
```

Report to the user:

- Full path to `*.tar.gz` and `.sha256`
- File size
- Which SSH key filenames were included
- Which gitconfig files were included
- Whether **work** and **personal** configs were both found
- Explicit **security checklist** (below)

### Step 4 — Security checklist (always print)

Tell the user:

1. Transfer the `.tar.gz` by a **private** channel (AirDrop, USB, `scp` to new laptop — not email/Slack).
2. Delete the pack folder and archive from the old laptop **after** confirming restore on the new laptop.
3. If the old laptop is sold/lost, **revoke or rotate** SSH keys on GitHub/EPAM after migration.
4. Never commit the archive into any git repo.
5. Re-run `gh auth login` on the new laptop instead of copying gh credential stores.

### Do not pack

- `private/**`, Firebase tokens, `.env`, API keys unrelated to Git
- Full browser cookie stores
- `~/.config/gh/` unless user explicitly insists (prefer fresh `gh auth login`)

---

## After restore on new laptop

In Cursor on the **new** laptop, say:

> I restored the git-identity pack. Verify SSH, git config, and help me push DBTravel from ~/Projects/Personal/DBTravel.

Expected personal repo remote: `https://github.com/fb2/db-schedule-pwa.git` or `git@github.com:fb2/db-schedule-pwa.git`

---

## Quick manual alternative (no Cursor)

On old laptop:

```sh
PACK=~/Desktop/git-identity-pack-$(date +%Y%m%d)
mkdir -p "$PACK/ssh" "$PACK/git"
cp ~/.ssh/config ~/.ssh/id_* "$PACK/ssh/" 2>/dev/null
cp ~/.gitconfig "$PACK/git/"
cp ~/.gitconfig-* "$PACK/git/" 2>/dev/null
tar czf "$PACK.tar.gz" -C "$(dirname "$PACK")" "$(basename "$PACK")"
```

Then AirDrop/USB to new laptop and follow `restore-on-new-laptop.md` above.

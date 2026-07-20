/**
 * Wireframe-only starring demo for Penang Pulse.
 * Pattern: All | Starred segmented control + per-item star (☆/★).
 * Persists IDs in cookie `penangPulseStars` (SameSite=Lax, 365 days).
 */
(() => {
  const COOKIE = "penangPulseStars";
  const DAYS = 365;

  const params = new URLSearchParams(location.search);
  const forceEmpty = params.get("empty") === "1";
  const initialView = params.get("view") === "starred" || forceEmpty ? "starred" : "all";

  function readCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    const hit = document.cookie
      .split("; ")
      .find((part) => part.startsWith(prefix));
    return hit ? decodeURIComponent(hit.slice(prefix.length)) : "";
  }

  function writeCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
  }

  function loadStars() {
    if (forceEmpty) return new Set();
    const raw = readCookie(COOKIE);
    if (!raw) return new Set();
    try {
      const parsed = JSON.parse(raw);
      return new Set(Array.isArray(parsed) ? parsed.map(String) : []);
    } catch {
      return new Set(
        raw
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
      );
    }
  }

  function saveStars(stars) {
    if (forceEmpty) return;
    writeCookie(COOKIE, JSON.stringify([...stars]), DAYS);
  }

  const stars = loadStars();
  let view = initialView;

  const switchEl = document.querySelector("[data-view-switch]");
  const emptyEl = document.querySelector("[data-empty-state]");
  const feedEl = document.querySelector("[data-feed]");
  const items = [...document.querySelectorAll("[data-item-id]")];

  function setStarButton(btn, starred, label) {
    btn.textContent = starred ? "★" : "☆";
    btn.setAttribute("aria-pressed", String(starred));
    btn.setAttribute("aria-label", starred ? `Remove star from ${label}` : `Star ${label}`);
    btn.title = starred ? "Remove star" : "Star this item";
  }

  function applyView() {
    if (switchEl) {
      switchEl.querySelectorAll("button[data-view]").forEach((btn) => {
        btn.setAttribute("aria-pressed", String(btn.dataset.view === view));
      });
    }

    const showStarredOnly = view === "starred";
    let visible = 0;

    items.forEach((item) => {
      const id = item.dataset.itemId;
      const starred = stars.has(id);
      const show = !showStarredOnly || starred;
      item.hidden = !show;
      if (show) visible += 1;

      const btn = item.querySelector("[data-star]");
      const label = item.dataset.itemLabel || id;
      if (btn) setStarButton(btn, starred, label);
    });

    // Detail page: single item, no feed filter
    const detailStar = document.querySelector("[data-detail-star]");
    if (detailStar) {
      const id = detailStar.dataset.itemId;
      const label = detailStar.dataset.itemLabel || id;
      setStarButton(detailStar, stars.has(id), label);
    }

    if (feedEl) feedEl.hidden = showStarredOnly && visible === 0;
    if (emptyEl) emptyEl.hidden = !(showStarredOnly && visible === 0);

    // Hide section chrome when all its stories are filtered out
    document.querySelectorAll("section").forEach((section) => {
      const sectionItems = [...section.querySelectorAll("[data-item-id]")];
      if (!sectionItems.length) {
        section.hidden = showStarredOnly;
        return;
      }
      section.hidden = sectionItems.every((el) => el.hidden);
    });
  }

  switchEl?.addEventListener("click", (event) => {
    const btn = event.target.closest("button[data-view]");
    if (!btn) return;
    view = btn.dataset.view;
    applyView();
  });

  document.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-star]");
    if (!btn) return;
    event.preventDefault();
    const id = btn.dataset.itemId || btn.closest("[data-item-id]")?.dataset.itemId;
    if (!id || forceEmpty) return;
    if (stars.has(id)) stars.delete(id);
    else stars.add(id);
    saveStars(stars);
    applyView();
  });

  applyView();
})();

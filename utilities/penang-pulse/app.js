const els = {
  weekLabel: document.querySelector("#weekLabel"),
  weeklyIntro: document.querySelector("#weeklyIntro"),
  viewAll: document.querySelector("#viewAll"),
  viewStarred: document.querySelector("#viewStarred"),
  emptyState: document.querySelector("#emptyState"),
  feedRoot: document.querySelector("#feedRoot"),
  itemTemplate: document.querySelector("#itemTemplate"),
  guidesStrip: document.querySelector("#guidesStrip"),
  guidesList: document.querySelector("#guidesList"),
};

const state = {
  feed: null,
  guides: [],
  view: "all",
  starred: new Set(),
};

const STAR_COOKIE_NAME = "penangPulseStars";
const STAR_COOKIE_DAYS = 365;
const SOON_DAYS = 14;
/** Safety net: Food & popups only — openings older than this are hidden. */
const FOOD_MAX_AGE_DAYS = 62;

function readCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`;
  const cookie = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
}

function writeCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  const path = window.location.pathname.replace(/[^/]*$/, "") || "/";
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=${path}; SameSite=Lax`;
}

function loadStarredIds() {
  const raw = readCookie(STAR_COOKIE_NAME);
  if (!raw) return new Set();
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return new Set(parsed.filter((item) => typeof item === "string").slice(0, 120));
    }
  } catch {
    /* ignore */
  }
  return new Set();
}

function persistStarred() {
  let values = [...state.starred];
  if (values.length > 120) {
    values = values.slice(-120);
    state.starred = new Set(values);
  }
  writeCookie(STAR_COOKIE_NAME, JSON.stringify(values), STAR_COOKIE_DAYS);
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(`${value}T12:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function startOfToday() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

function soonHorizon(today) {
  const horizon = new Date(today);
  horizon.setDate(horizon.getDate() + SOON_DAYS);
  return horizon;
}

/** start <= today <= end — currently running (e.g. long exhibitions). */
function isOngoing(item, today) {
  const start = parseDate(item.startDate);
  const end = parseDate(item.endDate) || start;
  if (!start || !end) return false;
  return start <= today && end >= today;
}

/**
 * Happening soon: ongoing now, or starts within the next SOON_DAYS.
 * Ended events (end < today) are never soon.
 */
function isHappeningSoon(item, today) {
  const start = parseDate(item.startDate);
  const end = parseDate(item.endDate) || start;
  if (!start && !end) return false;
  const effectiveEnd = end || start;
  if (effectiveEnd < today) return false;
  if (isOngoing(item, today)) return true;
  const effectiveStart = start || end;
  return effectiveStart >= today && effectiveStart <= soonHorizon(today);
}

/** Upcoming later: start is after the next-14-days window (not ongoing). */
function isUpcomingLater(item, today) {
  const start = parseDate(item.startDate);
  if (!start) return false;
  if (isOngoing(item, today)) return false;
  return start > soonHorizon(today);
}

function parseFlexibleDate(value) {
  if (!value || typeof value !== "string") return null;
  const iso = parseDate(value.slice(0, 10));
  if (iso) return iso;
  const match = value.match(/\b(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})\b/);
  if (!match) return null;
  const months = {
    jan: 0,
    january: 0,
    feb: 1,
    february: 1,
    mar: 2,
    march: 2,
    apr: 3,
    april: 3,
    may: 4,
    jun: 5,
    june: 5,
    jul: 6,
    july: 6,
    aug: 7,
    august: 7,
    sep: 8,
    sept: 8,
    september: 8,
    oct: 9,
    october: 9,
    nov: 10,
    november: 10,
    dec: 11,
    december: 11,
  };
  const month = months[match[2].toLowerCase()];
  if (month == null) return null;
  const date = new Date(Number(match[3]), month, Number(match[1]));
  return Number.isNaN(date.getTime()) ? null : date;
}

function foodItemDate(item) {
  return (
    parseDate(item.startDate) ||
    parseDate(item.endDate) ||
    parseFlexibleDate(item.publishedAt) ||
    parseFlexibleDate(item.dateLabel) ||
    parseFlexibleDate(item.title) ||
    parseFlexibleDate(item.summary)
  );
}

function isFreshFoodOpening(item, today) {
  const anchor = foodItemDate(item);
  if (!anchor) return true;
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() - FOOD_MAX_AGE_DAYS);
  return anchor >= cutoff;
}

function setStarButtonState(button, item, starred) {
  button.textContent = starred ? "★" : "☆";
  button.setAttribute("aria-pressed", String(starred));
  button.setAttribute(
    "aria-label",
    `${starred ? "Remove star from" : "Star"} ${item.title}`
  );
  button.title = starred ? "Remove star" : "Star this item";
}

function toggleStar(item, button) {
  const starred = !state.starred.has(item.id);
  if (starred) state.starred.add(item.id);
  else state.starred.delete(item.id);
  persistStarred();
  setStarButtonState(button, item, starred);
  if (state.view === "starred") render();
}

function createItemCard(item) {
  const node = els.itemTemplate.content.firstElementChild.cloneNode(true);
  const thumb = node.querySelector(".thumb");
  const title = node.querySelector(".title");
  const meta = node.querySelector(".meta");
  const blurb = node.querySelector(".blurb");
  const source = node.querySelector(".source");
  const starBtn = node.querySelector(".star-btn");

  title.textContent = item.title || "Untitled";
  meta.textContent = item.dateLabel || item.area || "";
  blurb.textContent = item.summary || "";

  const imageUrl = typeof item.imageUrl === "string" ? item.imageUrl.trim() : "";
  if (imageUrl) {
    thumb.textContent = "";
    const img = document.createElement("img");
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    // Set before src so the first request omits Referer (hotlink-sensitive CDNs).
    img.referrerPolicy = "no-referrer";
    img.addEventListener("error", () => {
      // Broken remote image: drop the thumb entirely (no gray placeholder).
      thumb.remove();
    });
    img.src = imageUrl;
    thumb.append(img);
  } else {
    // No imageUrl: omit the thumb block so title/meta lead the card.
    thumb.remove();
  }

  if (item.sourceUrl) {
    source.href = item.sourceUrl;
    source.textContent = item.sourceName ? `${item.sourceName} →` : "Source →";
  } else {
    source.hidden = true;
  }

  const starred = state.starred.has(item.id);
  setStarButtonState(starBtn, item, starred);
  starBtn.addEventListener("click", () => toggleStar(item, starBtn));
  return node;
}

function createSection(id, label, className) {
  const section = document.createElement("section");
  section.className = `section ${className}`;
  section.setAttribute("aria-labelledby", id);
  const heading = document.createElement("h2");
  heading.className = "section-label pad";
  heading.id = id;
  heading.textContent = label;
  section.append(heading);
  return section;
}

function render() {
  const feed = state.feed;
  if (!feed) return;

  els.weekLabel.textContent = feed.weekLabel || "This week";
  els.weeklyIntro.textContent =
    feed.intro || "What’s on in Penang — events and new food this week.";

  const items = Array.isArray(feed.items) ? feed.items : [];
  const visible =
    state.view === "starred" ? items.filter((item) => state.starred.has(item.id)) : items;

  els.emptyState.hidden = !(state.view === "starred" && visible.length === 0);
  els.feedRoot.hidden = !els.emptyState.hidden;
  els.feedRoot.replaceChildren();

  if (!els.emptyState.hidden) return;

  const today = startOfToday();
  const events = visible.filter((item) => item.kind === "event" || !item.kind);
  const food = visible.filter(
    (item) => item.kind === "food" && isFreshFoodOpening(item, today)
  );
  const revisits = visible.filter((item) => item.kind === "revisit");
  const soon = events.filter((item) => isHappeningSoon(item, today));
  const later = events.filter((item) => isUpcomingLater(item, today));
  const undatedEvents = events.filter(
    (item) => !isHappeningSoon(item, today) && !isUpcomingLater(item, today)
  );
  const soonItems = [...soon, ...undatedEvents];

  if (soonItems.length) {
    const section = createSection("soon-label", "Happening soon · Next 14 days", "section-soon");
    const list = document.createElement("div");
    list.className = "story-list";
    soonItems.forEach((item) => list.append(createItemCard(item)));
    section.append(list);
    els.feedRoot.append(section);
  }

  // Food + revisit share one desktop column so revisit sits under food, not under a tall events row.
  if (food.length || revisits.length) {
    const aside = document.createElement("div");
    aside.className = "feed-aside";

    if (food.length) {
      const section = createSection("food-label", "Food & popups", "section-food");
      const list = document.createElement("div");
      list.className = "story-list food-stack";
      food.forEach((item) => list.append(createItemCard(item)));
      section.append(list);
      aside.append(section);
    }

    if (revisits.length) {
      const section = createSection("revisit-label", "Worth revisiting", "section-revisit");
      const list = document.createElement("div");
      list.className = "story-list food-stack";
      revisits.forEach((item) => list.append(createItemCard(item)));
      section.append(list);
      aside.append(section);
    }

    els.feedRoot.append(aside);
  }

  if (later.length && state.view === "all") {
    const section = createSection("upcoming-label", "Upcoming later", "section-upcoming");
    const list = document.createElement("ul");
    list.className = "upcoming-list";
    later.forEach((item) => {
      const li = document.createElement("li");
      const title = document.createElement("span");
      title.textContent = item.title;
      const date = document.createElement("span");
      date.textContent = item.dateLabel || item.startDate || "";
      li.append(title, date);
      list.append(li);
    });
    section.append(list);
    els.feedRoot.append(section);
  }

  if (!soonItems.length && !food.length && !revisits.length && !later.length) {
    const empty = document.createElement("p");
    empty.className = "pad";
    empty.style.color = "var(--muted)";
    empty.textContent = "No items in this week’s feed yet.";
    els.feedRoot.append(empty);
  }
}

function setView(view) {
  state.view = view;
  els.viewAll.setAttribute("aria-pressed", String(view === "all"));
  els.viewStarred.setAttribute("aria-pressed", String(view === "starred"));
  renderGuides();
  render();
}

function renderGuides() {
  if (!els.guidesStrip || !els.guidesList) return;
  const guides = Array.isArray(state.guides) ? state.guides : [];
  const show = state.view === "all" && guides.length > 0;
  els.guidesStrip.hidden = !show;
  if (!show) {
    els.guidesList.replaceChildren();
    return;
  }

  const list = document.createDocumentFragment();
  guides.forEach((guide) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = guide.href || `./guides/${guide.slug}/`;
    const title = document.createElement("span");
    title.className = "g-title";
    title.textContent = guide.title || guide.slug || "Guide";
    const type = document.createElement("span");
    type.className = "g-type";
    // Format-agnostic label — no Text/Photos/Video on the home strip.
    type.textContent = "Field guide";
    a.append(title, type);
    li.append(a);
    list.append(li);
  });
  els.guidesList.replaceChildren(list);
}

async function loadGuides() {
  try {
    const response = await fetch("./guides/index.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    state.guides = Array.isArray(data.guides) ? data.guides : [];
  } catch {
    state.guides = [];
  }
  renderGuides();
}

async function loadFeed() {
  try {
    const response = await fetch("./feed.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.feed = await response.json();
    render();
  } catch (error) {
    els.weekLabel.textContent = "Feed unavailable";
    els.weeklyIntro.textContent = "Could not load this week’s Penang Pulse feed.";
    const banner = document.createElement("div");
    banner.className = "error-banner";
    banner.textContent = String(error.message || error);
    els.feedRoot.replaceChildren(banner);
  }
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;

  let refreshing = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  navigator.serviceWorker
    .register("./sw.js")
    .then((reg) => {
      const ping = () => reg.update().catch(() => {});
      document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") ping();
      });
      // Catch daily publishes without waiting for a hard refresh.
      setInterval(ping, 60 * 60 * 1000);
    })
    .catch(() => {});
}

els.viewAll.addEventListener("click", () => setView("all"));
els.viewStarred.addEventListener("click", () => setView("starred"));

state.starred = loadStarredIds();
loadGuides();
loadFeed();
registerServiceWorker();

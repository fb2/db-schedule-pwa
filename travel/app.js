import {
  findFocusPoint,
  focusFacts,
  groupBodyLines,
  parseRememberItems,
  relevantRememberItems,
  sectionTiming,
  todayIso,
  weekTiming
} from "./plan-view.js?v=4";

const FIREBASE_APP_URL = "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
const FIREBASE_AUTH_URL = "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
const FIREBASE_FIRESTORE_URL = "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";
const PLAN_CACHE_VERSION = "travel.plans.v1";
const LAST_USER_KEY = "travel.lastUser.v1";
const FB_CONFIG_KEY = "travel.firebaseConfig.v1";
const BROWSE_MONTH_KEY = "travel.browseMonth.v1";
const MAX_DOC_BYTES = 900_000;
const MONTHS = new Map([
  ["JAN", 0], ["JANUARY", 0],
  ["FEB", 1], ["FEBRUARY", 1],
  ["MAR", 2], ["MARCH", 2],
  ["APR", 3], ["APRIL", 3],
  ["MAY", 4],
  ["JUN", 5], ["JUNE", 5],
  ["JUL", 6], ["JULY", 6],
  ["AUG", 7], ["AUGUST", 7],
  ["SEP", 8], ["SEPT", 8], ["SEPTEMBER", 8],
  ["OCT", 9], ["OCTOBER", 9],
  ["NOV", 10], ["NOVEMBER", 10],
  ["DEC", 11], ["DECEMBER", 11]
]);
const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

let auth = null;
let db = null;
let store = null;
let currentUser = null;
let authState = "starting";
let plans = [];
let plansById = new Map();
let activeMonthId = "";
let cachedUserEmail = "";
let lastCacheAt = "";
let viewMode = readBrowseMonth() ? "browse" : "now";
let explicitSignOut = false;
let didInitialFocus = false;

const userLabel = document.getElementById("userLabel");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const signedInControls = document.getElementById("signedInControls");
const monthSelect = document.getElementById("monthSelect");
const prevMonthBtn = document.getElementById("prevMonthBtn");
const nextMonthBtn = document.getElementById("nextMonthBtn");
const refreshBtn = document.getElementById("refreshBtn");
const jumpNowBtn = document.getElementById("jumpNowBtn");
const importFile = document.getElementById("importFile");
const statusEl = document.getElementById("status");
const nowRail = document.getElementById("nowRail");
const monthOverview = document.getElementById("monthOverview");
const weekList = document.getElementById("weekList");
const empty = document.getElementById("empty");

boot();

async function boot() {
  bindEvents();
  const cached = readPlanCache();
  if (cached) {
    cachedUserEmail = cached.userEmail || "";
    applyPlans(cached.plans, { fromCache: true, cachedAt: cached.cachedAt });
    userLabel.textContent = cachedUserEmail || "Cached plans";
    setAppState("ready", cachedStatus(cached.cachedAt, "Checking for updates…"));
    render();
  } else {
    setAppState("starting", "Loading Firebase...");
  }

  try {
    await initFirebase();
  } catch (error) {
    console.error(error);
    if (plans.length) {
      setAppState("ready", cachedStatus(lastCacheAt, "Offline — showing cached plans."));
      render();
      return;
    }
    setAppState("offline", "Firebase is unavailable here. Open this app from Firebase Hosting.");
  }
}

function bindEvents() {
  monthSelect.addEventListener("change", () => {
    setBrowseMonth(monthSelect.value);
    render();
  });
  prevMonthBtn.addEventListener("click", () => moveMonth(-1));
  nextMonthBtn.addEventListener("click", () => moveMonth(1));
  refreshBtn.addEventListener("click", () => {
    if (currentUser) refreshPlans({ background: false });
  });
  jumpNowBtn.addEventListener("click", jumpToNow);
  importFile.addEventListener("change", importMonthFiles);
  nowRail.addEventListener("click", (event) => {
    const card = event.target.closest("[data-section-id]");
    if (!card) return;
    openSection(card.dataset.monthId, card.dataset.sectionId);
  });
}

async function initFirebase() {
  const firebaseConfig = await loadFirebaseConfig();
  const [{ initializeApp }, authMod, firestoreMod] = await Promise.all([
    import(FIREBASE_APP_URL),
    import(FIREBASE_AUTH_URL),
    import(FIREBASE_FIRESTORE_URL)
  ]);
  const app = initializeApp(firebaseConfig);
  auth = authMod.getAuth(app);
  db = firestoreMod.getFirestore(app);
  store = {
    getDocs: firestoreMod.getDocs,
    collection: firestoreMod.collection,
    doc: firestoreMod.doc,
    setDoc: firestoreMod.setDoc,
    serverTimestamp: firestoreMod.serverTimestamp
  };
  const provider = new authMod.GoogleAuthProvider();

  signInBtn.addEventListener("click", async () => {
    try {
      await authMod.signInWithPopup(auth, provider);
    } catch (error) {
      setStatus(`Sign-in failed: ${error.message}`);
    }
  });
  signOutBtn.addEventListener("click", async () => {
    explicitSignOut = true;
    viewMode = "now";
    writeBrowseMonth("");
    await authMod.signOut(auth);
  });
  authMod.onAuthStateChanged(auth, handleAuthChange);
}

async function loadFirebaseConfig() {
  try {
    const response = await fetch("/__/firebase/init.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Firebase config is only available from Firebase Hosting.");
    const config = await response.json();
    try { localStorage.setItem(FB_CONFIG_KEY, JSON.stringify(config)); } catch { /* ignore */ }
    return config;
  } catch (error) {
    try {
      const cached = JSON.parse(localStorage.getItem(FB_CONFIG_KEY) || "");
      if (cached?.apiKey || cached?.projectId) return cached;
    } catch { /* ignore */ }
    throw error;
  }
}

async function handleAuthChange(user) {
  currentUser = user;
  if (!user) {
    if (explicitSignOut) {
      plans = [];
      plansById = new Map();
      activeMonthId = "";
      setAppState("signed-out", "Sign in with Google to load private travel plans.");
      render();
      return;
    }
    if (plans.length) {
      setAppState("ready", cachedStatus(lastCacheAt, "Sign in to refresh."));
      render();
      return;
    }
    setAppState("signed-out", "Sign in with Google to load private travel plans.");
    render();
    return;
  }

  explicitSignOut = false;
  userLabel.textContent = user.email || "Signed in";
  if (cachedUserEmail && cachedUserEmail !== user.email) {
    const other = readPlanCache(user.email);
    plans = [];
    plansById = new Map();
    cachedUserEmail = user.email;
    if (other) applyPlans(other.plans, { fromCache: true, cachedAt: other.cachedAt });
  } else {
    cachedUserEmail = user.email;
    writeLastUser(user.email);
  }

  if (plans.length) {
    setAppState("ready", cachedStatus(lastCacheAt, "Checking for updates…"));
    render();
    refreshPlans({ background: true });
    return;
  }

  await refreshPlans({ background: false });
}

async function refreshPlans({ background = false } = {}) {
  if (!currentUser || !db || !store) return;
  if (!background) setAppState("loading", "Loading private travel plans...");

  try {
    const snapshot = await store.getDocs(store.collection(db, "travelPlans"));
    const next = snapshot.docs
      .map((item) => ({ id: item.id, ...serializeData(item.data()) }))
      .sort((a, b) => String(a.monthId || a.id).localeCompare(String(b.monthId || b.id)));
    const changed = plansSignature(next) !== plansSignature(plans);
    writePlanCache(currentUser.email, next);
    applyPlans(next);
    setAppState(
      "ready",
      next.length
        ? `${next.length} private month plan${next.length === 1 ? "" : "s"} · ${changed ? "updated" : "up to date"}`
        : "No travel plans uploaded yet."
    );
    render();
    if (viewMode === "now") requestAnimationFrame(() => scrollToFocus(true));
  } catch (error) {
    console.error(error);
    if (plans.length) {
      setAppState(
        "ready",
        cachedStatus(lastCacheAt, permissionDenied(error) ? "This account cannot refresh plans." : "Could not refresh — showing cache.")
      );
      render();
      return;
    }
    const message = permissionDenied(error)
      ? "This Google account is not allowed to access private travel plans."
      : "Could not load private travel plans.";
    setAppState(permissionDenied(error) ? "unauthorized" : "error", message);
    render();
  }
}

async function importMonthFiles(event) {
  const files = [...(event.target.files || [])];
  event.target.value = "";
  if (!files.length || !currentUser || !db || !store) return;
  if (!confirm(`Upload ${files.length} travel plan file${files.length === 1 ? "" : "s"}? Re-uploading a month replaces the stored version.`)) return;

  setAppState("loading", `Reading ${files.length} file${files.length === 1 ? "" : "s"}...`);
  try {
    const imported = [];
    for (const file of files) {
      const text = await file.text();
      const plan = parseTravelPlan(file.name, text);
      const payload = {
        ...cleanObject(plan),
        sourceFilename: file.name,
        importedBy: currentUser.email || currentUser.uid,
        updatedAt: store.serverTimestamp(),
        importedAt: store.serverTimestamp()
      };
      const bytes = new TextEncoder().encode(JSON.stringify(payload)).length;
      if (bytes > MAX_DOC_BYTES) {
        throw new Error(`${file.name} is too large for a single Firestore document.`);
      }
      await store.setDoc(store.doc(db, "travelPlans", plan.monthId), payload);
      imported.push(plan.monthId);
    }
    setBrowseMonth(imported.at(-1) || activeMonthId);
    setStatus(`Imported ${imported.length} month plan${imported.length === 1 ? "" : "s"}.`);
    await refreshPlans({ background: false });
  } catch (error) {
    console.error(error);
    setAppState("ready", `Import failed: ${error.message}`);
    render();
  }
}

function parseTravelPlan(filename, rawText) {
  const text = String(rawText || "").replace(/\r\n?/g, "\n").trim();
  if (!text) throw new Error(`${filename} is empty.`);

  const lines = text.split("\n");
  const title = findTitle(lines) || filename.replace(/\.[^.]+$/, "");
  const monthInfo = parseMonthFromTitle(title) || parseMonthFromFilename(filename);
  if (!monthInfo) throw new Error(`Could not determine month/year for ${filename}.`);

  const monthId = `${monthInfo.year}-${pad2(monthInfo.month + 1)}`;
  const base = findLineValue(lines, "BASE:");
  const sections = parseSections(lines, monthInfo);
  const summaryItems = parseNamedBlock(lines, "SUMMARY").filter(Boolean);
  const openItems = parseNamedBlock(lines, "OPEN ITEMS").filter(Boolean).map(parseOpenItem);
  const rememberItems = parseRememberItems(lines);
  const events = sections.map(sectionToEvent);
  const warnings = detectWarnings(events);
  const weeks = buildWeeks(events, monthInfo);

  return {
    monthId,
    title,
    base,
    rawText: text,
    sections,
    summaryItems,
    openItems,
    rememberItems,
    events,
    warnings,
    weeks,
    parsedAt: new Date().toISOString()
  };
}

function findTitle(lines) {
  return lines
    .map((line) => line.trim())
    .find((line) => line && !isDivider(line) && /TRAVEL\s*&\s*EVENTS\s+OVERVIEW/i.test(line));
}

function parseMonthFromTitle(title) {
  const match = String(title || "").match(/\b([A-Z]{3,9})\s+(\d{4})\b/i);
  if (!match) return null;
  const month = MONTHS.get(match[1].toUpperCase());
  return month === undefined ? null : { month, year: Number(match[2]) };
}

function parseMonthFromFilename(filename) {
  const match = String(filename || "").match(/([a-z]{3,9})[-_\s]+(\d{4})/i);
  if (!match) return null;
  const month = MONTHS.get(match[1].toUpperCase());
  return month === undefined ? null : { month, year: Number(match[2]) };
}

function findLineValue(lines, prefix) {
  const line = lines.find((item) => item.trim().toUpperCase().startsWith(prefix));
  return line ? line.trim().slice(prefix.length).trim() : "";
}

function parseSections(lines, monthInfo) {
  const sections = [];
  let current = null;
  const stopAt = lines.findIndex((line) => /SUMMARY:\s*KEY DATES/i.test(line));
  const endIndex = stopAt === -1 ? lines.length : stopAt;

  for (let i = 0; i < endIndex; i += 1) {
    const line = lines[i];
    const heading = normalizeHeading(line);
    if (heading && parseDateRange(heading, monthInfo)) {
      if (current) sections.push(finalizeSection(current));
      current = {
        id: `section-${sections.length + 1}`,
        title: heading,
        bodyLines: [],
        ...parseDateRange(heading, monthInfo)
      };
      continue;
    }
    if (current && !isDivider(line)) current.bodyLines.push(line);
  }
  if (current) sections.push(finalizeSection(current));
  return sections;
}

function normalizeHeading(line) {
  const trimmed = String(line || "").trim();
  if (!trimmed || isDivider(trimmed)) return "";
  const unwrapped = trimmed.replace(/^\*+\s*/, "").replace(/\s*\*+$/, "").trim();
  return /^[A-Z]{3,9}\s+\d{1,2}/.test(unwrapped) ? unwrapped : "";
}

function parseDateRange(heading, monthInfo) {
  const match = heading.match(/^([A-Z]{3,9})\s+(\d{1,2})(?:\s*(?:[\u2013-])\s*([A-Z]{3,9})?\s*(\d{1,2}))?/i);
  if (!match) return null;

  const startMonth = MONTHS.get(match[1].toUpperCase());
  if (startMonth === undefined) return null;
  const startDay = Number(match[2]);
  const endMonth = match[3] ? MONTHS.get(match[3].toUpperCase()) : startMonth;
  const endDay = match[4] ? Number(match[4]) : startDay;
  if (endMonth === undefined) return null;

  let startYear = monthInfo.year;
  let endYear = monthInfo.year;
  if (startMonth > monthInfo.month && monthInfo.month === 0) startYear -= 1;
  if (endMonth < startMonth) endYear += 1;

  return {
    startDate: isoDate(startYear, startMonth, startDay),
    endDate: isoDate(endYear, endMonth, endDay)
  };
}

function finalizeSection(section) {
  const body = trimBlankLines(section.bodyLines).join("\n");
  return {
    id: section.id,
    title: section.title,
    body,
    startDate: section.startDate,
    endDate: section.endDate,
    category: detectCategory(`${section.title}\n${body}`),
    status: detectStatus(`${section.title}\n${body}`),
    times: extractTimes(`${section.title}\n${body}`)
  };
}

function parseNamedBlock(lines, name) {
  const start = lines.findIndex((line) => line.toUpperCase().includes(name));
  if (start === -1) return [];

  const result = [];
  let seenContent = false;
  for (let i = start + 1; i < lines.length; i += 1) {
    const trimmed = lines[i].trim();
    if (isDivider(trimmed)) {
      if (seenContent) break;
      continue;
    }
    if (!trimmed) {
      if (seenContent) result.push("");
      continue;
    }
    seenContent = true;
    result.push(trimmed);
  }
  return trimBlankLines(result);
}

function parseOpenItem(line) {
  const checked = /^\[x\]/i.test(line);
  const urgent = /^\[!\]/.test(line);
  return {
    text: line.replace(/^\[[x!\s]\]\s*/i, "").trim(),
    checked,
    urgent
  };
}

function sectionToEvent(section) {
  return {
    id: section.id,
    title: section.title,
    startDate: section.startDate,
    endDate: section.endDate,
    category: section.category,
    status: section.status,
    times: section.times,
    summary: summarizeSection(section)
  };
}

function summarizeSection(section) {
  const bodyLine = section.body.split("\n").map((line) => line.trim()).find(Boolean);
  return bodyLine || section.title;
}

function detectCategory(text) {
  const title = text.split("\n")[0].toLowerCase();
  const value = text.toLowerCase();
  if (/\bcancelled\b/.test(value)) return "cancelled";
  if (/\[travel day\]|\bfly\b|\bflight\b/.test(title)) return "flight";
  if (/\[key event\]|workshop|presentation|sko|master class|people \/ hr/.test(title)) return "business";
  if (/\bhotel\b|\baccommodation\b/.test(title)) return "hotel";
  if (/\btransfer\b|\btrain\b|\bamtrak\b/.test(title)) return "transfer";
  if (/\b(flight|fly|airport|depart|arrive|airways|cathay|wizz|batik)\b/.test(value) && /→|->|depart/.test(value) && !/workshop|presentation/.test(title)) {
    return "flight";
  }
  if (/\b(meeting|office|business|forum|epam|scsk|mitsui|nissan|workshop)\b/.test(value)) return "business";
  if (/\b(hotel|check-in|check-out|accommodation)\b/.test(value) && !/workshop|presentation|key event/.test(title)) return "hotel";
  if (/\b(dinner|festival|primavera|sightseeing|weekend|free day|personal)\b/.test(value)) return "personal";
  return "event";
}

function detectStatus(text) {
  const value = text.toLowerCase();
  return {
    cancelled: /\bcancelled\b/.test(value),
    paid: /\bpaid\b|prepaid/.test(value),
    confirmed: /\bconfirmed\b|\[registered\]|\[must\]/.test(value),
    tbc: /\btbc\b|to be confirmed|to be booked/.test(value),
    urgent: /\[!\]|\bmust\b|\u26a0/.test(value)
  };
}

function extractTimes(text) {
  const times = [];
  const rangePattern = /(\d{1,2}):(\d{2})\s*(?:[\u2013-]|\u2192|to)\s*(\d{1,2}):(\d{2})/gi;
  let match;
  while ((match = rangePattern.exec(text))) {
    times.push({
      start: Number(match[1]) * 60 + Number(match[2]),
      end: Number(match[3]) * 60 + Number(match[4]),
      label: match[0]
    });
  }
  if (times.length) return times;

  const singlePattern = /\b(?:time|starts|doors|pickup|depart|arrive|reception|dinner):?\s*(\d{1,2}):(\d{2})\b/gi;
  while ((match = singlePattern.exec(text))) {
    const start = Number(match[1]) * 60 + Number(match[2]);
    times.push({ start, end: start + 60, label: match[0] });
  }
  return times;
}

function detectWarnings(events) {
  const warnings = [];
  const timed = events.filter((event) => event.times.length && event.startDate === event.endDate);
  for (let i = 0; i < timed.length; i += 1) {
    for (let j = i + 1; j < timed.length; j += 1) {
      if (timed[i].startDate !== timed[j].startDate) continue;
      if (timed[i].times.some((left) => timed[j].times.some((right) => rangesOverlap(left, right)))) {
        warnings.push({
          type: "time",
          date: timed[i].startDate,
          message: `Potential time overlap: ${timed[i].title} and ${timed[j].title}`
        });
      }
    }
  }

  const hotels = events.filter((event) => event.category === "hotel" && !event.status.cancelled);
  for (let i = 0; i < hotels.length; i += 1) {
    for (let j = i + 1; j < hotels.length; j += 1) {
      if (dateRangesOverlap(hotels[i], hotels[j])) {
        warnings.push({
          type: "hotel",
          date: hotels[j].startDate,
          message: `Overlapping lodging dates: ${hotels[i].title} and ${hotels[j].title}`
        });
      }
    }
  }
  return warnings;
}

function buildWeeks(events, monthInfo) {
  const dated = events.filter((event) => event.startDate && event.endDate);
  const anchors = dated.length ? dated : [{
    startDate: isoDate(monthInfo.year, monthInfo.month, 1),
    endDate: isoDate(monthInfo.year, monthInfo.month + 1, 0)
  }];
  const first = anchors.map((item) => item.startDate).sort()[0];
  const last = anchors.map((item) => item.endDate).sort().at(-1);
  const weeks = [];
  let cursor = weekStart(first);
  const finalWeek = weekStart(last);

  while (cursor <= finalWeek) {
    const weekEnd = addDays(cursor, 6);
    const week = {
      id: cursor,
      startDate: cursor,
      endDate: weekEnd,
      label: `${formatShortDate(cursor)} - ${formatShortDate(weekEnd)}`,
      eventIds: dated
        .filter((event) => event.startDate <= weekEnd && event.endDate >= cursor)
        .map((event) => event.id)
    };
    weeks.push(week);
    cursor = addDays(cursor, 7);
  }
  return weeks;
}

function render() {
  const hasPlans = plans.length > 0;
  const activePlan = plansById.get(activeMonthId);
  renderMonthSelect();
  jumpNowBtn.hidden = !hasPlans;
  empty.hidden = hasPlans;
  monthOverview.hidden = !activePlan;
  weekList.hidden = !activePlan;

  if (!hasPlans) {
    nowRail.hidden = true;
    nowRail.innerHTML = "";
    monthOverview.innerHTML = "";
    weekList.innerHTML = "";
    empty.textContent = authState === "unauthorized"
      ? "This account is not allowed to access private travel plans."
      : currentUser
        ? "No travel plans uploaded yet. Upload one or more monthly text files."
        : "Sign in with an allowed Google account to view private travel plans.";
    return;
  }

  renderNowRail();
  renderOverview(activePlan);
  renderWeeks(activePlan);
  if (viewMode === "now" && !didInitialFocus) {
    didInitialFocus = true;
    requestAnimationFrame(() => scrollToFocus(true));
  }
}

function renderMonthSelect() {
  monthSelect.innerHTML = plans
    .map((plan) => `<option value="${escapeAttr(plan.monthId)}">${escapeHtml(monthLabel(plan.monthId, plan.title))}</option>`)
    .join("");
  monthSelect.value = activeMonthId;
  const index = plans.findIndex((plan) => plan.monthId === activeMonthId);
  prevMonthBtn.disabled = index <= 0;
  nextMonthBtn.disabled = index === -1 || index >= plans.length - 1;
}

function renderNowRail() {
  const today = todayIso();
  const focus = findFocusPoint(plans, today);
  if (!focus.current) {
    nowRail.hidden = true;
    nowRail.innerHTML = "";
    return;
  }

  const remember = plans.flatMap((plan) => relevantRememberItems(plan.rememberItems || [], today));
  nowRail.hidden = false;
  nowRail.innerHTML = `
    <div class="now-grid">
      ${nowCardHtml("Today", focus.current, focusFacts(focus.current), "current")}
      ${focus.next ? nowCardHtml("Next", focus.next, focusFacts(focus.next), "next") : ""}
    </div>
    ${remember.length ? `<ul class="now-remember">${remember.slice(0, 4).map((item) => `<li><span>${item.kind === "take" ? "Take" : "Remember"}</span>${richText(item.text)}</li>`).join("")}</ul>` : ""}
  `;
}

function nowCardHtml(label, section, facts, kind) {
  return `<button type="button" class="now-card ${kind}" data-section-id="${escapeAttr(section.id)}" data-month-id="${escapeAttr(section.monthId)}">
    <span class="now-kicker">${escapeHtml(label)} · ${escapeHtml(formatLongDate(section.startDate))}</span>
    <strong>${escapeHtml(shortTitle(section.title))}</strong>
    ${facts.fact ? `<p>${highlightDetail(facts.fact)}</p>` : ""}
    ${facts.warning ? `<p class="now-warning">${highlightDetail(facts.warning)}</p>` : ""}
  </button>`;
}

function renderOverview(plan) {
  const counts = categoryCounts(plan.events || []);
  const activeOpenItems = (plan.openItems || []).filter((item) => !item.checked);
  const updated = plan.updatedAt || plan.importedAt || plan.parsedAt || lastCacheAt;
  const summary = (plan.summaryItems || []).slice(0, 10);
  const warnings = plan.warnings || [];

  monthOverview.innerHTML = `<details class="overview-card">
    <summary>
      <span>
        <span class="eyebrow">Month Overview</span>
        <strong>${escapeHtml(monthLabel(plan.monthId, plan.title))}</strong>
      </span>
      <span class="privacy-pill">Private</span>
    </summary>
    <div class="overview-body">
      ${plan.base ? `<p class="base-line">${richText(plan.base)}</p>` : ""}
      <div class="stat-grid">
        <div><strong>${(plan.events || []).length}</strong><span>dated sections</span></div>
        <div><strong>${activeOpenItems.length}</strong><span>open items</span></div>
        <div><strong>${warnings.length}</strong><span>alerts</span></div>
        <div><strong>${formatUpdated(updated)}</strong><span>last import</span></div>
      </div>
      <div class="chips">${Object.entries(counts).map(([category, count]) => chipHtml(category, `${labelForCategory(category)}: ${count}`)).join("")}</div>
      ${warnings.length ? `<div class="alert-box"><h3>Potential overlaps</h3><ul>${warnings.map((warning) => `<li>${richText(warning.message)}</li>`).join("")}</ul></div>` : ""}
      ${summary.length ? `<div class="summary-box"><h3>Key dates</h3><ul>${summary.map((item) => `<li>${highlightLine(item)}</li>`).join("")}</ul></div>` : ""}
      ${activeOpenItems.length ? `<div class="open-box"><h3>Open items</h3><ul>${activeOpenItems.slice(0, 8).map((item) => `<li class="${item.urgent ? "urgent" : ""}">${richText(item.text)}</li>`).join("")}</ul></div>` : ""}
    </div>
  </details>`;
}

function renderWeeks(plan) {
  const today = todayIso();
  const eventsById = new Map((plan.events || []).map((event) => [event.id, event]));
  const sectionsById = new Map((plan.sections || []).map((section) => [section.id, section]));
  const weeks = plan.weeks || [];
  const pastWeeks = weeks.filter((week) => weekTiming(week, today) === "past");
  const liveWeeks = weeks.filter((week) => weekTiming(week, today) !== "past");
  const openWeekId = chooseExpandedWeek(liveWeeks.length ? liveWeeks : weeks);

  const weekHtml = (week, open) => {
    const weekEvents = week.eventIds.map((id) => eventsById.get(id)).filter(Boolean);
    return `<details class="week-card" ${open ? "open" : ""}>
      <summary>
        <span>
          <strong>${escapeHtml(week.label)}</strong>
          <small>${weekEvents.length} item${weekEvents.length === 1 ? "" : "s"}</small>
        </span>
        <span class="week-summary-chips">${weekEvents.slice(0, 4).map((event) => chipHtml(event.category, labelForCategory(event.category))).join("")}</span>
      </summary>
      <div class="week-body">
        ${weekEvents.length ? weekEvents.map((event) => sectionHtml(sectionsById.get(event.id), event, today)).join("") : "<p class=\"muted\">No dated travel plan items this week.</p>"}
      </div>
    </details>`;
  };

  const pastHtml = pastWeeks.length
    ? `<details class="past-weeks">
        <summary>Earlier this month · ${pastWeeks.length} week${pastWeeks.length === 1 ? "" : "s"}</summary>
        <div class="past-weeks-body">${pastWeeks.map((week) => weekHtml(week, false)).join("")}</div>
      </details>`
    : "";

  weekList.innerHTML = pastHtml + liveWeeks.map((week) => weekHtml(week, week.id === openWeekId)).join("");
}

function sectionHtml(section, event, today) {
  if (!section) return "";
  const timing = sectionTiming(section, today);
  const body = section.body ? `<div class="detail-flow">${formatSectionBody(section.body)}</div>` : "";
  const head = `
    <div>
      <h3>${escapeHtml(section.title)}</h3>
      <p>${escapeHtml(formatDateRange(section.startDate, section.endDate))}</p>
    </div>
    <div class="section-chips">
      ${chipHtml(event.category, labelForCategory(event.category))}
      ${event.status.cancelled ? chipHtml("cancelled", "Cancelled") : ""}
      ${event.status.paid ? chipHtml("paid", "Paid") : ""}
      ${event.status.confirmed ? chipHtml("confirmed", "Confirmed") : ""}
      ${event.status.tbc ? chipHtml("tbc", "TBC") : ""}
    </div>`;

  if (timing === "past") {
    return `<details class="section-card past ${escapeAttr(event.category)}" id="sec-${escapeAttr(section.id)}">
      <summary class="section-head">${head}</summary>
      ${body}
    </details>`;
  }

  return `<article class="section-card ${escapeAttr(timing)} ${escapeAttr(event.category)}" id="sec-${escapeAttr(section.id)}">
    <div class="section-head">${head}</div>
    ${body}
  </article>`;
}

function moveMonth(offset) {
  const index = plans.findIndex((plan) => plan.monthId === activeMonthId);
  const next = plans[index + offset];
  if (!next) return;
  setBrowseMonth(next.monthId);
  render();
}

function setBrowseMonth(monthId) {
  if (!monthId || !plansById.has(monthId)) return;
  activeMonthId = monthId;
  viewMode = "browse";
  writeBrowseMonth(monthId);
}

function jumpToNow() {
  viewMode = "now";
  writeBrowseMonth("");
  const focus = findFocusPoint(plans, todayIso());
  if (focus.current?.monthId) activeMonthId = focus.current.monthId;
  didInitialFocus = false;
  render();
}

function openSection(monthId, sectionId) {
  if (monthId && plansById.has(monthId) && monthId !== activeMonthId) {
    setBrowseMonth(monthId);
    render();
  }
  requestAnimationFrame(() => {
    const target = document.getElementById(`sec-${sectionId}`);
    if (!target) return;
    if (target instanceof HTMLDetailsElement) target.open = true;
    const week = target.closest("details.week-card");
    if (week) week.open = true;
    target.scrollIntoView({ block: "start", behavior: "smooth" });
  });
}

function scrollToFocus(force) {
  if (!force && viewMode !== "now") return;
  const focus = findFocusPoint(plans, todayIso());
  if (!focus.current) return;
  if (focus.current.monthId && focus.current.monthId !== activeMonthId) {
    activeMonthId = focus.current.monthId;
    render();
    return;
  }
  const target = document.getElementById(`sec-${focus.current.id}`);
  if (!target) return;
  if (target instanceof HTMLDetailsElement) target.open = true;
  const week = target.closest("details.week-card");
  if (week) week.open = true;
  target.scrollIntoView({ block: "start", behavior: "instant" });
}

function chooseActiveMonth(preferred) {
  if (preferred && plansById.has(preferred)) return preferred;
  const current = todayIso().slice(0, 7);
  if (plansById.has(current)) return current;
  const focus = findFocusPoint(plans, todayIso());
  if (focus.current?.monthId && plansById.has(focus.current.monthId)) return focus.current.monthId;
  return plans.at(-1)?.monthId || "";
}

function chooseExpandedWeek(weeks) {
  if (!weeks.length) return "";
  const today = todayIso();
  const current = weeks.find((week) => week.startDate <= today && week.endDate >= today);
  return (current || weeks.find((week) => week.eventIds.length) || weeks[0]).id;
}

function hydratePlan(plan) {
  if (!plan) return plan;
  const next = { ...plan };
  if ((!next.rememberItems || !next.rememberItems.length) && next.rawText) {
    next.rememberItems = parseRememberItems(String(next.rawText).split("\n"));
  }
  if (next.sections) {
    next.sections = next.sections.map((section) => ({
      ...section,
      category: detectCategory(`${section.title}\n${section.body || ""}`),
      status: detectStatus(`${section.title}\n${section.body || ""}`)
    }));
    const categories = new Map(next.sections.map((section) => [section.id, section]));
    next.events = (next.events || []).map((event) => {
      const section = categories.get(event.id);
      return section ? { ...event, category: section.category, status: section.status } : event;
    });
  }
  return next;
}

function applyPlans(list, { fromCache = false, cachedAt = "" } = {}) {
  plans = (list || []).map(hydratePlan);
  plansById = new Map(plans.map((plan) => [plan.monthId || plan.id, plan]));
  if (viewMode === "browse") {
    activeMonthId = chooseActiveMonth(readBrowseMonth() || activeMonthId);
  } else {
    const focus = findFocusPoint(plans, todayIso());
    activeMonthId = focus.current?.monthId || chooseActiveMonth(activeMonthId);
  }
  if (fromCache) lastCacheAt = cachedAt || lastCacheAt;
}

function readBrowseMonth() {
  try { return sessionStorage.getItem(BROWSE_MONTH_KEY) || ""; } catch { return ""; }
}

function writeBrowseMonth(monthId) {
  try {
    if (monthId) sessionStorage.setItem(BROWSE_MONTH_KEY, monthId);
    else sessionStorage.removeItem(BROWSE_MONTH_KEY);
  } catch { /* ignore */ }
}

function cacheStorageKey(email) {
  return `${PLAN_CACHE_VERSION}:${email || "local"}`;
}

function readLastUser() {
  try { return localStorage.getItem(LAST_USER_KEY) || ""; } catch { return ""; }
}

function writeLastUser(email) {
  try { localStorage.setItem(LAST_USER_KEY, email || ""); } catch { /* ignore */ }
}

function readPlanCache(email = readLastUser()) {
  try {
    const raw = localStorage.getItem(cacheStorageKey(email));
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (!Array.isArray(data?.plans) || !data.plans.length) return null;
    return data;
  } catch {
    return null;
  }
}

function writePlanCache(email, list) {
  const payload = { userEmail: email || "", plans: list, cachedAt: new Date().toISOString() };
  try {
    localStorage.setItem(cacheStorageKey(email), JSON.stringify(payload));
    writeLastUser(email);
    lastCacheAt = payload.cachedAt;
    return;
  } catch {
    const slim = list.map(({ rawText, ...rest }) => rest);
    try {
      localStorage.setItem(cacheStorageKey(email), JSON.stringify({ ...payload, plans: slim }));
      writeLastUser(email);
      lastCacheAt = payload.cachedAt;
    } catch { /* ignore */ }
  }
}

function plansSignature(list) {
  return (list || [])
    .map((plan) => `${plan.monthId}:${plan.updatedAt || plan.importedAt || plan.parsedAt}:${(plan.sections || []).length}`)
    .join("|");
}

function cachedStatus(cachedAt, extra = "") {
  const when = formatUpdatedDateTime(cachedAt);
  return [`Showing cached plans${when ? ` from ${when}` : ""}`, extra].filter(Boolean).join(" · ");
}

function setAppState(state, message) {
  authState = state;
  setStatus(message);
  const isSignedIn = Boolean(currentUser);
  const canBrowse = isSignedIn || plans.length > 0;
  signInBtn.hidden = isSignedIn;
  signOutBtn.hidden = !isSignedIn;
  signInBtn.style.display = isSignedIn ? "none" : "";
  signOutBtn.style.display = isSignedIn ? "" : "none";
  signedInControls.hidden = !canBrowse || state === "unauthorized";
  refreshBtn.disabled = !isSignedIn || state === "loading";
  importFile.disabled = !isSignedIn || state === "loading";
  userLabel.textContent = currentUser
    ? (currentUser.email || "Signed in")
    : (plans.length ? (cachedUserEmail || "Cached plans") : "Signed out");
}

function setStatus(message) {
  statusEl.textContent = message;
}

function permissionDenied(error) {
  return String(error?.code || error?.message || "").toLowerCase().includes("permission");
}

function serializeData(value) {
  if (Array.isArray(value)) return value.map(serializeData);
  if (value && typeof value === "object") {
    if (typeof value.toDate === "function") return value.toDate().toISOString();
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, serializeData(item)]));
  }
  return value;
}

function cleanObject(value) {
  if (Array.isArray(value)) return value.map(cleanObject).filter((item) => item !== undefined);
  if (value && typeof value === "object" && typeof value.toDate !== "function") {
    return Object.fromEntries(
      Object.entries(value)
        .map(([key, item]) => [key, cleanObject(item)])
        .filter(([, item]) => item !== undefined)
    );
  }
  return value === undefined ? null : value;
}

function categoryCounts(events) {
  return events.reduce((result, event) => {
    result[event.category] = (result[event.category] || 0) + 1;
    return result;
  }, {});
}

function chipHtml(category, label) {
  return `<span class="chip ${escapeAttr(category)}">${escapeHtml(label)}</span>`;
}

function highlightLine(line) {
  return richText(line)
    .replace(/\b(FLY|FLIGHT|HOTEL|MUST|REGISTERED|CANCELLED|TBC)\b/g, "<strong>$1</strong>")
    .replace(/(\d{1,2}:\d{2})/g, "<time>$1</time>");
}

function formatSectionBody(body) {
  return groupBodyLines(body).map(blockHtml).join("");
}

function blockHtml(block) {
  switch (block.type) {
    case "heading":
      return `<h4 class="detail-heading">${escapeHtml(block.text)}</h4>`;
    case "callout":
      return `<p class="detail-callout">${highlightDetail(block.text)}</p>`;
    case "prose":
      return `<p class="detail-prose">${highlightDetail(block.text)}</p>`;
    case "field":
      return `<div class="detail-field"><span class="field-label">${escapeHtml(block.label)}</span><span class="field-value">${highlightDetail(block.value)}</span></div>`;
    case "checks":
      return `<ul class="detail-checks">${block.items.map((item) => `
        <li class="${item.checked ? "is-done" : ""} ${item.urgent ? "is-urgent" : ""}">
          <span class="check-mark" aria-hidden="true">${item.checked ? "☑" : "☐"}</span>
          <span>${highlightDetail(item.text)}${item.note ? `<small>${highlightDetail(item.note)}</small>` : ""}</span>
        </li>`).join("")}</ul>`;
    case "bullets":
      return `<ul class="detail-bullets">${block.items.map((item) => `<li>${highlightDetail(item)}</li>`).join("")}</ul>`;
    default:
      return "";
  }
}

function highlightDetail(line) {
  return richText(line)
    .replace(/\b(FLIGHT|HOTEL|TRANSFER|CHECK-IN|CHECK-OUT|Booking|PIN|Cost|Time|Venue|Note|CANCELLED|TBC|PAID|Depart|Arrive|Seat|Baggage|Address)\b/g, "<strong>$1</strong>")
    .replace(/(\d{1,2}:\d{2}(?:\s*(?:[\u2013-]|\u2192)\s*\d{1,2}:\d{2})?)/g, "<time>$1</time>");
}

function richText(value) {
  const text = String(value ?? "");
  const parts = [];
  const pattern = /https?:\/\/[^\s)]+/gi;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text))) {
    parts.push(escapeHtml(text.slice(lastIndex, match.index)));
    const url = match[0];
    parts.push(`<a href="${escapeAttr(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(shortLinkLabel(url))}</a>`);
    lastIndex = match.index + url.length;
  }

  parts.push(escapeHtml(text.slice(lastIndex)));
  return parts.join("");
}

function shortLinkLabel(url) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("maps.app.goo.gl") || parsed.hostname.includes("google.")) return "Google Maps";
    return parsed.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function shortTitle(title) {
  return String(title || "").replace(/^[A-Z]{3,9}\s+\d{1,2}(?:\s*[-–]\s*[A-Z]{3,9}?\s*\d{1,2})?(?:\s*\([A-Z]{3}\))?\s*[—-]\s*/i, "");
}

function labelForCategory(category) {
  return {
    flight: "Flight",
    hotel: "Hotel",
    transfer: "Transfer",
    business: "Business",
    personal: "Personal",
    event: "Event",
    cancelled: "Cancelled",
    paid: "Paid",
    confirmed: "Confirmed",
    tbc: "TBC"
  }[category] || category;
}

function monthLabel(monthId, title) {
  const match = String(monthId || "").match(/^(\d{4})-(\d{2})$/);
  if (!match) return title || monthId || "Travel plan";
  return `${MONTH_NAMES[Number(match[2]) - 1]} ${match[1]}`;
}

function formatDateRange(startDate, endDate) {
  return startDate === endDate ? formatLongDate(startDate) : `${formatLongDate(startDate)} to ${formatLongDate(endDate)}`;
}

function formatLongDate(iso) {
  const date = dateFromIso(iso);
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
}

function formatShortDate(iso) {
  const date = dateFromIso(iso);
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", timeZone: "UTC" });
}

function formatUpdated(value) {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return "n/a";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function formatUpdatedDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return "";
  return date.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function rangesOverlap(left, right) {
  return left.start < right.end && right.start < left.end;
}

function dateRangesOverlap(left, right) {
  return left.startDate <= right.endDate && right.startDate <= left.endDate;
}

function weekStart(iso) {
  const date = dateFromIso(iso);
  const day = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() - day + 1);
  return isoFromDate(date);
}

function addDays(iso, days) {
  const date = dateFromIso(iso);
  date.setUTCDate(date.getUTCDate() + days);
  return isoFromDate(date);
}

function dateFromIso(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function isoDate(year, monthIndex, day) {
  const date = new Date(Date.UTC(year, monthIndex, day));
  return isoFromDate(date);
}

function isoFromDate(date) {
  return `${date.getUTCFullYear()}-${pad2(date.getUTCMonth() + 1)}-${pad2(date.getUTCDate())}`;
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

function isDivider(line) {
  return /^[=\-]{8,}$/.test(String(line || "").trim());
}

function trimBlankLines(items) {
  const result = [...items];
  while (result.length && !String(result[0]).trim()) result.shift();
  while (result.length && !String(result.at(-1)).trim()) result.pop();
  return result;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

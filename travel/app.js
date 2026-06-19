import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import {
  collection,
  doc,
  getDocs,
  getFirestore,
  serverTimestamp,
  setDoc
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";

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
let currentUser = null;
let authState = "starting";
let plans = [];
let plansById = new Map();
let activeMonthId = "";

const userLabel = document.getElementById("userLabel");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const signedInControls = document.getElementById("signedInControls");
const monthSelect = document.getElementById("monthSelect");
const prevMonthBtn = document.getElementById("prevMonthBtn");
const nextMonthBtn = document.getElementById("nextMonthBtn");
const refreshBtn = document.getElementById("refreshBtn");
const importFile = document.getElementById("importFile");
const statusEl = document.getElementById("status");
const monthOverview = document.getElementById("monthOverview");
const weekList = document.getElementById("weekList");
const empty = document.getElementById("empty");

boot();

async function boot() {
  bindEvents();
  setAppState("starting", "Loading Firebase...");

  try {
    const firebaseConfig = await loadFirebaseConfig();
    const app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    const provider = new GoogleAuthProvider();

    signInBtn.addEventListener("click", async () => {
      try {
        await signInWithPopup(auth, provider);
      } catch (error) {
        setStatus(`Sign-in failed: ${error.message}`);
      }
    });
    signOutBtn.addEventListener("click", () => signOut(auth));
    onAuthStateChanged(auth, handleAuthChange);
  } catch (error) {
    console.error(error);
    setAppState("offline", "Firebase is unavailable here. Open this app from Firebase Hosting.");
  }
}

function bindEvents() {
  monthSelect.addEventListener("change", () => {
    activeMonthId = monthSelect.value;
    render();
  });
  prevMonthBtn.addEventListener("click", () => moveMonth(-1));
  nextMonthBtn.addEventListener("click", () => moveMonth(1));
  refreshBtn.addEventListener("click", () => currentUser && loadPlans());
  importFile.addEventListener("change", importMonthFiles);
}

async function loadFirebaseConfig() {
  const response = await fetch("/__/firebase/init.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Firebase config is only available from Firebase Hosting.");
  }
  return response.json();
}

async function handleAuthChange(user) {
  currentUser = user;
  plans = [];
  plansById = new Map();
  activeMonthId = "";

  if (!user) {
    setAppState("signed-out", "Sign in with Google to load private travel plans.");
    render();
    return;
  }

  userLabel.textContent = user.email || "Signed in";
  setAppState("loading", "Loading private travel plans...");
  await loadPlans();
}

async function loadPlans() {
  if (!currentUser || !db) return;
  setAppState("loading", "Loading private travel plans...");

  try {
    const snapshot = await getDocs(collection(db, "travelPlans"));
    plans = snapshot.docs
      .map((item) => ({ id: item.id, ...serializeData(item.data()) }))
      .sort((a, b) => String(a.monthId || a.id).localeCompare(String(b.monthId || b.id)));
    plansById = new Map(plans.map((plan) => [plan.monthId || plan.id, plan]));
    activeMonthId = chooseActiveMonth(activeMonthId);
    setAppState("ready", plans.length ? `${plans.length} private month plan${plans.length === 1 ? "" : "s"} loaded.` : "No travel plans uploaded yet.");
    render();
  } catch (error) {
    console.error(error);
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
  if (!files.length || !currentUser || !db) return;
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
        updatedAt: serverTimestamp(),
        importedAt: serverTimestamp()
      };
      const bytes = new TextEncoder().encode(JSON.stringify(payload)).length;
      if (bytes > MAX_DOC_BYTES) {
        throw new Error(`${file.name} is too large for a single Firestore document.`);
      }
      await setDoc(doc(db, "travelPlans", plan.monthId), payload);
      imported.push(plan.monthId);
    }
    activeMonthId = imported.at(-1) || activeMonthId;
    setStatus(`Imported ${imported.length} month plan${imported.length === 1 ? "" : "s"}.`);
    await loadPlans();
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
  const value = text.toLowerCase();
  if (/\bcancelled\b/.test(value)) return "cancelled";
  if (/\b(flight|fly|airport|depart|arrive|airways|air china|cathay|wizz)\b/.test(value)) return "flight";
  if (/\b(hotel|check-in|check-out|accommodation|room|nights)\b/.test(value)) return "hotel";
  if (/\b(transfer|taxi|ride|fast lane|luggage)\b/.test(value)) return "transfer";
  if (/\b(meeting|office|business|forum|presentation|epam|scsk|mitsui|nissan)\b/.test(value)) return "business";
  if (/\b(dinner|festival|primavera|private|sightseeing|weekend|free day|personal)\b/.test(value)) return "personal";
  return "event";
}

function detectStatus(text) {
  const value = text.toLowerCase();
  return {
    cancelled: /\bcancelled\b/.test(value),
    paid: /\bpaid\b|prepaid/.test(value),
    confirmed: /\bconfirmed\b|\[registered\]|\[must\]|\[x\]/.test(value),
    tbc: /\btbc\b|to be confirmed|\[ \]/.test(value),
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
  const isSignedIn = Boolean(currentUser);
  const activePlan = plansById.get(activeMonthId);
  renderMonthSelect();
  empty.hidden = isSignedIn && plans.length > 0;
  monthOverview.hidden = !isSignedIn || !activePlan;
  weekList.hidden = !isSignedIn || !activePlan;

  if (!isSignedIn) {
    monthOverview.innerHTML = "";
    weekList.innerHTML = "";
    empty.textContent = "Sign in with an allowed Google account to view private travel plans.";
    return;
  }
  if (!plans.length) {
    monthOverview.innerHTML = "";
    weekList.innerHTML = "";
    empty.textContent = authState === "unauthorized"
      ? "This account is not allowed to access private travel plans."
      : "No travel plans uploaded yet. Upload one or more monthly text files.";
    return;
  }
  renderOverview(activePlan);
  renderWeeks(activePlan);
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

function renderOverview(plan) {
  const counts = categoryCounts(plan.events || []);
  const activeOpenItems = (plan.openItems || []).filter((item) => !item.checked);
  const updated = plan.updatedAt || plan.importedAt || plan.parsedAt;
  const summary = (plan.summaryItems || []).slice(0, 10);
  const warnings = plan.warnings || [];

  monthOverview.innerHTML = `<details class="overview-card" open>
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
  const eventsById = new Map((plan.events || []).map((event) => [event.id, event]));
  const sectionsById = new Map((plan.sections || []).map((section) => [section.id, section]));
  const activeWeekId = chooseExpandedWeek(plan.weeks || []);
  weekList.innerHTML = (plan.weeks || []).map((week) => {
    const weekEvents = week.eventIds.map((id) => eventsById.get(id)).filter(Boolean);
    return `<details class="week-card" ${week.id === activeWeekId ? "open" : ""}>
      <summary>
        <span>
          <strong>${escapeHtml(week.label)}</strong>
          <small>${weekEvents.length} item${weekEvents.length === 1 ? "" : "s"}</small>
        </span>
        <span class="week-summary-chips">${weekEvents.slice(0, 4).map((event) => chipHtml(event.category, labelForCategory(event.category))).join("")}</span>
      </summary>
      <div class="week-body">
        ${weekEvents.length ? weekEvents.map((event) => sectionHtml(sectionsById.get(event.id), event)).join("") : "<p class=\"muted\">No dated travel plan items this week.</p>"}
      </div>
    </details>`;
  }).join("");
}

function sectionHtml(section, event) {
  if (!section) return "";
  return `<article class="section-card ${escapeAttr(event.category)}">
    <div class="section-head">
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
      </div>
    </div>
    ${section.body ? `<div class="detail-lines">${formatSectionBody(section.body)}</div>` : ""}
  </article>`;
}

function moveMonth(offset) {
  const index = plans.findIndex((plan) => plan.monthId === activeMonthId);
  const next = plans[index + offset];
  if (!next) return;
  activeMonthId = next.monthId;
  render();
}

function chooseActiveMonth(preferred) {
  if (preferred && plansById.has(preferred)) return preferred;
  const now = new Date();
  const current = `${now.getFullYear()}-${pad2(now.getMonth() + 1)}`;
  if (plansById.has(current)) return current;
  return plans.at(-1)?.monthId || "";
}

function chooseExpandedWeek(weeks) {
  if (!weeks.length) return "";
  const today = isoFromDate(new Date());
  const current = weeks.find((week) => week.startDate <= today && week.endDate >= today);
  return (current || weeks.find((week) => week.eventIds.length) || weeks[0]).id;
}

function setAppState(state, message) {
  authState = state;
  setStatus(message);
  const isSignedIn = Boolean(currentUser);
  signInBtn.hidden = isSignedIn;
  signOutBtn.hidden = !isSignedIn;
  signInBtn.style.display = isSignedIn ? "none" : "";
  signOutBtn.style.display = isSignedIn ? "" : "none";
  signedInControls.hidden = !isSignedIn || state === "unauthorized";
  refreshBtn.disabled = state === "loading";
  importFile.disabled = state === "loading";
  userLabel.textContent = currentUser ? (currentUser.email || "Signed in") : "Signed out";
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
  return String(body || "")
    .split("\n")
    .map(detailLineHtml)
    .join("");
}

function detailLineHtml(line) {
  const trimmed = line.trim();
  if (!trimmed) return "<div class=\"detail-spacer\"></div>";

  const field = trimmed.match(/^([A-Za-z][A-Za-z /-]{1,24}):\s*(.+)$/);
  if (field) {
    return `<div class="detail-line field-line">
      <span class="field-label">${escapeHtml(field[1])}</span>
      <span class="field-value">${highlightDetail(field[2])}</span>
    </div>`;
  }

  return `<div class="detail-line ${line.startsWith("    ") || line.startsWith("  ") ? "indented" : ""}">${highlightDetail(trimmed)}</div>`;
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

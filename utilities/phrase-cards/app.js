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
  getDoc,
  getDocs,
  getFirestore,
  setDoc
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";
import {
  getDownloadURL,
  getStorage,
  ref
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-storage.js";

const DB_NAME = "phrase-cards-cache";
const DB_VERSION = 1;
const BOX_GAPS = { 1: 1, 2: 3, 3: 10 };

let auth = null;
let db = null;
let storage = null;
let currentUser = null;
let pack = null;
let progress = new Map();
let view = "study";
let session = [];
let sessionIndex = 0;
let showingBack = false;
let activeDayId = null;
let usingOfflineProgress = false;
let activeAudio = null;

const statusEl = document.getElementById("status");
const offlineNote = document.getElementById("offlineNote");
const userLabel = document.getElementById("userLabel");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const signedInControls = document.getElementById("signedInControls");
const studyTab = document.getElementById("studyTab");
const daysTab = document.getElementById("daysTab");
const studyView = document.getElementById("studyView");
const daysView = document.getElementById("daysView");
const signedOutEmpty = document.getElementById("signedOutEmpty");
const sessionMeta = document.getElementById("sessionMeta");
const cardEl = document.getElementById("card");
const sessionEmpty = document.getElementById("sessionEmpty");
const dayRecap = document.getElementById("dayRecap");
const cardEyebrow = document.getElementById("cardEyebrow");
const cardFront = document.getElementById("cardFront");
const cardBack = document.getElementById("cardBack");
const playBtn = document.getElementById("playBtn");
const slowBtn = document.getElementById("slowBtn");
const flipBtn = document.getElementById("flipBtn");
const againBtn = document.getElementById("againBtn");
const gotItBtn = document.getElementById("gotItBtn");
const dayList = document.getElementById("dayList");
const prevDayBtn = document.getElementById("prevDayBtn");
const nextDayBtn = document.getElementById("nextDayBtn");
const dayNavLabel = document.getElementById("dayNavLabel");

boot();

async function boot() {
  bindEvents();
  try {
    pack = await loadLessons();
  } catch (error) {
    setStatus("Could not load the phrase pack.");
    console.error(error);
    return;
  }

  try {
    const firebaseConfig = await loadFirebaseConfig();
    const app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    storage = getStorage(app);
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
    setStatus("Firebase is only available on Firebase Hosting.");
    console.error(error);
  }
}

function bindEvents() {
  studyTab.addEventListener("click", () => setView("study"));
  daysTab.addEventListener("click", () => setView("days"));
  playBtn.addEventListener("click", () => playCurrent(1));
  slowBtn.addEventListener("click", () => playCurrent(0.75));
  flipBtn.addEventListener("click", toggleBack);
  againBtn.addEventListener("click", () => gradeCurrent("again"));
  gotItBtn.addEventListener("click", () => gradeCurrent("got"));
  prevDayBtn.addEventListener("click", () => shiftDay(-1));
  nextDayBtn.addEventListener("click", () => shiftDay(1));
  dayRecap.addEventListener("click", event => {
    const button = event.target.closest("[data-play-line]");
    if (!button) return;
    const line = allLines().find(item => item.id === button.dataset.playLine);
    if (line) playLine(line, 1);
  });
  dayList.addEventListener("click", event => {
    const button = event.target.closest("[data-day-id]");
    if (!button) return;
    setActiveDay(button.dataset.dayId);
    setView("study");
  });
  window.addEventListener("online", () => {
    offlineNote.textContent = "";
    if (currentUser) syncProgress();
  });
  window.addEventListener("offline", () => {
    offlineNote.textContent = "Offline";
  });
}

async function loadFirebaseConfig() {
  const response = await fetch("/__/firebase/init.json", { cache: "no-store" });
  if (!response.ok) throw new Error("Firebase config is only available from Firebase Hosting.");
  return response.json();
}

async function loadLessons() {
  const response = await fetch("./lessons.json", { cache: "no-store" });
  if (!response.ok) throw new Error("Missing lessons.json");
  return response.json();
}

async function handleAuthChange(user) {
  currentUser = user;
  progress = new Map();

  if (!user) {
    setSignedInUi(false);
    setStatus("Sign in with Google to study Malay phrases.");
    render();
    return;
  }

  setSignedInUi(true);
  setStatus("Loading your review pile...");
  await loadActiveDay();
  await syncProgress();
}

function setSignedInUi(isSignedIn) {
  signInBtn.hidden = isSignedIn;
  signOutBtn.hidden = !isSignedIn;
  signInBtn.style.display = isSignedIn ? "none" : "";
  signOutBtn.style.display = isSignedIn ? "" : "none";
  signedInControls.hidden = !isSignedIn;
  userLabel.textContent = isSignedIn ? (currentUser?.email || "Signed in") : "Signed out";
}

async function syncProgress() {
  if (!currentUser || !db) return;
  try {
    await flushPendingProgress();
    const snapshot = await getDocs(collection(db, "users", currentUser.uid, "phraseProgress"));
    progress = new Map();
    snapshot.forEach(item => progress.set(item.id, item.data()));
    usingOfflineProgress = false;
    await idbSet("cache", { id: "progress", uid: currentUser.uid, items: Object.fromEntries(progress) });
    if (view === "study") buildSession();
    setStatus(statusSummary());
    render();
    prefetchSessionAudio();
  } catch (error) {
    const cached = await idbGet("cache", "progress");
    if (cached?.items) {
      progress = new Map(Object.entries(cached.items));
      usingOfflineProgress = true;
    }
    setStatus(permissionDenied(error)
      ? "This Google account is not allowed to access Phrase Cards."
      : "Showing cached progress. Review still works offline.");
    if (permissionDenied(error)) {
      currentUser = null;
      setSignedInUi(false);
    } else if (view === "study") {
      buildSession();
    }
    render();
  }
}

function setView(next) {
  view = next;
  studyTab.classList.toggle("active", view === "study");
  daysTab.classList.toggle("active", view === "days");
  if (view === "study") buildSession();
  render();
}

function render() {
  const signedIn = Boolean(currentUser);
  signedOutEmpty.hidden = signedIn;
  studyView.hidden = !signedIn || view !== "study";
  daysView.hidden = !signedIn || view !== "days";
  if (!signedIn) return;
  if (view === "days") {
    renderDays();
    return;
  }
  renderCard();
}

function renderDays() {
  dayList.innerHTML = (pack.days || []).map(day => {
    const lines = day.lines || [];
    const seen = lines.filter(line => progress.has(line.id)).length;
    const current = day.id === activeDayId ? " current" : "";
    return `<button class="day-card${current}" type="button" data-day-id="${escapeAttr(day.id)}">
      <strong>Day ${day.day} — ${escapeHtml(day.title)}</strong>
      <span>${seen}/${lines.length} reviewed${day.id === activeDayId ? " · current" : ""}</span>
    </button>`;
  }).join("");
}

function buildSession() {
  ensureActiveDay();
  const today = todayKey();
  const lines = allLines().filter(line => line.dayId === activeDayId);
  const due = lines.filter(line => {
    const item = progress.get(line.id);
    return item && item.nextDue <= today;
  });
  const rest = lines.filter(line => !due.some(item => item.id === line.id));
  session = [...due, ...rest];
  sessionIndex = 0;
  showingBack = false;
  updateDayNav();
}

function updateDayNav() {
  const days = pack?.days || [];
  const index = days.findIndex(day => day.id === activeDayId);
  const day = days[index];
  dayNavLabel.textContent = day ? `Day ${day.day} — ${day.title}` : "Day";
  prevDayBtn.disabled = index <= 0;
  nextDayBtn.disabled = index < 0 || index >= days.length - 1;
}

function ensureActiveDay() {
  const days = pack?.days || [];
  if (days.some(day => day.id === activeDayId)) return;
  const unseen = allLines().find(line => !progress.has(line.id));
  activeDayId = unseen?.dayId || days[0]?.id || null;
}

async function loadActiveDay() {
  const cached = await idbGet("cache", "settings");
  if (cached?.activeDayId) activeDayId = cached.activeDayId;
  if (!currentUser || !db) return;
  try {
    const snapshot = await getDoc(doc(db, "users", currentUser.uid, "phraseSettings", "main"));
    if (snapshot.exists() && snapshot.data().activeDayId) {
      activeDayId = snapshot.data().activeDayId;
    }
  } catch (error) {
    console.error(error);
  }
}

function setActiveDay(dayId) {
  if (!dayId) return;
  activeDayId = dayId;
  saveActiveDay();
}

function shiftDay(delta) {
  const days = pack?.days || [];
  const index = days.findIndex(day => day.id === activeDayId);
  const next = days[index + delta];
  if (!next) return;
  setActiveDay(next.id);
  buildSession();
  render();
  prefetchSessionAudio();
}

async function saveActiveDay() {
  await idbSet("cache", {
    id: "settings",
    activeDayId,
    updatedAt: new Date().toISOString()
  });
  if (!currentUser || !db || !navigator.onLine) return;
  try {
    await setDoc(doc(db, "users", currentUser.uid, "phraseSettings", "main"), {
      activeDayId,
      updatedAt: new Date().toISOString()
    });
  } catch (error) {
    console.error(error);
  }
}

function renderCard() {
  const line = session[sessionIndex];
  sessionEmpty.hidden = Boolean(line);
  cardEl.hidden = !line;
  updateDayNav();
  if (!line) {
    sessionMeta.textContent = "";
    renderDayRecap();
    return;
  }

  const label = `${sessionIndex + 1} of ${session.length}`;
  sessionMeta.textContent = usingOfflineProgress ? `${label} · cached` : label;
  cardEyebrow.textContent = `Day ${line.dayNumber} — ${line.dayTitle}`;
  cardFront.textContent = line.text;
  cardBack.innerHTML = `
    <p class="meaning">${escapeHtml(line.meaning)}</p>
    ${line.formal && line.formal !== line.text ? `<p class="hint">Formal: ${escapeHtml(line.formal)}</p>` : ""}
    ${line.stress ? `<p class="hint">${escapeHtml(line.stress)}</p>` : ""}
  `;
  cardBack.hidden = !showingBack;
  flipBtn.textContent = showingBack ? "Hide" : "Meaning";
}

function renderDayRecap() {
  const lines = allLines().filter(item => item.dayId === activeDayId);
  dayRecap.innerHTML = lines.map(item => `
    <li>
      <div>
        <strong>${escapeHtml(item.text)}</strong>
        <span>${escapeHtml(item.meaning)}</span>
      </div>
      <button class="secondary" type="button" data-play-line="${escapeAttr(item.id)}">Play</button>
    </li>
  `).join("");
}

function toggleBack() {
  showingBack = !showingBack;
  renderCard();
}

async function gradeCurrent(result) {
  const line = session[sessionIndex];
  if (!line || !currentUser) return;
  const today = todayKey();
  const current = progress.get(line.id);
  let box = Number(current?.box) || 1;
  let reps = Number(current?.reps) || 0;
  if (result === "again") {
    box = 1;
    reps = 0;
  } else if (!current) {
    box = 2;
    reps = 1;
  } else {
    box = Math.min(3, box + 1);
    reps += 1;
  }
  const item = {
    lineId: line.id,
    language: pack.language,
    box,
    reps,
    nextDue: addDays(today, BOX_GAPS[box]),
    updatedAt: new Date().toISOString()
  };
  progress.set(line.id, item);
  await saveProgress(item);
  session.splice(sessionIndex, 1);
  if (sessionIndex >= session.length) sessionIndex = Math.max(0, session.length - 1);
  showingBack = false;
  setStatus(statusSummary());
  renderCard();
}

async function saveProgress(item) {
  await idbSet("cache", { id: "progress", uid: currentUser.uid, items: Object.fromEntries(progress) });
  if (!navigator.onLine || !db) {
    await idbSet("pending", { ...item, id: item.lineId });
    return;
  }
  try {
    await setDoc(doc(db, "users", currentUser.uid, "phraseProgress", item.lineId), item);
  } catch (error) {
    await idbSet("pending", { ...item, id: item.lineId });
    console.error(error);
  }
}

async function flushPendingProgress() {
  const pending = await idbAll("pending");
  if (!pending.length || !db || !currentUser) return;
  for (const item of pending) {
    await setDoc(doc(db, "users", currentUser.uid, "phraseProgress", item.lineId || item.id), item);
    await idbDelete("pending", item.id);
  }
}

async function playCurrent(rate) {
  const line = session[sessionIndex];
  if (line) await playLine(line, rate);
}

async function playLine(line, rate) {
  if (!line) return;
  stopAudio();
  try {
    const blob = await loadAudio(line);
    if (blob) {
      const url = URL.createObjectURL(blob);
      activeAudio = new Audio(url);
      activeAudio.playbackRate = rate;
      activeAudio.onended = () => URL.revokeObjectURL(url);
      await activeAudio.play();
      return;
    }
  } catch (error) {
    console.error(error);
  }
  speakFallback(line.speak || line.text, rate);
}

function stopAudio() {
  if (!activeAudio) return;
  activeAudio.pause();
  activeAudio = null;
}

async function loadAudio(line) {
  const cached = await idbGet("audio", line.id);
  if (cached?.blob) return cached.blob;
  if (!storage || !currentUser || !navigator.onLine || !line.audioPath) return null;
  const url = await getDownloadURL(ref(storage, line.audioPath));
  const response = await fetch(url);
  if (!response.ok) return null;
  const blob = await response.blob();
  await idbSet("audio", { id: line.id, blob });
  return blob;
}

async function prefetchSessionAudio() {
  for (const line of session.slice(0, 8)) {
    try {
      await loadAudio(line);
    } catch {
      break;
    }
  }
}

function speakFallback(text, rate) {
  if (!("speechSynthesis" in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = pack.locale || "ms-MY";
  utterance.rate = rate;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

function allLines() {
  return (pack.days || []).flatMap(day => (day.lines || []).map(line => ({
    ...line,
    dayId: day.id,
    dayNumber: day.day,
    dayTitle: day.title
  })));
}

function statusSummary() {
  const today = todayKey();
  const due = allLines().filter(line => {
    const item = progress.get(line.id);
    return item && item.nextDue <= today;
  }).length;
  const unseen = allLines().filter(line => !progress.has(line.id)).length;
  return `${due} due · ${unseen} new`;
}

function todayKey() {
  const now = new Date();
  return formatDate(now);
}

function addDays(key, count) {
  const [year, month, day] = key.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  date.setDate(date.getDate() + count);
  return formatDate(date);
}

function formatDate(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function permissionDenied(error) {
  return error?.code === "permission-denied" || String(error?.message || "").includes("Missing or insufficient permissions");
}

function setStatus(message) {
  statusEl.textContent = message;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function openIdb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const dbHandle = request.result;
      if (!dbHandle.objectStoreNames.contains("cache")) dbHandle.createObjectStore("cache", { keyPath: "id" });
      if (!dbHandle.objectStoreNames.contains("pending")) dbHandle.createObjectStore("pending", { keyPath: "id" });
      if (!dbHandle.objectStoreNames.contains("audio")) dbHandle.createObjectStore("audio", { keyPath: "id" });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function idbGet(storeName, key) {
  const dbHandle = await openIdb();
  return idbRequest(dbHandle.transaction(storeName).objectStore(storeName).get(key));
}

async function idbSet(storeName, value) {
  const dbHandle = await openIdb();
  return idbRequest(dbHandle.transaction(storeName, "readwrite").objectStore(storeName).put(value));
}

async function idbDelete(storeName, key) {
  const dbHandle = await openIdb();
  return idbRequest(dbHandle.transaction(storeName, "readwrite").objectStore(storeName).delete(key));
}

async function idbAll(storeName) {
  const dbHandle = await openIdb();
  return idbRequest(dbHandle.transaction(storeName).objectStore(storeName).getAll());
}

function idbRequest(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

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
  deleteDoc,
  doc,
  getDocs,
  getFirestore,
  serverTimestamp,
  setDoc,
  writeBatch
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";

const OFFLINE_SHOW_LIMIT = 10;
const DB_NAME = "kcrw-tracklists-cache";
const DB_VERSION = 1;

let auth = null;
let db = null;
let currentUser = null;
let shows = [];
let tracksByShow = new Map();
let marks = new Map();
let authState = "starting";
let usingOfflineCopy = false;
let activeShowId = null;

const showsEl = document.getElementById("shows");
const empty = document.getElementById("empty");
const statusEl = document.getElementById("status");
const offlineNote = document.getElementById("offlineNote");
const search = document.getElementById("search");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const userLabel = document.getElementById("userLabel");
const signedInControls = document.getElementById("signedInControls");
const refreshBtn = document.getElementById("refreshBtn");
const importFile = document.getElementById("importFile");
const detailDialog = document.getElementById("detailDialog");
const detail = document.getElementById("detail");

boot();

async function boot() {
  setAppState("starting", "Loading Firebase...");
  bindEvents();
  await loadCachedShows();

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
    setAppState("offline", "Firebase is unavailable here. Showing cached tracklists if present.");
    console.error(error);
  }
}

function bindEvents() {
  search.addEventListener("input", renderShows);
  refreshBtn.addEventListener("click", () => currentUser && loadRemoteData());
  importFile.addEventListener("change", importShowFile);
  detailDialog.addEventListener("click", event => {
    if (event.target === detailDialog) closeDetail();
  });
  showsEl.addEventListener("click", event => {
    const card = event.target.closest("[data-show-id]");
    if (card) openShow(card.dataset.showId);
  });
  detail.addEventListener("click", event => {
    const closeButton = event.target.closest("[data-close-detail]");
    if (closeButton) closeDetail();

    const markButton = event.target.closest("[data-toggle-mark]");
    if (markButton) toggleMark(markButton.dataset.showId, markButton.dataset.trackId);
  });
  window.addEventListener("online", () => {
    offlineNote.textContent = "";
    if (currentUser) loadRemoteData();
  });
  window.addEventListener("offline", () => {
    offlineNote.textContent = "Offline";
  });
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
  marks = new Map();

  if (!user) {
    setAppState("signed-out", shows.length ? "Sign in to sync saved shows and marks." : "Sign in with Google to load saved shows.");
    renderShows();
    return;
  }

  userLabel.textContent = user.email || "Signed in";
  setAppState("loading", "Loading saved KCRW shows...");
  await loadRemoteData();
}

async function loadRemoteData() {
  if (!currentUser || !db) return;

  setAppState("loading", "Loading saved KCRW shows...");
  try {
    await flushPendingMarks();
    const remoteShows = await loadShows();
    const [remoteTracks, remoteMarks] = await Promise.all([
      loadTracks(remoteShows),
      loadMarks()
    ]);
    shows = remoteShows;
    tracksByShow = remoteTracks;
    marks = remoteMarks;
    usingOfflineCopy = false;
    await saveCachedShows();
    setAppState("ready", shows.length ? `${shows.length} saved shows.` : "No saved shows yet. Import a show JSON file.");
    renderShows();
    if (activeShowId) renderDetail(activeShowId);
  } catch (error) {
    await loadCachedShows();
    const message = permissionDenied(error)
      ? "This Google account is not allowed to access the private KCRW tracklists."
      : "Could not reach Firestore. Showing offline copy if available.";
    setAppState(permissionDenied(error) ? "unauthorized" : "offline", message);
    renderShows();
  }
}

async function loadShows() {
  const snapshot = await getDocs(collection(db, "kcrwShows"));
  const items = snapshot.docs.map(item => ({ id: item.id, ...serializeData(item.data()) }));
  return sortShows(items);
}

async function loadTracks(showItems) {
  const result = new Map();
  await Promise.all(showItems.map(async show => {
    const snapshot = await getDocs(collection(db, "kcrwShows", show.id, "tracks"));
    result.set(show.id, snapshot.docs.map(item => ({ id: item.id, ...serializeData(item.data()) })).sort(trackSort));
  }));
  return result;
}

async function loadMarks() {
  const snapshot = await getDocs(collection(db, "users", currentUser.uid, "kcrwTrackMarks"));
  return new Map(snapshot.docs.filter(item => item.data().marked !== false).map(item => [item.id, serializeData(item.data())]));
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
  offlineNote.textContent = usingOfflineCopy || state === "offline" ? "Offline copy" : "";
}

function setStatus(message) {
  statusEl.textContent = message;
}

function renderShows() {
  const items = visibleShows();
  showsEl.innerHTML = items.map(showCardHtml).join("");
  empty.hidden = authState === "starting" || authState === "loading" || items.length > 0;
  if (authState === "ready") {
    setStatus(`${items.length} of ${shows.length} saved shows.`);
  }
}

function visibleShows() {
  const terms = normalize(search.value).split(/\s+/).filter(Boolean);
  if (!terms.length) return shows;
  return shows.filter(show => {
    const trackText = (tracksByShow.get(show.id) || [])
      .map(track => [track.artist, track.title, track.album, track.label].join(" "))
      .join(" ");
    const haystack = normalize([show.title, show.host, show.date, trackText].join(" "));
    return terms.every(term => haystack.includes(term));
  });
}

function showCardHtml(show) {
  const tracks = tracksByShow.get(show.id) || [];
  const markedCount = tracks.filter(track => isMarked(show.id, track.id)).length;
  return `<button type="button" class="show-card" data-show-id="${escapeAttr(show.id)}">
    ${showImageHtml(show)}
    <span>
      <h2>${escapeHtml(show.title || "Untitled show")}</h2>
      <p class="show-meta">${escapeHtml([show.host, formatDate(show.date)].filter(Boolean).join(" · "))}</p>
      <p class="show-summary">${tracks.length} tracks${markedCount ? ` · ${markedCount} marked` : ""}</p>
      <span class="chips">
        ${show.playlistId ? `<span class="chip">Playlist ${escapeHtml(show.playlistId)}</span>` : ""}
        ${usingOfflineCopy ? `<span class="chip">Offline</span>` : ""}
      </span>
    </span>
  </button>`;
}

function openShow(showId) {
  activeShowId = showId;
  renderDetail(showId);
  detailDialog.showModal();
}

function closeDetail() {
  activeShowId = null;
  detailDialog.close();
}

function renderDetail(showId) {
  const show = shows.find(item => item.id === showId);
  if (!show) return;
  const tracks = tracksByShow.get(showId) || [];
  detail.innerHTML = `<div class="detail-topbar">
    <button type="button" class="close-dialog" data-close-detail aria-label="Close tracklist">×</button>
    <div class="detail-actions">
      ${show.sourceUrl ? `<a class="button secondary" href="${escapeAttr(show.sourceUrl)}" target="_blank" rel="noopener">KCRW</a>` : ""}
    </div>
  </div>
  <section class="detail-hero">
    ${showImageHtml(show)}
    <div>
      <h2>${escapeHtml(show.title || "Untitled show")}</h2>
      <p>${escapeHtml([show.host, formatDate(show.date), `${tracks.length} tracks`].filter(Boolean).join(" · "))}</p>
      ${show.mediaUrl ? `<p><a href="${escapeAttr(show.mediaUrl)}" target="_blank" rel="noopener">Audio source</a></p>` : ""}
    </div>
  </section>
  <section class="track-list">
    ${tracks.map(track => trackRowHtml(show, track)).join("")}
  </section>`;
}

function trackRowHtml(show, track) {
  const marked = isMarked(show.id, track.id);
  const isBreak = track.artist === "[BREAK]";
  return `<article class="track-row ${isBreak ? "break-row" : ""}">
    <div class="track-time">${escapeHtml(formatTimestamp(track.offset))}</div>
    <div>
      <p class="track-title">${escapeHtml(track.title || (isBreak ? "[BREAK]" : "Untitled"))}</p>
      ${track.artist && !isBreak ? `<p class="track-artist">${escapeHtml(track.artist)}</p>` : ""}
      ${track.album || track.label ? `<p class="track-album">${escapeHtml([track.album, track.label].filter(Boolean).join(" · "))}</p>` : ""}
      <div class="track-actions">
        ${!isBreak && currentUser ? `<button type="button" class="${marked ? "marked" : "secondary"}" data-toggle-mark data-show-id="${escapeAttr(show.id)}" data-track-id="${escapeAttr(track.id)}">${marked ? "Marked" : "Mark"}</button>` : ""}
        ${!isBreak && spotifySearchUrl(track) ? `<a class="button secondary" href="${escapeAttr(spotifySearchUrl(track))}" target="_blank" rel="noopener">Spotify</a>` : ""}
      </div>
    </div>
  </article>`;
}

async function toggleMark(showId, trackId) {
  const track = (tracksByShow.get(showId) || []).find(item => item.id === trackId);
  const show = shows.find(item => item.id === showId);
  if (!track || !show || !currentUser) return;

  const markId = markKey(showId, trackId);
  const marked = !marks.has(markId);
  if (marked) {
    marks.set(markId, markPayload(show, track));
  } else {
    marks.delete(markId);
  }
  renderShows();
  renderDetail(showId);
  await saveCachedShows();

  try {
    if (!navigator.onLine) throw new Error("offline");
    if (marked) {
      await setDoc(doc(db, "users", currentUser.uid, "kcrwTrackMarks", markId), {
        ...markPayload(show, track),
        updatedAt: serverTimestamp()
      });
    } else {
      await deleteDoc(doc(db, "users", currentUser.uid, "kcrwTrackMarks", markId));
    }
  } catch (error) {
    await queuePendingMark({ markId, marked, payload: markPayload(show, track) });
    offlineNote.textContent = "Offline copy";
    setStatus("Mark saved locally and will sync when online.");
  }
}

function markPayload(show, track) {
  return cleanObject({
    showId: show.id,
    trackId: track.id,
    marked: true,
    artist: track.artist || "",
    title: track.title || "",
    album: track.album || "",
    label: track.label || "",
    offset: Number(track.offset || 0),
    sourceUrl: show.sourceUrl || "",
    showTitle: show.title || "",
    showDate: show.date || "",
    spotifySearchUrl: spotifySearchUrl(track)
  });
}

async function importShowFile(event) {
  const files = [...(event.target.files || [])];
  event.target.value = "";
  if (!files.length || !currentUser || !db) return;

  setStatus(`Importing ${files.length} show${files.length === 1 ? "" : "s"}...`);
  try {
    const imported = [];
    for (const file of files) {
      const bundle = normalizeImportBundle(JSON.parse(await file.text()));
      await saveShowBundle(bundle);
      imported.push(bundle.show.title);
    }
    setStatus(`Imported ${imported.length} show${imported.length === 1 ? "" : "s"}.`);
    await loadRemoteData();
  } catch (error) {
    console.error(error);
    setStatus(`Import failed: ${error.message}`);
  }
}

function normalizeImportBundle(raw) {
  const show = raw.show || raw.episode || raw;
  const tracks = raw.tracks || raw.tracklist || [];
  if (!show || !Array.isArray(tracks) || !tracks.length) {
    throw new Error("Expected a show bundle with show metadata and tracks.");
  }

  const sourceUrl = cleanText(show.sourceUrl || show.source_url || raw.sourceUrl || raw.url);
  const playlistUrl = cleanText(show.playlistUrl || show.playlist_url || show.playlistUrl);
  const showId = cleanText(show.id) || makeShowId(show);
  const normalizedTracks = tracks.map((track, index) => {
    const id = cleanText(track.id) || makeTrackId(track, index);
    return cleanObject({
      id,
      offset: Number(track.offset || 0),
      time: cleanText(track.time),
      artist: cleanText(track.artist),
      title: cleanText(track.title),
      album: cleanText(track.album),
      label: cleanText(track.label),
      year: cleanText(track.year),
      comments: cleanText(track.comments),
      playId: track.playId || track.play_id || null,
      ordinal: Number(track.ordinal ?? index),
      spotifySearchUrl: spotifySearchUrl(track)
    });
  });

  return {
    show: cleanObject({
      id: showId,
      title: cleanText(show.title) || "KCRW Show",
      date: cleanText(show.date),
      host: cleanText(show.host || show.program_title || raw.host),
      sourceUrl,
      mediaUrl: cleanText(show.mediaUrl || show.media_url),
      playlistUrl,
      playlistId: cleanText(show.playlistId || show.playlist_id),
      duration: Number(show.duration || 0),
      imageUrl: cleanText(show.imageUrl || show.image_url),
      trackCount: normalizedTracks.length
    }),
    tracks: normalizedTracks
  };
}

async function saveShowBundle(bundle) {
  const showRef = doc(db, "kcrwShows", bundle.show.id);
  await setDoc(showRef, {
    ...bundle.show,
    updatedAt: serverTimestamp(),
    importedAt: serverTimestamp()
  }, { merge: true });

  const nextTrackIds = new Set(bundle.tracks.map(track => track.id));
  const existingTracks = await getDocs(collection(db, "kcrwShows", bundle.show.id, "tracks"));
  let batch = writeBatch(db);
  let writes = 0;

  for (const item of existingTracks.docs) {
    if (!nextTrackIds.has(item.id)) {
      batch.delete(item.ref);
      writes += 1;
    }
  }

  for (const track of bundle.tracks) {
    batch.set(doc(db, "kcrwShows", bundle.show.id, "tracks", track.id), track);
    writes += 1;
    if (writes === 450) {
      await batch.commit();
      batch = writeBatch(db);
      writes = 0;
    }
  }
  if (writes) await batch.commit();
}

async function flushPendingMarks() {
  const pending = await getPendingMarks();
  if (!pending.length || !currentUser || !navigator.onLine) return;

  for (const item of pending) {
    if (item.marked) {
      await setDoc(doc(db, "users", currentUser.uid, "kcrwTrackMarks", item.markId), {
        ...item.payload,
        updatedAt: serverTimestamp()
      });
    } else {
      await deleteDoc(doc(db, "users", currentUser.uid, "kcrwTrackMarks", item.markId));
    }
  }
  await clearPendingMarks();
}

function sortShows(items) {
  return [...items].sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")) || String(b.title || "").localeCompare(String(a.title || "")));
}

function trackSort(a, b) {
  return Number(a.ordinal ?? a.offset ?? 0) - Number(b.ordinal ?? b.offset ?? 0);
}

function isMarked(showId, trackId) {
  return marks.has(markKey(showId, trackId));
}

function markKey(showId, trackId) {
  return `${showId}_${trackId}`;
}

function makeShowId(show) {
  return slugify([show.date, show.host, show.title].filter(Boolean).join(" "));
}

function makeTrackId(track, index) {
  return `${String(index + 1).padStart(3, "0")}-${slugify([track.artist, track.title, track.play_id || track.playId].filter(Boolean).join(" "))}`;
}

function slugify(value) {
  return String(value || "item")
    .normalize("NFKD")
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/[-\s]+/g, "-")
    .toLowerCase()
    .slice(0, 140) || "item";
}

function spotifySearchUrl(track) {
  const query = [track.artist, track.title].map(cleanText).filter(Boolean).join(" ");
  return query ? `https://open.spotify.com/search/${encodeURIComponent(query)}` : "";
}

function showImageHtml(show) {
  return show.imageUrl
    ? `<img src="${escapeAttr(show.imageUrl)}" alt="">`
    : `<span class="show-image-placeholder" aria-hidden="true">KCRW</span>`;
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function formatTimestamp(seconds) {
  const wholeSeconds = Math.max(0, Math.round(Number(seconds || 0)));
  const hours = Math.floor(wholeSeconds / 3600);
  const minutes = Math.floor((wholeSeconds % 3600) / 60);
  const secs = wholeSeconds % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function normalize(value) {
  return String(value || "").toLocaleLowerCase();
}

function cleanText(value) {
  return String(value ?? "").replace(/<[^>]+>/g, "").trim();
}

function cleanObject(value) {
  return Object.fromEntries(Object.entries(value).filter(([, item]) => item !== undefined));
}

function serializeData(value) {
  return JSON.parse(JSON.stringify(value, (key, item) => {
    if (key === "updatedAt" || key === "importedAt") return undefined;
    if (item && typeof item.toDate === "function") return item.toDate().toISOString();
    return item;
  }));
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

function permissionDenied(error) {
  return error?.code === "permission-denied" || String(error?.message || "").includes("Missing or insufficient permissions");
}

async function loadCachedShows() {
  const cached = await idbGet("cache", "latestShows");
  if (!cached) {
    renderShows();
    return;
  }
  shows = cached.shows || [];
  tracksByShow = new Map(Object.entries(cached.tracksByShow || {}));
  marks = new Map(Object.entries(cached.marks || {}));
  usingOfflineCopy = true;
  renderShows();
}

async function saveCachedShows() {
  const cacheShows = sortShows(shows).slice(0, OFFLINE_SHOW_LIMIT);
  const allowedIds = new Set(cacheShows.map(show => show.id));
  const tracks = {};
  for (const show of cacheShows) {
    tracks[show.id] = tracksByShow.get(show.id) || [];
  }
  const cachedMarks = Object.fromEntries([...marks].filter(([, mark]) => allowedIds.has(mark.showId)));
  await idbSet("cache", {
    id: "latestShows",
    shows: cacheShows,
    tracksByShow: tracks,
    marks: cachedMarks,
    savedAt: new Date().toISOString()
  });
}

async function queuePendingMark(item) {
  await idbSet("pendingMarks", { ...item, id: item.markId, queuedAt: new Date().toISOString() });
}

async function getPendingMarks() {
  return idbAll("pendingMarks");
}

async function clearPendingMarks() {
  const dbHandle = await openIdb();
  return idbRequest(dbHandle.transaction("pendingMarks", "readwrite").objectStore("pendingMarks").clear());
}

function openIdb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const dbHandle = request.result;
      if (!dbHandle.objectStoreNames.contains("cache")) dbHandle.createObjectStore("cache", { keyPath: "id" });
      if (!dbHandle.objectStoreNames.contains("pendingMarks")) dbHandle.createObjectStore("pendingMarks", { keyPath: "id" });
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

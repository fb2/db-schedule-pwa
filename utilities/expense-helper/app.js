import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getDocs,
  getFirestore,
  serverTimestamp,
  setDoc,
  updateDoc
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";
import {
  deleteObject,
  getDownloadURL,
  getStorage,
  ref,
  uploadBytes
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-storage.js";
import JSZip from "https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm";

const MAX_IMAGE_EDGE = 1024;
const JPEG_QUALITY = 0.72;

let auth = null;
let db = null;
let storage = null;
let currentUser = null;
let authState = "starting";
let buckets = [];
let items = [];
let receiptUrls = new Map();
let activeBucketId = "";
let viewMode = "active";

const statusEl = document.getElementById("status");
const userLabel = document.getElementById("userLabel");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const signedInControls = document.getElementById("signedInControls");
const activeViewBtn = document.getElementById("activeViewBtn");
const archiveViewBtn = document.getElementById("archiveViewBtn");
const refreshBtn = document.getElementById("refreshBtn");
const newBucketBtn = document.getElementById("newBucketBtn");
const bucketListPanel = document.getElementById("bucketListPanel");
const bucketList = document.getElementById("bucketList");
const emptyBuckets = document.getElementById("emptyBuckets");
const detailPanel = document.getElementById("bucketDetailPanel");
const backBtn = document.getElementById("backBtn");
const detailModeLabel = document.getElementById("detailModeLabel");
const bucketTitle = document.getElementById("bucketTitle");
const bucketMeta = document.getElementById("bucketMeta");
const downloadZipBtn = document.getElementById("downloadZipBtn");
const archiveBucketBtn = document.getElementById("archiveBucketBtn");
const itemForm = document.getElementById("itemForm");
const expenseDate = document.getElementById("expenseDate");
const expenseName = document.getElementById("expenseName");
const participants = document.getElementById("participants");
const receiptInput = document.getElementById("receiptInput");
const receiptLabel = document.getElementById("receiptLabel");
const saveItemBtn = document.getElementById("saveItemBtn");
const clearFormBtn = document.getElementById("clearFormBtn");
const itemList = document.getElementById("itemList");
const emptyItems = document.getElementById("emptyItems");
const bucketDialog = document.getElementById("bucketDialog");
const bucketForm = document.getElementById("bucketForm");
const bucketName = document.getElementById("bucketName");
const cancelBucketBtn = document.getElementById("cancelBucketBtn");

boot();

async function boot() {
  bindEvents();
  resetItemForm();
  setAppState("starting", "Loading Firebase...");

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
    console.error(error);
    setAppState("offline", "Firebase is unavailable here. Open from Firebase Hosting.");
  }
}

function bindEvents() {
  activeViewBtn.addEventListener("click", () => setViewMode("active"));
  archiveViewBtn.addEventListener("click", () => setViewMode("archived"));
  refreshBtn.addEventListener("click", () => currentUser && loadBuckets());
  newBucketBtn.addEventListener("click", openBucketDialog);
  backBtn.addEventListener("click", () => showBucketListOnly());
  bucketList.addEventListener("click", handleBucketListClick);
  itemForm.addEventListener("submit", saveItem);
  clearFormBtn.addEventListener("click", resetItemForm);
  receiptInput.addEventListener("change", updateReceiptLabel);
  itemList.addEventListener("click", handleItemClick);
  itemList.addEventListener("change", handleItemReceiptChange);
  archiveBucketBtn.addEventListener("click", toggleArchiveActiveBucket);
  downloadZipBtn.addEventListener("click", downloadActiveBucketZip);
  bucketForm.addEventListener("submit", createBucket);
  cancelBucketBtn.addEventListener("click", () => bucketDialog.close());
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
  buckets = [];
  items = [];
  receiptUrls = new Map();
  activeBucketId = "";

  if (!user) {
    setAppState("signed-out", "Sign in to load private expense buckets.");
    render();
    return;
  }

  userLabel.textContent = user.email || "Signed in";
  setAppState("loading", "Loading expense buckets...");
  await loadBuckets();
}

async function loadBuckets(preferredBucketId = activeBucketId) {
  if (!currentUser || !db) return;
  setAppState("loading", "Loading expense buckets...");

  try {
    const snapshot = await getDocs(collection(db, "expenseBuckets"));
    buckets = snapshot.docs
      .map((item) => ({ id: item.id, ...serializeData(item.data()) }))
      .sort(bucketSort);
    activeBucketId = chooseActiveBucket(preferredBucketId);
    await loadItems(activeBucketId);
    setAppState("ready", bucketStatusMessage());
    render();
  } catch (error) {
    console.error(error);
    buckets = [];
    items = [];
    activeBucketId = "";
    const message = permissionDenied(error)
      ? "This Google account is not allowed to access private expenses."
      : "Could not load expense buckets.";
    setAppState(permissionDenied(error) ? "unauthorized" : "error", message);
    render();
  }
}

async function loadItems(bucketId) {
  items = [];
  receiptUrls = new Map();
  if (!bucketId || !currentUser || !db) return;

  const snapshot = await getDocs(collection(db, "expenseBuckets", bucketId, "items"));
  items = snapshot.docs
    .map((item) => ({ id: item.id, ...serializeData(item.data()) }))
    .sort(itemSort);
  await hydrateReceiptUrls(items);
}

async function createBucket(event) {
  event.preventDefault();
  if (!currentUser || !db) return;

  const name = bucketName.value.trim();
  if (!name) return;

  bucketForm.querySelector("button[type='submit']").disabled = true;
  try {
    const ref = await addDoc(collection(db, "expenseBuckets"), {
      name,
      archivedAt: null,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
      createdBy: currentUser.email || currentUser.uid,
      itemCount: 0,
      missingReceiptCount: 0
    });
    bucketDialog.close();
    bucketName.value = "";
    viewMode = "active";
    await loadBuckets(ref.id);
  } catch (error) {
    console.error(error);
    setStatus(`Could not create bucket: ${error.message}`);
  } finally {
    bucketForm.querySelector("button[type='submit']").disabled = false;
  }
}

async function saveItem(event) {
  event.preventDefault();
  const bucket = activeBucket();
  if (!bucket || !currentUser || !db || !storage) return;

  const name = expenseName.value.trim();
  const date = expenseDate.value || todayIso();
  const participantValue = participants.value.trim();
  const sourceFile = receiptInput.files?.[0] || null;
  if (!name) return;

  saveItemBtn.disabled = true;
  setStatus(sourceFile ? "Resizing receipt and saving expense..." : "Saving expense without receipt...");

  try {
    const itemRef = doc(collection(db, "expenseBuckets", bucket.id, "items"));
    const receipt = sourceFile ? await uploadReceipt(bucket.id, itemRef.id, sourceFile) : null;
    await setDoc(itemRef, {
      date,
      name,
      participants: parseParticipants(participantValue),
      receiptPath: receipt?.path || "",
      receiptName: receipt?.name || "",
      receiptSize: receipt?.size || 0,
      receiptContentType: receipt?.contentType || "",
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
      createdBy: currentUser.email || currentUser.uid
    });
    resetItemForm();
    await recomputeBucketCounts(bucket.id);
    await loadBuckets(bucket.id);
    setStatus("Expense item saved.");
  } catch (error) {
    console.error(error);
    setStatus(`Save failed: ${error.message}`);
  } finally {
    saveItemBtn.disabled = false;
  }
}

async function uploadReceipt(bucketId, itemId, sourceFile) {
  const blob = await resizeImageToJpeg(sourceFile);
  const path = `expenseReceipts/${bucketId}/${itemId}.jpg`;
  const storageRef = ref(storage, path);
  await uploadBytes(storageRef, blob, {
    contentType: "image/jpeg",
    customMetadata: {
      originalName: sourceFile.name || "receipt",
      uploadedBy: currentUser.email || currentUser.uid
    }
  });
  return {
    path,
    name: sourceFile.name || `${itemId}.jpg`,
    size: blob.size,
    contentType: "image/jpeg"
  };
}

async function resizeImageToJpeg(file) {
  const bitmap = await loadBitmap(file);
  const scale = Math.min(1, MAX_IMAGE_EDGE / Math.max(bitmap.width, bitmap.height));
  const width = Math.max(1, Math.round(bitmap.width * scale));
  const height = Math.max(1, Math.round(bitmap.height * scale));
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  context.drawImage(bitmap, 0, 0, width, height);
  if (typeof bitmap.close === "function") bitmap.close();

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("Could not convert receipt image to JPEG."));
    }, "image/jpeg", JPEG_QUALITY);
  });
}

async function loadBitmap(file) {
  if ("createImageBitmap" in window) {
    try {
      return await createImageBitmap(file, { imageOrientation: "from-image" });
    } catch {
      return loadImageElement(file);
    }
  }

  return loadImageElement(file);
}

async function loadImageElement(file) {
  const url = URL.createObjectURL(file);
  try {
    const image = await new Promise((resolve, reject) => {
      const element = new Image();
      element.onload = () => resolve(element);
      element.onerror = () => reject(new Error("Could not read receipt image."));
      element.src = url;
    });
    return image;
  } finally {
    URL.revokeObjectURL(url);
  }
}

async function hydrateReceiptUrls(itemList) {
  const entries = await Promise.all(itemList
    .filter((item) => item.receiptPath)
    .map(async (item) => {
      try {
        return [item.id, await getDownloadURL(ref(storage, item.receiptPath))];
      } catch (error) {
        console.error(error);
        return [item.id, ""];
      }
    }));
  receiptUrls = new Map(entries.filter(([, url]) => url));
}

async function toggleArchiveActiveBucket() {
  const bucket = activeBucket();
  if (!bucket || !currentUser || !db) return;

  const shouldArchive = !bucket.archivedAt;
  const message = shouldArchive
    ? `Archive "${bucket.name}"? It will move out of the active list.`
    : `Restore "${bucket.name}" to active buckets?`;
  if (!confirm(message)) return;

  try {
    await updateDoc(doc(db, "expenseBuckets", bucket.id), {
      archivedAt: shouldArchive ? serverTimestamp() : null,
      updatedAt: serverTimestamp()
    });
    viewMode = shouldArchive ? "archived" : "active";
    await loadBuckets(bucket.id);
  } catch (error) {
    console.error(error);
    setStatus(`Could not update bucket: ${error.message}`);
  }
}

async function deleteItem(itemId) {
  const bucket = activeBucket();
  const item = items.find((candidate) => candidate.id === itemId);
  if (!bucket || !item || !currentUser || !db) return;
  if (!confirm(`Delete "${item.name}"?`)) return;

  try {
    await deleteDoc(doc(db, "expenseBuckets", bucket.id, "items", item.id));
    if (item.receiptPath) await deleteReceiptIfPresent(item.receiptPath);
    await recomputeBucketCounts(bucket.id);
    await loadBuckets(bucket.id);
    setStatus("Expense item deleted.");
  } catch (error) {
    console.error(error);
    setStatus(`Delete failed: ${error.message}`);
  }
}

async function attachReceiptToItem(itemId, file) {
  const bucket = activeBucket();
  const item = items.find((candidate) => candidate.id === itemId);
  if (!bucket || !item || !file || !currentUser || !db || !storage) return;

  setStatus("Resizing and attaching receipt...");
  try {
    const receipt = await uploadReceipt(bucket.id, item.id, file);
    await updateDoc(doc(db, "expenseBuckets", bucket.id, "items", item.id), {
      receiptPath: receipt.path,
      receiptName: receipt.name,
      receiptSize: receipt.size,
      receiptContentType: receipt.contentType,
      updatedAt: serverTimestamp()
    });
    await recomputeBucketCounts(bucket.id);
    await loadBuckets(bucket.id);
    setStatus("Receipt attached.");
  } catch (error) {
    console.error(error);
    setStatus(`Receipt upload failed: ${error.message}`);
  }
}

async function deleteReceiptIfPresent(path) {
  if (!path || !storage) return;
  try {
    await deleteObject(ref(storage, path));
  } catch (error) {
    if (!String(error?.code || error?.message || "").includes("object-not-found")) throw error;
  }
}

async function recomputeBucketCounts(bucketId) {
  const snapshot = await getDocs(collection(db, "expenseBuckets", bucketId, "items"));
  const nextItems = snapshot.docs.map((item) => item.data());
  await updateDoc(doc(db, "expenseBuckets", bucketId), {
    itemCount: nextItems.length,
    missingReceiptCount: nextItems.filter((item) => !item.receiptPath).length,
    updatedAt: serverTimestamp()
  });
}

async function downloadActiveBucketZip() {
  const bucket = activeBucket();
  if (!bucket || !items.length || !storage) return;

  const receiptedItems = items.filter((item) => item.receiptPath);
  if (!receiptedItems.length) {
    setStatus("No receipt photos to download in this bucket.");
    return;
  }

  downloadZipBtn.disabled = true;
  setStatus(`Preparing ${receiptedItems.length} receipt photo${receiptedItems.length === 1 ? "" : "s"}...`);

  try {
    const zip = new JSZip();
    for (let index = 0; index < receiptedItems.length; index += 1) {
      const item = receiptedItems[index];
      const url = await getDownloadURL(ref(storage, item.receiptPath));
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Could not download ${item.name}.`);
      zip.file(receiptFilename(item, index), await response.blob());
    }
    const blob = await zip.generateAsync({ type: "blob" });
    triggerDownload(blob, `${sanitizeFilename(bucket.name || "expense-bucket")}_receipts.zip`);
    setStatus("Receipt ZIP ready.");
  } catch (error) {
    console.error(error);
    setStatus(`ZIP download failed: ${error.message}`);
  } finally {
    downloadZipBtn.disabled = false;
  }
}

function render() {
  const signedIn = Boolean(currentUser);
  signedInControls.hidden = !signedIn || authState === "unauthorized";
  renderViewButtons();
  renderBuckets();
  renderDetail();
}

function renderBuckets() {
  const visible = visibleBuckets();
  bucketList.innerHTML = visible.map(bucketCardHtml).join("");
  emptyBuckets.hidden = Boolean(currentUser) && visible.length > 0;

  if (!currentUser) {
    emptyBuckets.textContent = "Sign in with an allowed Google account to manage expenses.";
  } else if (authState === "unauthorized") {
    emptyBuckets.textContent = "This account is not allowed to access private expenses.";
  } else {
    emptyBuckets.textContent = viewMode === "archived"
      ? "No archived buckets yet."
      : "No active buckets yet. Create one to start capturing receipts.";
  }
}

function bucketCardHtml(bucket) {
  const selected = bucket.id === activeBucketId;
  const missing = Number(bucket.missingReceiptCount || 0);
  const itemCount = Number(bucket.itemCount || 0);
  return `<button class="bucket-card ${missing ? "warning" : ""} ${selected ? "selected" : ""}" type="button" data-bucket-id="${escapeAttr(bucket.id)}">
    <span class="bucket-title-row">
      <strong>${escapeHtml(bucket.name || "Untitled bucket")}</strong>
      <span class="chip ${missing ? "warning" : "ok"}">${missing ? `${missing} missing` : "Receipts ok"}</span>
    </span>
    <span class="bucket-stats">
      <span class="chip">${itemCount} item${itemCount === 1 ? "" : "s"}</span>
      <span class="chip">${bucket.archivedAt ? "Archived" : "Active"}</span>
      <span class="chip">Updated ${escapeHtml(formatRelativeDate(bucket.updatedAt || bucket.createdAt))}</span>
    </span>
  </button>`;
}

function renderDetail() {
  const bucket = activeBucket();
  const hasBucket = Boolean(currentUser && bucket);
  detailPanel.hidden = !hasBucket;
  bucketListPanel.classList.toggle("detail-open", hasBucket);

  if (!bucket) {
    itemList.innerHTML = "";
    emptyItems.hidden = true;
    return;
  }

  bucketTitle.textContent = bucket.name || "Untitled bucket";
  detailModeLabel.textContent = bucket.archivedAt ? "Archived bucket" : "Active bucket";
  bucketMeta.textContent = `${items.length} item${items.length === 1 ? "" : "s"} · ${items.filter((item) => !item.receiptPath).length} missing receipt${items.filter((item) => !item.receiptPath).length === 1 ? "" : "s"}`;
  archiveBucketBtn.textContent = bucket.archivedAt ? "Restore" : "Archive";
  downloadZipBtn.disabled = !items.some((item) => item.receiptPath);
  itemForm.hidden = Boolean(bucket.archivedAt);
  itemList.innerHTML = items.map(itemCardHtml).join("");
  emptyItems.hidden = items.length > 0;
}

function itemCardHtml(item) {
  const missing = !item.receiptPath;
  return `<article class="item-card ${missing ? "warning" : ""}" data-item-id="${escapeAttr(item.id)}">
    <div class="item-head">
      <div>
        <strong>${escapeHtml(item.name || "Expense item")}</strong>
        <p class="muted">${escapeHtml(formatDate(item.date))}</p>
      </div>
      <span class="chip ${missing ? "warning" : "ok"}">${missing ? "Missing receipt" : "Receipt attached"}</span>
    </div>
    ${participantsHtml(item.participants)}
    ${item.receiptPath ? receiptPreviewHtml(item) : ""}
    <div class="item-actions">
      <label class="chip">
        ${missing ? "Attach receipt" : "Replace receipt"}
        <input type="file" accept="image/*" data-attach-receipt="${escapeAttr(item.id)}" hidden>
      </label>
      <button class="secondary" type="button" data-delete-item="${escapeAttr(item.id)}">Delete</button>
    </div>
  </article>`;
}

function receiptPreviewHtml(item) {
  const url = receiptUrls.get(item.id);
  if (!url) return `<button class="secondary" type="button" data-open-receipt="${escapeAttr(item.id)}">Open receipt</button>`;
  return `<a href="${escapeAttr(url)}" target="_blank" rel="noopener noreferrer">
    <img src="${escapeAttr(url)}" alt="Receipt for ${escapeAttr(item.name || "expense")}">
  </a>`;
}

function participantsHtml(value) {
  const items = Array.isArray(value) ? value : [];
  if (!items.length) return "";
  return `<p class="muted">Participants: ${escapeHtml(items.join(", "))}</p>`;
}

function renderViewButtons() {
  activeViewBtn.classList.toggle("active", viewMode === "active");
  archiveViewBtn.classList.toggle("active", viewMode === "archived");
}

async function handleBucketListClick(event) {
  const button = event.target.closest("[data-bucket-id]");
  if (!button) return;
  activeBucketId = button.dataset.bucketId;
  await loadItems(activeBucketId);
  render();
}

function handleItemClick(event) {
  const deleteButton = event.target.closest("[data-delete-item]");
  if (deleteButton) {
    deleteItem(deleteButton.dataset.deleteItem);
    return;
  }

  const receiptButton = event.target.closest("[data-open-receipt]");
  if (receiptButton) {
    openReceipt(receiptButton.dataset.openReceipt);
  }
}

function handleItemReceiptChange(event) {
  const input = event.target.closest("[data-attach-receipt]");
  if (!input) return;
  const file = input.files?.[0];
  input.value = "";
  if (file) attachReceiptToItem(input.dataset.attachReceipt, file);
}

async function openReceipt(itemId) {
  const item = items.find((candidate) => candidate.id === itemId);
  if (!item?.receiptPath || !storage) return;

  try {
    const url = receiptUrls.get(item.id) || await getDownloadURL(ref(storage, item.receiptPath));
    window.open(url, "_blank", "noopener,noreferrer");
  } catch (error) {
    console.error(error);
    setStatus(`Could not open receipt: ${error.message}`);
  }
}

function setViewMode(nextMode) {
  viewMode = nextMode;
  activeBucketId = chooseActiveBucket("");
  loadItems(activeBucketId).then(render);
}

function openBucketDialog() {
  bucketName.value = defaultBucketName();
  bucketDialog.showModal();
  bucketName.select();
}

function showBucketListOnly() {
  bucketListPanel.classList.remove("detail-open");
  detailPanel.hidden = true;
}

function resetItemForm() {
  expenseDate.value = todayIso();
  expenseName.value = "";
  participants.value = "";
  receiptInput.value = "";
  updateReceiptLabel();
}

function updateReceiptLabel() {
  const file = receiptInput.files?.[0];
  receiptLabel.textContent = file ? `Receipt: ${file.name}` : "Attach receipt photo";
}

function activeBucket() {
  return buckets.find((bucket) => bucket.id === activeBucketId) || null;
}

function visibleBuckets() {
  return buckets.filter((bucket) => viewMode === "archived" ? bucket.archivedAt : !bucket.archivedAt);
}

function chooseActiveBucket(preferred) {
  const visible = buckets.filter((bucket) => viewMode === "archived" ? bucket.archivedAt : !bucket.archivedAt);
  if (preferred && visible.some((bucket) => bucket.id === preferred)) return preferred;
  return visible[0]?.id || "";
}

function bucketStatusMessage() {
  const activeCount = buckets.filter((bucket) => !bucket.archivedAt).length;
  const archivedCount = buckets.length - activeCount;
  return `${activeCount} active bucket${activeCount === 1 ? "" : "s"} · ${archivedCount} archived`;
}

function bucketSort(left, right) {
  const leftTime = comparableDate(left.updatedAt || left.createdAt);
  const rightTime = comparableDate(right.updatedAt || right.createdAt);
  return rightTime - leftTime || String(left.name || "").localeCompare(String(right.name || ""));
}

function itemSort(left, right) {
  return String(right.date || "").localeCompare(String(left.date || ""))
    || comparableDate(right.createdAt) - comparableDate(left.createdAt)
    || String(left.name || "").localeCompare(String(right.name || ""));
}

function parseParticipants(value) {
  return String(value || "")
    .split(/[,;\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function receiptFilename(item, index) {
  const date = item.date || "undated";
  const name = sanitizeFilename(item.name || "expense").slice(0, 48) || "expense";
  return `${date}_${name}_${String(index + 1).padStart(2, "0")}.jpg`;
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function defaultBucketName() {
  const date = new Date();
  return `${date.getFullYear()} ${date.toLocaleDateString(undefined, { month: "short" })} business expenses`;
}

function todayIso() {
  const date = new Date();
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function formatDate(value) {
  if (!value) return "No date";
  const [year, month, day] = String(value).split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
}

function formatRelativeDate(value) {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return "n/a";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function comparableDate(value) {
  if (!value) return 0;
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? 0 : date.valueOf();
}

function serializeData(value) {
  if (Array.isArray(value)) return value.map(serializeData);
  if (value && typeof value === "object") {
    if (typeof value.toDate === "function") return value.toDate().toISOString();
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, serializeData(item)]));
  }
  return value;
}

function sanitizeFilename(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
}

function setAppState(state, message) {
  authState = state;
  setStatus(message);
  const signedIn = Boolean(currentUser);
  signInBtn.hidden = signedIn;
  signOutBtn.hidden = !signedIn;
  signInBtn.style.display = signedIn ? "none" : "";
  signOutBtn.style.display = signedIn ? "" : "none";
  signedInControls.hidden = !signedIn || state === "unauthorized";
  refreshBtn.disabled = state === "loading";
  newBucketBtn.disabled = state === "loading";
  userLabel.textContent = currentUser ? (currentUser.email || "Signed in") : "Signed out";
}

function setStatus(message) {
  statusEl.textContent = message || "";
}

function permissionDenied(error) {
  return String(error?.code || error?.message || "").toLowerCase().includes("permission");
}

function pad2(value) {
  return String(value).padStart(2, "0");
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
  return escapeHtml(value).replaceAll("`", "&#096;");
}

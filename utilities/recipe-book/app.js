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
  setDoc,
  writeBatch
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";

const firebaseConfig = {
  projectId: "fb-personal-utilities",
  appId: "1:137538560522:web:a542decb62c9dc677cb5f3",
  storageBucket: "fb-personal-utilities.firebasestorage.app",
  apiKey: "AIzaSyBFejdmSCT49G0hxv_7GFPJW_O96G_a6SY",
  authDomain: "fb-personal-utilities.firebaseapp.com",
  messagingSenderId: "137538560522"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

const recipes = [];
const byId = new Map();
let indexed = [];
let shortlist = new Set();
let view = "all";
let currentUser = null;

const cards = document.getElementById("cards");
const empty = document.getElementById("empty");
const count = document.getElementById("count");
const search = document.getElementById("search");
const dialog = document.getElementById("dialog");
const detail = document.getElementById("detail");
const allTab = document.getElementById("allTab");
const shortTab = document.getElementById("shortTab");
const shareShortlistBtn = document.getElementById("shareShortlistBtn");
const storageNote = document.getElementById("storageNote");
const signInBtn = document.getElementById("signInBtn");
const signOutBtn = document.getElementById("signOutBtn");
const userLabel = document.getElementById("userLabel");
const signedInControls = document.getElementById("signedInControls");
const importFile = document.getElementById("importFile");

signInBtn.addEventListener("click", async () => {
  try {
    await signInWithPopup(auth, provider);
  } catch (error) {
    setStatus(`Sign-in failed: ${error.message}`);
  }
});

signOutBtn.addEventListener("click", () => signOut(auth));
search.addEventListener("input", render);
allTab.addEventListener("click", () => {
  view = "all";
  render();
});
shortTab.addEventListener("click", () => {
  view = "shortlist";
  render();
});
document.getElementById("randomBtn").addEventListener("click", () => {
  const items = visibleRecipes();
  if (items.length) openRecipe(items[Math.floor(Math.random() * items.length)].id);
});
shareShortlistBtn.addEventListener("click", shareShortlist);
importFile.addEventListener("change", importRecipesFromFile);
dialog.addEventListener("click", event => {
  if (event.target === dialog) dialog.close();
});

onAuthStateChanged(auth, async user => {
  currentUser = user;
  recipes.length = 0;
  byId.clear();
  indexed = [];
  shortlist = new Set();
  render();

  if (!user) {
    setSignedInUi(false);
    signedInControls.hidden = true;
    userLabel.textContent = "Signed out";
    setStatus("Sign in with Google to load recipes.");
    return;
  }

  userLabel.textContent = user.email || "Signed in";
  setSignedInUi(true);

  signedInControls.hidden = false;
  setStatus("Loading private recipe data...");
  try {
    await Promise.all([loadRecipes(), loadShortlist()]);
    render();
  } catch (error) {
    signedInControls.hidden = true;
    recipes.length = 0;
    byId.clear();
    indexed = [];
    shortlist = new Set();
    render();
    setStatus("This Google account is not allowed to access the private recipe book.");
  }
});

function setSignedInUi(isSignedIn) {
  signInBtn.hidden = isSignedIn;
  signOutBtn.hidden = !isSignedIn;
  signInBtn.style.display = isSignedIn ? "none" : "";
  signOutBtn.style.display = isSignedIn ? "" : "none";
}

async function loadRecipes() {
  const snapshot = await getDocs(collection(db, "recipes"));
  for (const item of snapshot.docs) {
    const recipe = { id: item.id, ...item.data() };
    recipes.push(recipe);
    byId.set(recipe.id, recipe);
  }
  recipes.sort((a, b) => normalize(a.title).localeCompare(normalize(b.title)));
  indexed = recipes.map(recipe => ({ ...recipe, haystack: searchHaystack(recipe) }));
}

async function loadShortlist() {
  if (!currentUser) return;
  const snapshot = await getDocs(collection(db, "users", currentUser.uid, "shortlist"));
  shortlist = new Set(snapshot.docs.map(item => item.id));
}

function normalize(value) {
  return String(value || "").toLocaleLowerCase();
}

function searchHaystack(recipe) {
  return normalize([
    recipe.title,
    recipe.description,
    recipe.yield,
    (recipe.tags || []).join(" "),
    (recipe.ingredients || []).map(item => item.text).join(" "),
    (recipe.instructions || []).map(step => step.description).join(" ")
  ].join(" "));
}

function visibleRecipes() {
  const terms = normalize(search.value).split(/\s+/).filter(Boolean);
  return indexed.filter(recipe => {
    if (view === "shortlist" && !shortlist.has(recipe.id)) return false;
    return terms.every(term => recipe.haystack.includes(term));
  });
}

function render() {
  const items = visibleRecipes();
  cards.innerHTML = items.map(cardHtml).join("");
  empty.hidden = !currentUser || items.length > 0;
  count.textContent = currentUser
    ? `${items.length} of ${view === "shortlist" ? shortlist.size : recipes.length} recipes`
    : "Sign in with Google to load recipes.";
  shortTab.textContent = `Shortlist (${shortlist.size})`;
  shareShortlistBtn.disabled = shortlist.size === 0;
  allTab.classList.toggle("active", view === "all");
  shortTab.classList.toggle("active", view === "shortlist");
}

function cardHtml(recipe) {
  const selected = shortlist.has(recipe.id);
  const tags = (recipe.tags || []).slice(0, 3).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
  return `<article class="card">
    ${recipe.image ? `<img src="${recipe.image}" alt="">` : ""}
    <div class="card-body">
      <h2>${escapeHtml(recipe.title)}</h2>
      <p>${escapeHtml([recipe.yield, (recipe.tags || [])[0]].filter(Boolean).join(" · "))}</p>
      <div class="tag-row">${tags}</div>
      <div class="card-actions">
        <button type="button" class="secondary" onclick="openRecipe('${escapeAttr(recipe.id)}')">View</button>
        <button type="button" onclick="toggleShortlist('${escapeAttr(recipe.id)}')">${selected ? "Remove" : "Shortlist"}</button>
      </div>
    </div>
  </article>`;
}

window.openRecipe = function openRecipe(id) {
  const recipe = byId.get(id);
  if (!recipe) return;
  const selected = shortlist.has(id);
  detail.innerHTML = `<div>
    <button type="button" class="close-dialog" onclick="dialog.close()" aria-label="Close recipe">×</button>
    ${recipe.image ? `<img src="${recipe.image}" alt="">` : ""}
    <div class="detail-body">
      <h2>${escapeHtml(recipe.title)}</h2>
      <p class="description">${escapeHtml(recipe.description || recipe.yield || "")}</p>
      <div class="tag-row">${(recipe.tags || []).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
      <div class="actions">
        <button type="button" onclick="toggleShortlist('${escapeAttr(recipe.id)}'); openRecipe('${escapeAttr(recipe.id)}')">${selected ? "Remove from shortlist" : "Add to shortlist"}</button>
        <button type="button" class="secondary" onclick="shareRecipe('${escapeAttr(recipe.id)}')">Share link</button>
        <a class="button secondary" href="${escapeAttr(recipe.url)}" target="_blank" rel="noopener">Open source</a>
        <button type="button" class="secondary" onclick="dialog.close()">Close</button>
      </div>
      <h3>Ingredients</h3>
      ${sectionedList(recipe.ingredients || [])}
      <h3>Instructions</h3>
      <ol>${(recipe.instructions || []).map(step => `<li>${escapeHtml(step.description)}</li>`).join("")}</ol>
      ${(recipe.tips || []).length ? `<h3>Tips</h3><ul>${recipe.tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join("")}</ul>` : ""}
      ${recipe.imageCredit ? `<p class="credit">${escapeHtml(recipe.imageCredit)}</p>` : ""}
    </div>
  </div>`;
  dialog.showModal();
};

function sectionedList(items) {
  let lastSection = null;
  const parts = [];
  for (const item of items) {
    if (item.section && item.section !== lastSection) {
      if (lastSection !== null) parts.push("</ul>");
      parts.push(`<h3>${escapeHtml(item.section)}</h3><ul>`);
      lastSection = item.section;
    } else if (lastSection === null) {
      parts.push("<ul>");
      lastSection = "";
    }
    parts.push(`<li>${escapeHtml(item.text)}</li>`);
  }
  if (parts.length) parts.push("</ul>");
  return parts.join("");
}

window.toggleShortlist = async function toggleShortlist(id) {
  if (!currentUser) return;
  const ref = doc(db, "users", currentUser.uid, "shortlist", id);
  if (shortlist.has(id)) {
    shortlist.delete(id);
    await deleteDoc(ref);
  } else {
    shortlist.add(id);
    await setDoc(ref, {
      title: byId.get(id)?.title || "",
      url: byId.get(id)?.url || "",
      addedAt: new Date().toISOString()
    });
  }
  render();
};

window.shareRecipe = async function shareRecipe(id) {
  const recipe = byId.get(id);
  if (!recipe) return;
  const text = `${recipe.title}\n${recipe.url}`;
  if (navigator.share) {
    try {
      await navigator.share({ title: recipe.title, text, url: recipe.url });
      return;
    } catch (error) {
      if (error.name === "AbortError") return;
    }
  }
  await copyText(text);
  alert("Recipe link copied.");
};

async function shareShortlist() {
  const lines = [...shortlist].map(id => byId.get(id)).filter(Boolean).map(recipe => `${recipe.title}\n${recipe.url}`);
  if (!lines.length) return;
  const text = lines.join("\n\n");
  if (navigator.share) {
    try {
      await navigator.share({ title: "Recipe shortlist", text });
      return;
    } catch (error) {
      if (error.name === "AbortError") return;
    }
  }
  await copyText(text);
  alert("Shortlist links copied.");
}

async function importRecipesFromFile(event) {
  const file = event.target.files[0];
  event.target.value = "";
  if (!file || !currentUser) return;
  if (!confirm("Import this private recipe data into Firestore? Existing recipes with the same IDs will be overwritten.")) return;

  setStatus("Reading import file...");
  const imported = JSON.parse(await file.text());
  if (!Array.isArray(imported)) {
    throw new Error("Import file must contain a JSON array of recipes.");
  }

  setStatus(`Importing ${imported.length} recipes...`);
  for (let i = 0; i < imported.length; i += 450) {
    const batch = writeBatch(db);
    for (const recipe of imported.slice(i, i + 450)) {
      batch.set(doc(db, "recipes", String(recipe.id)), recipe);
    }
    await batch.commit();
  }

  recipes.length = 0;
  byId.clear();
  indexed = [];
  await loadRecipes();
  render();
  setStatus(`Imported ${imported.length} recipes.`);
}

async function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
  const area = document.createElement("textarea");
  area.value = text;
  document.body.append(area);
  area.select();
  document.execCommand("copy");
  area.remove();
}

function setStatus(message) {
  storageNote.textContent = message || "";
  if (!currentUser) count.textContent = message || "Sign in with Google to load recipes.";
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

const els = {
  weekLabel: document.querySelector("#weekLabel"),
  generatedAt: document.querySelector("#generatedAt"),
  introTitle: document.querySelector("#introTitle"),
  weeklyIntro: document.querySelector("#weeklyIntro"),
  productCount: document.querySelector("#productCount"),
  limitedCount: document.querySelector("#limitedCount"),
  sourceCount: document.querySelector("#sourceCount"),
  chainFilter: document.querySelector("#chainFilter"),
  tagFilter: document.querySelector("#tagFilter"),
  sortSelect: document.querySelector("#sortSelect"),
  productList: document.querySelector("#productList"),
  sourceList: document.querySelector("#sourceList"),
  productTemplate: document.querySelector("#productTemplate"),
  tabs: [...document.querySelectorAll(".tab")],
};

const state = {
  feed: null,
  section: "all",
};

const TAG_LABELS = {
  collab: "Collab",
  limited: "Limited",
  merch: "Merch",
  new: "New",
  regional: "Regional",
  renewal: "Renewal",
  returning: "Returning",
  seasonal: "Seasonal",
};

function formatDate(value) {
  if (!value) return "Date TBA";
  const date = new Date(`${value}T00:00:00+09:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    weekday: "short",
  }).format(date);
}

function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return `Generated ${new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)}`;
}

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function populateSelect(select, values, labeler = (value) => value) {
  if (!select) return;
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labeler(value);
    select.append(option);
  }
}

/** Cached SW can serve an older index without .product-thumb; repair so image append never targets null. */
function ensureProductThumbHost(card) {
  let thumbHost = card.querySelector(".product-thumb");
  if (!thumbHost) {
    thumbHost = document.createElement("div");
    thumbHost.className = "product-thumb";
    thumbHost.setAttribute("aria-hidden", "true");
    card.insertBefore(thumbHost, card.firstChild);
  }
  return thumbHost;
}

function productMatchesSection(product) {
  const tags = product.tags || [];
  if (state.section === "all") return true;
  if (state.section === "hot") return product.score >= 70;
  if (state.section === "short") return Boolean(product.timeGate) || tags.includes("limited");
  return tags.includes(state.section);
}

function filteredProducts() {
  const chain = els.chainFilter?.value ?? "all";
  const tag = els.tagFilter?.value ?? "all";
  const sort = els.sortSelect?.value ?? "recommended";
  const products = state.feed.products.filter((product) => {
    const tags = product.tags || [];
    if (chain !== "all" && product.chain !== chain) return false;
    if (tag !== "all" && !tags.includes(tag)) return false;
    return productMatchesSection({ ...product, tags });
  });

  return products.sort((a, b) => {
    if (sort === "newest") {
      return (b.releaseDate || "").localeCompare(a.releaseDate || "") || b.score - a.score;
    }
    if (sort === "urgency") {
      return Number(Boolean(b.timeGate)) - Number(Boolean(a.timeGate)) || b.score - a.score;
    }
    if (sort === "chain") {
      return a.chain.localeCompare(b.chain) || b.score - a.score;
    }
    return b.score - a.score;
  });
}

function badge(tag) {
  const span = document.createElement("span");
  span.className = `badge ${tag}`;
  span.textContent = TAG_LABELS[tag] || tag;
  return span;
}

function sourceLink(url, index) {
  const link = document.createElement("a");
  link.className = "source-link";
  link.href = url;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = index === 0 ? "Official source" : `Source ${index + 1}`;
  return link;
}

function renderProduct(product) {
  const fragment = els.productTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".product-card");
  if (!card) return fragment;

  const thumbHost = ensureProductThumbHost(card);
  const tags = product.tags || [];
  const sourceUrls = Array.isArray(product.sourceUrls) ? product.sourceUrls : [];

  card.dataset.chain = product.chain;
  const imageUrl = (product.imageUrl || "").trim();
  if (imageUrl) {
    const img = document.createElement("img");
    img.src = imageUrl;
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    img.addEventListener("error", () => {
      thumbHost?.remove();
      card.classList.add("product-card-no-thumb");
    });
    thumbHost.append(img);
  } else {
    thumbHost.remove();
    card.classList.add("product-card-no-thumb");
  }

  card.querySelector(".chain-pill").textContent = product.chain;
  card.querySelector(".score-pill").textContent = `${product.score} radar score`;
  card.querySelector("h2").textContent = product.name || product.nameJa;
  card.querySelector(".summary").textContent = [
    formatDate(product.releaseDate),
    product.summary,
    product.timeGate?.label,
  ]
    .filter(Boolean)
    .join(" · ");

  const badges = card.querySelector(".badges");
  if (badges) {
    for (const tag of tags.filter((item) => item !== "new").slice(0, 6)) {
      badges.append(badge(tag));
    }
  }

  const context = card.querySelector(".context");
  if (context) {
    context.textContent = product.englishContext
      ? `English context: ${product.englishContext}.`
      : "English context: automated glossary plus wording safeguards; open the official Japanese links for exact naming and allergens.";
  }

  const reasons = card.querySelector(".reasons");
  if (reasons) {
    for (const reason of product.scoreReasons || []) {
      const item = document.createElement("li");
      item.textContent = reason;
      reasons.append(item);
    }
  }

  const localSignals = card.querySelector(".local-signals");
  if (product.localSignals?.length) {
    const signal = product.localSignals[0];
    if (localSignals) {
      localSignals.textContent = `Local signal: ${signal.sourceName} matched "${signal.matchedText}".`;
    }
  } else if (localSignals) {
    localSignals.remove();
  }

  const sourceLinks = card.querySelector(".source-links");
  if (sourceLinks) {
    sourceUrls.slice(0, 3).forEach((url, index) => sourceLinks.append(sourceLink(url, index)));
  }

  return fragment;
}

function renderProducts() {
  if (!els.productList) return;
  const products = filteredProducts();
  els.productList.innerHTML = "";
  if (!products.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No products match these filters.";
    els.productList.append(empty);
    return;
  }

  const fragment = document.createDocumentFragment();
  products.forEach((product) => fragment.append(renderProduct(product)));
  els.productList.append(fragment);
}

function renderSources() {
  if (!els.sourceList) return;
  els.sourceList.innerHTML = "";
  for (const source of state.feed.sources) {
    const item = document.createElement("li");
    const label = document.createElement("span");
    const status = document.createElement("span");
    label.textContent = `${source.name} (${source.tier})`;
    status.textContent = source.ok ? `OK ${source.status}` : `Check ${source.status || "unknown"}`;
    item.append(label, status);
    els.sourceList.append(item);
  }
}

function renderSummary() {
  const products = state.feed.products;
  const limited = products.filter((product) => {
    const tags = product.tags || [];
    return product.timeGate || tags.includes("limited");
  }).length;
  els.weekLabel.textContent = state.feed.weekLabel;
  els.generatedAt.textContent = formatDateTime(state.feed.generatedAt);
  els.introTitle.textContent = "What to watch this week";
  els.weeklyIntro.textContent = state.feed.intro;
  els.productCount.textContent = products.length;
  els.limitedCount.textContent = limited;
  els.sourceCount.textContent = state.feed.sources.filter((source) => source.ok).length;
}

function render() {
  renderSummary();
  renderProducts();
  renderSources();
}

function setupControls() {
  populateSelect(els.chainFilter, uniqueSorted(state.feed.products.map((product) => product.chain)));
  populateSelect(
    els.tagFilter,
    uniqueSorted(state.feed.products.flatMap((product) => product.tags || [])),
    (value) => TAG_LABELS[value] || value
  );

  [els.chainFilter, els.tagFilter, els.sortSelect].forEach((control) => {
    if (control) control.addEventListener("change", renderProducts);
  });

  for (const tab of els.tabs) {
    tab.addEventListener("click", () => {
      state.section = tab.dataset.section;
      els.tabs.forEach((item) => item.classList.toggle("active", item === tab));
      renderProducts();
    });
  }
}

async function loadFeed() {
  if (!els.productTemplate) {
    throw new Error("Product template (#productTemplate) is missing.");
  }
  const response = await fetch("./feed.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`Feed request failed with ${response.status}`);
  state.feed = await response.json();
  setupControls();
  render();
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

loadFeed().catch((error) => {
  els.introTitle.textContent = "Feed unavailable";
  els.weeklyIntro.textContent = error.message;
});

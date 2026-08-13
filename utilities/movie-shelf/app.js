(() => {
  const MOVIES = window.MOVIES || [];
  const HOMES = window.MOVIE_HOMES || {};
  const CARD_W = 54;
  const CARD_H = 80;
  const THUMB_W = 108;
  const THUMB_H = 160;
  const SPHERE_R = 440;
  const FOV = 700;
  const PLACEHOLDER = ["#1a1a2e", "#16213e", "#0f3460", "#1b1b2f", "#2c1810", "#0d1b2a"];
  const TOP_DIRECTORS = [
    { name: "Dario Argento", count: 11, genre: "Giallo / Horror" },
    { name: "David Cronenberg", count: 11, genre: "Body Horror" },
    { name: "John Carpenter", count: 8, genre: "Horror / Sci-Fi" },
    { name: "Michael Mann", count: 7, genre: "Crime" },
    { name: "Lucio Fulci", count: 6, genre: "Horror / Giallo" },
    { name: "Fritz Lang", count: 6, genre: "Expressionist / Noir" },
    { name: "Jean-Pierre Melville", count: 5, genre: "French Noir" },
    { name: "Brian De Palma", count: 4, genre: "Thriller" },
    { name: "Alfred Hitchcock", count: 4, genre: "Suspense" },
    { name: "Wim Wenders", count: 3, genre: "Art Cinema" },
    { name: "John Woo", count: 3, genre: "Action" },
    { name: "Quentin Tarantino", count: 3, genre: "Crime" },
  ];

  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d", { alpha: false });
  const searchEl = document.getElementById("search");
  const chipsEl = document.getElementById("home-chips");
  const browseEl = document.getElementById("browse");
  const browseMeta = document.getElementById("browse-meta");
  const browseTrack = document.getElementById("browse-track");
  const detailsEl = document.getElementById("details");
  const pickBtn = document.getElementById("btn-pick");
  const loadingEl = document.getElementById("loading");

  let W = 0;
  let H = 0;
  let homeFilter = "all";
  let query = "";
  let matchSet = null;
  let mode = "sphere";
  let state = "idle";
  let selectedIdx = -1;
  let angleY = 0;
  let angleX = 0.3;
  let spinSpeed = 0.005;
  let targetAngleY = 0;
  let targetAngleX = 0.3;
  let spindownFrom = 0;
  let spindownFromX = 0.3;
  let spinT = 0;
  let viewCX = 0;
  const IDLE_ANGLE_X = 0.3;
  const PICK_YAW_OFFSET = 0.72;
  let loopOn = false;
  let lastIdle = 0;
  let drag = false;
  let moved = false;
  let lastMX = 0;
  let lastMY = 0;
  const MAX_SPIN = 0.22;

  const images = new Array(MOVIES.length).fill(null);
  const n = MOVIES.length;
  const basePts = fibSphere(n);
  const workPts = new Float64Array(basePts);
  const sortBuf = new Array(n).fill(null).map((_, i) => ({ i, z: 0 }));

  function homeLabel(home) {
    if (!home) return "Location unknown";
    const info = HOMES[home];
    if (!info) return "Location unknown";
    return `${info.label} · ${info.place}`;
  }

  function fibSphere(count) {
    const pts = new Float64Array(count * 3);
    if (count < 2) return pts;
    const phi = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const r = Math.sqrt(Math.max(0, 1 - y * y));
      const t = phi * i;
      pts[i * 3] = Math.cos(t) * r;
      pts[i * 3 + 1] = y;
      pts[i * 3 + 2] = Math.sin(t) * r;
    }
    return pts;
  }

  function rotatePtsY(pts, a) {
    const c = Math.cos(a);
    const s = Math.sin(a);
    for (let i = 0; i < pts.length; i += 3) {
      const x = pts[i];
      const z = pts[i + 2];
      pts[i] = x * c + z * s;
      pts[i + 2] = -x * s + z * c;
    }
  }

  function rotatePtsX(pts, a) {
    const c = Math.cos(a);
    const s = Math.sin(a);
    for (let i = 0; i < pts.length; i += 3) {
      const y = pts[i + 1];
      const z = pts[i + 2];
      pts[i + 1] = y * c - z * s;
      pts[i + 2] = y * s + z * c;
    }
  }

  function project(x, y, z) {
    const denom = FOV + z * SPHERE_R;
    const scale = denom > 80 ? FOV / denom : FOV / 80;
    return { sx: viewCX + x * SPHERE_R * scale, sy: H / 2 + y * SPHERE_R * scale, scale };
  }

  function centeringAngleX(idx) {
    const py = basePts[idx * 3 + 1];
    const pz = basePts[idx * 3 + 2];
    const ax = Math.atan2(py, pz);
    return Math.max(-0.62, Math.min(0.62, ax));
  }

  function facingAngleY(idx, ax) {
    const px = basePts[idx * 3];
    const py = basePts[idx * 3 + 1];
    const pz = basePts[idx * 3 + 2];
    const z1 = py * Math.sin(ax) + pz * Math.cos(ax);
    return Math.atan2(px, -z1) + PICK_YAW_OFFSET;
  }

  function unwrapForward(from, to) {
    const twoPi = Math.PI * 2;
    const delta = ((to - from) % twoPi + twoPi) % twoPi;
    return from + delta;
  }

  function unwrapShortest(from, to) {
    const twoPi = Math.PI * 2;
    let delta = ((to - from) % twoPi + twoPi) % twoPi;
    if (delta > Math.PI) delta -= twoPi;
    return from + delta;
  }

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    if (!viewCX) viewCX = W / 2;
    requestDraw();
  }

  function filteredIndices() {
    const q = query.trim().toLowerCase();
    const out = [];
    for (let i = 0; i < n; i++) {
      const m = MOVIES[i];
      if (homeFilter !== "all" && m.home !== homeFilter) continue;
      if (q && !`${m.t} ${m.y}`.toLowerCase().includes(q)) continue;
      out.push(i);
    }
    return out;
  }

  function refreshMatches() {
    const q = query.trim();
    if (!q && homeFilter === "all") {
      matchSet = null;
    } else {
      matchSet = new Set(filteredIndices());
    }
    requestDraw();
  }

  function visiblePool() {
    return filteredIndices();
  }

  function requestDraw() {
    if (mode !== "sphere" || document.hidden) return;
    if (loopOn) return;
    loopOn = true;
    requestAnimationFrame(loop);
  }

  function loop(now) {
    if (mode !== "sphere" || document.hidden) {
      loopOn = false;
      return;
    }
    const spinning = state === "idle" || state === "spinup" || state === "fast" || state === "spindown" || state === "seek";
    if (state === "idle" && !drag) {
      if (now - lastIdle < 33) {
        requestAnimationFrame(loop);
        return;
      }
      lastIdle = now;
    }
    draw();
    const keep = spinning || drag;
    if (!keep && state === "done") {
      loopOn = false;
      return;
    }
    requestAnimationFrame(loop);
  }

  function drawPlaceholder(x, y, w, h, idx) {
    ctx.fillStyle = PLACEHOLDER[idx % PLACEHOLDER.length];
    ctx.fillRect(x, y, w, h);
  }

  function draw() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);

    if (state === "idle") {
      if (!drag) {
        spinSpeed = 0.01;
        angleY += spinSpeed;
        angleX += (IDLE_ANGLE_X - angleX) * 0.08;
      }
    } else if (state === "spinup") {
      spinT++;
      spinSpeed = 0.005 + (MAX_SPIN - 0.005) * Math.min(1, spinT / 45);
      angleY += spinSpeed;
      if (spinT >= 45) {
        state = "fast";
        spinT = 0;
      }
    } else if (state === "fast") {
      spinT++;
      angleY += MAX_SPIN;
      if (spinT >= 60) {
        const ax = centeringAngleX(selectedIdx);
        spindownFrom = angleY;
        spindownFromX = angleX;
        targetAngleX = ax;
        targetAngleY = unwrapForward(angleY, facingAngleY(selectedIdx, ax));
        state = "spindown";
        spinT = 0;
      }
    } else if (state === "spindown" || state === "seek") {
      spinT++;
      const yawTravel = Math.abs(targetAngleY - spindownFrom);
      const pitchTravel = Math.abs(targetAngleX - spindownFromX);
      const dur =
        state === "seek"
          ? Math.max(36, Math.min(70, Math.round((yawTravel + pitchTravel) * 28)))
          : 70;
      const progress = Math.min(1, spinT / dur);
      const eased = 1 - Math.pow(1 - progress, 3);
      angleY = spindownFrom + (targetAngleY - spindownFrom) * eased;
      angleX = spindownFromX + (targetAngleX - spindownFromX) * eased;
      if (progress >= 1) {
        angleY = targetAngleY;
        angleX = targetAngleX;
        state = "done";
        showDetails(selectedIdx);
      }
    }

    const wantCX = state === "done" && W > 720 ? (W - 280) / 2 : W / 2;
    viewCX += (wantCX - viewCX) * (state === "done" ? 1 : 0.18);

    workPts.set(basePts);
    rotatePtsX(workPts, angleX);
    rotatePtsY(workPts, angleY);

    const angleChanged = state !== "done" || drag;
    if (angleChanged || state === "done") {
      for (let i = 0; i < n; i++) {
        sortBuf[i].i = i;
        sortBuf[i].z = workPts[i * 3 + 2];
      }
      sortBuf.sort((a, b) => a.z - b.z);
    }

    const fastAlphaScale = state === "fast" ? 0.55 : 1;
    const searching = Boolean(query.trim());
    ctx.strokeStyle = "#ffffff14";
    ctx.lineWidth = 0.5;
    ctx.beginPath();

    for (let s = 0; s < n; s++) {
      const { i, z } = sortBuf[s];
      if (state === "done" && i === selectedIdx) continue;
      const isMatch = !matchSet || matchSet.has(i);

      const x = workPts[i * 3];
      const y = workPts[i * 3 + 1];
      const { sx, sy, scale } = project(x, y, z);
      const w = CARD_W * scale;
      const h = CARD_H * scale;
      if (w < 5) continue;

      let alpha = Math.max(0.15, ((z + 1) / 2) * 0.85 + 0.15) * fastAlphaScale;
      if (matchSet && !isMatch) alpha *= 0.12;
      if (searching && isMatch) alpha = Math.max(alpha, 0.95);
      ctx.globalAlpha = alpha;
      const dx = sx - w / 2;
      const dy = sy - h / 2;
      if (images[i]) ctx.drawImage(images[i], dx, dy, w, h);
      else drawPlaceholder(dx, dy, w, h, i);
      if (isMatch) ctx.rect(dx, dy, w, h);
    }
    ctx.globalAlpha = 0.08;
    ctx.stroke();

    if (state === "done" && selectedIdx >= 0) {
      const x = workPts[selectedIdx * 3];
      const y = workPts[selectedIdx * 3 + 1];
      const z = workPts[selectedIdx * 3 + 2];
      const { sx, sy, scale } = project(x, y, z);
      let w = CARD_W * scale;
      let h = CARD_H * scale;
      const maxW = Math.min(150, W * 0.2);
      if (w > maxW) {
        const s = maxW / w;
        w *= s;
        h *= s;
      }
      ctx.globalAlpha = 1;
      if (images[selectedIdx]) {
        ctx.drawImage(images[selectedIdx], sx - w / 2, sy - h / 2, w, h);
      } else {
        drawPlaceholder(sx - w / 2, sy - h / 2, w, h, selectedIdx);
      }
      ctx.strokeStyle = "#d4a553";
      ctx.lineWidth = 2;
      ctx.strokeRect(sx - w / 2, sy - h / 2, w, h);
    }
    ctx.globalAlpha = 1;
  }

  function flyTo(idx, roulette) {
    if (idx < 0) return;
    if (!roulette && state === "done" && selectedIdx === idx) {
      showDetails(idx);
      return;
    }
    selectedIdx = idx;
    pickBtn.disabled = true;
    detailsEl.classList.remove("open");
    document.getElementById("trivia").style.opacity = "0";
    if (roulette) {
      state = "spinup";
      spinT = 0;
    } else {
      spindownFrom = angleY;
      spindownFromX = angleX;
      targetAngleX = centeringAngleX(idx);
      targetAngleY = unwrapShortest(angleY, facingAngleY(idx, targetAngleX));
      state = "seek";
      spinT = 0;
    }
    requestDraw();
  }

  function pickFilm() {
    if (state !== "idle" && state !== "done") return;
    const pool = visiblePool();
    if (!pool.length) return;
    flyTo(pool[Math.floor(Math.random() * pool.length)], true);
  }

  function showDetails(idx) {
    const m = MOVIES[idx];
    if (!m) return;
    document.getElementById("d-title").textContent = m.t;
    document.getElementById("d-year").textContent = String(m.y);
    document.getElementById("d-home").textContent = homeLabel(m.home);
    document.getElementById("d-link").href = m.l || "#";
    const img = document.getElementById("d-img");
    if (m.poster) {
      img.src = `./posters/${m.poster}`;
      img.style.display = "block";
    } else {
      img.removeAttribute("src");
      img.style.display = "none";
    }
    detailsEl.classList.add("open");
    document.getElementById("trivia").style.opacity = "0";
    pickBtn.disabled = false;
  }

  function closeDetails() {
    detailsEl.classList.remove("open");
    document.getElementById("trivia").style.opacity = "";
    state = "idle";
    spinSpeed = 0.005;
    selectedIdx = -1;
    pickBtn.disabled = false;
    requestDraw();
  }

  function coverAtPointer(mx, my) {
    let hit = -1;
    let hitZ = Infinity;
    for (let i = 0; i < n; i++) {
      const z = workPts[i * 3 + 2];
      if (z > 0) continue;
      const { sx, sy, scale } = project(workPts[i * 3], workPts[i * 3 + 1], z);
      const w = CARD_W * scale;
      const h = CARD_H * scale;
      if (w < 16) continue;
      if (mx < sx - w / 2 || mx > sx + w / 2 || my < sy - h / 2 || my > sy + h / 2) continue;
      if (z < hitZ) {
        hitZ = z;
        hit = i;
      }
    }
    return hit;
  }

  function openBrowse(indices) {
    mode = "browse";
    loopOn = false;
    detailsEl.classList.remove("open");
    const list = indices || visiblePool();
    browseMeta.textContent = list.length === 1 ? "1 disc" : `${list.length} discs`;
    browseTrack.replaceChildren();
    const frag = document.createDocumentFragment();
    for (const i of list) {
      const m = MOVIES[i];
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cover-card";
      const img = document.createElement("img");
      img.alt = "";
      img.loading = "lazy";
      if (m.poster) img.src = `./posters/${m.poster}`;
      const title = document.createElement("div");
      title.className = "c-title";
      title.textContent = m.t;
      const meta = document.createElement("div");
      meta.className = "c-meta";
      meta.textContent = `${m.y} · ${homeLabel(m.home)}`;
      btn.append(img, title, meta);
      btn.addEventListener("click", () => {
        closeBrowse();
        flyTo(i, false);
      });
      frag.append(btn);
    }
    browseTrack.append(frag);
    browseEl.hidden = false;
  }

  function closeBrowse() {
    browseEl.hidden = true;
    mode = "sphere";
    state = "idle";
    selectedIdx = -1;
    spinSpeed = 0.01;
    pickBtn.disabled = false;
    detailsEl.classList.remove("open");
    document.getElementById("trivia").style.opacity = "";
    loopOn = false;
    requestDraw();
  }

  function onSearch() {
    query = searchEl.value;
    refreshMatches();
    const hits = filteredIndices();
    if (query.trim() && hits.length >= 2) openBrowse(hits);
    else if (mode === "browse" && !query.trim()) closeBrowse();
  }

  function buildChips() {
    const opts = [
      ["all", "All"],
      ["hk", HOMES.hk ? HOMES.hk.label : "Hong Kong"],
      ["penang", HOMES.penang ? HOMES.penang.label : "Penang"],
    ];
    chipsEl.replaceChildren();
    for (const [id, label] of opts) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip" + (homeFilter === id ? " active" : "");
      btn.textContent = label;
      btn.addEventListener("click", () => {
        homeFilter = id;
        buildChips();
        refreshMatches();
        if (mode === "browse") openBrowse();
      });
      chipsEl.append(btn);
    }
  }

  function buildStats() {
    const counts = {};
    const years = [];
    const homes = { hk: 0, penang: 0, unknown: 0 };
    for (const m of MOVIES) {
      if (m.y) {
        years.push(m.y);
        const d = Math.floor(m.y / 10) * 10;
        counts[d] = (counts[d] || 0) + 1;
      }
      if (m.home === "hk" || m.home === "penang") homes[m.home]++;
      else homes.unknown++;
    }
    const decades = Object.entries(counts).sort((a, b) => a[0] - b[0]);
    const maxN = Math.max(1, ...decades.map(([, c]) => c));
    document.getElementById("stat-total").textContent = String(MOVIES.length);
    document.getElementById("stat-span").textContent = years.length
      ? `${Math.min(...years)} – ${Math.max(...years)}`
      : "";

    const homeRows = [
      ["Hong Kong", homes.hk],
      ["Penang", homes.penang],
      ["Untagged", homes.unknown],
    ];
    const maxH = Math.max(1, ...homeRows.map(([, c]) => c));
    document.getElementById("home-chart").innerHTML = homeRows
      .map(
        ([label, c]) =>
          `<div class="home-row"><div class="home-lbl">${label}</div><div class="home-bar-wrap"><div class="home-bar" style="width:${Math.round((c / maxH) * 100)}%"></div></div><div class="home-n">${c}</div></div>`
      )
      .join("");

    document.getElementById("decade-chart").innerHTML = decades
      .map(
        ([d, c]) =>
          `<div class="decade-row"><div class="decade-lbl">${d}s</div><div class="decade-bar-wrap"><div class="decade-bar" style="width:${Math.round((c / maxN) * 100)}%"></div></div><div class="decade-n">${c}</div></div>`
      )
      .join("");

    document.getElementById("director-list").innerHTML = TOP_DIRECTORS.map(
      (d) =>
        `<div class="dir-row"><div><span class="dir-name">${d.name}</span><span class="dir-genre">${d.genre}</span></div><div class="dir-n">${d.count}</div></div>`
    ).join("");
  }

  async function loadPosters() {
    if (!MOVIES.length) {
      document.getElementById("loading-msg").textContent = "No films in the catalogue yet.";
      return;
    }
    const jobs = MOVIES.map((m, i) => async () => {
      if (!m.poster) return;
      try {
        const res = await fetch(`./posters/${m.poster}`);
        if (!res.ok) return;
        const blob = await res.blob();
        if (typeof createImageBitmap === "function") {
          try {
            images[i] = await createImageBitmap(blob, {
              resizeWidth: THUMB_W,
              resizeHeight: THUMB_H,
              resizeQuality: "high",
            });
          } catch {
            const bmp = await createImageBitmap(blob);
            const thumb = document.createElement("canvas");
            thumb.width = THUMB_W;
            thumb.height = THUMB_H;
            thumb.getContext("2d").drawImage(bmp, 0, 0, THUMB_W, THUMB_H);
            images[i] = thumb;
            bmp.close();
          }
        } else {
          const url = URL.createObjectURL(blob);
          const img = new Image();
          await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
            img.src = url;
          });
          const thumb = document.createElement("canvas");
          thumb.width = THUMB_W;
          thumb.height = THUMB_H;
          thumb.getContext("2d").drawImage(img, 0, 0, THUMB_W, THUMB_H);
          images[i] = thumb;
          URL.revokeObjectURL(url);
        }
      } catch {
        /* keep placeholder */
      }
    });
    for (let i = 0; i < jobs.length; i += 20) {
      await Promise.all(jobs.slice(i, i + 20).map((fn) => fn()));
      requestDraw();
    }
    loadingEl.style.display = "none";
  }

  canvas.addEventListener("pointerdown", (e) => {
    if (mode !== "sphere") return;
    if (state !== "idle" && state !== "done") return;
    drag = true;
    moved = false;
    lastMX = e.clientX;
    lastMY = e.clientY;
    canvas.setPointerCapture(e.pointerId);
    requestDraw();
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - lastMX;
    const dy = e.clientY - lastMY;
    if (Math.abs(dx) + Math.abs(dy) > 3) moved = true;
    angleY += dx * 0.005;
    angleX += dy * 0.005;
    angleX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, angleX));
    lastMX = e.clientX;
    lastMY = e.clientY;
  });
  function endDrag(e) {
    if (!drag) return;
    drag = false;
    if (!moved) {
      const hit = coverAtPointer(e.clientX, e.clientY);
      if (hit >= 0) flyTo(hit, false);
    }
    requestDraw();
  }
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", () => {
    drag = false;
  });

  pickBtn.addEventListener("click", pickFilm);
  document.getElementById("btn-again").addEventListener("click", closeDetails);
  document.getElementById("btn-browse").addEventListener("click", () => openBrowse());
  document.getElementById("browse-close").addEventListener("click", closeBrowse);
  searchEl.addEventListener("input", onSearch);
  searchEl.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const hits = filteredIndices();
    if (hits.length === 1) {
      if (mode === "browse") closeBrowse();
      flyTo(hits[0], false);
    } else if (hits.length > 1) openBrowse(hits);
  });

  document.getElementById("stats-btn").addEventListener("click", () => {
    buildStats();
    document.getElementById("stats-overlay").classList.add("open");
  });
  document.getElementById("stats-close").addEventListener("click", () =>
    document.getElementById("stats-overlay").classList.remove("open")
  );
  document.getElementById("stats-overlay").addEventListener("click", (e) => {
    if (e.target.id === "stats-overlay") document.getElementById("stats-overlay").classList.remove("open");
  });

  const QUIZ_BANK =
    window.QUIZ_QUESTIONS && window.QUIZ_QUESTIONS.length ? window.QUIZ_QUESTIONS : null;
  let quizOpen = false;
  let quizLen = 10;
  let quizDiff = "all";
  let quizRound = [];
  let quizI = 0;
  let quizScore = 0;
  let quizLocked = false;
  let quizSeen = [];

  function quizShuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
    }
    return a;
  }

  function quizPool() {
    if (!QUIZ_BANK) return [];
    return QUIZ_BANK.filter((q) => {
      if (quizDiff === "12") return q.d <= 2;
      if (quizDiff === "34") return q.d >= 3 && q.d <= 4;
      if (quizDiff === "5") return q.d === 5;
      return true;
    });
  }

  function quizBuildRound() {
    const pool = quizPool();
    if (!pool.length) return [];
    const fresh = pool.filter((q) => quizSeen.indexOf(q.id) === -1);
    const src = fresh.length ? fresh : pool;
    const count = Math.min(quizLen, src.length);
    const picked = quizShuffle(src).slice(0, count);
    for (let i = 0; i < picked.length; i++) quizSeen.push(picked[i].id);
    if (quizSeen.length > 250) quizSeen = quizSeen.slice(-120);
    return picked;
  }

  function quizShow(view) {
    document.getElementById("quiz-setup").hidden = view !== "setup";
    document.getElementById("quiz-play").hidden = view !== "play";
    document.getElementById("quiz-end").hidden = view !== "end";
    document.getElementById("quiz-error").hidden = view !== "error";
  }

  function openQuiz() {
    quizOpen = true;
    document.getElementById("stats-overlay").classList.remove("open");
    document.getElementById("quiz-overlay").classList.add("open");
    document.getElementById("trivia").style.opacity = "0";
    if (!QUIZ_BANK) {
      quizShow("error");
      return;
    }
    quizShow("setup");
  }

  function closeQuiz() {
    quizOpen = false;
    document.getElementById("quiz-overlay").classList.remove("open");
    if (!detailsEl.classList.contains("open")) {
      document.getElementById("trivia").style.opacity = "";
    }
  }

  function quizRenderQ() {
    const q = quizRound[quizI];
    quizLocked = false;
    document.getElementById("quiz-progress").textContent =
      "Question " + (quizI + 1) + " of " + quizRound.length;
    document.getElementById("quiz-cat").textContent = q.cat || "";
    document.getElementById("quiz-q").textContent = q.q;
    const nextBtn = document.getElementById("quiz-next");
    nextBtn.disabled = true;
    nextBtn.textContent = quizI === quizRound.length - 1 ? "Results" : "Next";
    const box = document.getElementById("quiz-opts");
    box.replaceChildren();
    const opts = quizShuffle(q.options);
    for (let i = 0; i < opts.length; i++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quiz-opt";
      btn.textContent = opts[i];
      btn.addEventListener("click", () => quizPick(btn, q));
      box.append(btn);
    }
  }

  function quizPick(btn, q) {
    if (quizLocked) return;
    quizLocked = true;
    const chosen = btn.textContent;
    if (chosen === q.a) quizScore++;
    const buttons = document.querySelectorAll("#quiz-opts .quiz-opt");
    for (let i = 0; i < buttons.length; i++) {
      buttons[i].disabled = true;
      if (buttons[i].textContent === q.a) buttons[i].classList.add("correct");
      else if (buttons[i] === btn) buttons[i].classList.add("wrong");
    }
    document.getElementById("quiz-next").disabled = false;
  }

  function quizStart() {
    if (!QUIZ_BANK) {
      quizShow("error");
      return;
    }
    quizRound = quizBuildRound();
    quizI = 0;
    quizScore = 0;
    if (!quizRound.length) {
      quizShow("error");
      return;
    }
    quizShow("play");
    quizRenderQ();
  }

  function quizNext() {
    if (!quizLocked) return;
    if (quizI >= quizRound.length - 1) {
      document.getElementById("quiz-score").textContent = quizScore + "/" + quizRound.length;
      document.getElementById("quiz-score-sub").textContent = quizRound.length + " questions";
      quizShow("end");
      return;
    }
    quizI++;
    quizRenderQ();
  }

  document.getElementById("quiz-btn").addEventListener("click", openQuiz);
  document.getElementById("quiz-close").addEventListener("click", closeQuiz);
  document.getElementById("quiz-end-close").addEventListener("click", closeQuiz);
  document.getElementById("quiz-overlay").addEventListener("click", (e) => {
    if (e.target.id === "quiz-overlay") closeQuiz();
  });
  document.getElementById("quiz-start").addEventListener("click", quizStart);
  document.getElementById("quiz-again").addEventListener("click", quizStart);
  document.getElementById("quiz-next").addEventListener("click", quizNext);
  document.getElementById("quiz-len-chips").addEventListener("click", (e) => {
    const b = e.target.closest(".quiz-chip");
    if (!b) return;
    quizLen = +b.dataset.n;
    document.querySelectorAll("#quiz-len-chips .quiz-chip").forEach((c) =>
      c.classList.toggle("active", c === b)
    );
  });
  document.getElementById("quiz-diff-chips").addEventListener("click", (e) => {
    const b = e.target.closest(".quiz-chip");
    if (!b) return;
    quizDiff = b.dataset.d;
    document.querySelectorAll("#quiz-diff-chips .quiz-chip").forEach((c) =>
      c.classList.toggle("active", c === b)
    );
  });

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) requestDraw();
  });
  window.addEventListener("resize", resize);

  const triviaEl = document.getElementById("trivia-text");
  const facts = window.TRIVIA_FACTS && window.TRIVIA_FACTS.length ? window.TRIVIA_FACTS : [];
  let triviaIdx = facts.length ? Math.floor(Math.random() * facts.length) : 0;
  function showTrivia(idx) {
    if (!facts.length || quizOpen) return;
    triviaEl.style.opacity = "0";
    setTimeout(() => {
      if (quizOpen || detailsEl.classList.contains("open")) return;
      triviaEl.textContent = facts[idx % facts.length];
      triviaEl.style.opacity = "1";
    }, 900);
  }
  if (facts.length) {
    triviaEl.textContent = facts[triviaIdx];
    triviaEl.style.opacity = "1";
    setInterval(() => {
      if ((state === "idle" || state === "done") && !quizOpen) {
        triviaIdx = (triviaIdx + 1) % facts.length;
        showTrivia(triviaIdx);
      }
    }, 22000);
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }

  buildChips();
  resize();
  requestDraw();
  loadPosters();
})();

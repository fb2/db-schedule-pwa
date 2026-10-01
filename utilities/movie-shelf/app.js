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
  let anim = readAnim();
  let flowPhase = 0;
  let flowFrom = 0;
  let flowTarget = 0;
  let flowDur = 48;
  let flowHits = [];
  let flowCX = 0;
  let spotIds = [];
  let spotMode = "in";
  let spotMark = 0;
  let spotAlpha = 0;
  let spotHits = [];
  let spotWasIdle = false;
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
    draw(now);
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

  function readAnim() {
    const v = (new URLSearchParams(location.search).get("anim") || "").toLowerCase();
    if (v === "infinity" || v === "flow" || v === "eight") return "infinity";
    return "sphere";
  }

  function writeAnim(next) {
    const url = new URL(location.href);
    url.searchParams.set("anim", next);
    history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function syncAnimSwitch() {
    document.getElementById("anim-sphere").classList.toggle("active", anim === "sphere");
    document.getElementById("anim-infinity").classList.toggle("active", anim === "infinity");
    document.getElementById("anim-sphere").setAttribute("aria-pressed", anim === "sphere" ? "true" : "false");
    document.getElementById("anim-infinity").setAttribute("aria-pressed", anim === "infinity" ? "true" : "false");
  }

  function setAnim(next) {
    if (next !== "infinity") next = "sphere";
    if (next === anim && state === "idle") {
      writeAnim(anim);
      syncAnimSwitch();
      return;
    }
    anim = next;
    state = "idle";
    selectedIdx = -1;
    detailsEl.classList.remove("open");
    document.getElementById("trivia").style.opacity = "";
    pickBtn.disabled = false;
    writeAnim(anim);
    syncAnimSwitch();
    requestDraw();
  }

  let flowGeo = null;
  let flowGeoKey = "";

  function flowGeometry(ampX, ampY) {
    const key = ampX.toFixed(1) + ":" + ampY.toFixed(1);
    if (flowGeo && flowGeoKey === key) return flowGeo;
    const steps = 640;
    const pts = new Array(steps + 1);
    let total = 0;
    let prevX = ampX;
    let prevY = 0;
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI * 2;
      const x = Math.cos(t) * ampX;
      const y = Math.sin(2 * t) * ampY;
      if (i) total += Math.hypot(x - prevX, y - prevY);
      pts[i] = { x, y, t, depth: (Math.cos(t) + 1) / 2, len: total };
      prevX = x;
      prevY = y;
    }
    flowGeoKey = key;
    flowGeo = { pts, total };
    return flowGeo;
  }

  function sampleFlow(geo, dist) {
    const total = geo.total || 1;
    let d = dist % total;
    if (d < 0) d += total;
    const pts = geo.pts;
    let lo = 0;
    let hi = pts.length - 1;
    while (lo < hi - 1) {
      const mid = (lo + hi) >> 1;
      if (pts[mid].len < d) lo = mid;
      else hi = mid;
    }
    const a = pts[lo];
    const b = pts[hi];
    const span = b.len - a.len || 1;
    const u = Math.max(0, Math.min(1, (d - a.len) / span));
    const mag = Math.hypot(b.x - a.x, b.y - a.y) || 1;
    return {
      x: a.x + (b.x - a.x) * u,
      y: a.y + (b.y - a.y) * u,
      t: a.t + (b.t - a.t) * u,
      depth: a.depth + (b.depth - a.depth) * u,
      tx: (b.x - a.x) / mag,
      ty: (b.y - a.y) / mag,
    };
  }

  function mod(a, m) {
    return ((a % m) + m) % m;
  }

  function drawField() {
    if (!n) return;
    if (state === "idle" && !drag) angleY += 0.0032;
    const savedCX = viewCX;
    viewCX = flowCX || W / 2;
    workPts.set(basePts);
    rotatePtsX(workPts, IDLE_ANGLE_X);
    rotatePtsY(workPts, angleY);
    for (let i = 0; i < n; i++) {
      sortBuf[i].i = i;
      sortBuf[i].z = workPts[i * 3 + 2];
    }
    sortBuf.sort((a, b) => a.z - b.z);
    const searching = Boolean(query.trim());
    for (let s = 0; s < n; s++) {
      const { i, z } = sortBuf[s];
      const isMatch = !matchSet || matchSet.has(i);
      const x = workPts[i * 3];
      const y = workPts[i * 3 + 1];
      const { sx, sy, scale } = project(x, y, z);
      const w = CARD_W * scale * 0.7;
      const h = CARD_H * scale * 0.7;
      if (w < 3.5) continue;
      let alpha = 0.045 + ((z + 1) / 2) * 0.2;
      if (matchSet && !isMatch) alpha *= 0.12;
      if (searching && isMatch) alpha = Math.max(alpha, 0.5);
      ctx.globalAlpha = alpha;
      const dx = sx - w / 2;
      const dy = sy - h / 2;
      if (images[i]) ctx.drawImage(images[i], dx, dy, w, h);
      else drawPlaceholder(dx, dy, w, h, i);
    }
    ctx.globalAlpha = 1;
    viewCX = savedCX;
  }

  function drawFlow() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    const pool = filteredIndices();
    flowHits = [];

    if (state === "idle" && !drag) {
      flowPhase += 0.012;
    } else if (state === "seek" || state === "spindown" || state === "fast" || state === "spinup") {
      spinT++;
      const progress = Math.min(1, spinT / flowDur);
      const eased = 1 - Math.pow(1 - progress, 3);
      flowPhase = flowFrom + (flowTarget - flowFrom) * eased;
      if (progress >= 1) {
        flowPhase = flowTarget;
        state = "done";
        showDetails(selectedIdx);
      }
    }

    const wantCX = state === "done" && W > 720 ? (W - 280) / 2 : W / 2;
    if (!flowCX) flowCX = wantCX;
    flowCX += (wantCX - flowCX) * (state === "done" ? 1 : 0.18);
    drawField();
    if (!pool.length) return;

    const len = pool.length;
    const topLimit = 118;
    const bottomLimit = 188;
    const usable = Math.max(160, H - topLimit - bottomLimit);
    const ampY = usable * 0.4;
    const ampX = Math.min(Math.max(120, W * 0.5 - 72), 460);
    const cy = topLimit + usable / 2;
    const geo = flowGeometry(ampX, ampY);
    const spacing = CARD_W + 10;
    const count = Math.max(12, Math.round(geo.total / spacing));
    const scale = geo.total / count;
    const shift = Math.round(count / 2);
    const qEdge = Math.floor(flowPhase) - shift;
    const cards = [];

    for (let k = 0; k < count; k++) {
      const q = qEdge - k;
      const arc = mod((flowPhase - q) * scale, geo.total);
      const p = sampleFlow(geo, arc);
      cards.push({
        i: pool[mod(q + count, len)],
        q,
        depth: p.depth,
        weave: Math.sin(p.t),
        w: CARD_W,
        h: CARD_H,
        sx: flowCX + p.x,
        sy: cy + p.y,
      });
    }
    cards.sort((a, b) => a.weave - b.weave || a.q - b.q);

    for (const c of cards) {
      const frontPick = state === "done" && c.i === selectedIdx && c.depth > 0.92;
      if (frontPick) continue;
      const dx = c.sx - c.w / 2;
      const dy = c.sy - c.h / 2;
      ctx.globalAlpha = 0.74 + (c.weave + 1) * 0.13;
      if (images[c.i]) ctx.drawImage(images[c.i], dx, dy, c.w, c.h);
      else drawPlaceholder(dx, dy, c.w, c.h, c.i);
      flowHits.push({ i: c.i, x: dx, y: dy, w: c.w, h: c.h, depth: c.weave });
    }

    if (state === "done" && selectedIdx >= 0) {
      const front = cards.reduce((best, c) => (!best || c.depth > best.depth ? c : best), null);
      if (front) {
        const w = front.w * 1.04;
        const h = front.h * 1.04;
        const dx = front.sx - w / 2;
        const dy = front.sy - h / 2;
        ctx.globalAlpha = 1;
        if (images[front.i]) ctx.drawImage(images[front.i], dx, dy, w, h);
        else drawPlaceholder(dx, dy, w, h, front.i);
        ctx.strokeStyle = "#d4a553";
        ctx.lineWidth = 2;
        ctx.strokeRect(dx, dy, w, h);
        flowHits.push({ i: front.i, x: dx, y: dy, w, h, depth: 2 });
      }
    }
    ctx.globalAlpha = 1;
  }

  function flyToFlow(idx, roulette) {
    const pool = filteredIndices();
    const pos = pool.indexOf(idx);
    if (pos < 0) return;
    selectedIdx = idx;
    pickBtn.disabled = true;
    detailsEl.classList.remove("open");
    document.getElementById("trivia").style.opacity = "0";
    const len = pool.length;
    const mod = ((flowPhase % len) + len) % len;
    const at = Math.floor(mod);
    const frac = mod - at;
    let forward = pos - at;
    if (forward < 0) forward += len;
    let delta = forward - frac;
    if (!roulette && delta > len / 2) delta -= len;
    if (roulette) delta += len * (1 + Math.floor(Math.random() * 2));
    if (Math.abs(delta) < 0.02) {
      state = "done";
      showDetails(idx);
      requestDraw();
      return;
    }
    flowFrom = flowPhase;
    flowTarget = flowPhase + delta;
    flowDur = roulette ? Math.min(130, 54 + Math.abs(delta) * 3.2) : Math.max(26, Math.min(64, Math.abs(delta) * 16));
    state = "seek";
    spinT = 0;
    requestDraw();
  }

  function smoothStep(t) {
    const x = Math.max(0, Math.min(1, t));
    return x * x * (3 - 2 * x);
  }

  function shuffleIds(list) {
    const a = list.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
    }
    return a;
  }

  function pickSpot() {
    const pool = filteredIndices();
    let src = pool.filter((i) => spotIds.indexOf(i) === -1);
    if (src.length < Math.min(3, pool.length)) src = pool;
    spotIds = shuffleIds(src).slice(0, Math.min(3, src.length));
  }

  function tickSpot(now) {
    const idle = state === "idle";
    if (!idle) {
      spotWasIdle = false;
      spotAlpha = 0;
      spotHits = [];
      return;
    }
    if (!spotWasIdle || !spotIds.length) {
      spotWasIdle = true;
      pickSpot();
      spotMode = "in";
      spotMark = now;
      spotAlpha = 0;
    }
    const pool = filteredIndices();
    if (spotIds.some((id) => pool.indexOf(id) === -1)) {
      pickSpot();
      spotMode = "in";
      spotMark = now;
    }
    const elapsed = now - spotMark;
    if (spotMode === "in") {
      spotAlpha = smoothStep(elapsed / 900);
      if (elapsed >= 900) {
        spotAlpha = 1;
        spotMode = "hold";
        spotMark = now;
      }
    } else if (spotMode === "hold") {
      spotAlpha = 1;
      if (elapsed >= 10000) {
        spotMode = "out";
        spotMark = now;
      }
    } else {
      spotAlpha = 1 - smoothStep(elapsed / 900);
      if (elapsed >= 900) {
        pickSpot();
        spotMode = "in";
        spotMark = now;
        spotAlpha = 0;
      }
    }
  }

  function drawSpot(now) {
    spotHits = [];
    if (anim !== "sphere") return;
    tickSpot(now);
    if (spotAlpha < 0.02 || !spotIds.length || state !== "idle") return;
    const count = spotIds.length;
    const gapRatio = 0.2;
    let spotW = Math.round(Math.min(118, Math.max(84, Math.min(W, H) * 0.11)));
    let gap = Math.round(spotW * gapRatio);
    const maxRow = Math.max(120, W - 64);
    if (count * spotW + (count - 1) * gap > maxRow) {
      spotW = Math.floor((maxRow - (count - 1) * gap) / count);
      gap = Math.round(spotW * gapRatio);
    }
    const spotH = Math.round(spotW * (CARD_H / CARD_W));
    const totalW = count * spotW + (count - 1) * gap;
    const cx = viewCX || W / 2;
    const cy = H * 0.47;
    const xStart = cx - totalW / 2;
    const y = cy - spotH / 2;

    const grad = ctx.createRadialGradient(cx, cy, spotW * 0.2, cx, cy, totalW * 0.7);
    grad.addColorStop(0, `rgba(0,0,0,${0.46 * spotAlpha})`);
    grad.addColorStop(0.6, `rgba(0,0,0,${0.16 * spotAlpha})`);
    grad.addColorStop(1, "rgba(0,0,0,0)");
    ctx.globalAlpha = 1;
    ctx.fillStyle = grad;
    ctx.fillRect(cx - totalW, cy - spotH, totalW * 2, spotH * 2);

    for (let k = 0; k < count; k++) {
      const i = spotIds[k];
      const x = xStart + k * (spotW + gap);
      ctx.globalAlpha = spotAlpha;
      if (images[i]) ctx.drawImage(images[i], x, y, spotW, spotH);
      else drawPlaceholder(x, y, spotW, spotH, i);
      spotHits.push({ i, x, y, w: spotW, h: spotH });
    }
    ctx.globalAlpha = 1;
  }

  function spotAt(mx, my) {
    if (anim !== "sphere" || state !== "idle" || spotAlpha < 0.4) return -1;
    for (let i = spotHits.length - 1; i >= 0; i--) {
      const c = spotHits[i];
      if (mx >= c.x && mx <= c.x + c.w && my >= c.y && my <= c.y + c.h) return c.i;
    }
    return -1;
  }

  function draw(now) {
    if (anim === "infinity") {
      drawFlow();
      return;
    }
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
    drawSpot(now || performance.now());
    ctx.globalAlpha = 1;
  }

  function flyTo(idx, roulette) {
    if (anim === "infinity") {
      flyToFlow(idx, roulette);
      return;
    }
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
    if (anim === "infinity") {
      let hit = -1;
      let best = -1;
      for (const c of flowHits) {
        if (mx < c.x || mx > c.x + c.w || my < c.y || my > c.y + c.h) continue;
        if (c.depth >= best) {
          best = c.depth;
          hit = c.i;
        }
      }
      return hit;
    }
    const featured = spotAt(mx, my);
    if (featured >= 0) return featured;
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

  function recentIndices() {
    const rows = [];
    for (let i = 0; i < n; i++) if (MOVIES[i].added) rows.push(i);
    rows.sort((a, b) => {
      if (MOVIES[a].added !== MOVIES[b].added) return MOVIES[a].added < MOVIES[b].added ? 1 : -1;
      return MOVIES[a].t.localeCompare(MOVIES[b].t);
    });
    return rows;
  }

  function openBrowse(indices, heading) {
    mode = "browse";
    loopOn = false;
    detailsEl.classList.remove("open");
    const list = indices || visiblePool();
    browseMeta.textContent = heading || (list.length === 1 ? "1 disc" : `${list.length} discs`);
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
    if (!drag) {
      canvas.style.cursor =
        anim === "sphere" && spotAt(e.clientX, e.clientY) >= 0 ? "pointer" : "";
      return;
    }
    const dx = e.clientX - lastMX;
    const dy = e.clientY - lastMY;
    if (Math.abs(dx) + Math.abs(dy) > 3) moved = true;
    if (anim === "infinity") {
      if (state === "done") {
        detailsEl.classList.remove("open");
        document.getElementById("trivia").style.opacity = "";
        state = "idle";
        selectedIdx = -1;
        pickBtn.disabled = false;
      }
      flowPhase -= dx * 0.012;
      lastMX = e.clientX;
      lastMY = e.clientY;
      return;
    }
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

  document.getElementById("anim-sphere").addEventListener("click", () => setAnim("sphere"));
  document.getElementById("anim-infinity").addEventListener("click", () => setAnim("infinity"));

  pickBtn.addEventListener("click", pickFilm);
  document.getElementById("btn-again").addEventListener("click", closeDetails);
  document.getElementById("btn-browse").addEventListener("click", () => openBrowse());
  document.getElementById("btn-recent").addEventListener("click", () => {
    const list = recentIndices();
    const count = list.length === 1 ? "1 disc" : `${list.length} discs`;
    openBrowse(list, list.length ? `Recently added · ${count}` : "Recently added");
  });
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
  syncAnimSwitch();
  resize();
  requestDraw();
  loadPosters();
})();

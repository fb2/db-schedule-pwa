const els = {
  filmSelect: document.querySelector("#filmSelect"),
  meteredValue: document.querySelector("#meteredValue"),
  meteredUnit: document.querySelector("#meteredUnit"),
  correctedTime: document.querySelector("#correctedTime"),
  correctionMeta: document.querySelector("#correctionMeta"),
  startTimer: document.querySelector("#startTimer"),
  timerPanel: document.querySelector("#timerPanel"),
  timerRemaining: document.querySelector("#timerRemaining"),
  pauseTimer: document.querySelector("#pauseTimer"),
  resetTimer: document.querySelector("#resetTimer"),
  filmName: document.querySelector("#filmName"),
  filmNotes: document.querySelector("#filmNotes"),
  dataQuality: document.querySelector("#dataQuality"),
  sourceLink: document.querySelector("#sourceLink"),
};

const state = {
  films: [],
  selectedFilmId: localStorage.getItem("reciprocityFilmId") || "kodak-portra-400",
  meteredValue: Number(localStorage.getItem("reciprocityMeteredValue") || 10),
  meteredUnit: Number(localStorage.getItem("reciprocityMeteredUnit") || 1),
  timer: {
    durationSeconds: 0,
    remainingSeconds: 0,
    deadline: 0,
    running: false,
    intervalId: null,
    wakeLock: null,
  },
};

function selectedFilm() {
  return state.films.find((film) => film.id === state.selectedFilmId) || state.films[0];
}

function secondsFromInput() {
  const value = Math.max(0.1, Number(els.meteredValue.value) || 0.1);
  return value * Number(els.meteredUnit.value);
}

function roundSeconds(seconds) {
  if (seconds < 10) return Math.round(seconds * 10) / 10;
  if (seconds < 120) return Math.round(seconds);
  if (seconds < 3600) return Math.round(seconds / 5) * 5;
  return Math.round(seconds / 60) * 60;
}

function formatDuration(seconds) {
  const rounded = roundSeconds(seconds);
  if (rounded < 60) {
    return Number.isInteger(rounded) ? `${rounded}s` : `${rounded.toFixed(1)}s`;
  }

  const hours = Math.floor(rounded / 3600);
  const minutes = Math.floor((rounded % 3600) / 60);
  const secs = Math.round(rounded % 60);

  if (hours > 0) {
    return secs > 0 ? `${hours}h ${minutes}m ${secs}s` : `${hours}h ${minutes}m`;
  }

  return secs > 0 ? `${minutes}m ${secs}s` : `${minutes}m`;
}

function formatStops(stops) {
  const rounded = Math.round(stops * 10) / 10;
  return `${rounded > 0 ? "+" : ""}${rounded} stop${Math.abs(rounded) === 1 ? "" : "s"}`;
}

function interpolateTable(points, meteredSeconds) {
  const sorted = [...points].sort((a, b) => a.metered - b.metered);
  let warning = "";

  if (meteredSeconds <= sorted[0].metered) {
    return { correctedSeconds: meteredSeconds, warning };
  }

  let lower = sorted[0];
  let upper = sorted[sorted.length - 1];

  for (let index = 1; index < sorted.length; index += 1) {
    if (meteredSeconds <= sorted[index].metered) {
      lower = sorted[index - 1];
      upper = sorted[index];
      break;
    }
  }

  if (meteredSeconds > sorted[sorted.length - 1].metered) {
    lower = sorted[sorted.length - 2];
    upper = sorted[sorted.length - 1];
    warning = "Beyond the published table; extrapolated from the last segment.";
  }

  const x1 = Math.log(lower.metered);
  const x2 = Math.log(upper.metered);
  const y1 = Math.log(lower.corrected);
  const y2 = Math.log(upper.corrected);
  const ratio = (Math.log(meteredSeconds) - x1) / (x2 - x1);
  const correctedSeconds = Math.exp(y1 + ratio * (y2 - y1));

  return { correctedSeconds, warning };
}

function calculateCorrection(film, meteredSeconds) {
  const model = film.model;

  if (meteredSeconds <= model.thresholdSeconds) {
    return {
      correctedSeconds: meteredSeconds,
      warning: `No correction below ${formatDuration(model.thresholdSeconds)}.`,
    };
  }

  if (model.type === "power") {
    return {
      correctedSeconds: Math.pow(meteredSeconds, model.exponent),
      warning: "",
    };
  }

  if (model.type === "thresholdMultiplier") {
    return {
      correctedSeconds: meteredSeconds * model.multiplier,
      warning: "",
    };
  }

  if (model.type === "table") {
    return interpolateTable(model.points, meteredSeconds);
  }

  return { correctedSeconds: meteredSeconds, warning: "Unknown correction model." };
}

function correctionSummary(meteredSeconds, correctedSeconds, warning) {
  const multiplier = correctedSeconds / meteredSeconds;
  const stops = Math.log2(multiplier);
  const pieces = [`${multiplier.toFixed(multiplier < 10 ? 2 : 1)}x`, formatStops(stops)];
  if (warning) pieces.push(warning);
  return pieces.join(" · ");
}

function saveState() {
  localStorage.setItem("reciprocityFilmId", state.selectedFilmId);
  localStorage.setItem("reciprocityMeteredValue", String(els.meteredValue.value));
  localStorage.setItem("reciprocityMeteredUnit", String(els.meteredUnit.value));
}

function renderFilmSelect() {
  els.filmSelect.innerHTML = "";

  const sortedFilms = [...state.films].sort((a, b) => a.priority - b.priority || a.name.localeCompare(b.name));
  for (const film of sortedFilms) {
    const option = document.createElement("option");
    option.value = film.id;
    option.textContent = `${film.name} (${film.formats.join(", ")})`;
    els.filmSelect.append(option);
  }

  if (!state.films.some((film) => film.id === state.selectedFilmId)) {
    state.selectedFilmId = state.films[0]?.id;
  }
  els.filmSelect.value = state.selectedFilmId;
}

function render() {
  const film = selectedFilm();
  if (!film) return;

  const meteredSeconds = secondsFromInput();
  const { correctedSeconds, warning } = calculateCorrection(film, meteredSeconds);
  state.timer.durationSeconds = roundSeconds(correctedSeconds);

  els.correctedTime.textContent = formatDuration(correctedSeconds);
  els.correctionMeta.textContent = correctionSummary(meteredSeconds, correctedSeconds, warning);
  els.filmName.textContent = film.name;
  els.filmNotes.textContent = film.notes;
  els.dataQuality.textContent = film.quality;
  els.sourceLink.href = film.sourceUrl;
  els.sourceLink.textContent = film.sourceName;

  saveState();
}

async function requestWakeLock() {
  if (!("wakeLock" in navigator)) return;
  try {
    state.timer.wakeLock = await navigator.wakeLock.request("screen");
  } catch {
    state.timer.wakeLock = null;
  }
}

async function releaseWakeLock() {
  if (!state.timer.wakeLock) return;
  await state.timer.wakeLock.release().catch(() => {});
  state.timer.wakeLock = null;
}

function renderTimer() {
  els.timerRemaining.textContent = formatDuration(state.timer.remainingSeconds);
  els.pauseTimer.textContent = state.timer.running ? "Pause" : "Resume";
}

function finishTimer() {
  clearInterval(state.timer.intervalId);
  state.timer.running = false;
  state.timer.remainingSeconds = 0;
  renderTimer();
  releaseWakeLock();

  if ("vibrate" in navigator) {
    navigator.vibrate([300, 150, 300, 150, 500]);
  }
}

function tickTimer() {
  state.timer.remainingSeconds = Math.max(0, Math.ceil((state.timer.deadline - Date.now()) / 1000));
  renderTimer();

  if (state.timer.remainingSeconds <= 0) {
    finishTimer();
  }
}

function startTimer() {
  clearInterval(state.timer.intervalId);
  state.timer.remainingSeconds = Math.max(1, state.timer.durationSeconds);
  state.timer.deadline = Date.now() + state.timer.remainingSeconds * 1000;
  state.timer.running = true;
  els.timerPanel.classList.remove("hidden");
  requestWakeLock();
  renderTimer();
  state.timer.intervalId = setInterval(tickTimer, 250);
}

function pauseOrResumeTimer() {
  if (state.timer.running) {
    clearInterval(state.timer.intervalId);
    state.timer.running = false;
    state.timer.remainingSeconds = Math.max(0, Math.ceil((state.timer.deadline - Date.now()) / 1000));
    releaseWakeLock();
    renderTimer();
    return;
  }

  state.timer.deadline = Date.now() + state.timer.remainingSeconds * 1000;
  state.timer.running = true;
  requestWakeLock();
  state.timer.intervalId = setInterval(tickTimer, 250);
  renderTimer();
}

function resetTimer() {
  clearInterval(state.timer.intervalId);
  state.timer.running = false;
  state.timer.remainingSeconds = state.timer.durationSeconds;
  releaseWakeLock();
  els.timerPanel.classList.add("hidden");
  renderTimer();
}

function bindEvents() {
  els.filmSelect.addEventListener("change", () => {
    state.selectedFilmId = els.filmSelect.value;
    render();
  });
  els.meteredValue.addEventListener("input", render);
  els.meteredUnit.addEventListener("change", render);
  els.startTimer.addEventListener("click", startTimer);
  els.pauseTimer.addEventListener("click", pauseOrResumeTimer);
  els.resetTimer.addEventListener("click", resetTimer);
}

async function init() {
  const response = await fetch("./films.json");
  const data = await response.json();
  state.films = data.films;

  els.meteredValue.value = String(state.meteredValue);
  els.meteredUnit.value = String(state.meteredUnit);

  renderFilmSelect();
  bindEvents();
  render();

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }
}

init().catch((error) => {
  els.correctedTime.textContent = "Error";
  els.correctionMeta.textContent = error instanceof Error ? error.message : "Could not load film data.";
});

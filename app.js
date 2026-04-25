import { publicHolidays, routes } from "./schedules.js";

const state = {
  routeId: localStorage.getItem("routeId") || "central",
  directionId: localStorage.getItem("directionId") || "db-central",
  dayOverride: localStorage.getItem("dayOverride") || "auto",
  walkBuffer: Number(localStorage.getItem("walkBuffer") || 10),
};

const els = {
  routeTitle: document.querySelector("#routeTitle"),
  flipDirection: document.querySelector("#flipDirection"),
  nextTime: document.querySelector("#nextTime"),
  countdown: document.querySelector("#countdown"),
  departureMeta: document.querySelector("#departureMeta"),
  routeSelect: document.querySelector("#routeSelect"),
  directionSelect: document.querySelector("#directionSelect"),
  dayOverride: document.querySelector("#dayOverride"),
  walkBuffer: document.querySelector("#walkBuffer"),
  activeDayType: document.querySelector("#activeDayType"),
  upcomingList: document.querySelector("#upcomingList"),
  sourceText: document.querySelector("#sourceText"),
  sourceLink: document.querySelector("#sourceLink"),
};

function selectedRoute() {
  return routes.find((route) => route.id === state.routeId) || routes[0];
}

function selectedDirection() {
  const route = selectedRoute();
  return route.directions.find((direction) => direction.id === state.directionId) || route.directions[0];
}

function toDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(date, days) {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function dayTypeFor(date) {
  if (state.dayOverride !== "auto") return state.dayOverride;

  const holidays = publicHolidays[date.getFullYear()] || [];
  if (date.getDay() === 0 || holidays.includes(toDateKey(date))) return "sundayPH";
  if (date.getDay() === 6) return "saturday";
  return "weekday";
}

function dayTypeLabel(dayType) {
  return {
    weekday: "Weekday",
    saturday: "Saturday",
    sundayPH: "Sunday / public holiday",
  }[dayType];
}

function normalizeDeparture(item) {
  return typeof item === "string" ? { time: item, note: "" } : item;
}

function departureDateFor(baseDate, time) {
  const [hours, minutes] = time.split(":").map(Number);
  const date = new Date(baseDate);
  date.setHours(hours, minutes, 0, 0);
  return date;
}

function formatTime(date) {
  return new Intl.DateTimeFormat("en-HK", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

function formatDuration(ms) {
  const totalMinutes = Math.max(0, Math.round(ms / 60000));
  if (totalMinutes < 60) return `${totalMinutes} min`;

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return minutes === 0 ? `${hours} hr` : `${hours} hr ${minutes} min`;
}

function relativeDay(date, now) {
  const today = toDateKey(now);
  const departureDay = toDateKey(date);
  if (departureDay === today) return "Today";
  if (departureDay === toDateKey(addDays(now, 1))) return "Tomorrow";
  return new Intl.DateTimeFormat("en-HK", { weekday: "short", month: "short", day: "numeric" }).format(date);
}

function upcomingCutoff(now) {
  const cutoff = addDays(now, 1);
  cutoff.setHours(12, 0, 0, 0);
  return cutoff;
}

function collectDepartures(direction, now) {
  const threshold = new Date(now.getTime() + state.walkBuffer * 60000);
  const departures = [];

  for (let dayOffset = 0; dayOffset < 10; dayOffset += 1) {
    const date = addDays(now, dayOffset);
    const dayType = dayTypeFor(date);
    const schedule = direction.schedules[dayType] || [];

    for (const item of schedule) {
      const departure = normalizeDeparture(item);
      const departureDate = departureDateFor(date, departure.time);
      if (departureDate >= threshold) {
        departures.push({
          ...departure,
          date: departureDate,
          dayType,
        });
      }
    }
  }

  return departures.sort((a, b) => a.date - b.date);
}

function saveState() {
  localStorage.setItem("routeId", state.routeId);
  localStorage.setItem("directionId", state.directionId);
  localStorage.setItem("dayOverride", state.dayOverride);
  localStorage.setItem("walkBuffer", String(state.walkBuffer));
}

function populateRoutes() {
  els.routeSelect.innerHTML = "";

  for (const route of routes) {
    const option = document.createElement("option");
    option.value = route.id;
    option.textContent = route.label;
    els.routeSelect.append(option);
  }

  els.routeSelect.value = state.routeId;
}

function populateDirections() {
  const route = selectedRoute();
  els.directionSelect.innerHTML = "";

  for (const direction of route.directions) {
    const option = document.createElement("option");
    option.value = direction.id;
    option.textContent = direction.label;
    els.directionSelect.append(option);
  }

  if (!route.directions.some((direction) => direction.id === state.directionId)) {
    state.directionId = route.directions[0].id;
  }

  els.directionSelect.value = state.directionId;
}

function flipDirection() {
  const route = selectedRoute();
  const pairs = {
    "db-central": "central-db",
    "central-db": "db-central",
    "dbnorth-central": "central-dbnorth",
    "central-dbnorth": "dbnorth-central",
  };

  if (pairs[state.directionId]) {
    state.directionId = pairs[state.directionId];
  } else {
    const index = route.directions.findIndex((direction) => direction.id === state.directionId);
    state.directionId = route.directions[index === 0 ? 1 : 0]?.id || route.directions[0].id;
  }

  populateDirections();
  saveState();
  render();
}

function renderUpcoming(departures, now) {
  els.upcomingList.innerHTML = "";

  if (departures.length === 0) {
    const item = document.createElement("li");
    item.textContent = "No departures found in the next 10 days for this selection.";
    els.upcomingList.append(item);
    return;
  }

  const scheduleCutoff = upcomingCutoff(now);
  const visibleDepartures = departures.filter((departure) => departure.date <= scheduleCutoff);

  for (const departure of visibleDepartures) {
    const item = document.createElement("li");
    const note = departure.note ? `<span class="pill">${departure.note}</span>` : "";
    item.innerHTML = `
      <span class="upcoming-time">${formatTime(departure.date)}</span>
      <span class="upcoming-detail">${relativeDay(departure.date, now)} · ${dayTypeLabel(departure.dayType)} ${note}</span>
    `;
    els.upcomingList.append(item);
  }
}

function render() {
  const now = new Date();
  const route = selectedRoute();
  const direction = selectedDirection();
  const departures = collectDepartures(direction, now);
  const next = departures[0];
  const autoDayType = dayTypeFor(now);

  els.routeTitle.textContent = direction.label;
  els.activeDayType.textContent = state.dayOverride === "auto"
    ? `Auto: ${dayTypeLabel(autoDayType)}`
    : dayTypeLabel(state.dayOverride);
  els.sourceText.textContent = route.source.text;
  els.sourceLink.href = route.source.url;
  els.dayOverride.value = state.dayOverride;
  els.walkBuffer.value = String(state.walkBuffer);

  if (!next) {
    els.nextTime.textContent = "--:--";
    els.countdown.textContent = "No catchable ferry found.";
    els.departureMeta.textContent = "Try another route, direction, or day type.";
    renderUpcoming(departures, now);
    return;
  }

  const msUntilDeparture = next.date - now;
  const msUntilLeave = msUntilDeparture - state.walkBuffer * 60000;
  const leaveText = msUntilLeave <= 60000
    ? "Leave now"
    : `Leave in about ${formatDuration(msUntilLeave)}`;
  const noteText = next.note ? ` · ${next.note}` : "";

  els.nextTime.textContent = formatTime(next.date);
  els.countdown.textContent = `Departs in ${formatDuration(msUntilDeparture)}`;
  els.departureMeta.textContent = `${leaveText} with ${state.walkBuffer} min walk buffer · ${relativeDay(next.date, now)}${noteText}`;

  renderUpcoming(departures, now);
}

function bindEvents() {
  els.routeSelect.addEventListener("change", () => {
    state.routeId = els.routeSelect.value;
    populateDirections();
    saveState();
    render();
  });

  els.directionSelect.addEventListener("change", () => {
    state.directionId = els.directionSelect.value;
    saveState();
    render();
  });

  els.dayOverride.addEventListener("change", () => {
    state.dayOverride = els.dayOverride.value;
    saveState();
    render();
  });

  els.walkBuffer.addEventListener("change", () => {
    state.walkBuffer = Number(els.walkBuffer.value);
    saveState();
    render();
  });

  els.flipDirection.addEventListener("click", flipDirection);
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {
    // Offline cache is nice to have; the schedule still works without it.
  });
}

populateRoutes();
populateDirections();
bindEvents();
render();
setInterval(render, 30000);

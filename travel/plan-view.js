const MONTH_ABBREV = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

export function todayIso(date = new Date()) {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

export function groupBodyLines(body) {
  const lines = String(body || "").split("\n");
  const blocks = [];
  let index = 0;

  while (index < lines.length) {
    const trimmed = lines[index].trim();
    if (!trimmed) {
      if (blocks.at(-1)?.type !== "break") blocks.push({ type: "break" });
      index += 1;
      continue;
    }
    if (isBannerHeading(trimmed) || isLabelOnly(trimmed) || isBlockLabel(trimmed)) {
      blocks.push({ type: "heading", text: cleanHeading(trimmed) });
      index += 1;
      continue;
    }
    if (isWarningLine(trimmed)) {
      const taken = takeWrapped(lines, index);
      blocks.push({ type: "callout", text: taken.text });
      index = taken.next;
      continue;
    }
    if (isCheckLine(trimmed)) {
      const items = [];
      while (index < lines.length) {
        const current = lines[index].trim();
        if (!current) {
          const peek = peekNonEmpty(lines, index + 1);
          if (peek && isCheckLine(peek)) {
            index += 1;
            continue;
          }
          break;
        }
        if (!isCheckLine(current)) break;
        const item = parseCheck(current);
        index += 1;
        while (index < lines.length && isCheckNote(lines[index])) {
          item.note = joinText(item.note, lines[index].trim());
          index += 1;
          while (index < lines.length && isSoftWrap(lines[index - 1], lines[index])) {
            item.note = joinText(item.note, lines[index].trim());
            index += 1;
          }
        }
        items.push(item);
      }
      blocks.push({ type: "checks", items });
      continue;
    }
    if (isBulletLine(trimmed)) {
      const items = [];
      while (index < lines.length) {
        const current = lines[index].trim();
        if (!current || !isBulletLine(current)) break;
        let text = current.replace(/^[·•→-]\s+/, "");
        index += 1;
        while (index < lines.length && isSoftWrap(lines[index - 1], lines[index])) {
          text = joinText(text, lines[index].trim());
          index += 1;
        }
        items.push(text);
      }
      blocks.push({ type: "bullets", items });
      continue;
    }
    if (isFieldLine(trimmed)) {
      const { label, value } = splitField(trimmed);
      const taken = takeWrapped(lines, index, value);
      blocks.push({ type: "field", label, value: taken.text });
      index = taken.next;
      continue;
    }
    const taken = takeWrapped(lines, index);
    blocks.push({ type: "prose", text: taken.text });
    index = taken.next;
  }

  while (blocks[0]?.type === "break") blocks.shift();
  while (blocks.at(-1)?.type === "break") blocks.pop();
  return blocks;
}

export function collectDatedSections(plans) {
  return (plans || [])
    .flatMap((plan) => (plan.sections || []).map((section) => ({
      ...section,
      monthId: plan.monthId
    })))
    .filter((section) => section.startDate && section.endDate)
    .sort((left, right) => {
      const start = String(left.startDate).localeCompare(String(right.startDate));
      if (start) return start;
      const span = daySpan(left) - daySpan(right);
      if (span) return span;
      return importance(left) - importance(right);
    });
}

export function findFocusPoint(plans, today = todayIso()) {
  const sections = collectDatedSections(plans);
  const happening = sections
    .filter((section) => section.startDate <= today && section.endDate >= today)
    .sort((left, right) => {
      const span = daySpan(left) - daySpan(right);
      if (span) return span;
      return importance(left) - importance(right);
    });
  const upcoming = sections.filter((section) => section.startDate > today);
  const current = happening[0] || upcoming[0] || sections.at(-1) || null;
  const next = happening[0] ? upcoming[0] || null : upcoming[1] || null;
  return { today, current, next, happening, upcoming };
}

export function sectionTiming(section, today = todayIso()) {
  if (!section?.startDate || !section?.endDate) return "upcoming";
  if (section.endDate < today) return "past";
  if (section.startDate <= today && section.endDate >= today) return "current";
  return "upcoming";
}

export function weekTiming(week, today = todayIso()) {
  if (!week?.endDate) return "upcoming";
  if (week.endDate < today) return "past";
  if (week.startDate <= today && week.endDate >= today) return "current";
  return "upcoming";
}

export function parseRememberItems(lines) {
  const start = lines.findIndex((line) => /REMEMBER\s*&\s*TAKE/i.test(line));
  if (start === -1) return [];

  const items = [];
  for (let index = start + 1; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    if (/^[=\-]{8,}$/.test(trimmed) && items.length) break;
    if (!/^\[[ xX!]\]/.test(trimmed) && !/@TAKE|@REMEMBER/.test(trimmed)) continue;
    items.push({
      text: trimmed.replace(/^\[[x!\s]\]\s*/i, "").trim(),
      checked: /^\[[xX]\]/.test(trimmed),
      urgent: /^\[[!]\]/.test(trimmed),
      kind: /@TAKE/.test(trimmed) ? "take" : /@REMEMBER/.test(trimmed) ? "remember" : "task",
      scope: (trimmed.match(/\{([^}]+)\}/) || [])[1] || ""
    });
  }
  return items;
}

export function relevantRememberItems(items, today = todayIso()) {
  return (items || []).filter((item) => !item.checked && scopeTouchesDate(item.scope, today));
}

export function focusFacts(section) {
  if (!section) return { title: "", date: "", fact: "", warning: "" };
  const lines = String(section.body || "").split("\n").map((line) => line.trim()).filter(Boolean);
  const flight = lines.find((line) => /\b[A-Z]{2}\d{2,4}\b/.test(line) && /\b(depart|arrive|→|->)\b/i.test(line));
  const warning = lines.find((line) => /^⚠/.test(line));
  const leaveBy = lines.find((line) => /leave\b.*by\b/i.test(line));
  return {
    title: section.title || "",
    date: section.startDate === section.endDate
      ? section.startDate
      : `${section.startDate} – ${section.endDate}`,
    fact: flight || lines[0] || "",
    warning: warning || leaveBy || ""
  };
}

function takeWrapped(lines, start, initial) {
  let text = initial === undefined ? lines[start].trim() : initial;
  let index = start + 1;
  while (index < lines.length && isSoftWrap(lines[index - 1], lines[index])) {
    text = joinText(text, lines[index].trim());
    index += 1;
  }
  return { text, next: index };
}

function isSoftWrap(prevRaw, nextRaw) {
  const prev = String(prevRaw || "").trim();
  const next = String(nextRaw || "").trim();
  if (!prev || !next) return false;
  if (isStructuralStart(next) || isBlockLabel(next)) return false;
  if (/[,;:—–/]$/.test(prev)) return true;
  if (/[a-z0-9)]$/.test(prev) && /^[a-z(]/.test(next)) return true;
  const prevEnded = /[.!?]["')\]]?$/.test(prev);
  if (prevEnded && /^[A-Z⚠]/.test(next)) return false;
  return prev.length >= 55 && !prevEnded;
}

function isStructuralStart(trimmed) {
  return isBannerHeading(trimmed)
    || isLabelOnly(trimmed)
    || isBlockLabel(trimmed)
    || isWarningLine(trimmed)
    || isCheckLine(trimmed)
    || isBulletLine(trimmed)
    || isFieldLine(trimmed);
}

function isBlockLabel(trimmed) {
  return /^(FLIGHT|HOTEL|TRANSFER|TRAIN|EVENT|ACCOMMODATION)\b/i.test(trimmed) && !isFieldLine(trimmed);
}

function isBannerHeading(trimmed) {
  return /^=+.+=+$/.test(trimmed) || (/^\*{2,}/.test(trimmed) && /\*{2,}$/.test(trimmed));
}

function isLabelOnly(trimmed) {
  return /^[A-Z][A-Za-z0-9 /&'()-]{1,40}:$/.test(trimmed);
}

function isWarningLine(trimmed) {
  return /^⚠/.test(trimmed);
}

function isCheckLine(trimmed) {
  return /^\[[ xX!]\](?:\s|$)/.test(trimmed);
}

function isBulletLine(trimmed) {
  return /^[·•→]\s+\S/.test(trimmed);
}

function isFieldLine(trimmed) {
  return /^[A-Za-z][A-Za-z0-9 /&'().-]{0,28}:\s+\S/.test(trimmed);
}

function isCheckNote(rawLine) {
  if (!rawLine || !String(rawLine).trim()) return false;
  const trimmed = rawLine.trim();
  if (isCheckLine(trimmed) || isBannerHeading(trimmed) || isBlockLabel(trimmed) || isWarningLine(trimmed) || isFieldLine(trimmed)) return false;
  return /^ {3,}/.test(rawLine) || /^\t/.test(rawLine);
}

function parseCheck(line) {
  return {
    text: line.replace(/^\[[x!\s]\]\s*/i, "").trim(),
    checked: /^\[[xX]\]/.test(line),
    urgent: /^\[[!]\]/.test(line),
    note: ""
  };
}

function splitField(line) {
  const index = line.indexOf(":");
  return {
    label: line.slice(0, index).trim(),
    value: line.slice(index + 1).trim()
  };
}

function cleanHeading(line) {
  return line.replace(/^[=\*]+|[=\*]+$/g, "").trim();
}

function peekNonEmpty(lines, start) {
  for (let index = start; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    if (trimmed) return trimmed;
  }
  return "";
}

function joinText(left, right) {
  return [left, right].filter(Boolean).join(" ").replace(/\s+/g, " ").trim();
}

function daySpan(section) {
  return diffDays(section.startDate, section.endDate);
}

function importance(section) {
  return /KEY EVENT|TRAVEL DAY|MUST/i.test(section.title || "") ? 0 : 1;
}

function diffDays(startIso, endIso) {
  const start = dateFromIso(startIso);
  const end = dateFromIso(endIso);
  return Math.round((end - start) / 86400000);
}

function scopeTouchesDate(scope, today) {
  if (!scope) return false;
  const date = dateFromIso(today);
  const month = MONTH_ABBREV[date.getUTCMonth()];
  const day = date.getUTCDate();
  if (new RegExp(`\\b${month}\\b`, "i").test(scope)) {
    const days = [...scope.matchAll(/\b(\d{1,2})\b/g)].map((match) => Number(match[1]));
    if (!days.length) return true;
    return days.some((value) => Math.abs(value - day) <= 3) || (days[0] <= day && day <= (days.at(-1) || days[0]));
  }
  const monthIndex = MONTH_ABBREV.findIndex((name) => new RegExp(`\\b${name}\\b`, "i").test(scope));
  if (monthIndex === -1) return /US|TOKYO|SG|HK|KL|PHL|NY/i.test(scope);
  const next = (monthIndex + 1) % 12;
  const prev = (monthIndex + 11) % 12;
  return date.getUTCMonth() === next || date.getUTCMonth() === prev;
}

function dateFromIso(iso) {
  const [year, month, day] = String(iso).split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

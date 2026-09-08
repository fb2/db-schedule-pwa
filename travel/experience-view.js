const MONTHS = new Map([
  ["JAN", 0], ["JANUARY", 0],
  ["FEB", 1], ["FEBRUARY", 1],
  ["MAR", 2], ["MARCH", 2],
  ["APR", 3], ["APRIL", 3],
  ["MAY", 4],
  ["JUN", 5], ["JUNE", 5],
  ["JUL", 6], ["JULY", 6],
  ["AUG", 7], ["AUGUST", 7],
  ["SEP", 8], ["SEPT", 8], ["SEPTEMBER", 8],
  ["OCT", 9], ["OCTOBER", 9],
  ["NOV", 10], ["NOVEMBER", 10],
  ["DEC", 11], ["DECEMBER", 11]
]);

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const JUMP_LABELS = [
  [/flight|rail/i, "Flights"],
  [/hotel/i, "Hotel"],
  [/getting around|transit/i, "Transit"],
  [/food|dinner|eat/i, "Food"],
  [/show|jazz|music|concert/i, "Shows"],
  [/photo/i, "Photo"],
  [/moma/i, "MoMA"],
  [/park|run/i, "Run"],
  [/walk/i, "Walk"],
  [/suggest|shape|default/i, "Shape"],
  [/pack/i, "Pack"]
];

export function looksLikeExperience(filename, rawText) {
  if (/\.md$/i.test(filename || "")) return true;
  const text = String(rawText || "").trim();
  if (/TRAVEL\s*&\s*EVENTS\s+OVERVIEW/i.test(text)) return false;
  return /^#\s+\S/.test(text);
}

export function parseExperienceGuide(filename, rawText) {
  const text = String(rawText || "").replace(/\r\n?/g, "\n").trim();
  if (!text) throw new Error(`${filename} is empty.`);

  const lines = text.split("\n");
  const titleLine = lines.find((line) => /^#\s+\S/.test(line.trim())) || "";
  const parsed = parseGuideTitleLine(titleLine.replace(/^#\s+/, "").trim());
  if (!parsed.startDate || !parsed.endDate) {
    throw new Error(`${filename} needs a title like "# New York — 16–20 Sep 2026".`);
  }

  const chapters = groupChapters(parseMarkdownBlocks(text), parsed);
  const subtitle = firstProse(chapters[0]) || "";

  const title = parsed.title || filename.replace(/\.[^.]+$/, "");
  return {
    id: guideIdFromFilename(filename),
    title,
    place: placeHint(title),
    subtitle,
    startDate: parsed.startDate,
    endDate: parsed.endDate,
    rawMarkdown: text,
    chapters,
    parsedAt: new Date().toISOString()
  };
}

export function guidesForRange(guides, startDate, endDate) {
  if (!startDate || !endDate) return [];
  return (guides || []).filter((guide) => guide.startDate <= endDate && startDate <= guide.endDate);
}

export function guidesForMonth(guides, monthId) {
  const bounds = monthBounds(monthId);
  return bounds ? guidesForRange(guides, bounds.startDate, bounds.endDate) : [];
}

export function bestGuideForSection(section, guides) {
  const matches = guidesForRange(guides, section?.startDate, section?.endDate);
  return matches.sort((left, right) => daySpan(left) - daySpan(right) || left.title.localeCompare(right.title))[0] || null;
}

export function jumpChapters(guide) {
  return (guide?.chapters || []).filter((chapter) => chapter.kind !== "logistics" && chapter.heading);
}

export function dayChips(guide) {
  if (!guide?.startDate || !guide?.endDate) return [];
  const chips = [];
  let cursor = guide.startDate;
  while (cursor <= guide.endDate) {
    const date = dateFromIso(cursor);
    chips.push({
      iso: cursor,
      label: WEEKDAYS[date.getUTCDay()],
      day: String(date.getUTCDate())
    });
    cursor = addDays(cursor, 1);
    if (chips.length > 21) break;
  }
  return chips;
}

export function renderExperienceNav(guide, { activeDay = "", guideCount = 1 } = {}) {
  const jumps = jumpChapters(guide);
  const days = dayChips(guide);
  const jumpHtml = jumps.length
    ? `<div class="xp-jumps" role="navigation" aria-label="Guide sections">${jumps.map((chapter) => (
      `<button type="button" class="xp-jump" data-xp-jump="${escapeAttr(chapter.id)}">${escapeHtml(jumpLabel(chapter.heading))}</button>`
    )).join("")}</div>`
    : "";
  const dayHtml = days.length > 1
    ? `<div class="xp-days" role="navigation" aria-label="Days in this guide">${days.map((day) => (
      `<button type="button" class="xp-day${day.iso === activeDay ? " is-active" : ""}" data-xp-day="${escapeAttr(day.iso)}"><span>${escapeHtml(day.label)}</span><strong>${escapeHtml(day.day)}</strong></button>`
    )).join("")}</div>`
    : "";
  const switcher = guideCount > 1
    ? `<p class="xp-switch-hint">${guideCount} guides this month</p>`
    : "";
  return `${switcher}${dayHtml}${jumpHtml}`;
}

export function renderExperienceBody(guide) {
  const place = guide?.place || placeHint(guide?.title);
  const chapters = (guide?.chapters || []).filter((chapter) => chapter.heading || chapter.blocks.length);
  return chapters.map((chapter) => {
    const context = { place, kind: chapter.kind, heading: chapter.heading || "" };
    if (!chapter.heading) {
      return chapter.blocks.length
        ? `<div class="xp-lede-block">${chapter.blocks.map((block) => blockHtml(block, context)).join("")}</div>`
        : "";
    }
    const heading = `<h3 class="xp-h2" id="${escapeAttr(chapter.id)}">${formatInline(chapter.heading, { ...context, role: "heading" })}</h3>`;
    return `<section class="xp-chapter is-${escapeAttr(chapter.kind)}" aria-labelledby="${escapeAttr(chapter.id)}">
      ${heading}
      ${chapter.blocks.map((block) => blockHtml(block, context)).join("")}
    </section>`;
  }).join("");
}

export function formatGuideDates(guide) {
  if (!guide?.startDate) return "";
  if (guide.startDate === guide.endDate) return formatLongDate(guide.startDate);
  return `${formatLongDate(guide.startDate)} – ${formatLongDate(guide.endDate)}`;
}

function parseGuideTitleLine(line) {
  const text = String(line || "").trim();
  const split = text.search(/\s+[—–-]\s+(?=\d{1,2}\b)/);
  const title = split === -1 ? text : text.slice(0, split).trim();
  const dateText = split === -1 ? text : text.slice(split).replace(/^[—–\s-]+/, "");
  return { title, ...parseDatesFromText(dateText) };
}

function parseDatesFromText(text) {
  const cross = String(text || "").match(
    /(\d{1,2})\s+([A-Za-z]{3,9})\s*[–-]\s*(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})/i
  );
  if (cross) {
    const startMonth = MONTHS.get(cross[2].toUpperCase());
    const endMonth = MONTHS.get(cross[4].toUpperCase());
    const year = Number(cross[5]);
    if (startMonth !== undefined && endMonth !== undefined) {
      return {
        startDate: isoDate(year, startMonth, Number(cross[1])),
        endDate: isoDate(endMonth < startMonth ? year + 1 : year, endMonth, Number(cross[3]))
      };
    }
  }

  const same = String(text || "").match(/(\d{1,2})(?:\s*[–-]\s*(\d{1,2}))?\s+([A-Za-z]{3,9})\s+(\d{4})/i);
  if (!same) return { startDate: "", endDate: "" };
  const month = MONTHS.get(same[3].toUpperCase());
  if (month === undefined) return { startDate: "", endDate: "" };
  const year = Number(same[4]);
  const startDay = Number(same[1]);
  const endDay = same[2] ? Number(same[2]) : startDay;
  return {
    startDate: isoDate(year, month, startDay),
    endDate: isoDate(year, month, endDay)
  };
}

function parseMarkdownBlocks(text) {
  const lines = String(text || "").split("\n");
  const blocks = [];
  let index = 0;

  while (index < lines.length) {
    const trimmed = lines[index].trim();
    if (!trimmed) {
      index += 1;
      continue;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      blocks.push({
        type: "heading",
        level: heading[1].length,
        text: heading[2].trim(),
        id: slugify(heading[2])
      });
      index += 1;
      continue;
    }

    if (isTableRow(trimmed) && lines.slice(index + 1, index + 3).some((line) => isTableRow(line.trim()))) {
      const table = takeTable(lines, index);
      blocks.push(table.block);
      index = table.next;
      continue;
    }

    if (isBullet(trimmed)) {
      const items = [];
      while (index < lines.length && isBullet(lines[index].trim())) {
        let text = lines[index].trim().replace(/^[-*+]\s+/, "");
        index += 1;
        while (index < lines.length && isBulletContinue(lines[index])) {
          text = `${text} ${lines[index].trim()}`.replace(/\s+/g, " ");
          index += 1;
        }
        items.push(text);
      }
      blocks.push({ type: "bullets", items });
      continue;
    }

    if (/^\*\*[^*]+\*\*$/.test(trimmed)) {
      const inner = trimmed.slice(2, -2);
      blocks.push(isSectionLabel(inner)
        ? { type: "label", text: inner }
        : { type: "prose", text: trimmed });
      index += 1;
      continue;
    }

    const prose = [];
    while (index < lines.length) {
      const current = lines[index].trim();
      if (!current || current.startsWith("#") || isBullet(current) || isTableRow(current) || /^\*\*[^*]+\*\*$/.test(current)) break;
      prose.push(current);
      index += 1;
    }
    if (prose.length) blocks.push({ type: "prose", text: prose.join(" ") });
  }

  return blocks;
}

function groupChapters(blocks, guideDates) {
  const chapters = [];
  let current = { id: "", heading: "", kind: "lede", blocks: [] };

  const push = () => {
    if (current.heading || current.blocks.length) chapters.push(current);
  };

  for (const block of blocks) {
    if (block.type === "heading" && block.level === 1) continue;
    if (block.type === "heading" && block.level === 2) {
      push();
      current = {
        id: block.id,
        heading: block.text,
        kind: chapterKind(block.text),
        blocks: []
      };
      continue;
    }
    if (block.type === "heading" && block.level >= 3) {
      current.blocks.push({ type: "label", text: block.text, id: block.id });
      continue;
    }
    current.blocks.push(annotateDays(block, guideDates, current.kind));
  }
  push();
  return chapters;
}

function annotateDays(block, guideDates, kind) {
  if (block.type !== "bullets") return block;
  const seen = new Set();
  return {
    ...block,
    items: block.items.map((item) => {
      const iso = kind === "shape" ? resolveDayIso(item, guideDates) : "";
      const dayIso = iso && !seen.has(iso) ? iso : "";
      if (dayIso) seen.add(dayIso);
      return { text: item, dayIso };
    })
  };
}

function chapterKind(heading) {
  if (/flight|rail|hotel|getting around|packing|walking distance/i.test(heading)) return "logistics";
  if (/suggested|default if nothing/i.test(heading)) return "shape";
  return "experience";
}

function jumpLabel(heading) {
  for (const [pattern, label] of JUMP_LABELS) {
    if (pattern.test(heading)) return label;
  }
  return heading.split(/[—:(]/)[0].trim().slice(0, 14);
}

function firstProse(chapter) {
  return chapter?.blocks?.find((block) => block.type === "prose")?.text || "";
}

function takeTable(lines, start) {
  const rows = [];
  let index = start;
  while (index < lines.length && isTableRow(lines[index].trim())) {
    const cells = splitCells(lines[index]);
    if (!isSeparatorCells(cells)) rows.push(cells);
    index += 1;
  }
  const headers = rows.shift() || [];
  return {
    next: index,
    block: { type: "table", headers, rows }
  };
}

function isTableRow(trimmed) {
  return /^\|(.+)\|$/.test(trimmed);
}

function isSeparatorCells(cells) {
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.replace(/\s/g, "")));
}

function splitCells(line) {
  return line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
}

function isBullet(trimmed) {
  return /^[-*+]\s+\S/.test(trimmed);
}

function isBulletContinue(raw) {
  if (!raw || !String(raw).trim()) return false;
  if (!/^\s{2,}\S/.test(raw)) return false;
  const trimmed = raw.trim();
  return !isBullet(trimmed) && !trimmed.startsWith("#") && !isTableRow(trimmed);
}

function blockHtml(block, context = {}) {
  switch (block.type) {
    case "prose":
      return `<p class="xp-prose">${formatInline(block.text, context)}</p>`;
    case "label":
      return `<h4 class="xp-h3"${block.id ? ` id="${escapeAttr(block.id)}"` : ""}>${formatInline(block.text, { ...context, role: "text" })}</h4>`;
    case "bullets":
      return `<ul class="xp-list">${block.items.map((item) => {
        const text = typeof item === "string" ? item : item.text;
        const dayIso = typeof item === "string" ? "" : item.dayIso;
        const id = dayIso ? ` id="xp-day-${escapeAttr(dayIso)}"` : "";
        return `<li${id}>${formatInline(text, context)}</li>`;
      }).join("")}</ul>`;
    case "table":
      return tableHtml(block, context);
    default:
      return "";
  }
}

function tableHtml(block, context = {}) {
  const rows = (block.rows || []).map((row) => (Array.isArray(row) ? { cells: row, dayIso: "" } : row));
  if ((block.headers || []).length <= 2) {
    return `<dl class="xp-kv">${rows.map((row) => `
      <div${row.dayIso ? ` id="xp-day-${escapeAttr(row.dayIso)}"` : ""}>
        <dt>${formatInline(row.cells[0] || "", { ...context, role: "poi" })}</dt>
        <dd>${formatInline(row.cells[1] || "", context)}</dd>
      </div>`).join("")}</dl>`;
  }

  return `<div class="xp-cards">${rows.map((row) => {
    const [kicker, title, ...rest] = row.cells;
    const notes = rest.filter(Boolean).join(" · ");
    return `<article class="xp-card"${row.dayIso ? ` id="xp-day-${escapeAttr(row.dayIso)}"` : ""}>
      <p class="xp-card-kicker">${escapeHtml(kicker || "")}${title ? ` · ${formatInline(title, { ...context, role: "venue" })}` : ""}</p>
      ${rest[0] ? `<p class="xp-card-title">${formatInline(rest[0], { ...context, role: "text" })}</p>` : ""}
      ${notes && rest.length > 1 ? `<p class="xp-card-note">${formatInline(rest.slice(1).join(" · "), { ...context, role: "text" })}</p>` : ""}
    </article>`;
  }).join("")}</div>`;
}

function formatInline(value, context = {}) {
  const src = String(value ?? "");
  if ((context.role === "poi" || context.role === "venue" || context.role === "heading") && !/\*\*|\[/.test(src) && shouldLinkPoi(src, context)) {
    return mapsAnchor(escapeHtml(src), poiQuery(src, peekAddress(src), context.place));
  }
  const parts = [];
  let index = 0;

  while (index < src.length) {
    if (src.startsWith("**", index)) {
      const end = src.indexOf("**", index + 2);
      if (end !== -1) {
        const name = src.slice(index + 2, end);
        const after = src.slice(end + 2);
        const address = peekAddress(after);
        if (shouldLinkPoi(name, { ...context, address })) {
          parts.push(mapsAnchor(`<strong>${formatInline(name, { ...context, role: "text" })}</strong>`, poiQuery(name, address, context.place)));
        } else {
          parts.push(`<strong>${formatInline(name, { ...context, role: "text" })}</strong>`);
        }
        index = end + 2;
        continue;
      }
    }
    if (src[index] === "*" && src[index + 1] !== "*") {
      const end = src.indexOf("*", index + 1);
      if (end !== -1 && end > index + 1) {
        parts.push(`<em>${escapeHtml(src.slice(index + 1, end))}</em>`);
        index = end + 1;
        continue;
      }
    }
    if (src[index] === "`") {
      const end = src.indexOf("`", index + 1);
      if (end !== -1) {
        parts.push(`<code>${escapeHtml(src.slice(index + 1, end))}</code>`);
        index = end + 1;
        continue;
      }
    }
    const link = src.slice(index).match(/^\[([^\]]+)\]\((https?:[^)\s]+)\)/);
    if (link) {
      parts.push(`<a href="${escapeAttr(link[2])}" target="_blank" rel="noopener noreferrer">${escapeHtml(link[1])}</a>`);
      index += link[0].length;
      continue;
    }
    const auto = src.slice(index).match(/^https?:\/\/[^\s)]+/);
    if (auto) {
      parts.push(`<a href="${escapeAttr(auto[0])}" target="_blank" rel="noopener noreferrer">${escapeHtml(shortLinkLabel(auto[0]))}</a>`);
      index += auto[0].length;
      continue;
    }

    let next = index + 1;
    while (next < src.length && !"*`[".includes(src[next]) && !src.startsWith("http", next)) next += 1;
    parts.push(linkAddresses(src.slice(index, next), context.place));
    index = next;
  }

  return parts.join("");
}

function placeHint(title) {
  return String(title || "")
    .split(/[—–,]/)[0]
    .trim()
    .replace(/\s+(weekday|weekend|evening|mornings?|nights?|days?|must see)\b.*/i, "")
    .trim();
}

function mapsSearchUrl(query) {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function mapsAnchor(labelHtml, query) {
  return `<a class="xp-map" href="${escapeAttr(mapsSearchUrl(query))}" target="_blank" rel="noopener noreferrer">${labelHtml}</a>`;
}

function poiQuery(name, address, place) {
  const cleanName = String(name || "").replace(/\s*\((hotel|walk)\)\s*/ig, " ").replace(/\s+/g, " ").trim();
  return [cleanName, address, place].filter(Boolean).join(", ");
}

function peekAddress(after) {
  const trimmed = String(after || "").replace(/^\s*[—–-]\s*/, " ").replace(/^[:(]\s*/, " ");
  const match = matchAddress(trimmed);
  return match && match.index <= 2 ? match[0].replace(/[.,;:]+$/, "") : "";
}

function matchAddress(text) {
  const patterns = [
    /\d{1,5}\s+(?:West|East|North|South|W|E|N|S)\.?\s+\d+(?:st|nd|rd|th)?(?:\s+(?:Street|St|Ave|Avenue))?(?:\s*,\s*(?:NY|NJ|PA|NYC)\s*\d{5})?/,
    /\d{1,5}\s+[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)?\s+(?:Street|St|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Way|Plaza|Pl|Broadway)(?:\s+at\s+\d+(?:st|nd|rd|th)?)?(?:\s*,\s*(?:NY|NJ|PA|NYC)\s*\d{5})?/
  ];
  let best = null;
  for (const pattern of patterns) {
    const match = String(text || "").match(pattern);
    if (match && (best === null || match.index < best.index)) best = match;
  }
  return best;
}

function linkAddresses(text, place) {
  const src = String(text || "");
  const hits = [];
  const patterns = [
    /\d{1,5}\s+(?:West|East|North|South|W|E|N|S)\.?\s+\d+(?:st|nd|rd|th)?(?:\s+(?:Street|St|Ave|Avenue))?(?:\s*,\s*(?:NY|NJ|PA|NYC)\s*\d{5})?/g,
    /\d{1,5}\s+[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)?\s+(?:Street|St|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Way|Plaza|Pl|Broadway)(?:\s+at\s+\d+(?:st|nd|rd|th)?)?(?:\s*,\s*(?:NY|NJ|PA|NYC)\s*\d{5})?/g
  ];
  for (const pattern of patterns) {
    let match = pattern.exec(src);
    while (match) {
      hits.push({ start: match.index, end: match.index + match[0].length, text: match[0] });
      match = pattern.exec(src);
    }
  }
  hits.sort((left, right) => left.start - right.start || right.end - left.end);
  const kept = [];
  for (const hit of hits) {
    if (kept.some((item) => hit.start < item.end && item.start < hit.end)) continue;
    kept.push(hit);
  }
  let last = 0;
  let html = "";
  for (const hit of kept) {
    html += escapeHtml(src.slice(last, hit.start));
    html += mapsAnchor(escapeHtml(hit.text), poiQuery("", hit.text, place));
    last = hit.end;
  }
  return html + escapeHtml(src.slice(last));
}

function shouldLinkPoi(name, context = {}) {
  const text = String(name || "").trim();
  if (text.length < 3 || text.length > 48 || context.role === "text") return false;
  if (/[→:]/.test(text) && !context.address) return false;
  if (/\.$/.test(text) || /min walk|minutes/i.test(text)) return false;
  if (/^(purchased|paid|confirmed|tbc|cancelled|terminal\s*\d|not a short walk|opens to the public|on view|friday until|best single|upper loop)/i.test(text)) return false;
  if (/^(mon|tue|wed|thu|fri|sat|sun)\b/i.test(text)) return false;
  if (/^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b/i.test(text)) return false;
  if (/^[A-Z](?:\/[A-Z]){1,4}$/.test(text) || /^\d+\/\d+/.test(text)) return false;
  if (context.role === "poi" || context.role === "venue") return true;
  if (context.address) return true;
  if (context.role === "heading") return /moma|met\b|guggenheim|central park|aperture/i.test(text);
  if (isVenueName(text)) return true;
  const heading = `${context.heading || ""} ${context.kind || ""}`;
  if (/hotel|food|walk/i.test(heading)) return true;
  if (/photo|moma|park/i.test(heading) && !isPersonName(text)) return true;
  if (/show|jazz/i.test(heading)) {
    if (/\b(trio|quartet|quintet|band|orchestra|all-stars)\b/i.test(text)) return false;
    return isVenueName(text) || text.split(/\s+/).length >= 3;
  }
  return false;
}

function isSectionLabel(text) {
  return /^(on view|walk \/|walk from|openings on|other photo|jazz clubs|mid-size rooms|default if nothing)/i.test(text)
    || (text.length < 20 && !/[A-Z][a-z]+\s+[A-Z]/.test(text));
}

function isVenueName(name) {
  return /\b(hotel|restaurant|museum|theater|theatre|gallery|club|hall|pub|bar|cafe|café|kitchen|grill|tavern|diner|winery|studio|moma|guggenheim|aperture|met|icp|apollo|vanguard|birdland|iridium|rooster|victoria|note)\b/i.test(name);
}

function isPersonName(name) {
  if (isVenueName(name)) return false;
  if (/\b(trio|quartet|quintet|band|orchestra|all-stars)\b/i.test(name)) return true;
  return /^[A-Z][A-Za-z.'-]+\s+[A-Z][A-Za-z.'-]+$/.test(name);
}

function resolveDayIso(text, guideDates) {
  const match = String(text || "").match(/\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2})\b/i);
  if (!match || !guideDates?.startDate) return "";
  const day = Number(match[1]);
  const start = dateFromIso(guideDates.startDate);
  const first = isoDate(start.getUTCFullYear(), start.getUTCMonth(), day);
  if (first >= guideDates.startDate && first <= guideDates.endDate) return first;
  const end = dateFromIso(guideDates.endDate);
  const second = isoDate(end.getUTCFullYear(), end.getUTCMonth(), day);
  if (second >= guideDates.startDate && second <= guideDates.endDate) return second;
  return "";
}

function guideIdFromFilename(filename) {
  const slug = String(filename || "")
    .replace(/\.[^.]+$/, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "guide";
}

function monthBounds(monthId) {
  const match = String(monthId || "").match(/^(\d{4})-(\d{2})$/);
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  return {
    startDate: `${monthId}-01`,
    endDate: isoDate(year, month, 0)
  };
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48) || "section";
}

function daySpan(guide) {
  return Math.round((dateFromIso(guide.endDate) - dateFromIso(guide.startDate)) / 86400000);
}

function formatLongDate(iso) {
  return dateFromIso(iso).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC"
  });
}

function addDays(iso, days) {
  const date = dateFromIso(iso);
  date.setUTCDate(date.getUTCDate() + days);
  return isoFromDate(date);
}

function isoDate(year, monthIndex, day) {
  return isoFromDate(new Date(Date.UTC(year, monthIndex, day)));
}

function dateFromIso(iso) {
  const [year, month, day] = String(iso).split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function isoFromDate(date) {
  return `${date.getUTCFullYear()}-${pad2(date.getUTCMonth() + 1)}-${pad2(date.getUTCDate())}`;
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

function shortLinkLabel(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
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
  return escapeHtml(value);
}

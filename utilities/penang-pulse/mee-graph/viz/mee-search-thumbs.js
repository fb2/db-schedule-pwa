/* Live card thumbnails for Mee-Search (and the viz gallery).
   Cheap animated previews of views 02–05. Depends on d3; Origin Drill also
   needs a loaded MEE graph (pass g from MEE.load()). */
(function (global) {
  "use strict";

  function reducedMotion() {
    return (
      (global.MEE && typeof MEE.reducedMotion === "function" && MEE.reducedMotion()) ||
      (global.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches)
    );
  }

  function keepWarm(sim) {
    if (reducedMotion()) return;
    d3.interval(() => sim.alpha(0.09).restart(), 4200);
  }

  function thumbSunburst(svg, g) {
    const root = svg.append("g").attr("transform", "translate(150,79)");
    const data = {
      children: g.byType.culture.slice(0, 8).map((c) => ({
        colour: c.colour,
        children: g.neighbours(c.id, ["carried_by"], "in").slice(0, 4).map(() => ({ value: 1 })),
      })),
    };
    const h = d3.hierarchy(data).sum((d) => d.value || 0);
    d3.partition().size([2 * Math.PI, 66])(h);
    const arc = d3
      .arc()
      .startAngle((d) => d.x0)
      .endAngle((d) => d.x1)
      .innerRadius((d) => d.y0 + 14)
      .outerRadius((d) => d.y1 + 12)
      .padAngle(0.012);
    root
      .selectAll("path")
      .data(h.descendants().filter((d) => d.depth))
      .enter()
      .append("path")
      .attr("d", arc)
      .attr("fill", (d) => {
        let p = d;
        while (p.depth > 1) p = p.parent;
        return d3
          .color(p.data.colour)
          .brighter((d.depth - 1) * 0.4)
          .formatHex();
      })
      .attr("stroke", "#fdfdfb")
      .attr("stroke-width", 0.7);
    if (reducedMotion()) return;
    let a = 0;
    d3.timer((el) => {
      a = (el / 90) % 360;
      root.attr("transform", "translate(150,79) rotate(" + a + ")");
    });
  }

  function thumbFlow(svg) {
    const colsX = [26, 108, 190, 268];
    const bands = [];
    const pal = ["#c2603a", "#6f9455", "#8d6ca8", "#0f6e6e", "#b06a8a"];
    for (let i = 0; i < 5; i++) {
      for (let c = 0; c < 3; c++) {
        bands.push({
          x0: colsX[c] + 8,
          x1: colsX[c + 1],
          y0: 22 + i * 24 + c * 3,
          y1: 22 + ((i + c) % 5) * 24 + 4,
          h: 7,
          colour: pal[i],
        });
      }
    }
    svg
      .append("g")
      .selectAll("path")
      .data(bands)
      .enter()
      .append("path")
      .attr("d", (d) => {
        const cx = (d.x0 + d.x1) / 2;
        return (
          "M" +
          d.x0 +
          "," +
          d.y0 +
          "C" +
          cx +
          "," +
          d.y0 +
          " " +
          cx +
          "," +
          d.y1 +
          " " +
          d.x1 +
          "," +
          d.y1 +
          "L" +
          d.x1 +
          "," +
          (d.y1 + d.h) +
          "C" +
          cx +
          "," +
          (d.y1 + d.h) +
          " " +
          cx +
          "," +
          (d.y0 + d.h) +
          " " +
          d.x0 +
          "," +
          (d.y0 + d.h) +
          "Z"
        );
      })
      .attr("fill", (d) => d.colour)
      .attr("fill-opacity", 0.2);
    for (const x of colsX) {
      svg
        .append("rect")
        .attr("x", x)
        .attr("y", 18)
        .attr("width", 7)
        .attr("height", 122)
        .attr("fill", "#1c1c1a")
        .attr("fill-opacity", 0.5)
        .attr("rx", 2);
    }
    const dots = svg
      .append("g")
      .selectAll("circle")
      .data(bands.flatMap((b) => [
        { b, t: Math.random() },
        { b, t: Math.random() },
      ]))
      .enter()
      .append("circle")
      .attr("r", 1.7)
      .attr("fill", (d) => d.b.colour);
    const place = () => {
      dots
        .attr("cx", (d) => d.b.x0 + (d.b.x1 - d.b.x0) * d.t)
        .attr("cy", (d) => {
          const mt = 1 - d.t;
          return (
            mt * mt * mt * d.b.y0 +
            3 * mt * mt * d.t * d.b.y0 +
            3 * mt * d.t * d.t * d.b.y1 +
            d.t * d.t * d.t * d.b.y1 +
            d.b.h / 2
          );
        });
    };
    place();
    if (reducedMotion()) return;
    d3.timer(() => {
      dots.each((d) => {
        d.t = (d.t + 0.006) % 1;
      });
      place();
    });
  }

  function thumbOrbit(svg) {
    const root = svg.append("g").attr("transform", "translate(150,79)");
    const rings = [26, 46, 64];
    for (const r of rings) {
      root
        .append("circle")
        .attr("r", r)
        .attr("fill", "none")
        .attr("stroke", "#e6e6e2")
        .attr("stroke-dasharray", "2 4");
    }
    root.append("circle").attr("r", 17).attr("fill", "#fff").attr("stroke", "#b8352f").attr("stroke-width", 2);
    const pal = ["#c2603a", "#6f9455", "#8d6ca8", "#0f6e6e", "#d4a13b", "#b06a8a"];
    const sats = [];
    rings.forEach((rad, ri) => {
      const n = ri === 1 ? 7 : 4;
      for (let i = 0; i < n; i++) {
        sats.push({
          rad,
          a0: (i / n) * Math.PI * 2 + ri,
          spd: (ri % 2 ? -1 : 1) * (0.5 + ri * 0.12),
          colour: pal[(i + ri) % pal.length],
          r: 3 + (ri === 1 ? 1.4 : 2),
        });
      }
    });
    const c = root
      .append("g")
      .selectAll("circle")
      .data(sats)
      .enter()
      .append("circle")
      .attr("r", (d) => d.r)
      .attr("fill", (d) => d.colour)
      .attr("fill-opacity", 0.9)
      .attr("stroke", "#fdfdfb")
      .attr("stroke-width", 0.8);
    const place = (el) => {
      const t = el || 0;
      c.attr("cx", (d) => Math.cos(d.a0 + (t / 1000) * d.spd) * d.rad).attr(
        "cy",
        (d) => Math.sin(d.a0 + (t / 1000) * d.spd) * d.rad
      );
    };
    place(0);
    if (reducedMotion()) return;
    d3.timer(place);
  }

  function thumbTimeline(svg) {
    const lanes = 7;
    for (let i = 0; i < lanes; i++) {
      svg
        .append("rect")
        .attr("x", 20 + i * 9)
        .attr("y", 20 + i * 13)
        .attr("width", 90 + i * 22)
        .attr("height", 8)
        .attr("rx", 3)
        .attr("fill", i > 4 ? "#8d6ca8" : "#8a6d3b")
        .attr("fill-opacity", 0.26);
    }
    svg
      .append("rect")
      .attr("x", 20)
      .attr("y", 122)
      .attr("width", 260)
      .attr("height", 24)
      .attr("rx", 5)
      .attr("fill", "#b8352f")
      .attr("fill-opacity", 0.05)
      .attr("stroke", "#b8352f")
      .attr("stroke-opacity", 0.25)
      .attr("stroke-dasharray", "3 3");
    for (let i = 0; i < 22; i++) {
      svg
        .append("circle")
        .attr("cx", 30 + (i % 11) * 24)
        .attr("cy", 130 + Math.floor(i / 11) * 10)
        .attr("r", 2.6)
        .attr("fill", "#b8352f")
        .attr("fill-opacity", 0.4);
    }
    const head = svg.append("line").attr("y1", 12).attr("y2", 118).attr("stroke", "#b8352f").attr("stroke-width", 1.6);
    const place = (t) => head.attr("x1", 20 + t * 260).attr("x2", 20 + t * 260);
    place(0.35);
    if (reducedMotion()) return;
    d3.timer((el) => place((el / 4200) % 1));
  }

  function thumbForce(svg, g) {
    const cultures = g.byType.culture.slice(0, 7);
    const nodes = cultures.map((c) => ({ id: c.id, colour: c.colour, r: 7, hub: true }));
    const links = [];
    let k = 0;
    for (const c of cultures) {
      for (const rel of g.neighbours(c.id, ["carried_by"], "in").slice(0, 3)) {
        const id = rel.node.id + "_" + k++;
        nodes.push({ id, colour: rel.node.colour, r: 3.2 });
        links.push({ source: c.id, target: id });
      }
    }
    const l = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#1c1c1a")
      .attr("stroke-opacity", 0.2);
    const n = svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d) => d.r)
      .attr("fill", (d) => d.colour)
      .attr("fill-opacity", 0.9);
    const sim = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d) => d.id).distance(22).strength(0.5))
      .force("charge", d3.forceManyBody().strength(-38))
      .force("x", d3.forceX(150).strength(0.09))
      .force("y", d3.forceY(79).strength(0.12))
      .force("collide", d3.forceCollide((d) => d.r + 1.5))
      .alphaDecay(0.006);
    sim.on("tick", () => {
      n.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
      l.attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
    });
    keepWarm(sim);
  }

  const KIND = {
    origin: thumbSunburst,
    flow: thumbFlow,
    orbit: thumbOrbit,
    timeline: thumbTimeline,
    force: thumbForce,
  };

  function mountInto(el, kind, g) {
    const fn = KIND[kind];
    if (!el || !fn) return;
    el.replaceChildren();
    const svg = d3.select(el).append("svg").attr("viewBox", "0 0 300 158");
    fn(svg, g);
  }

  /** Mount every [data-ms-thumb] under root. */
  function mountLanding(root, g) {
    const scope = root || document;
    scope.querySelectorAll("[data-ms-thumb]").forEach((el) => {
      mountInto(el, el.getAttribute("data-ms-thumb"), g);
    });
  }

  global.MEE_THUMBS = {
    mountInto,
    mountLanding,
    kinds: KIND,
    thumbSunburst,
    thumbFlow,
    thumbOrbit,
    thumbTimeline,
    thumbForce,
    keepWarm,
  };
})(typeof window !== "undefined" ? window : globalThis);

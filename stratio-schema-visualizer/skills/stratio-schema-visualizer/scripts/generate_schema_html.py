#!/usr/bin/env python3
"""
Stratio Schema Visualizer — ER-style diagram generator.

Produces a standalone HTML file where each table is rendered as a card
(header + column rows) and FK relationships are drawn as bezier arrows
connecting specific columns between tables.

Usage:
    python3 generate_schema_html.py --input /tmp/schema.json --output /tmp/schema.html
"""

import json
import argparse
from datetime import datetime


# ---------------------------------------------------------------------------
# Relationship inference
# ---------------------------------------------------------------------------

def infer_relationships(tables: list) -> list:
    """Infer FK relationships from column naming conventions.

    Handles:
      - <prefix>_id  →  table named exactly <prefix>
      - <prefix>_ref →  table whose last name segment is <prefix>  (e.g. fac_ref → tbl_fac)
    """
    exact_map = {t["name"].lower(): t["name"] for t in tables}
    suffix_map: dict = {}
    for t in tables:
        parts = t["name"].lower().split("_")
        if parts:
            suffix_map[parts[-1]] = t["name"]

    relationships = []
    seen: set = set()

    for table in tables:
        for col in table.get("columns", []):
            if col.get("is_primary_key"):
                continue
            col_lower = col["name"].lower()
            ref_table = None
            ref_col = None

            if col_lower.endswith("_id"):
                prefix = col_lower[:-3]
                if prefix in exact_map and exact_map[prefix] != table["name"]:
                    ref_table = exact_map[prefix]
                    ref_col = "id"

            if ref_table is None and col_lower.endswith("_ref"):
                prefix = col_lower[:-4]
                if prefix in suffix_map and suffix_map[prefix] != table["name"]:
                    ref_table = suffix_map[prefix]
                    ref_col = col["name"]

            if ref_table is None:
                continue

            key = (table["name"], col["name"], ref_table)
            if key in seen:
                continue
            seen.add(key)
            relationships.append({
                "from_table": table["name"],
                "from_column": col["name"],
                "to_table": ref_table,
                "to_column": ref_col,
                "inferred": True,
                "cardinality": "N:1",  # default assumption; skill overrides with real query
            })
    return relationships


def total_columns(tables: list) -> int:
    return sum(len(t.get("columns", [])) for t in tables)


# ---------------------------------------------------------------------------
# HTML template  (uses __PLACEHOLDER__ style to avoid f-string brace conflicts)
# ---------------------------------------------------------------------------

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stratio Schema · __DOMAIN__</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #0d1117;
  --surface:  #161b22;
  --surface2: #1c2128;
  --border:   #30363d;
  --border2:  #484f58;
  --text:     #e6edf3;
  --text2:    #8b949e;
  --text3:    #656d76;
  --accent:   #58a6ff;
  --accent2:  #388bfd;
  --warn:     #e3b341;
  --green:    #3fb950;
  --pk:       #f0883e;
  --fk-hi:    rgba(227,179,65,.10);
}

html, body { height: 100%; overflow: hidden; background: var(--bg); color: var(--text); }
body {
  display: flex; flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

/* ── Header ── */
header {
  height: 50px; flex-shrink: 0;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center;
  padding: 0 18px; gap: 12px;
  z-index: 20;
}
.logo { display: flex; align-items: center; gap: 7px; }
.logo-mark {
  width: 26px; height: 26px; border-radius: 6px;
  background: linear-gradient(135deg,#1a4fa0,#0969da);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px;
}
.logo-text { font-size: 15px; font-weight: 700; letter-spacing: -.3px; }
.logo-text em { color: var(--accent); font-style: normal; }
.domain-chip {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 20px; padding: 3px 12px;
  font-size: 12px; color: var(--text2);
  font-family: 'SFMono-Regular', Consolas, monospace;
}
.hstats { margin-left: auto; display: flex; gap: 14px; align-items: center; }
.hstat  { font-size: 12px; color: var(--text3); }
.hstat b { color: var(--text); }
.sep { width: 1px; height: 20px; background: var(--border); }
.hbtn {
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--text2); padding: 4px 10px; border-radius: 6px;
  font-size: 11px; cursor: pointer; font-family: inherit;
  transition: background .12s, color .12s;
}
.hbtn:hover { background: var(--border2); color: var(--text); }

/* ── Canvas wrap ── */
#wrap {
  flex: 1; overflow: auto; position: relative;
  background-color: var(--bg);
  background-image:
    linear-gradient(var(--surface2) 1px, transparent 1px),
    linear-gradient(90deg, var(--surface2) 1px, transparent 1px);
  background-size: 28px 28px;
  background-position: -1px -1px;
}

/* ── Canvas (coordinate space) ── */
#canvas { position: relative; }

/* ── SVG overlay ── */
#svg-layer {
  position: absolute; top: 0; left: 0;
  pointer-events: none; overflow: visible;
}
/* Make paths hoverable */
.rel-hit  { pointer-events: stroke; cursor: crosshair; }
.rel-path { pointer-events: none; }

/* ── Table cards ── */
.tcard {
  position: absolute;
  width: 240px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,.45), 0 1px 3px rgba(0,0,0,.3);
  z-index: 1;
  user-select: none;
  transition: box-shadow .15s;
}
.tcard:hover {
  box-shadow: 0 6px 28px rgba(0,0,0,.55), 0 0 0 1px var(--border2);
}
.tcard.dragging {
  z-index: 50;
  box-shadow: 0 16px 48px rgba(0,0,0,.65), 0 0 0 1.5px var(--accent2);
}

/* Card header */
.thead {
  height: 36px;
  background: linear-gradient(135deg, #192740, #1d3060);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center;
  padding: 0 10px; gap: 7px;
  cursor: grab;
}
.thead:active { cursor: grabbing; }
.thead-icon { font-size: 11px; color: var(--accent2); opacity: .7; flex-shrink: 0; }
.thead-name {
  flex: 1; min-width: 0;
  font-size: 11.5px; font-weight: 700;
  font-family: 'SFMono-Regular', Consolas, monospace;
  color: var(--accent2);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.thead-count {
  flex-shrink: 0;
  font-size: 9px; color: var(--text3);
  background: rgba(0,0,0,.3); border-radius: 8px;
  padding: 1px 5px;
}

/* Column rows */
.crow {
  height: 26px;
  display: flex; align-items: center;
  padding: 0 8px; gap: 5px;
  border-bottom: 1px solid rgba(48,54,61,.6);
  transition: background .1s;
  position: relative;
}
.crow:last-child { border-bottom: none; }
.crow:hover { background: var(--surface2); }
.crow.pk   { border-left: 2px solid var(--pk); padding-left: 6px; }
.crow.fk   { } /* FK col, normal style */
.crow.rel-hi { background: var(--fk-hi) !important; }
.crow.rel-hi .cname { color: var(--warn); }

.pk-lbl {
  width: 16px; flex-shrink: 0;
  font-size: 9px; font-weight: 700;
  color: var(--pk); text-align: center;
}
.fk-lbl {
  width: 16px; flex-shrink: 0;
  font-size: 9px; color: var(--text3); text-align: center;
}
.cname {
  flex: 1; min-width: 0;
  font-size: 11px;
  font-family: 'SFMono-Regular', Consolas, monospace;
  color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ctype {
  flex-shrink: 0;
  font-size: 9.5px;
  font-family: 'SFMono-Regular', Consolas, monospace;
  padding: 1px 5px; border-radius: 3px;
  background: rgba(0,0,0,.25);
}
.ctype.t-str  { color: #58a6ff; }
.ctype.t-int  { color: #3fb950; }
.ctype.t-flt  { color: #e3b341; }
.ctype.t-bool { color: #bc8cff; }
.ctype.t-date { color: #ff7b72; }
.ctype.t-unk  { color: var(--text3); }

/* ── Tooltip ── */
#tip {
  position: fixed; z-index: 1000;
  background: #1c2128; border: 1px solid var(--border2);
  border-radius: 6px; padding: 6px 10px;
  font-size: 11px; color: var(--text2);
  max-width: 220px; line-height: 1.45;
  pointer-events: none; display: none;
  box-shadow: 0 4px 14px rgba(0,0,0,.45);
}

/* ── Legend ── */
#legend {
  position: fixed; bottom: 16px; right: 16px; z-index: 15;
  background: rgba(22,27,34,.94);
  border: 1px solid var(--border);
  border-radius: 8px; padding: 10px 14px;
  font-size: 11px; backdrop-filter: blur(6px);
}
.leg-title {
  font-size: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: .5px;
  color: var(--text3); margin-bottom: 8px;
}
.leg-row { display: flex; align-items: center; gap: 8px; color: var(--text2); margin-bottom: 5px; }
.leg-row:last-child { margin-bottom: 0; }
.l-box  { width: 12px; height: 12px; border: 1.5px solid var(--accent); background: #192740; border-radius: 2px; flex-shrink: 0; }
.l-pk   { width: 12px; height: 12px; border-left: 2px solid var(--pk); background: var(--surface2); flex-shrink: 0; }
.l-line {
  width: 26px; height: 2px; flex-shrink: 0;
  background: repeating-linear-gradient(
    90deg, var(--warn) 0, var(--warn) 5px, transparent 5px, transparent 9px
  );
}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-mark">◈</div>
    <div class="logo-text">Stratio <em>Schema</em></div>
  </div>
  <div class="domain-chip">__DOMAIN__</div>
  <div class="hstats">
    <div class="hstat"><b>__TABLE_COUNT__</b> tables</div>
    <div class="hstat"><b>__COL_COUNT__</b> columns</div>
    <div class="hstat"><b>__REL_COUNT__</b> relationships</div>
    <div class="sep"></div>
    <button class="hbtn" onclick="resetLayout()">⟳ Reset</button>
    <button class="hbtn" onclick="fitView()">⊞ Fit</button>
  </div>
</header>

<div id="wrap">
  <div id="canvas">
    <svg id="svg-layer"></svg>
  </div>
</div>

<div id="legend">
  <div class="leg-title">Legend</div>
  <div class="leg-row"><div class="l-box"></div> Table</div>
  <div class="leg-row"><div class="l-pk"></div> Primary key</div>
  <div class="leg-row"><div class="l-line"></div> Inferred FK</div>
</div>

<div id="tip"></div>

<script>
const DATA   = __DATA_JSON__;
const CARD_W = 240;
const HEAD_H = 36;
const ROW_H  = 26;
const COLS   = 3;      // tables per row in initial layout
const H_GAP  = 100;
const V_GAP  = 60;
const PAD    = 70;

const canvas = document.getElementById('canvas');
const svg    = document.getElementById('svg-layer');
const wrap   = document.getElementById('wrap');
const tip    = document.getElementById('tip');
const NS     = 'http://www.w3.org/2000/svg';

/* ── Lookup structures ── */
const byName = {};
const colIdx = {};   // colIdx[table][col] = row index
const fkCols = {};   // fkCols[table] = Set of FK column names

DATA.tables.forEach(t => {
  byName[t.name] = t;
  colIdx[t.name] = {};
  fkCols[t.name] = new Set();
  t.columns.forEach((c, i) => { colIdx[t.name][c.name] = i; });
});
DATA.relationships.forEach(r => {
  if (fkCols[r.from_table]) fkCols[r.from_table].add(r.from_column);
});

/* ── Positions ── */
const pos = {};   // pos[name] = {x, y}

function cardH(t) { return HEAD_H + t.columns.length * ROW_H; }

function computeLayout() {
  const rowMaxH = {};
  DATA.tables.forEach((t, i) => {
    const r = Math.floor(i / COLS);
    rowMaxH[r] = Math.max(rowMaxH[r] || 0, cardH(t));
  });
  let cumY = PAD;
  const rowY = {};
  Object.keys(rowMaxH).sort((a, b) => +a - +b).forEach(r => {
    rowY[+r] = cumY;
    cumY += rowMaxH[+r] + V_GAP;
  });
  DATA.tables.forEach((t, i) => {
    const c = i % COLS, r = Math.floor(i / COLS);
    pos[t.name] = { x: PAD + c * (CARD_W + H_GAP), y: rowY[r] };
  });
  const nCols = Math.min(DATA.tables.length, COLS);
  const W = PAD + nCols * (CARD_W + H_GAP) + PAD;
  const H = cumY + PAD;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';
  svg.setAttribute('width',  W);
  svg.setAttribute('height', H);
}

/* ── Render cards ── */
function renderCards() {
  canvas.querySelectorAll('.tcard').forEach(e => e.remove());
  DATA.tables.forEach(t => {
    const p = pos[t.name];
    const card = el('div', { class: 'tcard', id: 'card-' + t.name });
    card.style.left = p.x + 'px';
    card.style.top  = p.y + 'px';

    /* header */
    const hdr = el('div', { class: 'thead', title: t.description || t.name });
    hdr.innerHTML = `<span class="thead-icon">⬡</span>
      <span class="thead-name">${esc(t.name)}</span>
      <span class="thead-count">${t.columns.length}</span>`;
    card.appendChild(hdr);

    /* columns */
    t.columns.forEach(c => {
      const isFk = fkCols[t.name].has(c.name);
      const isPk = !!c.is_primary_key;
      const row = el('div', {
        class: 'crow' + (isPk ? ' pk' : '') + (isFk ? ' fk' : ''),
        id: `R__${t.name}__${c.name}`,
      });
      const tc  = typeClass(c.type);
      row.innerHTML = `
        ${isPk ? '<span class="pk-lbl">PK</span>' : (isFk ? '<span class="fk-lbl">FK</span>' : '<span class="fk-lbl"></span>')}
        <span class="cname">${esc(c.name)}</span>
        <span class="ctype ${tc}">${esc((c.type || '').toUpperCase())}</span>`;
      if (c.description) attachTooltip(row, c.description);
      card.appendChild(row);
    });

    canvas.appendChild(card);
    makeDraggable(card, hdr, t.name);
  });
}

/* ── Type class ── */
function typeClass(t) {
  const b = (t || '').toLowerCase().split(/[(< ]/)[0];
  if (['string','varchar','char','text','clob'].includes(b))             return 't-str';
  if (['int','integer','long','bigint','smallint','tinyint'].includes(b)) return 't-int';
  if (['float','double','decimal','numeric','real'].includes(b))          return 't-flt';
  if (['boolean','bool'].includes(b))                                     return 't-bool';
  if (['date','timestamp','datetime','time'].includes(b))                 return 't-date';
  return 't-unk';
}

/* ── Tooltip ── */
function attachTooltip(rowEl, text) {
  rowEl.addEventListener('mouseenter', e => { tip.textContent = text; tip.style.display = 'block'; moveTooltip(e); });
  rowEl.addEventListener('mousemove',  moveTooltip);
  rowEl.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
}
function moveTooltip(e) {
  const x = Math.min(e.clientX + 14, window.innerWidth - 240);
  tip.style.left = x + 'px';
  tip.style.top  = (e.clientY - 8) + 'px';
}

/* ── Dragging ── */
function makeDraggable(card, handle, name) {
  let drag = false, ox = 0, oy = 0;
  handle.addEventListener('mousedown', e => {
    if (e.button) return;
    drag = true;
    card.classList.add('dragging');
    const cr = canvas.getBoundingClientRect();
    ox = e.clientX - cr.left - pos[name].x;
    oy = e.clientY - cr.top  - pos[name].y;
    e.preventDefault();
  });
  document.addEventListener('mousemove', e => {
    if (!drag) return;
    const cr = canvas.getBoundingClientRect();
    pos[name].x = Math.max(0, e.clientX - cr.left - ox);
    pos[name].y = Math.max(0, e.clientY - cr.top  - oy);
    card.style.left = pos[name].x + 'px';
    card.style.top  = pos[name].y + 'px';
    drawArrows();
  });
  document.addEventListener('mouseup', () => {
    if (!drag) return;
    drag = false;
    card.classList.remove('dragging');
  });
}

/* ── Arrow drawing ── */
function anchor(name, col, side) {
  const p = pos[name];
  if (!p) return null;
  const i = colIdx[name]?.[col];
  if (i === undefined) return null;
  return {
    x: side === 'r' ? p.x + CARD_W : p.x,
    y: p.y + HEAD_H + i * ROW_H + ROW_H / 2,
  };
}

function drawArrows() {
  /* rebuild SVG keeping only defs */
  svg.innerHTML = `<defs>
    <marker id="mArr"   markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0,9 3.5,0 7" fill="#e3b341" opacity=".85"/>
    </marker>
    <marker id="mArrHi" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0,9 3.5,0 7" fill="#fbd38d"/>
    </marker>
  </defs>`;

  DATA.relationships.forEach((r, idx) => {
    const fp = pos[r.from_table], tp = pos[r.to_table];
    if (!fp || !tp) return;

    /* Choose exit/entry sides based on horizontal center */
    const fcx = fp.x + CARD_W / 2, tcx = tp.x + CARD_W / 2;
    const fSide = fcx <= tcx ? 'r' : 'l';
    const tSide = fcx <= tcx ? 'l' : 'r';

    const from = anchor(r.from_table, r.from_column, fSide);
    const tCol = r.to_column || 'id';
    const to   = anchor(r.to_table, tCol, tSide);
    if (!from || !to) return;

    /* Bezier control points */
    const dx   = Math.abs(to.x - from.x);
    const off  = Math.max(55, dx * 0.45);
    const cp1x = fSide === 'r' ? from.x + off : from.x - off;
    const cp2x = tSide === 'l' ? to.x   - off : to.x   + off;
    const d    = `M${from.x},${from.y} C${cp1x},${from.y} ${cp2x},${to.y} ${to.x},${to.y}`;

    /* Visible path */
    const path = svgEl('path', {
      d, stroke: '#e3b341', 'stroke-width': '1.5', 'stroke-opacity': '.6',
      'stroke-dasharray': '6 4', fill: 'none',
      'marker-end': 'url(#mArr)', class: 'rel-path',
    });
    /* Wide invisible hit area */
    const hit = svgEl('path', {
      d, stroke: 'transparent', 'stroke-width': '14',
      fill: 'none', class: 'rel-hit',
    });

    /* Dots */
    const d1 = dot(from.x, from.y);
    const d2 = dot(to.x, to.y);

    /* Hover */
    const srcRow = document.getElementById(`R__${r.from_table}__${r.from_column}`);
    const tgtRow = document.getElementById(`R__${r.to_table}__${tCol}`);

    hit.addEventListener('mouseenter', () => {
      path.setAttribute('stroke', '#fbd38d');
      path.setAttribute('stroke-opacity', '1');
      path.setAttribute('stroke-width', '2.5');
      path.setAttribute('marker-end', 'url(#mArrHi)');
      d1.setAttribute('fill', '#fbd38d'); d1.setAttribute('r', '4.5');
      d2.setAttribute('fill', '#fbd38d'); d2.setAttribute('r', '4.5');
      if (srcRow) srcRow.classList.add('rel-hi');
      if (tgtRow) tgtRow.classList.add('rel-hi');
    });
    hit.addEventListener('mouseleave', () => {
      path.setAttribute('stroke', '#e3b341');
      path.setAttribute('stroke-opacity', '.6');
      path.setAttribute('stroke-width', '1.5');
      path.setAttribute('marker-end', 'url(#mArr)');
      d1.setAttribute('fill', '#e3b341'); d1.setAttribute('r', '3');
      d2.setAttribute('fill', '#e3b341'); d2.setAttribute('r', '3');
      if (srcRow) srcRow.classList.remove('rel-hi');
      if (tgtRow) tgtRow.classList.remove('rel-hi');
    });

    svg.appendChild(path);
    svg.appendChild(hit);
    svg.appendChild(d1);
    svg.appendChild(d2);
    /* Cardinality badges — driven by verified data, never hardcoded */
    const card = r.cardinality || '?';
    const srcLabel = (card === '1:1') ? '1' : (card === 'N:1') ? 'N' : '?';
    const tgtLabel = (card === '?')   ? '?' : '1';
    const unknown  = (card === '?');
    svg.appendChild(cardBadge(from.x, from.y, fSide, srcLabel, unknown));
    svg.appendChild(cardBadge(to.x,   to.y,   tSide, tgtLabel, unknown));
  });
}

/* ── Helpers ── */
function el(tag, attrs = {}) {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  return e;
}
function svgEl(tag, attrs = {}) {
  const e = document.createElementNS(NS, tag);
  Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  return e;
}
function dot(x, y) {
  return svgEl('circle', { cx: x, cy: y, r: 3, fill: '#e3b341', opacity: '.5', class: 'rel-path' });
}
function cardBadge(x, y, side, label, unknown) {
  /* Circle badge showing verified cardinality at each arrow endpoint.
     unknown=true renders in grey to signal unverified data. */
  const offset  = side === 'r' ? 18 : -18;
  const bx      = x + offset;
  const stroke  = unknown ? '#656d76' : '#e3b341';
  const fill    = unknown ? '#8b949e' : '#e3b341';
  const bg      = unknown ? '#1c2128' : '#161b22';
  const g = svgEl('g', { class: 'rel-path' });
  g.appendChild(svgEl('circle', {
    cx: bx, cy: y, r: 7,
    fill: bg, stroke: stroke, 'stroke-width': '1.2', opacity: '.92',
  }));
  const t = svgEl('text', {
    x: bx, y: y,
    'text-anchor': 'middle', 'dominant-baseline': 'central',
    fill: fill, 'font-size': '9',
    'font-family': "'SFMono-Regular', Consolas, monospace",
    'font-weight': '700',
  });
  t.textContent = label;
  g.appendChild(t);
  return g;
}
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ── Controls ── */
function resetLayout() { computeLayout(); renderCards(); drawArrows(); }

function fitView() {
  /* Find bounding box of all cards */
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  DATA.tables.forEach(t => {
    const p = pos[t.name];
    minX = Math.min(minX, p.x);
    minY = Math.min(minY, p.y);
    maxX = Math.max(maxX, p.x + CARD_W);
    maxY = Math.max(maxY, p.y + cardH(t));
  });
  const cw = wrap.clientWidth, ch = wrap.clientHeight;
  const bw = maxX - minX + PAD * 2, bh = maxY - minY + PAD * 2;
  const s  = Math.min(1, cw / bw, ch / bh);
  const tx = (cw - bw * s) / 2 - (minX - PAD) * s;
  const ty = (ch - bh * s) / 2 - (minY - PAD) * s;
  /* Scroll to center */
  wrap.scrollLeft = Math.max(0, (minX - PAD) * s - (cw - bw * s) / 2);
  wrap.scrollTop  = Math.max(0, (minY - PAD) * s - (ch - bh * s) / 2);
}

/* ── Bootstrap ── */
computeLayout();
renderCards();
drawArrows();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Stratio Schema Visualizer HTML generator")
    parser.add_argument("--input",  required=True, help="Input JSON data file")
    parser.add_argument("--output", required=True, help="Output HTML file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("relationships"):
        data["relationships"] = infer_relationships(data["tables"])

    if not data.get("generated_at"):
        data["generated_at"] = datetime.now().isoformat(timespec="seconds")

    ntables = len(data["tables"])
    ncols   = total_columns(data["tables"])
    nrels   = len(data.get("relationships", []))

    html = TEMPLATE
    html = html.replace("__DATA_JSON__",    json.dumps(data, ensure_ascii=False, indent=2))
    html = html.replace("__DOMAIN__",       data["domain"])
    html = html.replace("__TABLE_COUNT__",  str(ntables))
    html = html.replace("__COL_COUNT__",    str(ncols))
    html = html.replace("__REL_COUNT__",    str(nrels))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓  Written to: {args.output}")
    print(f"   Domain      : {data['domain']}")
    print(f"   Tables      : {ntables}")
    print(f"   Columns     : {ncols}")
    print(f"   Relationships: {nrels}")


if __name__ == "__main__":
    main()

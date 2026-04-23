# Stratio Brand — Presentation (.pptx) Guidelines

> **Regla de logo:** fondo blanco (`#FFFFFF`) → `assets/logo-dark.png` · cualquier otro fondo → `assets/logo-white.png`

Always read `/mnt/skills/public/pptx/SKILL.md` and `/mnt/skills/public/pptx/pptxgenjs.md` for technical implementation.
Apply the following Stratio-specific layouts on top of those skills.

---

## Setup

```javascript
const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9'; // 10" × 5.625"

// Brand colors (NO # prefix in pptxgenjs)
const C = {
  white:    "FFFFFF",
  action6:  "0776DF",
  space17:  "0F1B27",
  black:    "1A1A1A",
  gray:     "6B7280",
};
```

---

## Slide Types (based on official Stratio template)

### 1. PORTADA (Title Slide)

**Layout:** White background — left ~55% content, right ~45% architectural/tech photo (B&W or desaturated).

```
┌────────────────────┬──────────────────┐
│ [logo dark]        │                  │
│                    │  [photo: arch/   │
│ Cliente - Stratio  │   city, b&w or   │
│ Objetivo sesión    │   desaturated]   │
│                    │                  │
│ [Logo Cliente]     │                  │
│                    │                  │
│ Mes, Año           │                  │
└────────────────────┴──────────────────┘
```

- Background: White
- Logo `assets/logo-dark.png` — top-left, ~1.6" wide, y=0.3
- Title: Inter Bold 36pt, color `1A1A1A`, x=0.4, y=1.8
- Subtitle: Inter SemiBold 16pt, color `0776DF` (Action 6), x=0.4, y=2.7
- Client logo placeholder: gray text or actual logo image, x=0.8, y=3.4
- Date: Inter Bold 10pt, color `0776DF`, bottom-left x=0.4, y=5.1
- Right side photo: x=5.5, y=0, w=4.5, h=5.625, sizing cover; use B&W architectural/tech image
- If no photo available: light gray rectangle fill `F0F0F0`

---

### 2. AGENDA Slide

**Layout:** White left ~65%, Action 6 angled panel right ~35% with logo white inside.

```
┌──────────────────────┬──────────────┐
│                      │╲             │
│  1. Punto 1 agenda   │  [logo white]│
│  2. Punto 2 agenda   │  (Action 6)  │
│                      │             ╱│
└──────────────────────┴──────────────┘
```

- Background: White
- Right blue panel: RECTANGLE fill `0776DF`, x=6.2, y=0, w=3.8, h=5.625
- Diagonal left edge of panel: RIGHT_TRIANGLE fill White, x=5.5, y=0, w=0.9, h=5.625 (creates angled separation)
- Logo `assets/logo-mono-white.png`: x=6.8, y=0.25, w=2.8, h=0.55  ← panel azul → mono-white (icono 100% blanco)
- Numbered list: Inter 16pt `1A1A1A`, left side x=0.5, y=1.8; active item bold, inactive regular

---

### 3. CONTENT / SECTION Slide

**Layout:** Clean white, large section title + subtitle, thin Action 6 divider, then content area.

```
┌──────────────────────────────────────┐
│  Título punto 1  (bold, black, 28pt) │
│  Subtítulo (gray, 14pt)              │
│  ─────────────────────────────────── │  ← thin Action 6 line
│                                      │
│  [content area — text, tables, etc.] │
│                                      │
└──────────────────────────────────────┘
```

- Background: White
- Title: Inter Bold 28pt, `1A1A1A`, x=0.5, y=0.4
- Subtitle: Inter Regular 14pt, `6B7280`, x=0.5, y=1.1
- Divider: RECTANGLE fill `0776DF`, x=0.5, y=1.55, w=9, h=0.03
- Content area starts at y≈1.7

---

### 4. CLOSING / "¡Gracias!" Slide

**Layout:** Full-bleed dark city/tech-at-night photo, logo white centered top, large white "¡Gracias!" centered.

```
┌──────────────────────────────────────┐
│         [full-bleed dark photo]      │
│           [semi-dark overlay]        │
│           [logo white centered]      │
│                                      │
│             ¡Gracias!                │
│                                      │
└──────────────────────────────────────┘
```

- Background: full-bleed city/data-at-night photo; fallback = Space 17 `0F1B27` solid
- Overlay: RECTANGLE fill `0F1B27` transparency=30, full slide size (improves legibility)
- Logo `assets/logo-mono-white.png`: centered, x=3.5, y=0.6, w=3.0, h=0.7  ← fondo oscuro/foto → mono-white
- "¡Gracias!": Inter Regular 64pt White, centered, y=2.2

---

## Footer (Content & Agenda slides only)

```javascript
// Left
slide.addText("Stratio Generative AI Data Fabric", {
  x: 0.4, y: 5.35, w: 6, h: 0.2,
  fontSize: 7, fontFace: "Inter", color: "AAAAAA", margin: 0
});
// Right — slide number
slide.addText("N", {
  x: 9.3, y: 5.35, w: 0.5, h: 0.2,
  fontSize: 7, fontFace: "Inter", color: "AAAAAA", align: "right", margin: 0
});
```

---

## Standard Slide Order

1. Portada
2. Agenda (optional)
3. Content slides (one per section)
4. ¡Gracias!

---

## Typography Summary

| Element            | Font  | Size  | Weight   | Color    |
|--------------------|-------|-------|----------|----------|
| Portada title      | Inter | 36pt  | Bold     | `1A1A1A` |
| Portada subtitle   | Inter | 16pt  | SemiBold | `0776DF` |
| Portada date       | Inter | 10pt  | Bold     | `0776DF` |
| Agenda items       | Inter | 16pt  | Regular/Bold | `1A1A1A` |
| Content title      | Inter | 28pt  | Bold     | `1A1A1A` |
| Content subtitle   | Inter | 14pt  | Regular  | `6B7280` |
| Body text          | Inter | 14pt  | Regular  | `1A1A1A` |
| Closing text       | Inter | 64pt  | Regular  | `FFFFFF` |
| Footer             | Inter | 7pt   | Regular  | `AAAAAA` |

---

## ⚠️ PptxGenJS Critical Rules
- **Never use `#` prefix** in hex colors — corrupts files
- **Never reuse options objects** across multiple addShape/addText calls
- Use `sizing: { type: "cover" }` for full-bleed photos
- Use `margin: 0` when aligning text edges with shapes precisely

---
name: stratio-brand
description: Apply Stratio Generative AI Data Fabric corporate branding and formatting to any document or web page. Use this skill whenever the user asks to create, format, or style a Word document (.docx), presentation (.pptx), PDF, spreadsheet (.xlsx), web page, HTML component, or React app that should follow Stratio's visual identity. Trigger on phrases like "create a document", "make a presentation", "build a web page", "create a landing page", "format this", "corporate style", "Stratio branding", "generate a report", or any document/web creation request in a professional/corporate context. Always apply Stratio brand guidelines when producing deliverables intended for internal or external use.
---

# Stratio Brand Skill

This skill ensures all documents and deliverables produced by Claude follow Stratio Generative AI Data Fabric's corporate visual identity.

**Always read this skill before creating any document, presentation, PDF, or spreadsheet for Stratio projects.**

---

## Brand Identity

### Company
**Stratio Generative AI Data Fabric**
Website: stratio.com

### Color Palette

| Name       | Hex       | Usage                                      |
|------------|-----------|--------------------------------------------|
| White      | `#FFFFFF`  | Backgrounds, text on dark, negative space  |
| Action 6   | `#0776DF`  | Primary accent, CTAs, links, highlights    |
| Space 17   | `#0F1B27`  | Dark backgrounds, primary headings, footer |

**Color Rules:**
- Use **Space 17** (`#0F1B27`) for primary headings, title slides, and dark section headers
- Use **Action 6** (`#0776DF`) for accents, subheadings, dividers, table headers, and key highlights
- Use **White** (`#FFFFFF`) for page/slide backgrounds and text on dark backgrounds
- Avoid other colors unless explicitly requested — maintain brand consistency

### Typography

**Font: Inter** (all weights)
- Load from Google Fonts when needed: `https://fonts.google.com/specimen/Inter`
- Fallback stack: `Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`

| Element         | Font   | Weight   | Size guidance     |
|-----------------|--------|----------|-------------------|
| Document Title  | Inter  | Bold 700 | Large (24–32pt)   |
| Section Heading | Inter  | SemiBold 600 | Medium (16–20pt) |
| Subheading      | Inter  | Medium 500 | (13–15pt)        |
| Body Text       | Inter  | Regular 400 | (10–12pt)        |
| Caption / Meta  | Inter  | Light 300 | Small (8–9pt)     |

---

## Logo Usage

Four logo variants are included in `assets/`:

| File | Description | Preview |
|------|-------------|---------|
| `assets/logo-dark.png` | Blue icon + Space 17 text | Standard logo for white backgrounds |
| `assets/logo-white.png` | Blue icon + white text | Standard logo for dark/colored backgrounds |
| `assets/logo-mono-dark.png` | All Space 17 (no blue) | Monochrome, use when color printing unavailable |
| `assets/logo-mono-white.png` | All white (no blue) | Monochrome, use on dark when color unavailable |

**Logo Rules — STRICT background rule (always apply):**

| Background | Logo to use | File |
|------------|-------------|------|
| Blanco (`#FFFFFF`) | Icono azul + texto oscuro | `assets/logo-dark.png` |
| Azul (`#0776DF`) o cualquier color saturado | Todo blanco (icono + texto) | `assets/logo-mono-white.png` |
| Oscuro / foto / Space 17 | Todo blanco (icono + texto) | `assets/logo-mono-white.png` |

- **Fondo blanco → `logo-dark.png`. Cualquier otro caso → `logo-mono-white.png`.**
- `logo-white.png` (icono azul + texto blanco) se reserva para fondos neutros oscuros donde el icono azul siga siendo visible — uso excepcional.
- `logo-mono-dark.png` (todo Space 17) solo para impresión monocroma — nunca en digital por defecto.
- Los logos tienen fondo transparente (RGBA). Al subir nuevos logos, siempre verificar que sean RGBA; si son RGB, eliminar el fondo con el script de Python incluido en `assets/remove_bg.py`.
- Nunca estirar, recolorear, rotar ni añadir efectos al logo.
- Espacio mínimo: igual a la altura del icono "S". Ancho mínimo: 120px digital / 3cm impreso.

---

## Document Type Guidelines

For detailed implementation instructions for each document type, read the corresponding reference file:

- **Word (.docx)** → see `references/docx-brand.md`
- **Presentations (.pptx)** → see `references/pptx-brand.md`
- **PDF** → see `references/pdf-brand.md`
- **Spreadsheets (.xlsx)** → see `references/xlsx-brand.md`
- **Web / HTML / React** → see `references/web-brand.md`

---

## Universal Rules (apply to ALL document types)

1. **Font is always Inter** — never substitute with Arial, Calibri, or other system fonts unless Inter is unavailable
2. **No gradients** except where explicitly noted (title slides may use Space 17 → a slightly lighter dark tone)
3. **Headings use Space 17**, accents and highlights use Action 6, backgrounds use White
4. **Footer on every page/slide**: include "Stratio Generative AI Data Fabric" on the left and page number on the right, in Inter Light, small size, color Space 17 or white depending on background
5. **No clip art, decorative borders, or non-brand colors**
6. **White space is intentional** — keep layouts clean and uncluttered
7. **Tables**: header row uses Action 6 background with white text; alternating rows use very light blue tint (`#EBF4FD`) and white
8. **Always use the brand's dark-on-light or light-on-dark contrast** — never light text on light background

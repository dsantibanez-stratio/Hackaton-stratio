# Stratio Brand — Web / HTML Guidelines

Always read `/mnt/skills/public/frontend-design/SKILL.md` for general frontend best practices.
Apply the following Stratio-specific tokens and patterns on top of that skill.

> **Regla de logo:** fondo blanco → `logo-dark.png` · cualquier otro fondo → `logo-mono-white.png`

---

## CSS Variables (siempre incluir en `:root`)

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* Brand colors */
  --color-white:    #FFFFFF;
  --color-action6:  #0776DF;   /* Primary accent / CTA */
  --color-space17:  #0F1B27;   /* Dark backgrounds / headings */

  /* Extended palette */
  --color-body:       #1A1A1A;
  --color-muted:      #6B7280;
  --color-border:     #E2E8F0;
  --color-surface:    #F8FAFC;
  --color-table-alt:  #EBF4FD;
  --color-blue-light: #57A9F4;  /* secondary data color */

  /* Typography */
  --font-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Spacing scale */
  --space-xs:  0.25rem;
  --space-sm:  0.5rem;
  --space-md:  1rem;
  --space-lg:  1.5rem;
  --space-xl:  2.5rem;
  --space-2xl: 4rem;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(15,27,39,0.08);
  --shadow-md: 0 4px 16px rgba(15,27,39,0.10);
  --shadow-lg: 0 8px 32px rgba(15,27,39,0.14);
}
```

---

## Typography

```css
body {
  font-family: var(--font-base);
  font-size: 16px;
  color: var(--color-body);
  background: var(--color-white);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

h1 { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 700; color: var(--color-space17); line-height: 1.15; }
h2 { font-size: clamp(1.5rem, 3vw, 2.25rem); font-weight: 600; color: var(--color-space17); }
h3 { font-size: 1.25rem; font-weight: 600; color: var(--color-space17); }
h4 { font-size: 1rem;    font-weight: 500; color: var(--color-space17); }

.subtitle   { font-size: 1.125rem; font-weight: 500; color: var(--color-action6); }
.body-large { font-size: 1.125rem; color: var(--color-body); }
.caption    { font-size: 0.75rem;  color: var(--color-muted); }
.overline   { font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.1em;
               text-transform: uppercase; color: var(--color-action6); }
```

---

## Layout Patterns

### Page wrapper
```css
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
}

@media (max-width: 768px) {
  .page-container { padding: 0 var(--space-md); }
}
```

### Título de página (obligatorio)

Al igual que en las presentaciones — donde cada deck tiene un título explícito en la portada — **toda página web debe incluir un título visible** que identifique el contenido. Se implementa en dos lugares:

1. **`<title>` del documento** — siempre con formato `Nombre del contenido · Stratio`
2. **Subtítulo en la navbar**, debajo del logo — texto pequeño en Action 6 que contextualiza la página

```html
<!-- En el <head> -->
<title>Resumen Ejecutivo · Stratio</title>

<!-- En la navbar, junto al logo -->
<nav>
  <div class="navbar-brand">
    <img src="assets/logo-dark.png" alt="Stratio" height="28">
    <span class="navbar-page-title">Resumen Ejecutivo</span>  <!-- ← título de página -->
  </div>
  ...
</nav>
```

```css
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.navbar-brand-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border);
  margin: 0 0.25rem;
}
.navbar-page-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-action6);   /* Action 6 — igual que el subtítulo de portada en PPTX */
  letter-spacing: 0;
}
```

**Regla:** el título de página en la navbar debe coincidir siempre con el `<title>` del documento (sin el sufijo `· Stratio`). Si la página no tiene navbar, el título va en el hero como `.overline` (mayúsculas, Action 6, tracking amplio).

---

### Navbar
```css
.navbar {
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-md) var(--space-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
/* Logo en navbar blanca: logo-dark.png */
.navbar-logo { height: 28px; }

/* Dark navbar variant */
.navbar--dark {
  background: var(--color-space17);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
/* Logo en navbar oscura: logo-mono-white.png */
/* Título de página en navbar oscura: color blanco, no Action 6 */
.navbar--dark .navbar-page-title { color: rgba(255,255,255,0.7); }
.navbar--dark .navbar-brand-divider { background: rgba(255,255,255,0.15); }
```

### Hero Section
```css
/* Light hero (white bg) */
.hero {
  background: var(--color-white);
  padding: var(--space-2xl) var(--space-xl);
}
.hero__eyebrow { /* use .overline class */ }
.hero__title   { /* use h1 styles */ }
.hero__subtitle { color: var(--color-muted); font-size: 1.125rem; max-width: 600px; }

/* Dark hero (Space 17 bg) */
.hero--dark {
  background: var(--color-space17);
  color: var(--color-white);
}
.hero--dark h1, .hero--dark h2 { color: var(--color-white); }
/* Logo in dark hero: use logo-mono-white.png */
```

### Cards
```css
.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.card__accent {
  /* Top accent bar */
  border-top: 3px solid var(--color-action6);
  border-radius: var(--radius-md);
}
```

### Section dividers
```css
.section-divider {
  height: 3px;
  background: var(--color-action6);
  border: none;
  margin: var(--space-lg) 0;
  width: 48px; /* short accent bar under titles */
}
.section-divider--full { width: 100%; height: 1px; background: var(--color-border); }
```

---

## Components

### Buttons
```css
.btn {
  font-family: var(--font-base);
  font-size: 0.9375rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  padding: 0.625rem 1.5rem;
  cursor: pointer;
  border: none;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* Primary */
.btn--primary {
  background: var(--color-action6);
  color: var(--color-white);
}
.btn--primary:hover {
  background: #0668c8;
  box-shadow: 0 4px 12px rgba(7,118,223,0.35);
  transform: translateY(-1px);
}

/* Secondary */
.btn--secondary {
  background: transparent;
  color: var(--color-action6);
  border: 1.5px solid var(--color-action6);
}
.btn--secondary:hover { background: var(--color-table-alt); }

/* Dark */
.btn--dark {
  background: var(--color-space17);
  color: var(--color-white);
}
```

### Tables
```css
.table { width: 100%; border-collapse: collapse; font-size: 0.9375rem; }
.table thead tr { background: var(--color-action6); }
.table thead th {
  color: var(--color-white);
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: left;
}
.table tbody tr:nth-child(even) { background: var(--color-table-alt); }
.table tbody td {
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-body);
}
.table tbody tr:hover { background: #dbeafe44; }
```

### Tags / Badges
```css
.badge {
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}
.badge--blue  { background: var(--color-table-alt); color: var(--color-action6); }
.badge--dark  { background: var(--color-space17);   color: var(--color-white);   }
.badge--green { background: #D1FAE5; color: #065F46; }
```

---

## Footer
```css
.footer {
  background: var(--color-space17);
  color: rgba(255,255,255,0.7);
  padding: var(--space-xl);
  font-size: 0.875rem;
}
.footer__brand { color: var(--color-white); font-weight: 600; }
.footer__accent { color: var(--color-action6); }
.footer a { color: rgba(255,255,255,0.7); text-decoration: none; }
.footer a:hover { color: var(--color-white); }
/* Logo in footer: use logo-mono-white.png (dark background) */
```

---

## Logo Usage in HTML

```html
<!-- White background (navbar, cards, hero light) -->
<img src="assets/logo-dark.png" alt="Stratio" height="32">

<!-- Dark/colored background (dark navbar, dark hero, footer, cards on color) -->
<img src="assets/logo-mono-white.png" alt="Stratio" height="32">
```

---

## Dark Mode (optional)
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-white:   #0F1B27;
    --color-body:    #E2E8F0;
    --color-surface: #1a2d3f;
    --color-border:  rgba(255,255,255,0.1);
    --color-muted:   #94A3B8;
  }
  /* Switch logo to mono-white in dark mode */
}
```

---

## Do / Don't

| ✅ Do | ❌ Don't |
|-------|---------|
| Usar Inter en todos los pesos | Mezclar otras fuentes |
| Fondos blancos + acentos Action 6 | Gradientes no marcados |
| Espaciado generoso y limpio | Sobrecargar con elementos |
| Tablas con cabecera Action 6 | Colores fuera de paleta |
| Logo sin fondo (RGBA) | Logos con recuadro de color |
| Botones con hover animado | Bordes redondeados excesivos |

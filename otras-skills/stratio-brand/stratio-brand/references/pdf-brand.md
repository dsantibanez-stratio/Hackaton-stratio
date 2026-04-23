# Stratio Brand — PDF Guidelines

Always read `/mnt/skills/public/pdf/SKILL.md` for technical implementation details.
Apply the following Stratio-specific settings on top of that skill.

## General Approach
PDFs are typically generated from HTML or from a .docx export. Apply the same styles as `docx-brand.md` when generating from scratch, with these additions for HTML-to-PDF:

## HTML/CSS Template Variables
```css
:root {
  --color-primary: #0F1B27;    /* Space 17 */
  --color-accent: #0776DF;     /* Action 6 */
  --color-white: #FFFFFF;
  --color-body: #1A1A1A;
  --color-muted: #666666;
  --color-table-alt: #EBF4FD;
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

## Page Layout (for HTML-to-PDF)
```css
@page {
  size: A4;
  margin: 2.5cm 2.5cm 3cm 3cm;
  @bottom-left {
    content: "Stratio Generative AI Data Fabric";
    font-family: var(--font-family);
    font-size: 8pt;
    color: var(--color-muted);
  }
  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-family: var(--font-family);
    font-size: 8pt;
    color: var(--color-muted);
  }
}
```

## Key Styles
```css
body {
  font-family: var(--font-family);
  font-size: 11pt;
  color: var(--color-body);
  background: var(--color-white);
  line-height: 1.5;
}

h1 {
  font-size: 24pt;
  font-weight: 700;
  color: var(--color-primary);
  border-bottom: 3pt solid var(--color-accent);
  padding-bottom: 6pt;
  margin-bottom: 12pt;
}

h2 {
  font-size: 16pt;
  font-weight: 600;
  color: var(--color-primary);
  margin-top: 18pt;
}

h3 {
  font-size: 13pt;
  font-weight: 500;
  color: var(--color-accent);
  margin-top: 12pt;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead tr {
  background-color: var(--color-accent);
  color: var(--color-white);
}

tr:nth-child(even) {
  background-color: var(--color-table-alt);
}

td, th {
  padding: 6pt 8pt;
  border: 0.5pt solid #CCCCCC;
  font-size: 10pt;
}

/* Cover page */
.cover {
  background-color: var(--color-primary);
  color: var(--color-white);
  min-height: 100vh;
  padding: 60pt;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.cover h1 {
  color: var(--color-white);
  border-bottom-color: var(--color-accent);
  font-size: 32pt;
}

.cover .subtitle {
  color: var(--color-accent);
  font-size: 16pt;
  font-weight: 300;
}
```

## Cover Page Structure (HTML)
```html
<div class="cover">
  <img src="assets/logo-white.png" class="cover-logo" alt="Stratio" style="width: 200px; margin-bottom: 40pt;" />
  <h1>Document Title</h1>
  <p class="subtitle">Subtitle or document type</p>
  <p class="cover-meta">Author · Date · Version</p>
</div>
```

**Logo in body pages:** use `assets/logo-dark.png` in the header on white-background pages.

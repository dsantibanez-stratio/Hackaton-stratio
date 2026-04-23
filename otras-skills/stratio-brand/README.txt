# Stratio Brand Skill — Export Package
=============================================

## Contenido

### stratio-brand.skill
Archivo de skill listo para instalar en Claude.ai.
→ Ve a Configuración → Skills → Subir skill

### stratio-brand/
Archivos fuente de la skill (editables):
  SKILL.md                        → Definición principal y reglas universales
  references/docx-brand.md        → Guía de formato Word (.docx)
  references/pptx-brand.md        → Guía de presentaciones (.pptx)
  references/pdf-brand.md         → Guía de PDFs
  references/xlsx-brand.md        → Guía de hojas de cálculo (.xlsx)
  references/web-brand.md         → Guía de páginas web / HTML / React
  assets/logo-dark.png            → Logo azul + texto oscuro (fondo blanco)
  assets/logo-white.png           → Logo azul + texto blanco (fondos oscuros)
  assets/logo-mono-dark.png       → Logo monocromático oscuro (impresión)
  assets/logo-mono-white.png      → Logo monocromático blanco (fondos color/oscuro)
  assets/remove_bg.py             → Script para procesar logos nuevos

### logos/
Los 4 logos con fondo transparente (RGBA), listos para usar en cualquier proyecto.

## Regla de logo (resumen)
  Fondo BLANCO              → logo-dark.png
  Fondo azul / oscuro / foto → logo-mono-white.png

## Colores de marca
  White     #FFFFFF
  Action 6  #0776DF  (azul principal, acentos, CTAs)
  Space 17  #0F1B27  (fondos oscuros, títulos)

## Tipografía
  Inter (todos los pesos) — https://fonts.google.com/specimen/Inter

## Para actualizar logos
  pip install Pillow
  python3 stratio-brand/assets/remove_bg.py

---
Stratio Generative AI Data Fabric · stratio.com

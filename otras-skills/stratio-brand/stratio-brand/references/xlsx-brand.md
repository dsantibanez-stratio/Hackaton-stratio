# Stratio Brand — Spreadsheet (.xlsx) Guidelines

Always read `/mnt/skills/public/xlsx/SKILL.md` for technical implementation details.
Apply the following Stratio-specific settings on top of that skill.

## Workbook Setup
- Default font: Inter (fallback: Calibri if Inter unavailable)
- Default font size: 11pt
- Default color: `#1A1A1A`
- Grid lines: visible, color `#E0E0E0`
- Background: White (`#FFFFFF`)

## Named Styles

### Title Row (row 1 of each sheet)
- Background: Space 17 (`#0F1B27`)
- Font: Inter Bold, 14pt, White (`#FFFFFF`)
- Height: 40px
- Merge across used columns

### Column Headers (usually row 2 or first data row)
- Background: Action 6 (`#0776DF`)
- Font: Inter SemiBold, 11pt, White (`#FFFFFF`)
- Height: 28px
- Borders: thin white border between cells

### Data Rows
- Odd rows: White (`#FFFFFF`)
- Even rows: `#EBF4FD` (very light blue)
- Font: Inter Regular, 11pt, `#1A1A1A`
- Height: 22px
- Borders: `#E0E0E0` thin borders

### Subtotal / Summary Rows
- Background: `#D6EAF8` (light blue)
- Font: Inter SemiBold, 11pt, Space 17 (`#0F1B27`)

### Grand Total Row
- Background: Space 17 (`#0F1B27`)
- Font: Inter Bold, 11pt, White (`#FFFFFF`)

## Tab (Sheet) Styling
- Active/primary sheet tab: Action 6 (`#0776DF`)
- Secondary sheet tabs: Space 17 (`#0F1B27`)

## Charts (embedded in sheets)
- Primary series: Action 6 (`#0776DF`)
- Secondary series: `#57A9F4`
- Tertiary series: Space 17 (`#0F1B27`)
- Background: White
- Grid lines: `#EEEEEE`
- Font: Inter, 10pt, `#444444`
- Chart title: Inter SemiBold, 13pt, Space 17

## Print Setup
- Paper: A4
- Orientation: Landscape for wide tables, Portrait for narrow
- Scale to fit: 1 page wide
- Header: "Stratio Generative AI Data Fabric" left, date right
- Footer: Sheet name left, page number right
- Repeat header rows on each printed page

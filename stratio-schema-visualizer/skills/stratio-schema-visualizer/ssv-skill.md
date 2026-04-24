---
name: stratio-schema-visualizer
description: Use this skill to visually explore and understand the relational schema of tables in a Stratio data domain or collection. Triggers when the user asks to "show the schema", "visualize the tables", "draw an ER diagram", "show relationships between tables", "explore the data structure", "show the data model", "what tables are in my domain", "esquema relacional", "diagrama de entidades", or wants to understand how tables in a Stratio collection relate to each other. Also triggers when the user mentions "relational diagram", "entity relationship", "table structure", "column details", or simply asks to "see the data model" in a Stratio context. Use proactively whenever the user seems to be exploring an unfamiliar domain.
---

# Stratio Schema Visualizer

Generates an interactive, browser-based relational schema diagram from a Stratio data domain. Shows tables as nodes, columns with types and governance descriptions, inferred FK relationships as directed edges with verified cardinality, and data quality badges. Output is a fully standalone HTML file — no server needed.

## Workflow

### Step 1 — Identify the target domain

**The user must specify which domain/collection to visualize.** If they have not done so:
1. Call `stratio_data-list_domains` with `domain_type: "both"`
2. Present the list as a numbered menu (name + short description, one per line)
3. Ask: "Which domain would you like to visualize?"
4. Wait for the user's answer before proceeding

If they give a partial name or keyword instead of an exact name, call `stratio_data-search_domains` to find the best match, then confirm the match with the user before continuing.

### Step 2 — Fetch table metadata

For the selected domain, make these calls (run in parallel when possible):

```
stratio_data-list_domain_tables(domain_name)           → list of table names
stratio_data-get_tables_details(domain_name, ALL)      → descriptions, business context
stratio_data-get_tables_quality_details(domain_name)   → quality scores per table
```

Then for **each table**, call:
```
stratio_data-get_table_columns_details(domain_name, table_name)  → columns, types, descriptions
```

If there are more than 12 tables, process in batches of 6 using parallel subagents to avoid timeouts.

If a table fails (permissions, timeout), skip it gracefully and note which ones were skipped at the end.

Extract the quality score for each table from `get_tables_quality_details`. The score is a number 0–100 representing data quality percentage. If the call fails or a table has no score, set `quality_score: null`.

### Step 3 — Build the data structure

Assemble a JSON object in this exact shape and write it to `/tmp/stratio_schema_input.json`:

```json
{
  "domain": "domain-name",
  "generated_at": "ISO-8601 timestamp",
  "tables": [
    {
      "name": "table_name",
      "description": "Business description from governance (empty string if none)",
      "quality_score": 85,
      "columns": [
        {
          "name": "column_name",
          "type": "string",
          "description": "Column description (empty string if none)",
          "is_primary_key": false
        }
      ]
    }
  ],
  "relationships": []
}
```

Leave `relationships` as an empty array for now — it will be populated in the next step.

Mark `is_primary_key: true` for any column named exactly `id` or following the pattern `<table_name>_id` in its own table.

### Step 3b — Infer and verify relationships with real data

**Accuracy is the top priority of this skill. Never show cardinality that has not been verified against actual data.**

#### 3b.1 — Infer candidate FK relationships

Scan all column names looking for:
- Columns ending in `_id` whose prefix matches another table's name (e.g. `customer_id` → table `customer`)
- Columns ending in `_ref` whose prefix matches the last segment of another table's name (e.g. `pac_ref` → table `tbl_pac`)

Build a candidate list: `[{from_table, from_column, to_table, to_column}]`.

#### 3b.2 — Verify cardinality with a SQL query per relationship

For **each** candidate relationship, call `stratio_data-execute_sql` with:

```sql
SELECT
  COUNT(*)                      AS total_rows,
  COUNT(DISTINCT <from_column>) AS distinct_vals
FROM <from_table>
WHERE <from_column> IS NOT NULL
```

Determine cardinality from the result:
- `total_rows == distinct_vals` → **`"1:1"`** (each FK value appears exactly once)
- `total_rows > distinct_vals`  → **`"N:1"`** (multiple rows share the same FK value)
- Query fails or returns 0 rows → **`"?"`** (unknown — do not guess)

If there are more than 5 relationships, run the queries in parallel.

#### 3b.3 — Populate relationships in the JSON

Replace the empty `relationships` array with the verified list:

```json
"relationships": [
  {
    "from_table": "orders",
    "from_column": "customer_id",
    "to_table":   "customers",
    "to_column":  "id",
    "cardinality": "N:1",
    "inferred": true
  }
]
```

Only include relationships where the query succeeded. Skip any candidate where the query errored or the column does not exist.

### Step 4 — Generate the HTML visualization

Find this skill's directory (the folder containing this SKILL.md), then run:

```bash
SKILL_DIR=$(find ~/.claude -path "*/stratio-schema-visualizer/scripts/generate_schema_html.py" 2>/dev/null | head -1 | xargs -I{} dirname {} | xargs -I{} dirname {})

# Fallback: look in current project
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR=$(find . -path "*/stratio-schema-visualizer/scripts/generate_schema_html.py" 2>/dev/null | head -1 | xargs -I{} dirname {} | xargs -I{} dirname {} 2>/dev/null)
fi

# Output goes to the project's visualizaciones/ folder with a timestamp
PROJECT_ROOT=$(git -C "$(dirname "$SKILL_DIR")" rev-parse --show-toplevel 2>/dev/null || dirname "$(dirname "$SKILL_DIR")")
VIZ_DIR="$PROJECT_ROOT/visualizaciones"
mkdir -p "$VIZ_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DOMAIN_SLUG=$(echo "<domain_name>" | tr ' /' '__')
OUTPUT_FILE="$VIZ_DIR/${DOMAIN_SLUG}_${TIMESTAMP}.html"

python3 "$SKILL_DIR/scripts/generate_schema_html.py" \
  --input /tmp/stratio_schema_input.json \
  --output "$OUTPUT_FILE"
```

Replace `<domain_name>` with the actual domain name (spaces and slashes replaced with underscores).

### Step 5 — Open in browser

```bash
xdg-open "$OUTPUT_FILE" 2>/dev/null || python3 -m webbrowser "$OUTPUT_FILE" 2>/dev/null || echo "Open manually: $OUTPUT_FILE"
```

Tell the user:

> "El esquema relacional de **\<domain\>** está abierto en el navegador. Funcionalidades disponibles:
>
> **Diagrama**
> - **Arrastra** las tablas para reorganizar el layout
> - **Scroll** para hacer zoom
> - **Hover sobre una columna** para ver su descripción de governance
> - **Hover sobre una flecha** para ver el detalle de la relación y su cardinalidad
> - **Hover sobre el badge de calidad** (%) para ver el score de calidad de datos de la tabla
>
> **Cabecera — botones de acción**
> - **▶ Presentar** — activa el modo presentación: resalta la entidad central y permite avanzar paso a paso por el modelo, atenuando el resto del diagrama en cada paso
> - **↺ Restablecer** — vuelve al layout original
> - **⊞ Ajustar** — centra y escala el diagrama para que quepa en pantalla
> - **📊 Análisis** — abre un panel lateral derecho con dos pestañas: **Resumen** (entidad central, lista de entidades y mapa de relaciones) y **Salud del esquema** (avisos sobre PKs ausentes, tablas aisladas, cardinalidad no verificada y descripciones de governance ausentes). El botón muestra un badge naranja con el número total de avisos.
> - **📄 Exportar DDL** — descarga un fichero `.sql` con los `CREATE TABLE` inferidos del esquema
> - **⬇ Exportar PNG** — descarga una captura del diagrama completo en alta resolución
> - **🇬🇧 English / 🇪🇸 Español** — cambia el idioma de toda la interfaz
>
> **Barra de filtros** (debajo de la cabecera)
> Toggles para mostrar/ocultar en tiempo real: tipos de dato · columnas no clave · descripciones (tooltips) · relaciones sin verificar
>
> **Leyenda** (esquina inferior derecha)
> Explica los colores de los badges de calidad (verde ≥ 80 %, amarillo 40–79 %, rojo < 40 %), las claves primarias y las FK inferidas."

If any tables were skipped (permissions/timeout), mention them at the end.

## Features of the generated HTML

The output is a fully standalone HTML file that embeds all assets. It requires an internet connection on first load to fetch fonts and the html2canvas library from CDN, but works offline after that.

### Table cards
- Each table is rendered as a draggable card with a dark header showing the table name, column count, and optionally a **data quality badge** (colour-coded: green ≥ 80 %, yellow 40–79 %, red < 40 %)
- Hovering over the quality badge shows a tooltip: *"Calidad de datos: X%"*
- PK columns are marked with a red left border and a `PK` label
- FK columns are marked with a `FK` label
- Each column shows its data type as a colour-coded chip
- Hovering over a column shows its governance description in a tooltip (can be toggled off)

### Relationships
- Drawn as dashed bezier arrows with cardinality badges at each endpoint
- Verified cardinalities (`1:1`, `N:1`) are shown in blue; unverified (`?`) in grey
- Hovering over an arrow highlights the source and target column rows

### Header bar
| Button | Action |
|--------|--------|
| ▶ Presentar / Present | Activates presentation mode |
| ↺ Restablecer / Reset | Restores the original auto-layout |
| ⊞ Ajustar / Fit | Fits the full diagram in the viewport |
| 📊 Análisis / Analysis | Opens right-side panel with Summary and Schema Health tabs |
| 📄 Exportar DDL / Export DDL | Downloads `schema_<domain>.sql` |
| ⬇ Exportar PNG / Export PNG | Downloads a 2× resolution PNG of the canvas |
| 🇬🇧 English / 🇪🇸 Español | Toggles the UI language |

### Filter bar
Four real-time toggles below the header:
- **Tipos de dato / Data types** — show/hide the type chips on columns
- **Columnas no clave / Non-key columns** — show/hide all non-PK, non-FK rows
- **Descripciones / Descriptions** — enable/disable governance description tooltips
- **Relaciones sin verificar / Unverified relations** — show/hide arrows with `?` cardinality

### Analysis panel (📊)
A single right-side panel with two tabs, opened via the **Análisis / Analysis** button. The button shows an orange badge with the total number of health warnings.

**Summary tab** — generated client-side from governance metadata (no extra API calls):
- Intro sentence with entity and relationship counts
- Central entity (most connections) with its governance description
- Full entity list with one-line descriptions
- Relationship map showing source → target and the linking column

**Schema Health tab** — auto-computed warnings grouped by category:
- **Clave primaria ausente / Missing Primary Key** — tables with no PK column
- **Tablas aisladas / Isolated Tables** — tables with no relationships
- **Cardinalidad no verificada / Unverified Cardinality** — relationships where the SQL query failed or was not authorised
- **Descripciones de governance ausentes / Missing Governance Descriptions** — columns without a description

### Presentation mode
Step-by-step walkthrough of the schema:
1. Highlights the central entity (most connections), dims everything else
2. Each "Next" step adds one connected table and its arrow, scrolling the canvas smoothly
3. Final step reveals any remaining isolated tables
4. A bottom bar shows the step counter, a description of the current entity, and Prev / Next / Exit controls
5. Fully translatable; language switch works while in presentation mode

### DDL export
Downloads a `.sql` file with `CREATE TABLE` statements inferred from the schema:
- Type mapping: `STRING → VARCHAR(255)`, `INTEGER → INT`, `FLOAT → FLOAT`, `BOOLEAN → BOOLEAN`, `DATE → DATE`, `TIMESTAMP → TIMESTAMP`, others → `TEXT`
- Primary keys included as `PRIMARY KEY (col)` constraint
- Governance descriptions included as inline SQL comments (truncated to 80 chars)
- Header block with domain name and generation date

## Notes

- **Correctness is non-negotiable.** Every relationship and its cardinality shown in the diagram must be backed by a real SQL query result. Never show a cardinality badge based on naming convention alone.
- Relationships whose query returned `"?"` are still shown in the diagram but with a `?` badge and a visual indicator that cardinality is unverified.
- `quality_score: null` means the quality data was unavailable (permissions or no data) — no badge is shown for that table.
- The output HTML is fully standalone — embeds all JS from CDN on first load, then works offline.
- The script requires only Python 3 stdlib (json, argparse) — no pip installs needed.
- If the domain has no tables with column access, inform the user that permissions may be limiting visibility.

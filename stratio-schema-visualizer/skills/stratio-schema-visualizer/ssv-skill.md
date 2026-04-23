---
name: stratio-schema-visualizer
description: Use this skill to visually explore and understand the relational schema of tables in a Stratio data domain or collection. Triggers when the user asks to "show the schema", "visualize the tables", "draw an ER diagram", "show relationships between tables", "explore the data structure", "show the data model", "what tables are in my domain", "esquema relacional", "diagrama de entidades", or wants to understand how tables in a Stratio collection relate to each other. Also triggers when the user mentions "relational diagram", "entity relationship", "table structure", "column details", or simply asks to "see the data model" in a Stratio context. Use proactively whenever the user seems to be exploring an unfamiliar domain.
---

# Stratio Schema Visualizer

Generates an interactive, browser-based relational schema diagram from a Stratio data domain. Shows tables as nodes, columns with types and governance descriptions, and inferred FK relationships as directed edges. Output is a standalone HTML file — no server needed.

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

python3 "$SKILL_DIR/scripts/generate_schema_html.py" \
  --input /tmp/stratio_schema_input.json \
  --output /tmp/stratio_schema_$(echo "<domain_name>" | tr ' /' '__').html
```

Replace `<domain_name>` with the actual domain name (spaces and slashes replaced with underscores).

### Step 5 — Open in browser

```bash
OUTPUT_FILE="/tmp/stratio_schema_<domain_name>.html"
xdg-open "$OUTPUT_FILE" 2>/dev/null || python3 -m webbrowser "$OUTPUT_FILE" 2>/dev/null || echo "Open manually: $OUTPUT_FILE"
```

Tell the user:
> "The schema visualization is open in your browser. You can:
> - **Click any table** to see its full column list with types and descriptions
> - **Drag tables** to rearrange the layout
> - **Scroll** to zoom in/out
> - **Hover over connections** to see the relationship details
> - Use the **Fit** button to re-center the view, or **Layout** to switch between layout modes"

If any tables were skipped (permissions/timeout), mention them at the end.

## Notes

- **Correctness is non-negotiable.** Every relationship and its cardinality shown in the diagram must be backed by a real SQL query result. Never show a cardinality badge based on naming convention alone.
- Relationships whose query returned `"?"` are still shown in the diagram but with a `?` badge and a visual indicator that cardinality is unverified.
- The output HTML is fully standalone — embeds all JS from CDN on first load, then works offline.
- The script requires only Python 3 stdlib (json, argparse) — no pip installs needed.
- If the domain has no tables with column access, inform the user that permissions may be limiting visibility.

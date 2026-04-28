# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This repo contains Claude Code **skills** (plugins) built for Stratio's data platform. The primary skill is `stratio-schema-visualizer` (SSV), which generates interactive browser-based ER diagrams from a Stratio data domain. A secondary skill, `stratio-brand`, provides Stratio corporate brand assets and guidelines.

## MCP server

The `StratioData` MCP server is configured in `.mcp.json` and must be in `✓ Connected` state for the SSV skill to work. It exposes the tools the skill calls: `list_domains`, `list_domain_tables`, `get_tables_details`, `get_tables_quality_details`, `get_table_columns_details`, `execute_sql`, and others.

## Running the HTML generator manually

```bash
# Single domain (technical only)
python3 stratio-schema-visualizer/skills/stratio-schema-visualizer/scripts/generate_schema_html.py \
  --input /tmp/stratio_schema_tech.json \
  --output /tmp/stratio_schema_<domain>.html

# Dual-view (technical + semantic)
python3 stratio-schema-visualizer/skills/stratio-schema-visualizer/scripts/generate_schema_html.py \
  --input /tmp/stratio_schema_tech.json \
  --input-semantic /tmp/stratio_schema_sem.json \
  --output /tmp/stratio_schema_<domain>.html
```

Requires only Python 3 stdlib — no pip installs. Input schema is defined in `ssv-skill.md` Step 3. When `--input-semantic` is provided, the HTML embeds both datasets and shows a view selector in the header.

## Architecture — stratio-schema-visualizer

The skill is split into two files:

**`ssv-skill.md`** — agent instructions. Defines the 5-step workflow Claude follows: identify domain → fetch metadata via MCP → build JSON → infer+verify FK relationships via SQL → run the generator script → open in browser. This file is the source of truth for what Claude does; modify it to change skill behavior.

**`scripts/generate_schema_html.py`** — the HTML/CSS/JS generator. Contains a single large `TEMPLATE = r"""..."""` string with all the frontend code. Python substitutes `__PLACEHOLDER__` tokens and writes a fully standalone HTML file. All visual features (filters, panels, presentation mode, exports, i18n) live here.

### Key frontend patterns inside the template

- **i18n**: `I18N` (static labels) and `I18N_DYN` (function-valued, for dynamic content) dictionaries with `es`/`en` keys. `applyLang()` iterates `[data-i18n]` attributes. Panels are re-rendered on language switch.
- **Filters**: CSS body-class pattern — `toggleFilter(key)` adds/removes classes like `body.hide-types`, `body.hide-nonkey`, `body.hide-unverified`. CSS rules do the actual hiding.
- **Relationships**: SVG `<g>` elements with `class="unverified-rel"` (for the filter) and `data-pres-idx` (for presentation mode step targeting).
- **Presentation mode**: `PRES` state object with `steps[]` built by `buildSteps()`. `applyStep(n)` shows/hides table cards and SVG groups by index.
- **Analysis panel**: single right-side panel (`#analysis-panel`) with two tabs — Summary and Schema Health — replacing what were previously two separate panels. `toggleAnalysisPanel(tab)` opens/closes it; `switchTab(tab)` switches between `'summary'` and `'health'` panes.
- **Quality badges**: color thresholds — green ≥ 80, yellow 40–79, red < 40. `quality_score: null` = no badge shown. The quality tooltip respects the `FILTERS.descs` toggle — `attachQualityTooltip()` guards `mouseenter` and `mousemove` with `if (!FILTERS.descs) return`.

### Dual-view (technical + semantic)

The HTML embeds two datasets injected as `__DATA_JSON_TECH__` and `__DATA_JSON_SEM__` placeholders, plus a boolean `__HAS_SEMANTIC__`. At runtime:

```js
const DATA_TECH    = __DATA_JSON_TECH__;
const DATA_SEM     = __DATA_JSON_SEM__;
const HAS_SEMANTIC = __HAS_SEMANTIC__;
let ACTIVE_VIEW = HAS_SEMANTIC ? 'sem' : 'tech';
let DATA = HAS_SEMANTIC ? DATA_SEM : DATA_TECH;
```

`byName`, `colIdx`, `fkCols`, and `JUNCTION_TABLES` are mutable `let` variables rebuilt by `rebuildLookups()` whenever `DATA` changes. `switchView(v)` reassigns `DATA`, calls `rebuildLookups()` + `resetLayout()` + `renderHealthPanel()` + `renderSummaryPanel()` + `updateHeaderStats()`. The segmented control (CSS class `view-sel` / `view-btn`) in the header is hidden when `HAS_SEMANTIC` is false.

### Domain-qualified SQL

`execute_sql` queries for cardinality verification must use domain-qualified table names: `FROM semantic_demo_health.visitas`, not just `FROM visitas`. Without the qualifier, the Stratio virtualizer throws "Table or view not found".

### Cardinality rule (non-negotiable)

Every relationship in the semantic view must be backed by a real `execute_sql` result. Never infer or guess cardinality from naming conventions. Unverified relationships get `cardinality: "?"` and a grey badge. In the technical view, all cardinalities are always `"?"` — SQL is not available on physical tables.

## Skill trigger

The skill auto-triggers when the user asks to visualize a schema, draw an ER diagram, explore a domain's data model, or similar — see the `description` frontmatter in `ssv-skill.md` for the full trigger list.

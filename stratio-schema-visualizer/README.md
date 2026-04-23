# Stratio Schema Visualizer (SSV)

Skill de Claude Code que genera un **diagrama ER interactivo** a partir de los metadatos de un dominio de datos de Stratio, mostrando tablas, columnas y relaciones con cardinalidad verificada.

---

## Cómo funciona

La skill sigue un flujo de 5 pasos cada vez que se invoca:

### 1. Identificación del dominio
El usuario debe indicar qué colección/dominio quiere visualizar. Si no lo especifica, la skill lista los dominios disponibles (vía `stratio_data-list_domains`) y espera a que el usuario elija uno antes de continuar.

### 2. Recopilación de metadatos
Para el dominio seleccionado se invocan en paralelo:
- `stratio_data-list_domain_tables` — lista de tablas
- `stratio_data-get_tables_details` — descripciones de negocio y contexto de governance
- `stratio_data-get_table_columns_details` (por cada tabla) — columnas, tipos y descripciones

### 3. Inferencia de relaciones FK
La skill detecta relaciones candidatas entre tablas buscando patrones de nomenclatura en los nombres de columna:
- `<prefijo>_id` cuyo prefijo coincide con el nombre de otra tabla
- `<prefijo>_ref` cuyo prefijo coincide con el último segmento del nombre de otra tabla (ej. `fac_ref` → `tbl_fac`)

### 3b. Verificación de cardinalidad con datos reales
**Este paso es el más importante de la skill.** Por cada relación candidata se ejecuta una query SQL real sobre los datos:

```sql
SELECT
  COUNT(*)                      AS total_rows,
  COUNT(DISTINCT <columna_fk>)  AS distinct_vals
FROM <tabla_origen>
WHERE <columna_fk> IS NOT NULL
```

El resultado determina la cardinalidad con certeza:

| Resultado | Cardinalidad | Badge en el diagrama |
|-----------|-------------|----------------------|
| `total_rows == distinct_vals` | **1:1** | ámbar `1` — `1` |
| `total_rows > distinct_vals` | **N:1** | ámbar `N` — `1` |
| Query falla o sin autorización | **desconocida** | gris `?` — `?` |

### 4. Generación del HTML
Se ejecuta el script `scripts/generate_schema_html.py` que produce un fichero HTML standalone con el diagrama completo.

### 5. Apertura en el navegador
El fichero se abre automáticamente en el navegador del usuario.

---

## Qué muestra el diagrama

### Tarjetas de tabla
Cada tabla del dominio aparece como una tarjeta con:
- **Cabecera** con el nombre de la tabla y el número de columnas. Al pasar el cursor se muestra la descripción de negocio de governance.
- **Fila por columna** con:
  - Indicador `PK` (clave primaria) o `FK` (clave foránea participante en una relación)
  - Nombre de la columna en tipografía monoespaciada
  - Tipo de dato con código de color por categoría:
    - 🔵 Azul — `STRING`, `VARCHAR`, `TEXT`
    - 🟢 Verde — `INT`, `BIGINT`, `LONG`
    - 🟡 Amarillo — `FLOAT`, `DECIMAL`, `NUMERIC`
    - 🟣 Morado — `BOOLEAN`
    - 🔴 Rojo — `DATE`, `TIMESTAMP`, `DATETIME`

### Flechas de relación
Cada relación FK se dibuja como una curva bézier que conecta exactamente la columna FK de origen con la columna PK de destino. Incluye:
- **Badges de cardinalidad** en cada extremo (`N`/`1`, `1`/`1` o `?`/`?`)
- **Puntos de anclaje** en los bordes de las tarjetas
- **Efecto hover**: al pasar el cursor sobre una flecha, se resaltan en naranja las dos columnas conectadas y la curva se intensifica

### Interactividad
| Acción | Resultado |
|--------|-----------|
| **Clic en una flecha** / hover | Resalta columnas conectadas |
| **Arrastrar** una tarjeta por su cabecera | Reposiciona la tabla en el canvas |
| **Botón Reset** | Restaura el layout inicial en cuadrícula |
| **Botón Fit** | Centra la vista sobre el contenido |
| **Scroll** en el canvas | Navega por el diagrama |

---

## Limitaciones conocidas

### 1. Acceso a datos requerido para cardinalidad verificada
La verificación de cardinalidad mediante queries SQL requiere que el dominio tenga **permisos de lectura de datos** activos en la API key configurada. Si el dominio solo expone metadatos (governance), las queries fallan con error de autorización y los badges aparecen en gris con `?`.

> **Impacto:** La cardinalidad mostrada es desconocida, no incorrecta. El diagrama nunca muestra una cardinalidad no verificada como si fuera cierta.

### 2. Inferencia de relaciones basada en convenciones de nomenclatura
La skill detecta relaciones FK a partir de patrones en los nombres de columna (`_id`, `_ref`). Si un dominio usa convenciones distintas (ej. `id_cliente`, `fk_pedido`) o no sigue ninguna convención, las relaciones no se detectarán aunque existan.

> **Impacto:** Pueden faltar relaciones en el diagrama. No aparecerán relaciones incorrectas, pero sí podrían faltar algunas reales.

### 3. Cardinalidad N:M no soportada
La inferencia actual solo detecta relaciones directas columna-a-columna. Las relaciones muchos-a-muchos (N:M) implementadas mediante tablas intermedias se mostrarán como dos relaciones N:1 independientes, no como una N:M.

### 4. Solo relaciones de primer nivel
La skill analiza las FK directas de cada tabla pero no recorre la jerarquía de relaciones de forma recursiva. Si la tabla A referencia a B y B referencia a C, ambas relaciones se muestran, pero no se infiere ninguna relación transitiva entre A y C.

### 5. Tablas sin acceso a metadatos
Si el usuario no tiene permisos sobre alguna tabla del dominio, esa tabla se omite del diagrama y se informa al final del proceso. Las relaciones que implicaban esa tabla también se omiten.

### 6. Dependencia del MCP de StratioData
La skill requiere que el servidor MCP `StratioData` esté conectado y accesible. Si el servidor no está disponible o la API key ha expirado, la skill no puede ejecutarse.

---

## Requisitos técnicos

- **Claude Code** con el MCP `StratioData` configurado y con estado `✓ Connected`
- **Python 3** (stdlib únicamente, sin dependencias externas)
- **Navegador web** para visualizar el HTML generado
- El HTML generado es un fichero standalone que no requiere servidor ni conexión después de la primera carga (las librerías JS se cargan desde CDN en la primera apertura)

---

## Estructura del proyecto

```
stratio-schema-visualizer/
├── .claude-plugin/
│   └── plugin.json                  # Metadatos del plugin
└── skills/
    └── stratio-schema-visualizer/
        ├── ssv-skill.md             # Instrucciones de la skill para Claude
        ├── scripts/
        │   └── generate_schema_html.py   # Generador del HTML interactivo
        └── evals/
            └── evals.json           # Casos de prueba
```

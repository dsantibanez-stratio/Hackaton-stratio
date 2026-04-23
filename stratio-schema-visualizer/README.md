# Stratio Schema Visualizer (SSV)

Skill de Claude Code que genera un **diagrama ER interactivo** a partir de los metadatos de un dominio de datos de Stratio. Muestra tablas, columnas, relaciones con cardinalidad verificada y calidad de datos — todo en un único fichero HTML standalone que se abre directamente en el navegador.

---

## Cómo funciona

La skill sigue un flujo automático cada vez que se invoca. El usuario solo tiene que indicar el nombre del dominio.

### 1. Identificación del dominio
Si el usuario no especifica el dominio, la skill lista los disponibles y espera a que elija uno. Si da un nombre parcial, busca la coincidencia más probable y confirma antes de continuar.

### 2. Recopilación de metadatos
Se invocan en paralelo tres llamadas al MCP de Stratio:
- `list_domain_tables` — lista de tablas autorizadas
- `get_tables_details` — descripciones de negocio y contexto de governance
- `get_tables_quality_details` — score de calidad de datos por tabla (0–100)

Después, para cada tabla en paralelo:
- `get_table_columns_details` — columnas, tipos y descripciones de governance

### 3. Inferencia de relaciones FK
La skill detecta relaciones candidatas por convención de nomenclatura:
- `<prefijo>_id` cuyo prefijo coincide con el nombre de otra tabla
- `<prefijo>_ref` cuyo prefijo coincide con el segmento final de otra tabla (`fac_ref` → `tbl_fac`)

### 3b. Verificación de cardinalidad con datos reales
Por cada relación candidata se ejecuta una query SQL real:

```sql
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT <columna_fk>) AS distinct_vals
FROM <tabla_origen> WHERE <columna_fk> IS NOT NULL
```

| Resultado | Cardinalidad | Badge |
|-----------|-------------|-------|
| `total_rows == distinct_vals` | **1:1** | azul `1 — 1` |
| `total_rows > distinct_vals` | **N:1** | azul `N — 1` |
| Query falla / sin autorización | **desconocida** | gris `? — ?` |

> La cardinalidad nunca se muestra como verificada si no hay una query real que la respalde.

### 4. Generación y apertura del HTML
Se ejecuta `scripts/generate_schema_html.py`, que produce un fichero HTML completamente standalone, y se abre automáticamente en el navegador.

---

## Qué muestra el diagrama

### Cabecera
La cabecera identifica el dominio visualizado con el título **"Esquema relacional · \<Nombre de la colección\>"** junto al chip con el nombre técnico del dominio. También muestra el recuento de tablas, columnas y relaciones del esquema.

### Tarjetas de tabla
Cada tabla aparece como una tarjeta arrastrable con:
- **Cabecera oscura** con el nombre de la tabla, el número de columnas y, opcionalmente, el **badge de calidad de datos** con código de color
- **Fila por columna** con etiqueta `PK` / `FK`, nombre en tipografía monoespaciada y tipo de dato con chip de color:

| Color | Tipos |
|-------|-------|
| 🔵 Azul | `STRING`, `VARCHAR`, `TEXT` |
| 🟢 Verde | `INT`, `INTEGER`, `BIGINT` |
| 🟡 Amarillo | `FLOAT`, `DECIMAL`, `NUMERIC` |
| 🟣 Morado | `BOOLEAN` |
| 🔴 Rojo | `DATE`, `TIMESTAMP`, `DATETIME` |

### Badge de calidad de datos
Aparece en la cabecera de cada tarjeta cuando el dominio expone datos de calidad:

| Color | Rango | Significado |
|-------|-------|-------------|
| 🟢 Verde | ≥ 80 % | Calidad alta |
| 🟡 Amarillo | 40 – 79 % | Calidad media |
| 🔴 Rojo | < 40 % | Calidad baja |

Al pasar el cursor sobre el badge aparece un tooltip: *"Calidad de datos: X%"*. La leyenda del diagrama también explica la escala de colores.

### Flechas de relación
Curvas bézier que conectan exactamente la columna FK de origen con la columna de destino, con:
- Badges de cardinalidad en cada extremo (`1:1`, `N:1` o `?`)
- Efecto hover que resalta en azul las dos columnas conectadas

---

## Funcionalidades interactivas

### Barra de filtros
Debajo de la cabecera, cuatro toggles aplican cambios en tiempo real sin recargar:

| Toggle | Efecto |
|--------|--------|
| **Tipos de dato** | Muestra/oculta los chips de tipo en cada columna |
| **Columnas no clave** | Muestra/oculta todas las filas que no son PK ni FK |
| **Descripciones** | Activa/desactiva los tooltips de governance al hacer hover |
| **Relaciones sin verificar** | Muestra/oculta las flechas con cardinalidad `?` |

### Panel Schema Health (⚕)
Panel lateral derecho con avisos automáticos sobre la calidad del modelo de datos, agrupados por categoría:

- **Clave primaria ausente** — tablas sin ninguna columna PK definida
- **Tablas aisladas** — tablas sin ninguna relación detectada
- **Cardinalidad no verificada** — relaciones cuya query SQL no pudo ejecutarse
- **Descripciones de governance ausentes** — columnas sin descripción en el catálogo

El botón de la cabecera muestra el número total de avisos como badge naranja.

### Panel Resumen del dominio (📖)
Panel lateral izquierdo generado automáticamente a partir de la metadata de governance ya recuperada, sin llamadas adicionales:

- **Párrafo introductorio** — número de entidades y relaciones del dominio
- **Entidad central** — tabla con más conexiones, con su descripción de governance
- **Lista de entidades** — todas las tablas con su primera frase descriptiva
- **Mapa de relaciones** — listado de `tabla_origen → tabla_destino` con la columna de enlace

### Modo presentación (▶)
Walkthrough paso a paso del modelo, pensado para explicar el esquema a una audiencia:

1. Se resalta la **entidad central** (tabla con más conexiones) y se atenúa el resto del diagrama
2. Cada pulsación de **Siguiente** añade una tabla conectada y su flecha, haciendo scroll suave hasta ella
3. La barra inferior muestra el paso actual, la descripción de la entidad y los controles de navegación
4. **Salir** restaura la vista completa

### Export DDL (📄)
Descarga un fichero `.sql` con los `CREATE TABLE` inferidos del esquema:
- Mapeo de tipos: `STRING → VARCHAR(255)`, `INTEGER → INT`, `DATE → DATE`, `BOOLEAN → BOOLEAN`, etc.
- Clave primaria como constraint `PRIMARY KEY`
- Descripciones de governance como comentarios SQL inline
- Bloque de cabecera con nombre del dominio y fecha de generación

### Export PNG (⬇)
Captura el canvas completo del diagrama (no solo la parte visible) a doble resolución y lo descarga como imagen PNG.

### Cambio de idioma (🇬🇧 / 🇪🇸)
Toda la interfaz — cabecera, botones, filtros, leyenda, paneles y modo presentación — alterna entre **español** e **inglés** en tiempo real con un único botón. La descripción de governance se mantiene en el idioma del catálogo.

---

## Resumen de controles

| Botón / Acción | Función |
|----------------|---------|
| ▶ Presentar | Activa el modo presentación paso a paso |
| 📖 Resumen | Abre el panel de resumen del dominio (izquierda) |
| ↺ Restablecer | Vuelve al layout automático inicial |
| ⊞ Ajustar | Encaja el diagrama completo en la ventana |
| ⚕ Salud del esquema | Abre el panel de avisos del modelo (derecha) |
| 📄 Exportar DDL | Descarga `schema_<dominio>.sql` |
| ⬇ Exportar PNG | Descarga captura PNG en alta resolución |
| 🇬🇧 / 🇪🇸 | Alterna el idioma de la interfaz |
| Arrastrar tarjeta | Reposiciona la tabla en el canvas |
| Hover sobre columna | Muestra descripción de governance (si activo) |
| Hover sobre badge `%` | Muestra el score de calidad de datos |
| Hover sobre flecha | Resalta las columnas conectadas |

---

## Limitaciones conocidas

### Cardinalidad no verificada sin acceso SQL
La verificación de cardinalidad requiere permisos de lectura de datos. Si el dominio solo expone metadatos, las queries fallan y los badges aparecen en gris con `?`. El diagrama nunca muestra una cardinalidad no verificada como si fuera cierta.

### Inferencia de relaciones por nomenclatura
Las FK se detectan por patrones en los nombres de columna (`_id`, `_ref`). Convenciones distintas pueden resultar en relaciones no detectadas. No aparecerán relaciones incorrectas, pero pueden faltar algunas reales.

### Sin soporte para relaciones N:M
Las relaciones muchos-a-muchos implementadas mediante tabla intermedia se muestran como dos relaciones `N:1` independientes.

### Tablas sin permisos
Las tablas a las que el usuario no tiene acceso se omiten del diagrama y se indica cuáles fueron al finalizar.

---

## Requisitos técnicos

- **Claude Code** con el MCP `StratioData` configurado y con estado `✓ Connected`
- **Python 3** (stdlib únicamente, sin dependencias externas para el generador)
- **Navegador web** moderno para visualizar el HTML generado
- Conexión a internet en la primera apertura del HTML (carga de fuentes y `html2canvas` desde CDN); funciona offline después

---

## Estructura del proyecto

```
stratio-schema-visualizer/
├── README.md                            # Este fichero
└── skills/
    └── stratio-schema-visualizer/
        ├── ssv-skill.md                 # Instrucciones detalladas del workflow para Claude
        ├── scripts/
        │   └── generate_schema_html.py  # Generador del HTML interactivo (toda la lógica visual)
        └── evals/
            └── evals.json               # Casos de prueba
```

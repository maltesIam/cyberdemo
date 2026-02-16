# Answer-With-Precision-BTH - V2

> **Version:** 2.0  
> **Estado:** Definicion funcional y tecnica completa  
> **Objetivo:** Documento unico de referencia para construir el plugin Answer-With-Precision-BTH

---

## 1) Resumen ejecutivo

Este documento define un sistema de preguntas y respuestas sobre datos de CyberDemo con:

- respuestas exactas sobre datos e insights (objetivo: 99% de queries validas),
- queries verificadas (OpenSearch/SQL) con validacion previa obligatoria,
- minimo de alucinaciones mediante abstencion controlada,
- arquitectura reutilizable por cualquier agente,
- alto determinismo operativo,
- mejora continua basada en uso real con versionado recuperable.

Arquitectura hibrida:

1. **Plugin con skills + tools** como interfaz universal para agentes.
2. **Motor Python determinista** como capa de ejecucion real.
3. **Catalogo de datos canonico + data dictionary versionado** como fuente de verdad.
4. **Abstencion controlada** para evitar respuestas inventadas.
5. **Mejora continua** con versionado de plugin por cada iteracion.

---

## 2) Objetivo del sistema

Construir una capacidad de preguntas y respuestas sobre datos de CyberDemo que:

- permita preguntar libremente por datos e insights,
- ejecute queries correctas con alta tasa de exito,
- no invente campos, metricas ni conclusiones,
- funcione de forma generica con OpenSearch, Postgres y otros motores relacionales,
- sea reusable por cualquier agente conectado al ecosistema,
- aprenda de cada interaccion y mejore sin romper lo que funciona.

---

## 3) Conceptos clave (glosario operativo)

| Concepto                       | Definicion                                                                                                                                    | Ejemplo                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Catalogo canonico**          | Fuente unica oficial de verdad de datos y semantica. Incluye datasets, campos, tipos, relaciones, metricas, joins, enums y campos deprecados. | `catalog.json` con definicion de indice `assets-inventory-v1`                             |
| **Data dictionary versionado** | Documento tecnico del catalogo con historial git. Permite trazabilidad, deteccion de breaking changes y auditoria de esquema.                 | `dictionary_v1.2.json` publicado en CI                                                    |
| **Plan semantico**             | Representacion neutral de intencion analitica independiente del motor. AST compilable a DSL u SQL.                                            | `{metric: "incident_count", filters: [{field: "severity", op: "eq", value: "critical"}]}` |
| **Compilador**                 | Transforma plan semantico a query valida por motor (OpenSearch DSL / SQL).                                                                    | `semantic_plan -> SELECT count(*) FROM incidents WHERE severity='critical'`               |
| **Abstencion controlada**      | Politica donde el agente NO responde cuando falta evidencia, falla validacion o hay ambiguedad. No es error; es calidad.                      | "No puedo calcular ese KPI: el campo X no existe en el catalogo."                         |
| **Provenance**                 | Trazabilidad completa: query ejecutada, motor, filtros, timestamp, hash de resultados y fuente.                                               | `{query_hash: "abc123", engine: "opensearch", executed_at: "2026-02-08T14:00Z"}`          |
| **Dry-run**                    | Ejecucion de prueba sin resultados reales para validar que la query es sintactica y semanticamente correcta.                                  | OpenSearch: `_validate/query`; SQL: `EXPLAIN`                                             |
| **Confidence gate**            | Umbral numerico de confianza. Por debajo del umbral se activa abstencion.                                                                     | `confidence_threshold: 0.7`                                                               |
| **Golden test**                | Pregunta de negocio real con respuesta esperada conocida. Se usa como regression test.                                                        | "Cuantos incidentes criticos hay abiertos?" -> esperado: 5                                |

---

## 4) Preguntas originales y respuestas consolidadas

### Pregunta 1: Catalogo canonico, data dictionary, abstencion

> "que es el catalogo de datos canonico? A que te refieres con data dictionary versionado? que contendría? como se generaría? que es abstencion controlada?"

#### 1) Catalogo de datos canonico

Fuente unica de verdad del modelo de datos autorizado. Incluye:

- datasets/indices/tablas disponibles,
- definicion de cada campo (nombre, tipo, nullable, enum, descripcion semantica),
- relaciones entre entidades (joins tecnicos y relaciones de negocio),
- metricas canonicas y su formula,
- ejemplos de query validos,
- campos deprecados/prohibidos.

Impide que el agente improvise estructuras inexistentes.

#### 2) Data dictionary versionado

Documento tecnico del catalogo, gestionado con versionado git.

**Contenido minimo:**

| Seccion         | Contenido                                                                               |
| --------------- | --------------------------------------------------------------------------------------- |
| Dataset         | Nombre logico/fisico, descripcion funcional, owner, SLA de actualizacion                |
| Campos          | Nombre, tipo, nullable, enum, ejemplo, descripcion semantica, estado (activo/deprecado) |
| Relaciones      | Joins tecnicos (FK), relaciones semanticas de negocio                                   |
| Metricas        | Nombre, formula, dimensiones, reglas de negocio                                         |
| Temporalidad    | Timezone, convenciones temporales, granularidad                                         |
| Queries ejemplo | Queries validadas por motor                                                             |

**Generacion (semi-automatica):**

1. Extraer esquema tecnico (OpenSearch mappings / SQL schemas / modelos backend).
2. Enriquecer con semantica funcional y reglas de negocio.
3. Publicar salida dual: `json` (maquina) + `md` (personas).
4. Validar consistencia con tests automaticos.
5. Versionar en git con changelog.

**Frecuencia de actualizacion:**

- CI por cada merge con cambio de esquema (obligatorio).
- Job diario de drift detection.
- On-demand antes de demos o despliegues.

#### 3) Abstencion controlada

Politica donde el agente no da conclusion firme cuando:

- campo no existe en catalogo,
- query no pasa validacion,
- ambiguedad de definicion (ej: MTTR operativo vs total),
- confidence por debajo del umbral,
- datos insuficientes para la pregunta.

Respuesta tipica: "No puedo calcular ese KPI: [razon concreta]. Alternativa: [sugerencia]."

### Pregunta 2: Genericidad multi-motor y virtualizador

> "quiero que sea generico para opensearch, postgres y cualquier relacional. hace falta un virtualizador de queries?"

**Si**, la genericidad es la mejor decision de arquitectura.

**Enfoque:**

1. **Capa semantica unica** (plan neutral).
2. **Compiladores por motor** (semantico -> DSL, semantico -> SQL).
3. **Validadores por motor** (tipos, campos, funciones, limites).
4. **Dry-run por motor** (SQL: EXPLAIN; OpenSearch: \_validate/query + size:0).

**Virtualizador semantico (recomendado):** servicio que recibe consulta semantica, compila, valida, ejecuta y normaliza. Ligero y propio.

**Federacion completa (opcional):** Trino/Denodo; util para cross-engine joins masivos; overkill en fase inicial.

### Pregunta 3: Plugin vs script vs skill textual

> "que seria mejor, un programa python con comando custom, o un plugin con skills completas?"

**Hibrido**: plugin con skills + motor Python determinista como backend.

- Plugin/skills = interfaz universal multiagente.
- Motor Python = ejecucion determinista real.
- Script suelto = solo para prototipo; no para plataforma.
- Skill textual sin validacion = alto riesgo de alucinacion.

---

## 5) Arquitectura por capas

### 5.1 Capa 1: Interfaz de agente (plugin + skills + tools)

Expone capacidades estables para todos los agentes con contratos JSON estrictos.

### 5.2 Capa 2: Motor Python determinista

| Componente          | Funcion                                             |
| ------------------- | --------------------------------------------------- |
| Intent parser       | Extrae intencion analitica de la pregunta           |
| Semantic planner    | Genera AST neutral compilable                       |
| Compiladores SQL/OS | Transforman plan a query por motor                  |
| Validadores         | Verifican campos, tipos, funciones contra catalogo  |
| Dry-run manager     | Ejecuta validacion sin resultados                   |
| Executor            | Ejecuta query real con timeout y limites            |
| Result normalizer   | Unifica formato de resultados entre motores         |
| Confidence gate     | Decide si la confianza es suficiente para responder |

### 5.3 Capa 3: Fuente de verdad

Catalogo canonico + data dictionary versionado.

### 5.4 Capa 4: Calidad y gobernanza

Tests unitarios de compiladores/validadores, tests de integracion por motor, golden tests de preguntas reales, alertas de drift, logs de provenance.

### 5.5 Capa 5: Mejora continua

Captura de interacciones, scoring de calidad, propuesta de mejoras, simulacion de impacto, aplicacion controlada, versionado de plugin.

---

## 6) Plugin: estructura y componentes

### 6.1 Estructura de archivos

```
extensions/Answer-With-Precision-BTH/
  SoulInTheBot.plugin.json
  skills/
    ask-data-insight/SKILL.md
    run-data-query/SKILL.md
    explain-metric/SKILL.md
    catalog-discovery/SKILL.md
    debug-query-failure/SKILL.md
    compare-periods/SKILL.md
    anomaly-investigator/SKILL.md
    build-executive-brief/SKILL.md
    governance-audit/SKILL.md
    data-source-health/SKILL.md
    continuous-improvement/SKILL.md
  src/
    hooks.ts
    config.ts
  tests/
    skills.test.ts
    hooks.test.ts
    integration.test.ts
  mcps/
    catalog-mcp/
    query-planner-mcp/
    query-validator-mcp/
    query-executor-mcp/
    insight-mcp/
    provenance-mcp/
    governance-mcp/
    continuous-improvement-mcp/
```

### 6.2 Skills completas (11)

| #   | Skill                    | Que hace                                               | MCPs que usa                                               |
| --- | ------------------------ | ------------------------------------------------------ | ---------------------------------------------------------- |
| 1   | `ask-data-insight`       | Pregunta de negocio a insight con evidencia            | catalog, planner, validator, executor, insight, provenance |
| 2   | `run-data-query`         | Ejecuta query explicita con validacion estricta        | validator, executor, provenance                            |
| 3   | `explain-metric`         | Explica definicion canonica de una metrica             | catalog, governance                                        |
| 4   | `catalog-discovery`      | Explora datasets, campos, joins y disponibilidad       | catalog                                                    |
| 5   | `debug-query-failure`    | Diagnostica y corrige query fallida                    | validator, planner, executor, provenance                   |
| 6   | `compare-periods`        | Comparativa temporal vs periodo anterior               | planner, validator, executor, insight                      |
| 7   | `anomaly-investigator`   | Detecta outliers/anomalias y posibles causas           | planner, executor, insight, provenance                     |
| 8   | `build-executive-brief`  | Resumen ejecutivo con metricas auditables              | insight, provenance, governance                            |
| 9   | `governance-audit`       | Verifica cumplimiento de reglas de calidad/seguridad   | governance, provenance, catalog                            |
| 10  | `data-source-health`     | Estado de fuentes, frescura, cobertura y drift         | catalog, governance                                        |
| 11  | `continuous-improvement` | Aprende de cada interaccion, propone mejoras, versiona | provenance, governance, catalog, continuous-improvement    |

### 6.3 Hooks del plugin

| Hook           | Funcion                                          | Obligatorio |
| -------------- | ------------------------------------------------ | ----------- |
| `PreToolUse`   | Bloquea ejecucion sin validate + dry_run previo  | Si          |
| `PostToolUse`  | Registra provenance obligatorio                  | Si          |
| `PreResponse`  | Verifica que respuesta tiene evidencia ejecutada | Si          |
| `SessionStart` | Carga version activa del data dictionary         | Si          |
| `SessionEnd`   | Emite resumen de trazabilidad                    | Si          |
| `SessionEnd`   | Envia interaccion a continuous-improvement-mcp   | Si          |

### 6.4 Configuracion central

| Parametro                       | Tipo     | Default                  | Descripcion            |
| ------------------------------- | -------- | ------------------------ | ---------------------- |
| `default_engine`                | enum     | `opensearch`             | Motor por defecto      |
| `allowed_engines`               | string[] | `[opensearch, postgres]` | Motores permitidos     |
| `max_rows_returned`             | int      | `1000`                   | Limite de filas        |
| `max_query_time_ms`             | int      | `30000`                  | Timeout de query       |
| `require_dry_run`               | bool     | `true`                   | Dry-run obligatorio    |
| `require_provenance`            | bool     | `true`                   | Provenance obligatorio |
| `abstention_threshold`          | float    | `0.7`                    | Umbral de confianza    |
| `dictionary_version_pin`        | string   | `latest`                 | Version del dictionary |
| `timezone_canonical`            | string   | `UTC`                    | Timezone por defecto   |
| `pii_policy_mode`               | enum     | `mask`                   | Politica de PII        |
| `sql_dialect_default`           | string   | `postgresql`             | Dialecto SQL default   |
| `relational_dialect_allowlist`  | string[] | `[postgresql, mysql]`    | Dialectos permitidos   |
| `improvement_auto_apply`        | bool     | `false`                  | Auto-aplicar mejoras   |
| `improvement_requires_approval` | bool     | `true`                   | Mejoras con aprobacion |
| `plugin_versioning_mode`        | enum     | `semantic`               | Modo de versionado     |
| `version_retention_policy`      | string   | `keep_last_10`           | Retencion de versiones |

---

## 7) MCPs (8 servidores Python deterministas)

### 7.1 MCP A: `catalog-mcp` (fuente de verdad)

**Tools:**

| Tool                     | Descripcion                                     |
| ------------------------ | ----------------------------------------------- |
| `list_datasets`          | Lista datasets/indices/tablas disponibles       |
| `describe_dataset`       | Schema completo de un dataset                   |
| `list_fields`            | Campos de un dataset con tipos y metadata       |
| `get_metric_definition`  | Definicion canonica de una metrica              |
| `get_join_paths`         | Relaciones tecnicas de enlace entre datasets    |
| `get_semantic_relations` | Relaciones de negocio/semantica entre entidades |
| `get_field_semantics`    | Significado funcional de un campo               |
| `get_enum_values`        | Valores posibles de un campo enum               |
| `get_dictionary_version` | Version actual del data dictionary              |
| `get_data_freshness`     | Frescura de datos por dataset                   |

**Introspeccion por motor:**

| Motor      | Introspector                        | Fuente                             |
| ---------- | ----------------------------------- | ---------------------------------- |
| OpenSearch | `schema_introspector_opensearch.py` | `_mapping`, `_field_caps`          |
| Postgres   | `schema_introspector_postgres.py`   | `information_schema`, `pg_catalog` |
| Relacional | `schema_introspector_relational.py` | SQLAlchemy Inspector + dialect     |

**Programas:** `catalog_loader.py`, `dictionary_service.py`, `join_graph.py`, `semantic_relations_graph.py`, `field_semantics_service.py`, `freshness_checker.py`.

**Scripts:** `build_data_dictionary.py`, `validate_data_dictionary.py`, `publish_dictionary_version.py`.

### 7.2 MCP B: `query-planner-mcp` (plan semantico neutral)

**Tools:**

| Tool                     | Descripcion                            |
| ------------------------ | -------------------------------------- |
| `parse_intent`           | Extrae intencion analitica de pregunta |
| `build_semantic_plan`    | Genera AST neutral                     |
| `optimize_semantic_plan` | Optimiza plan                          |
| `compile_to_opensearch`  | Compila a OpenSearch DSL               |
| `compile_to_postgres`    | Compila a SQL Postgres                 |
| `compile_to_relational`  | Compila a SQL generico                 |

**Compiladores por motor:**

| Motor      | Compilador                                   |
| ---------- | -------------------------------------------- |
| OpenSearch | `compiler_opensearch.py` (DSL JSON)          |
| Postgres   | `compiler_postgres.py` (SQL Postgres)        |
| Relacional | `compiler_relational.py` (dialect-aware SQL) |

**Programas:** `intent_parser.py`, `semantic_ast.py`, `plan_builder.py`, `plan_optimizer.py`, `query_template_library.py`.

**Scripts:** `rebuild_query_templates.py`, `lint_semantic_plans.py`.

### 7.3 MCP C: `query-validator-mcp` (garantia de no invencion)

**Tools:**

| Tool                        | Descripcion                               |
| --------------------------- | ----------------------------------------- |
| `validate_opensearch_query` | Valida query OpenSearch contra catalogo   |
| `validate_postgres_query`   | Valida query SQL Postgres contra catalogo |
| `validate_relational_query` | Valida query SQL generico                 |
| `dry_run_opensearch`        | Dry-run en OpenSearch                     |
| `dry_run_postgres`          | Dry-run en Postgres                       |
| `dry_run_relational`        | Dry-run generico                          |
| `enforce_guardrails`        | Aplica reglas de seguridad/limite         |
| `repair_query`              | Intenta reparar query invalida            |

**Validacion por motor:**

| Motor      | Validador                 | Dry-run                      |
| ---------- | ------------------------- | ---------------------------- |
| OpenSearch | `validator_opensearch.py` | `_validate/query` + `size:0` |
| Postgres   | `validator_postgres.py`   | `EXPLAIN` controlado         |
| Relacional | `validator_relational.py` | `EXPLAIN` o equivalente      |

**Programas:** `guardrail_engine.py`, `query_repair.py`, `policy_rules.py`.

**Scripts:** `run_validation_suite.py`, `check_guardrail_coverage.py`.

### 7.4 MCP D: `query-executor-mcp` (ejecucion real)

**Tools:**

| Tool                  | Descripcion                    |
| --------------------- | ------------------------------ |
| `execute_opensearch`  | Ejecuta en OpenSearch          |
| `execute_postgres`    | Ejecuta en Postgres            |
| `execute_relational`  | Ejecuta en relacional generico |
| `normalize_result`    | Unifica formato de resultados  |
| `paginate_result`     | Paginacion de resultados       |
| `sample_rows`         | Muestra de filas               |
| `get_execution_stats` | Estadisticas de ejecucion      |

**Ejecutores por motor:**

| Motor      | Ejecutor                 |
| ---------- | ------------------------ |
| OpenSearch | `executor_opensearch.py` |
| Postgres   | `executor_postgres.py`   |
| Relacional | `executor_relational.py` |

**Programas:** `result_normalizer.py`, `pagination_service.py`, `execution_stats.py`.

**Scripts:** `replay_known_queries.py`, `benchmark_execution_latency.py`.

### 7.5 MCP E: `insight-mcp` (insights deterministas)

**Tools:** `compute_kpi`, `compare_periods`, `detect_anomalies`, `build_root_cause_hypotheses`, `generate_business_summary`, `score_confidence`.

Motor-agnostic: usa resultados normalizados del ejecutor.

**Programas:** `kpi_engine.py`, `time_compare.py`, `anomaly_engine.py`, `hypothesis_engine.py`, `summary_generator.py`, `confidence_model.py`.

**Scripts:** `run_kpi_regression_tests.py`, `run_anomaly_backtests.py`.

### 7.6 MCP F: `provenance-mcp` (auditabilidad total)

**Tools:** `record_query_provenance`, `get_query_provenance`, `get_answer_evidence`, `trace_decision_path`, `export_audit_bundle`.

Guarda: motor, dialecto, query compilada, query ejecutada, parametros, timestamp, hash de resultados.

**Programas:** `provenance_store.py`, `evidence_linker.py`, `decision_trace.py`, `audit_exporter.py`.

**Scripts:** `purge_old_provenance.py`, `verify_provenance_integrity.py`.

### 7.7 MCP G: `governance-mcp` (calidad, drift, abstencion)

**Tools:** `check_schema_drift`, `check_data_quality`, `check_metric_contracts`, `evaluate_abstention`, `validate_response_policy`.

**Programas:** `drift_detector.py`, `quality_rules_engine.py`, `metric_contract_checker.py`, `abstention_engine.py`, `response_policy_enforcer.py`.

**Scripts:** `nightly_drift_scan.py`, `quality_report.py`, `contract_compatibility_report.py`.

### 7.8 MCP H: `continuous-improvement-mcp` (mejora continua)

**Tools:** `capture_interaction_outcome`, `score_interaction_quality`, `propose_improvements`, `simulate_improvement_impact`, `apply_improvement_patch`, `create_plugin_version`, `list_plugin_versions`, `rollback_plugin_version`.

**Datos almacenados:** conversacion, queries compiladas/ejecutadas, resultados/errores, decisiones de abstencion, governance signals, provenance completo, evaluacion de exito.

**Programas:** `interaction_logger.py`, `quality_scorer.py`, `improvement_recommender.py`, `improvement_simulator.py`, `version_manager.py`, `rollback_manager.py`.

**Scripts:** `daily_improvement_report.py`, `apply_approved_improvements.py`, `tag_plugin_version.py`, `rollback_to_version.py`.

---

## 8) Flujo determinista obligatorio

Todas las skills operan en este flujo fijo:

```
1. DISCOVER  -> catalog-mcp: obtener esquema
2. PLAN      -> query-planner-mcp: generar plan semantico
3. VALIDATE  -> query-validator-mcp: validar + dry-run
4. EXECUTE   -> query-executor-mcp: ejecutar + normalizar
5. ANALYZE   -> insight-mcp: generar insight/KPI
6. RECORD    -> provenance-mcp: registrar evidencia
7. GOVERN    -> governance-mcp: verificar politica de respuesta
8. IMPROVE   -> continuous-improvement-mcp: registrar interaccion
```

**Si falla validacion/politica:**

- No ejecuta.
- Activa abstencion controlada.
- Devuelve explicacion y alternativa valida.
- Registra el fallo en provenance e improvement.

---

## 9) Contrato del plan semantico

```json
{
  "metric": "incident_count",
  "dimensions": ["severity", "status"],
  "filters": [
    { "field": "severity", "op": "eq", "value": "critical" },
    { "field": "created_at", "op": "gte", "value": "2026-02-01T00:00:00Z" }
  ],
  "time_range": { "start": "2026-02-01", "end": "2026-02-08" },
  "sort": [{ "field": "created_at", "order": "desc" }],
  "limit": 100,
  "engine_hint": "opensearch"
}
```

Este contrato es neutral y compilable a OpenSearch DSL o SQL sin ambiguedad.

---

## 10) Estrategia de exactitud 99%

| Regla                             | Implementacion                        |
| --------------------------------- | ------------------------------------- |
| Nunca ejecutar sin validacion     | Hook `PreToolUse` bloquea             |
| Salida estructurada obligatoria   | Schema JSON estricto en tools         |
| Dry-run siempre                   | `require_dry_run: true`               |
| Reintentos acotados               | Max 2 con repair_query                |
| Abstencion controlada             | `confidence_threshold: 0.7`           |
| Insights solo de datos ejecutados | Hook `PreResponse` verifica evidencia |
| Provenance en cada respuesta      | Hook `PostToolUse` registra           |
| Golden dataset de preguntas       | `scripts/run_kpi_regression_tests.py` |
| Deteccion de drift                | `scripts/nightly_drift_scan.py`       |

---

## 11) Criterios de exito

### 11.1 Funcionalidad

- [ ] 11 skills registradas y funcionales en el plugin.
- [ ] 8 MCPs operativos con todas las tools definidas.
- [ ] Catalogo canonico generado y versionado.
- [ ] Data dictionary con version control en git.
- [ ] Compiladores OpenSearch + Postgres + Relacional funcionales.
- [ ] Validadores por motor activos.
- [ ] Dry-run obligatorio operativo.
- [ ] Abstencion controlada habilitada.
- [ ] Flujo de 8 pasos determinista completo.

### 11.2 Calidad

- [ ] Golden tests pasando (min 20 preguntas de negocio).
- [ ] Tasa de queries validas >= 95%.
- [ ] Respuestas con provenance completo.
- [ ] Drift detection activo.
- [ ] Hook chain completa (Pre/Post/Session).

### 11.3 Mejora continua

- [ ] Captura de interacciones funcional.
- [ ] Scoring de calidad automatico.
- [ ] Propuesta de mejoras generada.
- [ ] Versionado de plugin operativo.
- [ ] Rollback funcional.

### 11.4 Performance

- [ ] Latencia end-to-end < 5s para query tipica.
- [ ] Dry-run < 500ms.
- [ ] Compilacion < 200ms.

---

## 12) Volumetria de componentes

| Tipo                     | Cantidad |
| ------------------------ | -------- |
| Skills                   | 11       |
| MCPs                     | 8        |
| Tools (total)            | 63       |
| Programas Python (total) | 47       |
| Scripts (total)          | 22       |
| Hooks                    | 6        |
| Parametros de config     | 16       |
| Introspectores por motor | 3        |
| Compiladores por motor   | 3        |
| Validadores por motor    | 3        |
| Ejecutores por motor     | 3        |

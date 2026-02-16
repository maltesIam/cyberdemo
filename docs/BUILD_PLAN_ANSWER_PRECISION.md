# Plan de Construccion - Answer-With-Precision-BTH

> **Definicion:** `Answer-With-Precision-BTH.md` (V2)  
> **Modelo:** 5 agentes de construccion en paralelo + 1 agente validador  
> **Regla de oro:** NADA se marca como completado sin validacion del Agente V

---

## 1) Roles de agentes

### Agentes de construccion

| Agente | Nombre                | Responsabilidad                                                         |
| ------ | --------------------- | ----------------------------------------------------------------------- |
| **A1** | MCP Core (A-D)        | catalog-mcp, query-planner-mcp, query-validator-mcp, query-executor-mcp |
| **A2** | MCP Extended (E-H)    | insight-mcp, provenance-mcp, governance-mcp, continuous-improvement-mcp |
| **A3** | Plugin + Skills       | Plugin structure, 11 skills, config, hooks                              |
| **A4** | Catalogo + Dictionary | Introspectores, generador de dictionary, validadores de schema, scripts |
| **A5** | Tests + Golden        | Tests unitarios, integracion, golden tests, performance benchmarks      |

### Agente validador

| Agente | Nombre    | Responsabilidad                               |
| ------ | --------- | --------------------------------------------- |
| **V**  | Validador | Verificacion completa contra la definicion V2 |

---

## 2) Reglas del Agente V (Validador)

### 2.1 Cuando actua

- Cada vez que un agente A1-A5 declara que una tarea esta completada.
- Al final de cada iteracion.
- Antes de cerrar cualquier fase.

### 2.2 Que verifica (obligatorio por cada tarea)

1. **Leer la definicion** en `Answer-With-Precision-BTH.md` V2 de la funcionalidad.
2. **Localizar el codigo** en el repositorio.
3. **Verificar en el codigo** que:
   - El archivo/modulo existe con el nombre correcto.
   - Todas las tools/funciones definidas estan implementadas (no solo algunas).
   - Los contratos de entrada/salida coinciden con la definicion.
   - Tests existen y pasan.
4. **Ejecutar tests** relacionados.
5. **Verificar integracion** (el modulo esta conectado, no es codigo muerto).
6. **Comparar contra la definicion** punto por punto.

### 2.3 Formato de validacion

```
### V-XXX: [Nombre tarea]
- Ref definicion: Seccion X.Y de Answer-With-Precision-BTH.md V2
- Archivos verificados: [lista]
- Tools/funciones verificadas: [lista vs definicion]
- Tests ejecutados: [lista y resultado]
- Integracion verificada: Si/No
- Cumplimiento: COMPLETO / PARCIAL (detalle) / RECHAZADO
- Fecha: YYYY-MM-DD
```

### 2.4 Rechazo

- Si PARCIAL o RECHAZADO: devuelve al agente con detalle de lo que falta.
- La tarea NO se marca completada.
- El agente corrige y redeclara.
- V vuelve a validar.

---

## 3) Fases de construccion

### Fase 0: Preparacion

| ID    | Tarea                                                                   | Agente | Dependencia |
| ----- | ----------------------------------------------------------------------- | ------ | ----------- |
| F0-01 | Leer Answer-With-Precision-BTH.md V2 completo                           | Todos  | -           |
| F0-02 | Crear estructura de directorios `extensions/Answer-With-Precision-BTH/` | A3     | F0-01       |
| F0-03 | Verificar que OpenSearch y Postgres estan accesibles                    | V      | -           |
| F0-04 | Verificar datos sinteticos existentes en indices                        | V      | -           |

### Fase 1: Catalogo + Dictionary (A4) + MCP A (A1)

| ID    | Tarea                                                         | Agente | Ref V2  | Validacion V                                                   |
| ----- | ------------------------------------------------------------- | ------ | ------- | -------------------------------------------------------------- |
| F1-01 | Introspector OpenSearch (`schema_introspector_opensearch.py`) | A4     | Sec 7.1 | V: archivo existe, lee \_mapping/\_field_caps, output correcto |
| F1-02 | Introspector Postgres (`schema_introspector_postgres.py`)     | A4     | Sec 7.1 | V: lee information_schema, output correcto                     |
| F1-03 | Introspector Relacional (`schema_introspector_relational.py`) | A4     | Sec 7.1 | V: SQLAlchemy Inspector, multi-dialect                         |
| F1-04 | `catalog_loader.py`                                           | A4     | Sec 7.1 | V: carga y unifica output de introspectores                    |
| F1-05 | `dictionary_service.py`                                       | A4     | Sec 7.1 | V: CRUD de dictionary con versionado                           |
| F1-06 | `join_graph.py`                                               | A4     | Sec 7.1 | V: relaciones tecnicas                                         |
| F1-07 | `semantic_relations_graph.py`                                 | A4     | Sec 7.1 | V: relaciones de negocio                                       |
| F1-08 | `field_semantics_service.py`                                  | A4     | Sec 7.1 | V: significado funcional de campos                             |
| F1-09 | `freshness_checker.py`                                        | A4     | Sec 7.1 | V: detecta stale data                                          |
| F1-10 | Script `build_data_dictionary.py`                             | A4     | Sec 7.1 | V: genera dictionary json+md                                   |
| F1-11 | Script `validate_data_dictionary.py`                          | A4     | Sec 7.1 | V: valida consistencia                                         |
| F1-12 | Script `publish_dictionary_version.py`                        | A4     | Sec 7.1 | V: versiona en git                                             |
| F1-13 | MCP A server: todas las 10 tools conectadas                   | A1     | Sec 7.1 | V: verifica las 10 tools listadas funcionan                    |
| F1-14 | Tests unitarios de MCP A                                      | A5     | Sec 7.1 | V: coverage >= 80%                                             |

### Fase 2: MCP B + C + D (A1) - Core de queries

| ID    | Tarea                                          | Agente | Ref V2      | Validacion V                        |
| ----- | ---------------------------------------------- | ------ | ----------- | ----------------------------------- |
| F2-01 | `intent_parser.py`                             | A1     | Sec 7.2     | V: parsea pregunta a intent struct  |
| F2-02 | `semantic_ast.py`                              | A1     | Sec 7.2     | V: AST neutral segun contrato Sec 9 |
| F2-03 | `plan_builder.py` + `plan_optimizer.py`        | A1     | Sec 7.2     | V: genera y optimiza plan           |
| F2-04 | `compiler_opensearch.py`                       | A1     | Sec 7.2     | V: compila plan a DSL JSON correcto |
| F2-05 | `compiler_postgres.py`                         | A1     | Sec 7.2     | V: compila plan a SQL Postgres      |
| F2-06 | `compiler_relational.py`                       | A1     | Sec 7.2     | V: compila plan a SQL multi-dialect |
| F2-07 | `query_template_library.py`                    | A1     | Sec 7.2     | V: templates reutilizables          |
| F2-08 | MCP B server: 6 tools conectadas               | A1     | Sec 7.2     | V: las 6 tools funcionan            |
| F2-09 | `validator_opensearch.py`                      | A1     | Sec 7.3     | V: valida contra catalogo           |
| F2-10 | `validator_postgres.py`                        | A1     | Sec 7.3     | V: valida contra catalogo           |
| F2-11 | `validator_relational.py`                      | A1     | Sec 7.3     | V: valida multi-dialect             |
| F2-12 | `guardrail_engine.py` + `policy_rules.py`      | A1     | Sec 7.3     | V: limites y seguridad              |
| F2-13 | `query_repair.py`                              | A1     | Sec 7.3     | V: repara queries invalidas         |
| F2-14 | MCP C server: 8 tools conectadas               | A1     | Sec 7.3     | V: las 8 tools funcionan            |
| F2-15 | `executor_opensearch.py`                       | A1     | Sec 7.4     | V: ejecuta con timeout              |
| F2-16 | `executor_postgres.py`                         | A1     | Sec 7.4     | V: ejecuta con timeout              |
| F2-17 | `executor_relational.py`                       | A1     | Sec 7.4     | V: ejecuta multi-dialect            |
| F2-18 | `result_normalizer.py`                         | A1     | Sec 7.4     | V: formato unificado                |
| F2-19 | `pagination_service.py` + `execution_stats.py` | A1     | Sec 7.4     | V: paginacion y stats               |
| F2-20 | MCP D server: 7 tools conectadas               | A1     | Sec 7.4     | V: las 7 tools funcionan            |
| F2-21 | Tests unitarios de MCP B + C + D               | A5     | Sec 7.2-7.4 | V: coverage >= 80%                  |
| F2-22 | Tests integracion compiladores por motor       | A5     | Sec 7.2-7.4 | V: 3 motores cubiertos              |

### Fase 3: MCP E + F + G + H (A2) - Insights, provenance, governance, improvement

| ID    | Tarea                                                     | Agente | Ref V2      | Validacion V              |
| ----- | --------------------------------------------------------- | ------ | ----------- | ------------------------- |
| F3-01 | `kpi_engine.py`                                           | A2     | Sec 7.5     | V: calcula KPIs correctos |
| F3-02 | `time_compare.py`                                         | A2     | Sec 7.5     | V: comparativa temporal   |
| F3-03 | `anomaly_engine.py`                                       | A2     | Sec 7.5     | V: detecta outliers       |
| F3-04 | `hypothesis_engine.py` + `summary_generator.py`           | A2     | Sec 7.5     | V: root cause + summary   |
| F3-05 | `confidence_model.py`                                     | A2     | Sec 7.5     | V: score de confianza     |
| F3-06 | MCP E server: 6 tools conectadas                          | A2     | Sec 7.5     | V: las 6 tools funcionan  |
| F3-07 | `provenance_store.py`                                     | A2     | Sec 7.6     | V: persiste provenance    |
| F3-08 | `evidence_linker.py` + `decision_trace.py`                | A2     | Sec 7.6     | V: linkea evidencia       |
| F3-09 | `audit_exporter.py`                                       | A2     | Sec 7.6     | V: exporta bundles        |
| F3-10 | MCP F server: 5 tools conectadas                          | A2     | Sec 7.6     | V: las 5 tools funcionan  |
| F3-11 | `drift_detector.py`                                       | A2     | Sec 7.7     | V: detecta drift          |
| F3-12 | `quality_rules_engine.py` + `metric_contract_checker.py`  | A2     | Sec 7.7     | V: reglas y contratos     |
| F3-13 | `abstention_engine.py` + `response_policy_enforcer.py`    | A2     | Sec 7.7     | V: abstencion funcional   |
| F3-14 | MCP G server: 5 tools conectadas                          | A2     | Sec 7.7     | V: las 5 tools funcionan  |
| F3-15 | `interaction_logger.py` + `quality_scorer.py`             | A2     | Sec 7.8     | V: captura y puntua       |
| F3-16 | `improvement_recommender.py` + `improvement_simulator.py` | A2     | Sec 7.8     | V: propone y simula       |
| F3-17 | `version_manager.py` + `rollback_manager.py`              | A2     | Sec 7.8     | V: versiona y rollback    |
| F3-18 | MCP H server: 8 tools conectadas                          | A2     | Sec 7.8     | V: las 8 tools funcionan  |
| F3-19 | Tests unitarios MCP E + F + G + H                         | A5     | Sec 7.5-7.8 | V: coverage >= 80%        |
| F3-20 | Scripts de MCP E-H (8 scripts)                            | A2     | Sec 7.5-7.8 | V: todos ejecutables      |

### Fase 4: Plugin + Skills + Hooks (A3)

| ID    | Tarea                                                         | Agente | Ref V2      | Validacion V                   |
| ----- | ------------------------------------------------------------- | ------ | ----------- | ------------------------------ |
| F4-01 | `SoulInTheBot.plugin.json` (manifest con 11 skills, 8 MCPs)   | A3     | Sec 6.1     | V: manifest completo y valido  |
| F4-02 | Skill `ask-data-insight` (SKILL.md + wiring)                  | A3     | Sec 6.2 #1  | V: skill funcional, usa 6 MCPs |
| F4-03 | Skill `run-data-query`                                        | A3     | Sec 6.2 #2  | V: skill funcional             |
| F4-04 | Skill `explain-metric`                                        | A3     | Sec 6.2 #3  | V: skill funcional             |
| F4-05 | Skill `catalog-discovery`                                     | A3     | Sec 6.2 #4  | V: skill funcional             |
| F4-06 | Skill `debug-query-failure`                                   | A3     | Sec 6.2 #5  | V: skill funcional             |
| F4-07 | Skill `compare-periods`                                       | A3     | Sec 6.2 #6  | V: skill funcional             |
| F4-08 | Skill `anomaly-investigator`                                  | A3     | Sec 6.2 #7  | V: skill funcional             |
| F4-09 | Skill `build-executive-brief`                                 | A3     | Sec 6.2 #8  | V: skill funcional             |
| F4-10 | Skill `governance-audit`                                      | A3     | Sec 6.2 #9  | V: skill funcional             |
| F4-11 | Skill `data-source-health`                                    | A3     | Sec 6.2 #10 | V: skill funcional             |
| F4-12 | Skill `continuous-improvement`                                | A3     | Sec 6.2 #11 | V: skill funcional             |
| F4-13 | Hook `PreToolUse`: bloquea sin validate+dry_run               | A3     | Sec 6.3     | V: bloqueo verificado          |
| F4-14 | Hook `PostToolUse`: registra provenance                       | A3     | Sec 6.3     | V: provenance registrado       |
| F4-15 | Hook `PreResponse`: verifica evidencia                        | A3     | Sec 6.3     | V: bloquea sin evidencia       |
| F4-16 | Hook `SessionStart`: carga dictionary version                 | A3     | Sec 6.3     | V: carga verificada            |
| F4-17 | Hook `SessionEnd`: resumen trazabilidad + envio a improvement | A3     | Sec 6.3     | V: ambos ejecutan              |
| F4-18 | `config.ts` con 16 parametros                                 | A3     | Sec 6.4     | V: los 16 parametros presentes |
| F4-19 | Tests de skills                                               | A5     | Sec 6.2     | V: 11 skills con tests         |
| F4-20 | Tests de hooks                                                | A5     | Sec 6.3     | V: 6 hooks con tests           |

### Fase 5: Integracion + Golden Tests + Performance (A5)

| ID    | Tarea                                                            | Agente | Ref V2   | Validacion V                           |
| ----- | ---------------------------------------------------------------- | ------ | -------- | -------------------------------------- |
| F5-01 | Flujo determinista completo: 8 pasos end-to-end OpenSearch       | A5     | Sec 8    | V: flujo pasa                          |
| F5-02 | Flujo determinista completo: 8 pasos end-to-end Postgres         | A5     | Sec 8    | V: flujo pasa                          |
| F5-03 | Golden tests: min 20 preguntas de negocio con respuesta esperada | A5     | Sec 10   | V: 20+ tests, todos pasan              |
| F5-04 | Test abstencion: pregunta sobre campo inexistente                | A5     | Sec 10   | V: abstencion activada                 |
| F5-05 | Test abstencion: ambiguedad de metrica                           | A5     | Sec 10   | V: abstencion activada                 |
| F5-06 | Test dry-run obligatorio: verificar que se bloquea sin dry-run   | A5     | Sec 10   | V: bloqueo verificado                  |
| F5-07 | Test provenance: verificar registro completo                     | A5     | Sec 10   | V: provenance tiene todos los campos   |
| F5-08 | Test drift detection                                             | A5     | Sec 10   | V: drift detectado                     |
| F5-09 | Test improvement capture                                         | A5     | Sec 10   | V: interaccion registrada              |
| F5-10 | Test version + rollback                                          | A5     | Sec 10   | V: version creada y rollback funcional |
| F5-11 | Benchmark: latencia < 5s end-to-end                              | A5     | Sec 11.4 | V: benchmark pasa                      |
| F5-12 | Benchmark: dry-run < 500ms                                       | A5     | Sec 11.4 | V: benchmark pasa                      |
| F5-13 | Benchmark: compilacion < 200ms                                   | A5     | Sec 11.4 | V: benchmark pasa                      |

---

## 4) Orden de ejecucion y dependencias

```
Iteracion 1 (setup + catalogo + MCP A):
  A3: F0-02 (estructura)
  A4: F1-01 a F1-12 (introspectores, dictionary, scripts)
  A1: F1-13 (MCP A server)
  A5: F1-14 (tests MCP A)
  V:  Valida F0-03, F0-04, toda Fase 1

Iteracion 2 (MCP B + C + D):
  A1: F2-01 a F2-20 (planner, validator, executor)
  A5: F2-21, F2-22 (tests)
  V:  Valida toda Fase 2

Iteracion 3 (MCP E + F + G + H):
  A2: F3-01 a F3-20 (insights, provenance, governance, improvement)
  A5: F3-19 (tests)
  V:  Valida toda Fase 3

Iteracion 4 (plugin + skills + hooks):
  A3: F4-01 a F4-18 (plugin, 11 skills, hooks, config)
  A5: F4-19, F4-20 (tests skills y hooks)
  V:  Valida toda Fase 4

Iteracion 5 (integracion + golden + performance + cierre):
  A5: F5-01 a F5-13 (integracion, golden, benchmarks)
  A1-A4: correcciones de rechazos V
  V:  VALIDACION FINAL COMPLETA
```

---

## 5) Validacion final del Agente V

### 5.1 Checklist por seccion

| Seccion V2 | Que verificar                                                                      | Items   |
| ---------- | ---------------------------------------------------------------------------------- | ------- |
| Sec 6.1    | Estructura de archivos del plugin                                                  | 1       |
| Sec 6.2    | 11 skills implementadas y funcionales                                              | 11      |
| Sec 6.3    | 6 hooks implementados y funcionales                                                | 6       |
| Sec 6.4    | 16 parametros de configuracion                                                     | 16      |
| Sec 7.1    | MCP A: 10 tools + 6 programas + 3 scripts + 3 introspectores                       | 22      |
| Sec 7.2    | MCP B: 6 tools + 5 programas + 2 scripts + 3 compiladores                          | 16      |
| Sec 7.3    | MCP C: 8 tools + 3 programas + 2 scripts + 3 validadores                           | 16      |
| Sec 7.4    | MCP D: 7 tools + 3 programas + 2 scripts + 3 ejecutores                            | 15      |
| Sec 7.5    | MCP E: 6 tools + 6 programas + 2 scripts                                           | 14      |
| Sec 7.6    | MCP F: 5 tools + 4 programas + 2 scripts                                           | 11      |
| Sec 7.7    | MCP G: 5 tools + 5 programas + 3 scripts                                           | 13      |
| Sec 7.8    | MCP H: 8 tools + 6 programas + 4 scripts                                           | 18      |
| Sec 8      | Flujo determinista 8 pasos funcional                                               | 8       |
| Sec 10     | Estrategia 99%: 9 reglas implementadas                                             | 9       |
| Sec 11     | Criterios de exito: funcionalidad (9) + calidad (5) + mejora (5) + performance (3) | 22      |
| **TOTAL**  |                                                                                    | **198** |

### 5.2 Regla final

**El proyecto NO se considera completado hasta que el Agente V emita reporte APROBADO con 0 items rechazados y 198/198 verificados.**

---

## 6) Volumetria

| Metrica                           | Cantidad                 |
| --------------------------------- | ------------------------ |
| Total tareas de construccion      | 80                       |
| Tareas A1 (MCP Core)              | 21                       |
| Tareas A2 (MCP Extended)          | 20                       |
| Tareas A3 (Plugin + Skills)       | 20                       |
| Tareas A4 (Catalogo + Dictionary) | 12                       |
| Tareas A5 (Tests + Golden)        | 15                       |
| Validaciones del Agente V         | 80 + 1 final (198 items) |
| Iteraciones                       | 5                        |

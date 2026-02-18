# Plan de Construccion V3 - AnswerWithPrecisionX

> **Version:** 3.0
> **Base:** Answer-With-Precision-BTH.md V2 + BUILD_PLAN V1
> **Fecha:** 2026-02-17
> **Objetivo Principal:** Q&A sobre cualquier dataset con 99% precisión usando LangChain/LangGraph

---

## MEJORAS V3 vs V1

| Aspecto | V1 | V3 |
|---------|----|----|
| Core tecnológico | Programas Python genéricos | **LangChain + LangGraph avanzado (ReAct, CodeAct)** |
| Hooks | Mencionados en hooks.ts | **Hooks programáticos ejecutables (Python/Bash)** |
| Validación | Agente V manual | **Validación automatizada con JSON Schema** |
| Determinismo | Implícito | **Explícito con audit logging y git hooks** |
| Catálogo | Estático | **Dinámico con RAG semántico vectorial** |
| Reflexión | No incluido | **Agente secundario de mejora continua** |

---

## 1) ARQUITECTURA CORE - LangChain/LangGraph

### 1.1 Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANSWERWITHPRECISIONX                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA 1: PLUGIN INTERFACE                       │  │
│  │  11 Skills + 6 Hooks + Config                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA 2: LANGGRAPH ORCHESTRATOR                 │  │
│  │  StateGraph + ReAct Agent + CodeAct Patterns                      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │ Catalog │ │ Planner │ │Validator│ │Executor │ │ Insight │     │  │
│  │  │  Node   │→│  Node   │→│  Node   │→│  Node   │→│  Node   │     │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA 3: LANGCHAIN TOOLS                        │  │
│  │  63 Tools organizadas en 8 MCPs                                   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                 │  │
│  │  │OpenSearch│ │PostgreSQL│ │  MySQL │ │ SQLite  │                 │  │
│  │  │Connector │ │Connector │ │Connector│ │Connector│                 │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA 4: RAG SEMÁNTICO                          │  │
│  │  Catálogo Vectorial + Data Dictionary + Embeddings                │  │
│  │  ChromaDB/FAISS + Sentence Transformers                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Programas Python Core con LangChain/LangGraph

| Programa | Líneas Est. | LangChain/LangGraph Features |
|----------|-------------|------------------------------|
| `core/orchestrator.py` | 800+ | StateGraph, CompiledGraph, conditional edges |
| `core/intent_agent.py` | 600+ | ReActAgent, tool_calling, structured output |
| `core/semantic_planner.py` | 700+ | LangGraph workflow, state management |
| `core/query_compiler.py` | 900+ | CodeAct pattern, multi-engine compilation |
| `core/validator_agent.py` | 500+ | Tool validation, schema checking |
| `core/executor_agent.py` | 600+ | Async execution, retry logic |
| `core/insight_generator.py` | 700+ | RAG retrieval, analysis chains |
| `core/confidence_scorer.py` | 400+ | Classification chains, thresholds |
| `core/abstention_handler.py` | 300+ | Decision logic, alternatives |
| `rag/catalog_indexer.py` | 500+ | VectorStore, embeddings, ChromaDB |
| `rag/semantic_retriever.py` | 400+ | Similarity search, reranking |
| `rag/dictionary_rag.py` | 450+ | Hybrid search, metadata filtering |
| **TOTAL CORE** | **~6,800+** | |

---

## 2) AGENTES DE CONSTRUCCIÓN V3

### 2.1 Asignación Mejorada

| Agente | Rol | Responsabilidades V3 |
|--------|-----|----------------------|
| **A1** | LangGraph Core | Orchestrator, StateGraph, nodos principales |
| **A2** | LangChain Tools | 63 tools, conectores, MCPs |
| **A3** | RAG Semántico | Catálogo vectorial, embeddings, retrieval |
| **A4** | Plugin + Skills | 11 skills, hooks programáticos, config |
| **A5** | Tests + Validation | Tests unitarios, integración, golden tests |
| **V** | Validator | Verificación automática con JSON Schema |
| **R** | Reflection | Mejora continua, versionado (secundario) |

### 2.2 Dependencias entre Agentes

```
A3 (RAG) ──────┐
               ├──→ A1 (LangGraph) ──→ A4 (Plugin) ──→ A5 (Tests) ──→ V (Validate)
A2 (Tools) ────┘                                                           │
                                                                           ↓
                                                                      R (Reflect)
```

---

## 3) FASES DE CONSTRUCCIÓN V3

### FASE 0: Setup + Infraestructura Determinista

| ID | Tarea | Agente | Entregable |
|----|-------|--------|------------|
| F0-01 | Crear estructura plugin `~/.claude/plugins/answer-with-precision-x/` | A4 | Directorios |
| F0-02 | Crear `requirements.txt` con LangChain/LangGraph deps | A1 | requirements.txt |
| F0-03 | Crear `hooks/hooks.json` con hooks programáticos | A4 | hooks.json ejecutable |
| F0-04 | Crear scripts de validación pre-build | V | validate_*.py |
| F0-05 | Crear JSON Schemas para progress, audit, catalog | V | schemas/*.json |
| F0-06 | Crear sistema de audit logging | V | scripts/audit_logger.py |
| F0-07 | Setup virtualenv con dependencias | A1 | .venv activable |

### FASE 1: RAG Semántico + Catálogo (A3)

| ID | Tarea | Descripción | Líneas Est. |
|----|-------|-------------|-------------|
| F1-01 | `rag/embeddings_manager.py` | Sentence Transformers, modelo embeddings | 300 |
| F1-02 | `rag/vector_store.py` | ChromaDB/FAISS wrapper | 400 |
| F1-03 | `rag/catalog_indexer.py` | Indexación de schemas en vectores | 500 |
| F1-04 | `rag/semantic_retriever.py` | Búsqueda semántica de campos/tablas | 400 |
| F1-05 | `rag/dictionary_rag.py` | RAG sobre data dictionary | 450 |
| F1-06 | `rag/metadata_enricher.py` | Enriquecimiento semántico automático | 350 |
| F1-07 | `catalog/introspector_opensearch.py` | Lectura mappings OpenSearch | 300 |
| F1-08 | `catalog/introspector_postgres.py` | Lectura information_schema | 300 |
| F1-09 | `catalog/introspector_sql.py` | SQLAlchemy Inspector multi-dialect | 350 |
| F1-10 | `catalog/catalog_builder.py` | Generación catálogo unificado | 400 |
| F1-11 | `catalog/dictionary_generator.py` | Generación data dictionary | 350 |
| **SUBTOTAL** | | | **4,100** |

### FASE 2: LangGraph Orchestrator (A1)

| ID | Tarea | Descripción | LangGraph Features |
|----|-------|-------------|-------------------|
| F2-01 | `core/state.py` | TypedDict state definitions | State management |
| F2-02 | `core/orchestrator.py` | StateGraph principal 8 nodos | CompiledGraph |
| F2-03 | `core/nodes/catalog_node.py` | Nodo descubrimiento catálogo | Conditional edges |
| F2-04 | `core/nodes/planner_node.py` | Nodo planificación semántica | State transitions |
| F2-05 | `core/nodes/validator_node.py` | Nodo validación query | Tool calling |
| F2-06 | `core/nodes/executor_node.py` | Nodo ejecución query | Async execution |
| F2-07 | `core/nodes/insight_node.py` | Nodo generación insights | RAG retrieval |
| F2-08 | `core/nodes/provenance_node.py` | Nodo registro evidencia | State persistence |
| F2-09 | `core/nodes/governance_node.py` | Nodo políticas respuesta | Decision logic |
| F2-10 | `core/nodes/abstention_node.py` | Nodo abstención controlada | Conditional routing |
| F2-11 | `core/intent_agent.py` | ReAct agent para parsing intent | ReActAgent |
| F2-12 | `core/semantic_planner.py` | Generación AST semántico neutral | Structured output |
| F2-13 | `core/confidence_scorer.py` | Modelo scoring confianza | Classification |
| **SUBTOTAL** | | | **~5,200 líneas** |

### FASE 3: LangChain Tools + MCPs (A2)

| ID | Tarea | MCP | Tools |
|----|-------|-----|-------|
| F3-01 | `mcps/catalog/tools.py` | catalog-mcp | 10 tools |
| F3-02 | `mcps/planner/tools.py` | planner-mcp | 6 tools |
| F3-03 | `mcps/validator/tools.py` | validator-mcp | 8 tools |
| F3-04 | `mcps/executor/tools.py` | executor-mcp | 7 tools |
| F3-05 | `mcps/insight/tools.py` | insight-mcp | 6 tools |
| F3-06 | `mcps/provenance/tools.py` | provenance-mcp | 5 tools |
| F3-07 | `mcps/governance/tools.py` | governance-mcp | 5 tools |
| F3-08 | `mcps/improvement/tools.py` | improvement-mcp | 8 tools |
| F3-09 | `engines/compiler_opensearch.py` | Compilador DSL | CodeAct |
| F3-10 | `engines/compiler_postgres.py` | Compilador SQL Postgres | CodeAct |
| F3-11 | `engines/compiler_sql.py` | Compilador SQL genérico | CodeAct |
| F3-12 | `engines/executor_opensearch.py` | Ejecutor OpenSearch | Async |
| F3-13 | `engines/executor_postgres.py` | Ejecutor PostgreSQL | Async |
| F3-14 | `engines/executor_sql.py` | Ejecutor SQL genérico | Async |
| F3-15 | `engines/result_normalizer.py` | Normalización resultados | - |
| **SUBTOTAL** | | **8 MCPs** | **63 tools, ~6,000 líneas** |

### FASE 4: Plugin + Skills + Hooks (A4)

| ID | Tarea | Tipo | Descripción |
|----|-------|------|-------------|
| F4-01 | `plugin.json` | Config | Manifest con 11 skills, 8 MCPs |
| F4-02 | `SKILL.md` | Skill | Main skill /awpx |
| F4-03 | `skills/ask-data-insight.md` | Skill | Pregunta → insight |
| F4-04 | `skills/run-data-query.md` | Skill | Query explícita |
| F4-05 | `skills/explain-metric.md` | Skill | Explicar métrica |
| F4-06 | `skills/catalog-discovery.md` | Skill | Explorar catálogo |
| F4-07 | `skills/debug-query-failure.md` | Skill | Debug queries |
| F4-08 | `skills/compare-periods.md` | Skill | Comparativa temporal |
| F4-09 | `skills/anomaly-investigator.md` | Skill | Detectar anomalías |
| F4-10 | `skills/build-executive-brief.md` | Skill | Resumen ejecutivo |
| F4-11 | `skills/governance-audit.md` | Skill | Auditoría calidad |
| F4-12 | `skills/data-source-health.md` | Skill | Health check fuentes |
| F4-13 | `skills/continuous-improvement.md` | Skill | Mejora continua |
| F4-14 | `hooks/hooks.json` | Hooks | 6 hooks programáticos |
| F4-15 | `hooks/pre_tool_use.py` | Hook | Bloquea sin validación |
| F4-16 | `hooks/post_tool_use.py` | Hook | Registra provenance |
| F4-17 | `hooks/stop_validator.py` | Hook | Verifica completitud |
| **SUBTOTAL** | | | **11 skills, 6 hooks** |

### FASE 5: Tests + Validación (A5 + V)

| ID | Tarea | Tipo | Target |
|----|-------|------|--------|
| F5-01 | `tests/unit/test_orchestrator.py` | Unit | Core orchestrator |
| F5-02 | `tests/unit/test_rag.py` | Unit | RAG components |
| F5-03 | `tests/unit/test_compilers.py` | Unit | Query compilers |
| F5-04 | `tests/unit/test_tools.py` | Unit | 63 tools |
| F5-05 | `tests/integration/test_flow_opensearch.py` | Integration | Flow OpenSearch |
| F5-06 | `tests/integration/test_flow_postgres.py` | Integration | Flow PostgreSQL |
| F5-07 | `tests/integration/test_abstention.py` | Integration | Abstención |
| F5-08 | `tests/golden/test_business_questions.py` | Golden | 20+ preguntas negocio |
| F5-09 | `tests/performance/test_latency.py` | Performance | <5s e2e, <500ms dry-run |
| F5-10 | `scripts/run_all_tests.sh` | Script | Runner completo |
| F5-11 | `scripts/validate_plugin.py` | Script | Validación estructura |
| F5-12 | `scripts/check_coverage.py` | Script | Coverage >=80% |

---

## 4) DETERMINISMO GARANTIZADO

### 4.1 Hooks Programáticos

```json
// hooks/hooks.json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": {"tool_name": "execute_*"},
      "action": {
        "type": "command",
        "command": "python3 hooks/pre_tool_use.py",
        "blockOnFailure": true
      }
    },
    {
      "event": "PostToolUse",
      "action": {
        "type": "command",
        "command": "python3 hooks/post_tool_use.py"
      }
    },
    {
      "event": "Stop",
      "action": {
        "type": "command",
        "command": "python3 hooks/stop_validator.py",
        "blockOnFailure": true
      }
    }
  ]
}
```

### 4.2 JSON Schemas para Validación

| Schema | Valida |
|--------|--------|
| `schemas/semantic_plan.json` | Estructura del plan semántico AST |
| `schemas/query_result.json` | Formato resultado normalizado |
| `schemas/provenance.json` | Registro de evidencia |
| `schemas/progress.json` | Progreso construcción |
| `schemas/audit_log.json` | Log de auditoría |

### 4.3 Audit Logging

```python
# Cada operación registra:
{
  "timestamp": "ISO-8601",
  "operation": "string",
  "actor": "agent_id",
  "input": {...},
  "output": {...},
  "duration_ms": int,
  "status": "success|failure|blocked"
}
```

---

## 5) MÉTRICAS DE ÉXITO V3

| Métrica | Target | Medición |
|---------|--------|----------|
| Programas Python LangChain/LangGraph | 47+ | Conteo archivos .py |
| Líneas de código Python | 15,000+ | wc -l |
| Skills funcionales | 11 | Tests pasan |
| MCPs operativos | 8 | Tests pasan |
| Tools implementadas | 63 | Conteo @tool decorators |
| Hooks programáticos | 6 | Ejecución verificada |
| Coverage tests | >=80% | pytest-cov |
| Golden tests | >=20 | Preguntas negocio |
| Latencia e2e | <5s | Benchmark |
| Precisión queries | >=99% | Golden tests pass rate |

---

## 6) COMANDOS DE EJECUCIÓN

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
./scripts/run_all_tests.sh

# Validar plugin
python3 scripts/validate_plugin.py

# Verificar coverage
python3 scripts/check_coverage.py

# Benchmark performance
python3 tests/performance/test_latency.py
```

---

## 7) VOLUMETRÍA FINAL V3

| Componente | Cantidad |
|------------|----------|
| Programas Python | 47+ |
| Líneas código (est.) | 15,000+ |
| Skills | 11 |
| MCPs | 8 |
| Tools | 63 |
| Hooks | 6 |
| JSON Schemas | 5 |
| Scripts | 22 |
| Tests | 50+ |
| Golden questions | 20+ |

---

*BUILD_PLAN_ANSWER_PRECISION V3 - Enfoque LangChain/LangGraph*

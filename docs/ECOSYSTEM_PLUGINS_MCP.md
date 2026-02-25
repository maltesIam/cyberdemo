# Ecosistema de Plugins, MCPs, Tools, Hooks y Skills — Documento Funcional

*Versión: 1.0.0*
*Fecha: 2026-02-25*

---

## Tabla de Contenidos

1. [Visión General del Ecosistema](#1-visión-general-del-ecosistema)
2. [Plugins Custom (Propios)](#2-plugins-custom-propios)
3. [Plugins Oficiales Instalados](#3-plugins-oficiales-instalados)
4. [Hooks Globales y Hookify](#4-hooks-globales-y-hookify)
5. [Comandos Custom (Slash Commands)](#5-comandos-custom-slash-commands)
6. [Agentes Custom](#6-agentes-custom)
7. [MCP Servers del Proyecto CyberDemo](#7-mcp-servers-del-proyecto-cyberdemo)
8. [El MCP Bridge: Arquitectura ActivePieces ↔ Claude Code](#8-el-mcp-bridge-arquitectura-activepieces--claude-code)
9. [Skill plugin-dev — Creación de Plugins para cualquier entorno](#9-skill-plugin-dev--creación-de-plugins-para-cualquier-entorno)
10. [Qué Está Disponible en OpenCloud (Contenedor)](#10-qué-está-disponible-en-opencloud-contenedor)
11. [Resumen de Inventario Total](#11-resumen-de-inventario-total)

---

## 1. Visión General del Ecosistema

El entorno de desarrollo actual tiene un ecosistema complejo con múltiples capas de herramientas:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA COMPLETO                                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  CLAUDE CODE (CLI Local)                                        │   │
│  │                                                                  │   │
│  │  Plugins Custom (5)     Plugins Oficiales (29)                  │   │
│  │  ├── software-builder-x  ├── plugin-dev (creador de plugins)   │   │
│  │  ├── answer-with-precision-x  ├── serena (navegación código)   │   │
│  │  ├── sync-origin         ├── playwright (E2E browser)          │   │
│  │  ├── python2wf2p         ├── context7 (documentación)          │   │
│  │  └── sync-originY        ├── hookify (crear hooks)             │   │
│  │                          ├── feature-dev, code-review, ...     │   │
│  │  Comandos (4)            └── ... (24 más)                      │   │
│  │  ├── /CommitX                                                   │   │
│  │  ├── /CompilaX           Agentes (1 global + 18 en plugins)    │   │
│  │  ├── /TestandRunX        ├── pruebas-en-navegador              │   │
│  │  └── /ralph-loopXX       ├── build-agent (×4)                  │   │
│  │                          ├── tdd-verifier, review-agent        │   │
│  │  Hooks Globales (1)      └── ... (12 más en plugins)           │   │
│  │  └── sbx-build-log-protection                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         │ WebSocket (port 3001)          HTTP/MCP Protocol              │
│         ▼                                      │                        │
│  ┌──────────────────┐                         ▼                        │
│  │  MCP WS Server   │               ┌──────────────────────┐          │
│  │  (CyberDemo)     │               │  ActivePieces Cloud  │          │
│  │  8 tools SOC     │               │  (MCP Bridge)        │          │
│  │  Puerto 3001     │               │  Flows → MCP Tools   │          │
│  └──────────────────┘               └──────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Plugins Custom (Propios)

Almacenados en `/home/oscar/custom-claude-plugins/` y enlazados a `~/.claude/plugins/`.

### 2.1 software-builder-x (v21.0.0)

**Propósito**: Construcción determinística de software con TDD, 6 agentes paralelos y verificación anti-cheat.

**Cuándo se usa**: Cuando necesitas construir un proyecto completo desde una especificación funcional. Ejecuta diseño → planificación → construcción → verificación en un pipeline controlado.

**Skills (6):**

| Skill | Comando | Descripción |
|-------|---------|-------------|
| sbx | `/sbx` | Orquestación principal del pipeline completo |
| design | `/sbx-design` | Crea especificación funcional con verificación de estructura |
| plan | `/sbx-plan` | Genera BUILD_PLAN.md, TEST_PLAN.md y PROGRESS.md |
| build | `/sbx-build` | Ejecuta 6 agentes paralelos (4 build + 1 TDD + 1 review) |
| verify | `/sbx-verify` | Verificación final de requisitos, tests y completitud |
| analyze | `/sbx-analyze` | Análisis profundo de compliance y lecciones aprendidas |

**Agentes (5):**

| Agente | Función |
|--------|---------|
| build-agent (×4) | Implementa código siguiendo TDD (rojo → verde → refactor) |
| tdd-verifier | Verifica que los tests cubren todos los Acceptance Criteria |
| review-agent | Verifica coherencia REQ → Código y actualiza progreso |
| design-reviewer | Revisa la especificación funcional buscando gaps |
| gap-analyzer | Analiza gaps entre spec, plan y tests |

**Hooks (8):** Protección de archivos de ejecución, validación TDD pre-edit, detección de stubs post-edit, tracking de ejecución de tests, validación de progreso.

**Modelo de seguridad (3 capas):**
1. **Capa 1 — Enforcer físico**: Cuenta archivos reales, detecta stubs, ejecuta tests directamente via subprocess
2. **Capa 2 — Agentes semánticos**: TDD Verifier y Review Agent hacen análisis de coherencia
3. **Capa 3 — Validación de ejecución**: El enforcer verifica que los agentes realmente ejecutaron su trabajo

---

### 2.2 answer-with-precision-x (v3.1.0)

**Propósito**: Sistema de preguntas y respuestas sobre datos con 99% de precisión. Usa un flujo determinístico de 8 pasos con abstención controlada (si no puede responder con certeza, lo dice).

**Cuándo se usa**: Cuando necesitas consultar datos y obtener respuestas verificables con trazabilidad completa.

**Skills (13):**

| Skill | Descripción |
|-------|-------------|
| `awpx` | Q&A principal: "¿Cuántos usuarios hay?" → respuesta con proveniencia |
| `catalog-discovery` | Descubre tablas y fuentes de datos disponibles |
| `run-data-query` | Ejecuta queries validadas contra la fuente de datos |
| `ask-data-insight` | Genera insights a partir de datos |
| `anomaly-investigator` | Investiga anomalías en los datos |
| `compare-periods` | Compara datos entre periodos de tiempo |
| `explain-metric` | Explica qué significa una métrica y cómo se calcula |
| `build-executive-brief` | Crea resúmenes ejecutivos con datos |
| `governance-audit` | Audita gobernanza de datos |
| `data-source-health` | Verifica estado de fuentes de datos |
| `debug-query-failure` | Debuggea queries que fallan |
| `continuous-improvement` | Identifica oportunidades de mejora |
| `hola-mundo` | Skill de prueba básica |

**Agentes (6):** planner-agent, catalog-agent, executor-agent, reflection-agent, insight-agent, governance-agent.

**Flujo de 8 pasos:** DISCOVER → PLAN → VALIDATE → EXECUTE → ANALYZE → RECORD → VERIFY → OUTPUT

---

### 2.3 sync-origin (v18.0.0)

**Propósito**: Sincronización determinística entre un fork (SoulInTheBot) y el repositorio origen. Usa manifest + supervisor + auditoría + 10 agentes paralelos.

**Cuándo se usa**: Cuando necesitas hacer merge de cambios del upstream sin perder tus cambios locales.

**Skills (1):** `sync-origin` — Sincronización completa con clasificación de archivos.

**Agentes (9):** supervisor, category-a (conflictos), category-b (solo local), category-c (solo origin), category-d (renombrados), category-e (configuración), diff-analyzer, compatibility-checker, impact-analyzer.

**Clasificación de archivos en 5 categorías:**

| Categoría | Significado | Acción |
|-----------|-------------|--------|
| A | Archivo modificado en ambos (conflicto) | Merge inteligente |
| B | Solo modificado localmente | Mantener sin cambios |
| C | Solo modificado en origin | Aplicar cambios verificando impacto |
| D | Archivo renombrado | Seguir el rename |
| E | Archivo de configuración (JSON/YAML) | Merge especial campo a campo |

---

### 2.4 python2wf2p (v1.0.0)

**Propósito**: Convierte programas Python (LangChain/LangGraph) a flujos de trabajo Flowise V3 / ActivePieces.

**Cuándo se usa**: Cuando tienes un pipeline de IA en Python y quieres convertirlo a un flujo visual en ActivePieces para que se ejecute como automatización.

**Skills (1):** Conversión Python → Workflow con pipeline multi-agente (análisis, mapeo, ejecución, extracción).

**Agentes (5):** Análisis del código Python, mapeo a nodos Flowise, ejecución de conversión, extracción de resultados, validación.

---

## 3. Plugins Oficiales Instalados

29 plugins del marketplace oficial, organizados por categoría:

### Desarrollo y Código

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **plugin-dev** | Toolkit completo para crear plugins, skills, hooks, agentes | `/plugin-dev:create-plugin` |
| **feature-dev** | Desarrollo guiado de features con análisis de codebase | `/feature-dev` |
| **code-review** | Code review con checklist de calidad | Revisión de PRs |
| **code-simplifier** | Simplifica código manteniendo funcionalidad | Post-implementación |
| **pr-review-toolkit** | Suite completa de revisión de PRs (5 agentes) | Antes de merge |
| **commit-commands** | Helpers para git commits y PRs | `/commit`, `/commit-push-pr` |
| **ralph-loop** | Loop iterativo inteligente con condición de parada | Tareas repetitivas |
| **explanatory-output-style** | Estilo de output con insights educativos | Siempre activo |

### Navegación y Análisis de Código

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **serena** | Navegación semántica de código (find_symbol, etc.) | Exploración de codebase |
| **typescript-lsp** | Language Server Protocol para TypeScript | Autocompletado, tipos |
| **pyright-lsp** | Language Server Protocol para Python | Análisis estático |
| **context7** | Consulta documentación actualizada de librerías | `context7:query-docs` |

### Testing y Browser

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **playwright** | Automatización de browser (click, navigate, snapshot) | Tests E2E |
| **figma** | Integración con Figma para implementar diseños | Figma → código |

### DevOps y Plataformas

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **github** | Integración completa con GitHub API | Issues, PRs, Actions |
| **gitlab** | Integración con GitLab | Issues, MRs |
| **vercel** | Deploy a Vercel | `/deploy`, `/vercel-logs` |
| **firebase** | Integración con Firebase/GCP | Firestore, Auth, Functions |
| **sentry** | Monitoreo de errores | Setup, debugging, AI monitoring |
| **linear** | Gestión de issues en Linear | Tracking de tareas |
| **slack** | Notificaciones en Slack | Comunicación |

### AI/ML

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **huggingface-skills** | Herramientas de Hugging Face Hub | Train, datasets, papers |

### Code Review Automatizado

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **greptile** | Review con contexto de codebase | Análisis de PRs |
| **coderabbit** | Code review con IA | Feedback automatizado |

### Seguridad y Gobernanza

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **security-guidance** | Mejores prácticas de seguridad | Auditoría |
| **hookify** | Creación de reglas/hooks para prevenir comportamientos | `/hookify` |

### Documentación y Management

| Plugin | Descripción | Uso típico |
|--------|-------------|-----------|
| **claude-md-management** | Gestión de archivos CLAUDE.md | `/claude-md-improver` |
| **claude-code-setup** | Recomendaciones de automatización | Onboarding |
| **document-skills** | Crear PDFs, DOCX, PPTX, XLSX | Documentación |
| **frontend-design** | Interfaces frontend de alta calidad | Diseño UI |

---

## 4. Hooks Globales y Hookify

### 4.1 Hook Global Activo

**Hook**: `sbx-build-log-protection.sh`
**Tipo**: PreToolUse (Write, Edit, Bash)
**Propósito**: Protege los archivos de ejecución del build enforcer. Impide que cualquier agente escriba directamente en `.sbx/build-execution-log.json`, `.sbx/progress.json`, `.sbx/tdd-semantic-verification.json` o `.sbx/review-semantic-verification.json`. Solo `build-enforcer.py` puede escribir en estos archivos.

### 4.2 Hookify — Sistema de Creación de Hooks

**Plugin**: hookify
**Comando**: `/hookify`
**Propósito**: Crear reglas para prevenir comportamientos no deseados de Claude Code.

**Tipos de hooks soportados:**

| Tipo | Cuándo se ejecuta | Ejemplo |
|------|-------------------|---------|
| PreToolUse | Antes de usar una herramienta | Bloquear `rm -rf` |
| PostToolUse | Después de usar una herramienta | Verificar que no hay console.log |
| Stop | Antes de terminar la sesión | Asegurar que los tests pasan |

**Ejemplos incluidos:**
- `sensitive-files-warning.local.md` — Avisar antes de modificar archivos sensibles
- `require-tests-stop.local.md` — Requerir tests antes de parar
- `dangerous-rm.local.md` — Advertir antes de rm peligrosos
- `console-log-warning.local.md` — Advertir sobre console.log

### 4.3 Hooks dentro de Plugins Custom

Los plugins custom incluyen sus propios hooks que se activan cuando el plugin está en uso:

| Plugin | Hooks | Propósito |
|--------|-------|-----------|
| software-builder-x | 8 hooks | Enforce TDD, proteger log, validar stubs, tracking tests |
| answer-with-precision-x | 3 hooks | Pre-query validation, post-query provenance, completeness check |
| sync-origin | 10 hooks | Bloquear overwrites, audit logging, guard validation |

---

## 5. Comandos Custom (Slash Commands)

Almacenados en `~/.claude/commands/`:

### /CommitX
**Qué hace**: Stage all → commit con Co-Authored-By → push al remote MaltesIam
**Uso**: Después de completar una tarea, para commitear y pushear en un solo paso

### /CompilaX
**Qué hace**: Auto-detecta el tipo de proyecto (Node.js, Python, monorepo) y lo compila/levanta
**Uso**: Después de cambios, para recompilar y levantar servidores de desarrollo

### /TestandRunX
**Qué hace**: Ejecuta tests unitarios y E2E, levanta servicios Docker si necesario, verifica health
**Uso**: Verificar que todo funciona antes de commitear

### /ralph-loopXX
**Qué hace**: Inicia un loop iterativo inteligente que deduce la condición de finalización del prompt
**Uso**: Tareas repetitivas que necesitan iteración hasta cumplir una condición

---

## 6. Agentes Custom

### pruebas-en-navegador

**Ubicación**: `~/.claude/agents/`
**Modelo**: Sonnet
**Herramientas**: Bash, Read, Write, Edit, Grep, Glob

**Propósito**: Agente especializado en tests E2E con Playwright. Simula un usuario real navegando e interactuando con la aplicación web.

**Uso típico**: Verificar funcionalidades en el navegador, probar flujos completos de usuario, detectar regresiones visuales, validar integración UI-Backend.

---

## 7. MCP Servers del Proyecto CyberDemo

El proyecto CyberDemo tiene **dos implementaciones MCP** distintas:

### 7.1 MCP WS Server — Servidor WebSocket (Puerto 3001)

**Ubicación**: `frontend/src/mcp/`
**Protocolo**: WebSocket (ws://localhost:3001)

```
Claude/Agent → WebSocket → MCP WS Server (port 3001)
                               ↓
                         Tool Registry (8 tools)
                               ↓
                         React Context → UI State Updates
                               ↓
                         React Application (render)
```

**8 Tools disponibles:**

| Tool | Descripción | Input |
|------|-------------|-------|
| `show_simulation` | Mostrar simulación de ataque | scenario, phase |
| `generate_chart` | Crear gráfico (bar/line/pie) | type, title, data[] |
| `run_demo_scenario` | Ejecutar escenario demo (1-3) | scenario_id |
| `get_demo_state` | Obtener estado actual del demo | — |
| `update_dashboard` | Actualizar dashboard con KPIs | kpis, alerts |
| `show_alert_timeline` | Mostrar timeline de incidentes | entries[] |
| `highlight_asset` | Resaltar asset en grafo (pulse/glow/zoom) | asset_id, mode |
| `show_postmortem` | Mostrar informe post-incidente | incident_id |

**Archivos clave:**

| Archivo | Propósito |
|---------|-----------|
| `src/mcp/server.ts` | Servidor WS standalone, manejo de clientes híbrido |
| `src/mcp/handler.ts` | Enrutamiento de mensajes y validación |
| `src/mcp/context.tsx` | React Context Provider con hooks |
| `src/mcp/tools/index.ts` | Registro de 8 herramientas |
| `src/mcp/types.ts` | Tipos: MCPMessage, MCPResponse, DemoState |

**Cómo ejecutarlo:**
```bash
cd frontend && npx tsx src/mcp/server.ts
# O: npm run mcp-server
```

### 7.2 UIBridge — Puente Backend→Frontend via WS

**Ubicación**: `backend/src/services/ui_bridge.py`
**Protocolo**: WebSocket client async (Python → port 3001)

El UIBridge es un **cliente** del MCP WS Server. El backend envía comandos de control al frontend a través de él:

```python
bridge = UIBridge()  # ws://localhost:3001
await bridge.send_navigation("/siem")      # Navegar a página
await bridge.send_highlight(["WS-EXEC-PC01"])  # Resaltar asset
await bridge.send_chart(chart_data)        # Mostrar gráfico
await bridge.send_timeline(timeline_data)  # Mostrar timeline
```

---

## 8. El MCP Bridge: Arquitectura ActivePieces ↔ Claude Code

Esta es la pieza más compleja del ecosistema. Explica cómo ActivePieces actúa como **puente MCP** que permite a Claude Code (y otros clientes MCP) ejecutar flujos de automatización remotos.

### 8.1 ¿Qué es ActivePieces?

ActivePieces es una plataforma de automatización (similar a Zapier/n8n) que permite crear "flows" (flujos de trabajo) visuales. En nuestro entorno, lo llamamos "OpenCloud" porque corre como servicio en contenedor.

**Repositorio local**: `/home/oscar/NewProjects/actievepieces/activepieces/`

### 8.2 ¿Qué es el MCP Bridge?

ActivePieces implementa un **MCP Server** integrado que expone sus flujos de automatización como herramientas MCP estándar. Esto significa que cualquier cliente MCP (Claude Code, Cursor, Windsurf) puede:

1. **Conectarse** al MCP Server de ActivePieces via HTTP
2. **Listar** los tools disponibles (cada flow con trigger MCP = 1 tool)
3. **Ejecutar** un tool, lo que dispara la ejecución del flow completo
4. **Recibir** la respuesta del flow

### 8.3 Arquitectura Completa del Bridge

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ARQUITECTURA MCP BRIDGE                              │
│                                                                        │
│  ┌──────────────────┐                    ┌──────────────────────────┐ │
│  │  CLAUDE CODE      │                    │  ACTIVEPIECES CLOUD      │ │
│  │  (CLI Local)      │     HTTP/MCP       │  (Contenedor Docker)     │ │
│  │                   │    Protocol         │                          │ │
│  │  1. Lista tools   │───────────────────►│  MCP Server Controller   │ │
│  │  2. Llama tool    │  Bearer Token Auth  │  (/v1/projects/{id}/     │ │
│  │  3. Recibe result │◄───────────────────│   mcp-server/http)       │ │
│  │                   │                    │          │                │ │
│  └──────────────────┘                    │          ▼                │ │
│                                          │  ┌────────────────────┐  │ │
│  También funciona con:                   │  │  MCP Service        │  │ │
│  ┌──────────────┐                        │  │  buildServer()      │  │ │
│  │  Cursor      │────────────────────────│  │  - Lista flows      │  │ │
│  │  Windsurf    │  Mismo protocolo MCP   │  │  - Filtra enabled   │  │ │
│  │  Cualquier   │                        │  │  - Registra tools   │  │ │
│  │  MCP Client  │                        │  │  - Valida schemas   │  │ │
│  └──────────────┘                        │  └────────┬───────────┘  │ │
│                                          │           │               │ │
│                                          │           ▼               │ │
│                                          │  ┌────────────────────┐  │ │
│                                          │  │  Webhook Service    │  │ │
│                                          │  │  handleWebhook()    │  │ │
│                                          │  │  - Ejecuta flow     │  │ │
│                                          │  │  - Pasa params      │  │ │
│                                          │  │  - Retorna response │  │ │
│                                          │  └────────┬───────────┘  │ │
│                                          │           │               │ │
│                                          │           ▼               │ │
│                                          │  ┌────────────────────┐  │ │
│                                          │  │  FLOWS             │  │ │
│                                          │  │  ┌──────────────┐  │  │ │
│                                          │  │  │ Flow 1       │  │  │ │
│                                          │  │  │ MCP Trigger   │  │  │ │
│                                          │  │  │ → Actions... │  │  │ │
│                                          │  │  │ → Reply MCP  │  │  │ │
│                                          │  │  └──────────────┘  │  │ │
│                                          │  │  ┌──────────────┐  │  │ │
│                                          │  │  │ Flow 2       │  │  │ │
│                                          │  │  │ MCP Trigger   │  │  │ │
│                                          │  │  │ → Actions... │  │  │ │
│                                          │  │  └──────────────┘  │  │ │
│                                          │  └────────────────────┘  │ │
│                                          └──────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.4 ¿Cómo funciona paso a paso?

#### Paso 1: Configurar un Flow con MCP Trigger en ActivePieces

En la UI de ActivePieces, creas un flow con:
- **Trigger**: `MCP Tool` (del piece `@activepieces/piece-mcp`)
- **Configuración del trigger**:
  - `toolName`: Nombre visible para Claude (ej: "analyze_security_alert")
  - `toolDescription`: Qué hace esta herramienta
  - `inputSchema`: Parámetros que acepta (TEXT, NUMBER, BOOLEAN, ARRAY, OBJECT, DATE)
  - `returnsResponse`: Si debe esperar la respuesta o ejecutar en background
- **Actions**: Los pasos del flow (llamar APIs, procesar datos, etc.)
- **Último paso**: `Reply to MCP Client` (envía la respuesta de vuelta)

#### Paso 2: Habilitar el MCP Server del Proyecto

En Settings → MCP Server:
- Activar el toggle "Enable MCP Access"
- Copiar el **Server URL**: `https://tu-activepieces.com/api/v1/projects/{projectId}/mcp-server/http`
- Copiar el **Bearer Token**: Token de 72 caracteres generado automáticamente

#### Paso 3: Configurar Claude Code para conectar

Crear `.mcp.json` en la raíz del proyecto:

```json
{
  "mcpServers": {
    "activepieces": {
      "type": "http",
      "url": "https://tu-activepieces.com/api/v1/projects/{projectId}/mcp-server/http",
      "headers": {
        "Authorization": "Bearer {token-de-72-caracteres}"
      }
    }
  }
}
```

O añadirlo globalmente en `~/.claude.json`.

#### Paso 4: Claude Code usa los tools

Una vez configurado, Claude Code puede:

```
> lista los tools disponibles de activepieces
# Muestra: analyze_security_alert, generate_report, send_notification, ...

> usa el tool analyze_security_alert con alert_id="INC-001"
# Claude llama al MCP server → ActivePieces ejecuta el flow → recibe respuesta
```

### 8.5 Flujo Técnico Detallado de una Llamada

```
1. CLAUDE CODE envía request MCP
   POST /api/v1/projects/{id}/mcp-server/http
   Authorization: Bearer {token}
   Body: { "jsonrpc":"2.0", "method":"tools/call", "params":{"name":"tool_xxxx","arguments":{...}} }

2. MCP SERVER CONTROLLER (mcp-server-controller.ts)
   - Extrae projectId de la URL
   - Busca McpServer en la base de datos
   - Valida Bearer token contra mcp.token almacenado
   - Si no coincide → 401 Unauthorized

3. MCP SERVICE buildServer() (mcp-service.ts)
   - Busca todos los flows ENABLED del proyecto
   - Filtra solo los que tienen trigger @activepieces/piece-mcp
   - Para cada flow:
     a. Extrae toolName, toolDescription, inputSchema del trigger
     b. Convierte inputSchema a Zod schema para validación
     c. Registra tool con server.tool() usando nombre: {toolName}_{flowId:4}

4. TOOL HANDLER se ejecuta
   - Recibe argumentos validados por Zod
   - Llama webhookService.handleWebhook({ flowId, payload: args })
   - Si returnsResponse=true: espera que el flow termine y envíe Reply
   - Si returnsResponse=false: responde inmediatamente con "✅ Ejecutado"

5. FLOW SE EJECUTA
   - MCP Trigger recibe el payload
   - Actions del flow procesan los datos
   - Reply to MCP Client envía StopResponse {status:200, body:{...}}

6. RESPUESTA LLEGA A CLAUDE CODE
   - Formato MCP estándar: { content: [{ type:"text", text:"resultado" }] }
```

### 8.6 Tipos de Parámetros Soportados

Los tools MCP en ActivePieces aceptan estos tipos de parámetros:

| Tipo MCP | Tipo Zod | Ejemplo |
|----------|----------|---------|
| TEXT | z.string() | "Analizar alerta INC-001" |
| NUMBER | z.number() | 42.5 |
| BOOLEAN | z.boolean() | true |
| DATE | z.string() (ISO) | "2026-02-25T10:00:00Z" |
| ARRAY | z.array(z.string()) | ["host1", "host2"] |
| OBJECT | z.record(z.string(), z.string()) | {"key": "value"} |

### 8.7 Autenticación y Seguridad

| Aspecto | Implementación |
|---------|----------------|
| Tipo de auth | Bearer Token en header Authorization |
| Longitud del token | 72 caracteres aleatorios |
| Almacenamiento | Columna `token` en tabla `mcp_server` (PostgreSQL) |
| Rotación | Endpoint POST `/rotate` genera nuevo token e invalida el anterior |
| Scope | Un MCP Server por proyecto (unique index en projectId) |
| Endpoint público | `/http` tiene `skipAuth: true` pero valida Bearer token internamente |

### 8.8 ¿Qué NO es el Bridge?

Es importante aclarar lo que el bridge **no hace**:

- **No es un proxy**: No retransmite requests a otro MCP server. ActivePieces **es** el MCP server
- **No es un gateway genérico**: Solo expone flows de ActivePieces como tools, no agrega otros servers
- **No es bidireccional automáticamente**: Claude llama a ActivePieces, pero ActivePieces no llama a Claude (para eso necesitarías configurar flows que hagan HTTP calls al endpoint de Claude)

---

## 9. Skill plugin-dev — Creación de Plugins para cualquier entorno

### 9.1 ¿Qué es plugin-dev?

**Plugin**: plugin-dev (oficial de Anthropic)
**Comando principal**: `/plugin-dev:create-plugin`

Es el toolkit completo para crear plugins, skills, hooks, agentes y comandos para Claude Code. **Cualquier componente creado con plugin-dev funciona tanto en CLI local como en OpenCloud** (si el entorno de Claude Code está configurado para cargar plugins).

### 9.2 Las 7 Skills de plugin-dev

| Skill | Comando | Propósito |
|-------|---------|-----------|
| **create-plugin** | `/plugin-dev:create-plugin` | Workflow guiado de 8 fases para crear un plugin completo |
| **plugin-structure** | `/plugin-dev:plugin-structure` | Entender la estructura de directorios y plugin.json |
| **skill-development** | `/plugin-dev:skill-development` | Crear skills con progressive disclosure |
| **agent-development** | `/plugin-dev:agent-development` | Crear agentes autónomos con system prompt |
| **hook-development** | `/plugin-dev:hook-development` | Crear hooks Pre/PostToolUse/Stop |
| **command-development** | `/plugin-dev:command-development` | Crear slash commands con frontmatter |
| **mcp-integration** | `/plugin-dev:mcp-integration` | Integrar MCP servers en plugins |

### 9.3 Workflow de Creación (8 fases)

```
Fase 1: Discovery        → Entender el propósito del plugin
Fase 2: Component Plan   → Determinar skills, commands, agents, hooks, MCP
Fase 3: Detailed Design  → Diseñar cada componente
Fase 4: Structure        → Crear directorio y plugin.json
Fase 5: Implementation   → Implementar cada componente
Fase 6: Validation       → Ejecutar plugin-validator agent
Fase 7: Testing          → Verificar en Claude Code
Fase 8: Documentation    → Documentar uso y ejemplos
```

### 9.4 MCP Integration — Los 4 Tipos de Servidor

La skill `mcp-integration` documenta cómo integrar MCP servers en plugins:

| Tipo | Protocolo | Uso ideal | Ejemplo |
|------|-----------|-----------|---------|
| **stdio** | stdin/stdout JSON-RPC | Herramientas locales, custom servers | Servidor Node.js local |
| **SSE** | Server-Sent Events | Servicios cloud con OAuth | Asana, hosted MCP servers |
| **HTTP** | REST API | APIs stateless con token | ActivePieces MCP Server |
| **WebSocket** | WS/WSS bidireccional | Streaming en tiempo real | CyberDemo MCP WS Server |

**Configuración stdio (local):**
```json
{
  "my-server": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": { "API_KEY": "${MY_API_KEY}" }
  }
}
```

**Configuración HTTP (ActivePieces):**
```json
{
  "activepieces": {
    "type": "http",
    "url": "https://api.example.com/api/v1/projects/{id}/mcp-server/http",
    "headers": { "Authorization": "Bearer ${AP_TOKEN}" }
  }
}
```

### 9.5 ¿Cómo usar plugin-dev para poner cosas en OpenCloud?

El flujo para crear un plugin que funcione en OpenCloud:

1. **Crear el plugin localmente**: `/plugin-dev:create-plugin`
2. **Añadir MCP integration**: `/plugin-dev:mcp-integration` para conectar al MCP server de ActivePieces
3. **Crear flows en ActivePieces**: Definir los flujos que el plugin necesita ejecutar remotamente
4. **Configurar .mcp.json**: Apuntar a la URL del MCP server de ActivePieces con el token
5. **Distribuir**: Checkear `.mcp.json` en git para que el equipo tenga la misma config

---

## 10. Qué Está Disponible en OpenCloud (Contenedor)

### 10.1 Lo que SÍ está disponible

ActivePieces (OpenCloud) expone como herramientas MCP todos los **flows que tengan trigger MCP habilitado**. Esto significa que cualquier flujo de automatización que crees en ActivePieces se convierte en un tool callable desde Claude Code.

**Potencialmente disponibles** (si se crean los flows correspondientes):

| Capacidad | Cómo hacerla disponible |
|-----------|------------------------|
| Análisis de seguridad | Crear flow con trigger MCP que llame APIs de SIEM |
| Generación de reportes | Crear flow que genere PDF/DOCX con datos |
| Envío de notificaciones | Crear flow que envíe email/Slack |
| Consulta de datos | Crear flow que consulte bases de datos |
| Ejecución de scripts | Crear flow que ejecute código en contenedor |
| Integración con 300+ apps | ActivePieces tiene 300+ pieces/conectores |

### 10.2 Lo que NO está disponible en OpenCloud directamente

Los plugins de Claude Code (software-builder-x, answer-with-precision-x, etc.) son **locales** y no se ejecutan en ActivePieces. Sin embargo, puedes crear flows en ActivePieces que repliquen parte de su funcionalidad.

### 10.3 Estado Actual de la Configuración

| Componente | Estado | Acción necesaria |
|------------|--------|------------------|
| ActivePieces MCP Server (código) | Implementado | Está en el repo |
| ActivePieces instance running | Verificar | Levantar contenedor Docker |
| Flows con trigger MCP | No creados aún | Crear flows para cada tool deseado |
| `.mcp.json` en proyecto | No existe | Crear con URL y token de ActivePieces |
| Claude Code conectado | No configurado | Añadir mcpServers config |

---

## 11. Resumen de Inventario Total

### Totales por Tipo

| Tipo | Custom | Oficial | Total |
|------|--------|---------|-------|
| Plugins | 5 | 29 | 34 |
| Skills | 21+ | 50+ | 71+ |
| Agentes | 19 | 10+ | 29+ |
| Hooks (en plugins) | 21+ | 10+ | 31+ |
| Hooks globales | 1 | — | 1 |
| Comandos custom | 4 | — | 4 |
| MCP Servers | 2 | — | 2 |
| MCP Tools (CyberDemo) | 8 | — | 8 |

### Todos los Plugins Custom con sus componentes

```
software-builder-x (v21.0.0)
├── 6 skills: sbx, design, plan, build, verify, analyze
├── 5 agents: build-agent, tdd-verifier, review-agent, design-reviewer, gap-analyzer
├── 8 hooks: enforce flow, validate TDD, detect stubs, track tests, ...
└── Scripts: build-enforcer.py, verify-build.py, verify-design.py, ...

answer-with-precision-x (v3.1.0)
├── 13 skills: awpx, catalog-discovery, run-data-query, ...
├── 6 agents: planner, catalog, executor, reflection, insight, governance
├── 3 hooks: pre-query, post-query, completeness
└── MCP servers: awpx_planner, awpx_catalog, awpx_executor, ...

sync-origin (v18.0.0)
├── 1 skill: sync-origin
├── 9 agents: supervisor, cat-a/b/c/d/e, diff-analyzer, compatibility, impact
├── 10 hooks: block overwrites, audit, guard, anti-false-missing, ...
└── Schema: manifest validation

python2wf2p (v1.0.0)
├── 1 skill: Python → Workflow conversion
├── 5 agents: analysis, mapping, execution, extraction, validation
├── Hooks: conversion validation
└── Commands: convert command

sync-originY (v1.0.0)
└── 1 skill: hola-mundo (test)
```

### MCP Servers del Proyecto

```
CyberDemo MCP WS Server (port 3001)
├── 8 tools: show_simulation, generate_chart, run_demo_scenario, ...
├── WebSocket protocol
├── Hybrid client handling (Claude + React)
└── State synchronization

ActivePieces MCP Server (HTTP)
├── N tools (1 por flow con MCP trigger habilitado)
├── HTTP/StreamableHTTP protocol
├── Bearer token authentication
└── Flows as tools
```

### Rutas Clave del Sistema

```
~/.claude/                              Configuración global de Claude Code
├── settings.json                       Settings + hooks globales + plugins habilitados
├── commands/                           Slash commands custom
│   ├── CommitX.md
│   ├── CompilaX.md
│   ├── TestandRunX.md
│   └── ralph-loopXX.md
├── agents/                             Agentes custom globales
│   └── pruebas-en-navegador.md
└── plugins/                            Plugins instalados
    ├── installed_plugins.json          Registro central (34 plugins)
    ├── software-builder-x → symlink   Plugin custom
    ├── answer-with-precision-x → symlink
    ├── sync-origin → symlink
    ├── python2wf2p → symlink
    └── cache/
        ├── local/                      Cache de plugins locales
        ├── claude-plugins-official/    Cache de plugins oficiales (29)
        └── anthropic-agent-skills/     Skills de Anthropic (2)

~/custom-claude-plugins/                Código fuente de plugins custom
├── software-builder-x/
├── answer-with-precision-x/
├── sync-origin/
└── python2wf2p/

~/NewProjects/actievepieces/activepieces/   ActivePieces (OpenCloud)
└── packages/
    ├── server/api/src/app/mcp/        MCP Server backend
    ├── shared/src/lib/mcp/            Tipos compartidos
    └── react-ui/.../mcp-server/       UI de configuración MCP
```

---

*Documento generado: 2026-02-25*
*Basado en: análisis del filesystem ~/.claude/, ~/custom-claude-plugins/, código fuente de ActivePieces, y proyecto CyberDemo*

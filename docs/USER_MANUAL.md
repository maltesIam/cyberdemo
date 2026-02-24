# Manual de Usuario — CyberDemo
## Plataforma SOC con Analista IA Automatizado

**Versión:** 1.0.0
**Fecha:** 2026-02-24
**Sistema:** CyberDemo Attack Surface Platform + SoulInTheBot Agent

---

## INVENTARIO DE DOCUMENTOS DEL PROYECTO

Antes de entrar en el manual, esta es la lista completa de documentos funcionales que existen en el proyecto:

| Documento | Ruta | Qué contiene |
|-----------|------|-------------|
| **FUNCTIONAL_SPEC.md** | `docs/FUNCTIONAL_SPEC.md` | Especificación funcional completa del frontend interactivo: requisitos, personas de usuario, áreas funcionales FA-001 a FA-006, matriz de trazabilidad. 52KB. |
| **FRONTEND_FUNCTIONAL_SPEC.md** | `docs/FRONTEND_FUNCTIONAL_SPEC.md` | Especificación de los 6 componentes de demo del frontend: DemoControlBar, aIP Widget, NarrationFooter, DemoCasesPanel, AnalyzeButton, SimulationPage. |
| **FRONTEND_DESCRIPTION.md** | `docs/FRONTEND_DESCRIPTION.md` | Descripción en español de funcionalidades del frontend. |
| **CyberDemoDescription.md** | `docs/CyberDemoDescription.md` | Descripción funcional completa: UI, APIs, Python, plugin, skill, hooks. Documento de referencia principal. |
| **CyberDemoDescriptionCC.md** | `docs/CyberDemoDescriptionCC.md` | Versión alternativa de la descripción funcional. |
| **Interaccion_CyberProduct_Agent.md** | `docs/Interaccion_CyberProduct_Agent.md` | Documento técnico de integración bidireccional MCP entre el agente y el producto: flujos, tools, protocolo JSON-RPC 2.0. |
| **CYBERDEMO_AGENT_INTEGRATION.md** | `docs/CYBERDEMO_AGENT_INTEGRATION.md` | Manual detallado de integración del agente con flujos de investigación SOC. |
| **MCP_SERVER_PLAN.md** | `docs/MCP_SERVER_PLAN.md` | Plan de implementación del frontend MCP Server WebSocket con las 8 tools de visualización. |
| **MCP_SERVER_PROGRESS.md** | `docs/MCP_SERVER_PROGRESS.md` | Progreso de implementación de los MCP servers. |
| **ATTACK_SURFACE_WOW_DEFINITION.md** | `docs/ATTACK_SURFACE_WOW_DEFINITION.md` | Definición de la superficie de ataque y efectos visuales WOW. |
| **BUILD_PLAN.md** | `docs/BUILD_PLAN.md` | Plan de construcción con 118 tareas en 8 fases para todo el sistema. |
| **FRONTEND_BUILD_PLAN.md** | `docs/FRONTEND_BUILD_PLAN.md` | Plan específico del frontend: 56 tareas en 5 fases. |
| **PROGRESS.md** | `docs/PROGRESS.md` | Progreso general del proyecto. |
| **FRONTEND_PROGRESS.md** | `docs/FRONTEND_PROGRESS.md` | Progreso del frontend: 56/56 tareas (100%) completadas. |
| **TEST_PLAN.md** | `docs/TEST_PLAN.md` | Plan de pruebas: 150 tests en unit, integration, E2E. |
| **FRONTEND_TEST_PLAN.md** | `docs/FRONTEND_TEST_PLAN.md` | Plan de tests específico del frontend. |
| **SOC_ANALYST_GUIDE.md** | `docs/SOC_ANALYST_GUIDE.md` | Guía operativa para el analista SOC usando la plataforma. |
| **THREAT_ENRICHMENT_DESIGN.md** | `docs/THREAT_ENRICHMENT_DESIGN.md` | Diseño del sistema de enriquecimiento de amenazas. |
| **VULNERABILITY_ENRICHMENT_DESIGN.md** | `docs/VULNERABILITY_ENRICHMENT_DESIGN.md` | Diseño del sistema de enriquecimiento de vulnerabilidades. |
| **PLAN_CONSTRUCCION_TDD.md** | `docs/PLAN_CONSTRUCCION_TDD.md` | Plan con metodología TDD para construcción del sistema. |
| **FUNCIONALIDADES_FALTANTES.md** / **V2** | `docs/FUNCIONALIDADES_FALTANTES*.md` | Análisis de funcionalidades pendientes y plan de cierre. |
| **DefinicionPendiente.md** | `docs/DefinicionPendiente.md` | Definiciones funcionales pendientes de especificar. |
| **RALPH_LOOP_ITERATION_*.md** | `docs/RALPH_LOOP_ITERATION_*.md` | Reportes de cada iteración del ciclo de construcción Ralph Loop. |
| **wireframes.html** | `wireframes.html` (raíz) | Wireframes visuales HTML de los componentes interactivos con opciones de diseño A y B. |

---

# PARTE 1 — DESCRIPCIÓN FUNCIONAL

## 1. ¿Qué es CyberDemo?

CyberDemo es una **plataforma de simulación de SOC** (Security Operations Center) que demuestra cómo un **Analista SOC Tier-1 puede ser automatizado** usando inteligencia artificial (SoulInTheBot/Claude). El sistema combina:

- Una **interfaz web React** con 14 vistas operativas de un SOC real
- Un **agente IA** que investiga incidentes, enriquece IOCs y toma decisiones
- **Datos sintéticos realistas** (1.000 activos, 650 incidentes, 3.000 CVEs, 200 IOCs)
- **3 servidores MCP** que conectan el agente con la plataforma de forma bidireccional
- **3 casos de demo determinísticos** que muestran los tres tipos de respuesta posibles

### El problema que resuelve

En un SOC tradicional, el analista trabaja solo frente a múltiples sistemas (SIEM, EDR, Threat Intel, CTEM), correlaciona eventos manualmente y toma decisiones bajo presión. CyberDemo demuestra cómo el agente IA colabora en tiempo real con el analista humano, automatizando el análisis mientras mantiene al humano en el control de las decisiones críticas.

### Los tres tipos de respuesta que demuestra

| Tipo | Escenario | Comportamiento |
|------|-----------|----------------|
| **Tipo 1 — Auto-contención** | Malware en workstation estándar (WS-FIN-042) | El agente detecta, analiza y contiene automáticamente sin intervención humana |
| **Tipo 2 — Aprobación humana** | Malware en laptop del CFO (LAPTOP-CFO-01) | El agente detecta y analiza, pero solicita aprobación humana antes de contener un activo VIP |
| **Tipo 3 — Falso positivo** | Actividad sospechosa en servidor dev (SRV-DEV-03) | El agente investiga y determina que es un falso positivo, cierra el caso sin acción |

---

## 2. Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ECOSISTEMA CYBERDEMO                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   👤 ANALISTA HUMANO                    🤖 AGENTE IA (SoulInTheBot)         │
│   ══════════════════                    ════════════════════════════        │
│   • Ve alertas en la UI                 • Recibe solicitudes del producto   │
│   • Hace clic en "Analizar"             • Analiza, correlaciona, enriquece │
│   • Aprueba o rechaza                   • Decide: contener / escalar /      │
│     acciones del agente                   descartar                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTEND REACT (puerto 5173)          BACKEND FASTAPI (puerto 8000)       │
│   ─────────────────────────            ──────────────────────────────       │
│   • 14 vistas operativas SOC           • APIs REST (SIEM/EDR/Intel/CTEM)   │
│   • Demo Control Bar (header)          • MCP SOC Server (/mcp/messages)    │
│   • aIP Assist Widget (flotante)       • MCP Data Server (/data-mcp)       │
│   • Narration Footer (streaming)       • Policy Engine determinístico      │
│   • Demo Cases Panel (dashboard)       • Generadores de datos sintéticos   │
│   • Analyze with AI (incidentes)       • Sistema de aprobaciones HITL      │
│   • Simulation Page (/simulation)      • WebSocket endpoints               │
│   • MCP Frontend (puerto 3001)         • OpenSearch + PostgreSQL           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Interfaz de Usuario — Vistas Principales

La aplicación está en `http://localhost:5173`. El layout tiene una **barra lateral izquierda** (Sidebar) con navegación, un **header** con la barra de control demo y un **footer** con el panel de narración.

### 3.1 Vistas Operativas del SOC

| Ruta | Vista | Para qué se usa en una demo |
|------|-------|----------------------------|
| `/generation` | **GenerationPage** | Punto de partida: generar/resetear todos los datos sintéticos. Ejecutar aquí antes de cualquier demo. |
| `/dashboard` | **DashboardPage** | KPIs SOC en tiempo real + panel de Demo Cases (3 botones de caso). |
| `/assets` | **AssetsPage** | Inventario de activos con filtros. Aquí se ve WS-FIN-042, LAPTOP-CFO-01, SRV-DEV-03. |
| `/incidents` | **IncidentsPage** | Lista de incidentes SIEM. Cada fila tiene botón "Analyze with AI". |
| `/detections` | **DetectionsPage** | Detecciones EDR con severidad, hash, cmdline, árbol de procesos. |
| `/ctem` | **CTEMPage** | Exposición de vulnerabilidades CVE y riesgo por activo. |
| `/timeline` | **TimelinePage** | Secuencia de acciones del agente con timestamps y decisiones. |
| `/graph` | **GraphPage** | Grafo visual Cytoscape de relaciones incidente-activo-IOC. |
| `/postmortems` | **PostmortemsPage** | Informes post-incidente: causa raíz, impacto, remediación. |
| `/tickets` | **TicketsPage** | Tickets de remediación creados por el agente. |
| `/collab` | **CollabPage** | Chat de colaboración del equipo SOC en tiempo real. |
| `/audit` | **AuditPage** | Trazabilidad completa de acciones con exportación de logs. |
| `/config` | **ConfigPage** | Política de contención, umbrales de confianza, integraciones. |
| `/simulation` | **SimulationPage** | Página dedicada para demos formales con layout de 3 columnas. |

---

## 4. Componentes de Demo — El Corazón de la Demostración

Estos 6 componentes son los que hacen la experiencia de demo interactiva. Se construyeron sobre la plataforma SOC existente.

### 4.1 Demo Control Bar (Barra de Control Global)

**Ubicación:** Header superior, visible en TODAS las páginas
**Archivo:** `frontend/src/components/demo/DemoControlBar.tsx`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [▼ APT29 Espionage Campaign]  [▶ Play] [⏸ Pause] [⏹ Stop]  Velocidad: ──●─  │
│  Fases MITRE: [●][●][●][○][○][○][○][○][○][○]                    [⊟ Colapsar] │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Qué hace:**
- **Dropdown de escenarios**: 6 escenarios de ataque APT para seleccionar
  - APT29 Espionage Campaign (Cozy Bear)
  - FIN7 Financial Attack
  - Lazarus Group Destructive
  - REvil/Sodinokibi Ransomware
  - SolarWinds-style Supply Chain
  - Insider Threat
- **Botón Play (▶)**: Inicia la simulación del escenario seleccionado
- **Botón Pause (⏸)**: Pausa la simulación manteniendo el estado actual
- **Botón Stop (⏹)**: Detiene y reinicia la simulación
- **Speed Slider**: Ajusta velocidad de 0.5x (lento) a 4x (rápido)
- **MITRE Progress**: 10 círculos de colores representando las fases ATT&CK
  - Verde = completada
  - Cian pulsante = activa ahora
  - Gris = pendiente
- **Toggle Colapsar**: Oculta/muestra la barra para más espacio

**Atajos de teclado:**
- `Espacio` — Alternar Play/Pause
- `Esc` — Detener simulación

**Reglas de negocio:**
- Solo se puede ejecutar un escenario a la vez
- Pause conserva el estado exacto (se puede reanudar)
- Stop reinicia al estado inicial

---

### 4.2 aIP Assist Widget (Asistente IA Flotante)

**Ubicación:** Esquina inferior derecha, flotante en TODAS las páginas
**Archivo:** `frontend/src/components/demo/DemoFloatingWidget.tsx`

```
                                          ┌─────────────────────────────┐
                                          │  🤖 aIP Assist         [✕]  │
                                          │  ─────────────────────────  │
                                          │  💡 Sugerencia nueva:       │
                                          │  "He detectado el hash      │
                                          │   abc123 en 3 endpoints.   │
                                          │   ¿Quieres que los aísle?" │
                                          │                             │
                                          │  [Analizar] [Ignorar] [Ver] │
                                          │                             │
                                          │  ● Pensando...             │
                                          └─────────────────────────────┘
        Estado colapsado: [🤖 3]
```

**Qué hace:**
- **Estado colapsado**: Botón compacto con badge numérico de sugerencias no leídas
- **Estado expandido**: Panel con lista de sugerencias del agente
- **Indicador "Pensando..."**: Animación cuando el agente está procesando
- **Botones por sugerencia:**
  - **Analizar**: Acepta la sugerencia y el agente ejecuta la acción
  - **Ignorar**: Descarta la sugerencia (queda en historial)
  - **Ver detalles**: Muestra información técnica adicional

**Comportamiento:**
- Las sugerencias se generan automáticamente mientras el agente trabaja
- El badge del estado colapsado muestra cuántas sugerencias nuevas hay
- Se conecta via WebSocket a `/api/v1/aip-assist/ws/{session}`

---

### 4.3 Narration Footer (Panel de Narración en Tiempo Real)

**Ubicación:** Footer inferior, visible en TODAS las páginas (siempre visible en `/simulation`)
**Archivo:** `frontend/src/components/demo/NarrationFooter.tsx`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📋 Narración del Agente                           [Filtro: ▼ Todos] [▲ ∨] │
│  ─────────────────────────────────────────────────────────────────────────  │
│  10:42:15 [INFO]    Analizando incidente INC-2026-001...                   │
│  10:42:17 [INFO]    Obteniendo árbol de procesos de DET-8821               │
│  10:42:18 [WARNING] Hash abc123 detectado en 3 endpoints adicionales       │
│  10:42:20 [SUCCESS] Confirmado: Familia TrickBot, atribución Wizard Spider │
│  10:42:22 [INFO]    Asset WS-FIN-042: workstation estándar, no VIP        │
│  10:42:23 [SUCCESS] Aplicando contención automática...                     │
│  10:42:24 [SUCCESS] ✅ Host WS-FIN-042 aislado de la red                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Qué hace:**
- Muestra el **razonamiento del agente en tiempo real** (streaming)
- Cada mensaje tiene: timestamp, tipo de color, contenido
- **Tipos de mensaje con color:**
  - 🔵 INFO — Azul: acciones en curso
  - 🟡 WARNING — Amarillo: hallazgos sospechosos
  - 🔴 ERROR — Rojo: fallos o problemas
  - 🟢 SUCCESS — Verde: confirmaciones y éxitos
- **Auto-scroll**: Se desplaza automáticamente al mensaje más reciente
- **Filtro por tipo**: Ver solo INFO, WARNING, ERROR o SUCCESS
- **Toggle colapsar**: Ocultar/mostrar el panel
- La narración continúa en segundo plano aunque esté colapsado

---

### 4.4 Demo Cases Panel (Panel de Casos de Demo)

**Ubicación:** Dashboard (`/dashboard`), panel central
**Archivo:** `frontend/src/components/demo/DemoCasesPanel.tsx`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Demo Cases                                                                 │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ 🛡️               │  │ 👤               │  │ 🔍              │            │
│  │ Malware Auto-   │  │ VIP Threat      │  │ False Positive  │            │
│  │ Containment     │  │ Response        │  │ Detection       │            │
│  │                 │  │                 │  │                 │            │
│  │ Host: WS-FIN-042│  │ Host:           │  │ Host: SRV-DEV-03│            │
│  │ Type: Standard  │  │ LAPTOP-CFO-01   │  │ Type: Dev server│            │
│  │ Expected:       │  │ Type: VIP asset │  │ Expected:       │            │
│  │ Auto-containment│  │ Expected:       │  │ False positive  │            │
│  │                 │  │ Approval req.   │  │                 │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Qué hace:**
- Muestra 3 tarjetas, cada una representando un caso de demo predefinido
- **Un click = invoca el agente** para ejecutar ese caso
- Cada tarjeta muestra: nombre, host, tipo de amenaza, resultado esperado
- **Estados de la tarjeta:**
  - Normal (gris): disponible para ejecutar
  - Loading (cian pulsante + spinner): ejecutando
  - Completed (verde + icono resultado): finalizado
  - Approval Required (amarillo): esperando decisión humana
- Solo se puede ejecutar un caso a la vez
- Cuando termina, muestra el resultado en la tarjeta

**Caso 1 — Malware Auto-Containment (CASE-001):**
- Host: `WS-FIN-042` (workstation finanzas, activo estándar)
- Amenaza: Malware detectado por EDR
- Resultado: El agente analiza, confirma malware real, contiene automáticamente
- No requiere intervención humana

**Caso 2 — VIP Threat Response (CASE-002):**
- Host: `LAPTOP-CFO-01` (laptop del CFO, activo VIP)
- Amenaza: Malware detectado en laptop de directivo
- Resultado: El agente analiza, pero el Policy Engine detecta que es VIP y solicita aprobación
- Aparece la **Approval Card** con botones Approve/Reject

**Caso 3 — False Positive Detection (CASE-003):**
- Host: `SRV-DEV-03` (servidor de desarrollo)
- Amenaza: Actividad sospechosa
- Resultado: El agente investiga y determina que es un falso positivo
- Cierra el incidente sin tomar ninguna acción de contención

---

### 4.5 Approval Card (Tarjeta de Aprobación)

**Aparece dentro del Caso 2 cuando el agente requiere aprobación humana**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  VIP asset requires human approval                                      │
│                                                                             │
│  El agente ha detectado malware en LAPTOP-CFO-01 (CFO). Por política de    │
│  seguridad, los activos VIP requieren aprobación humana antes de            │
│  proceder con la contención de red.                                         │
│                                                                             │
│  [✅ Approve]   [❌ Reject]                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Approve**: El analista aprueba la contención, el agente procede
- **Reject**: El analista rechaza, el agente registra la decisión y cierra
- Este es el flujo **Human-in-the-Loop (HITL)** — el momento más impactante de la demo

---

### 4.6 Analyze with AI Button (Botón de Análisis IA)

**Ubicación:** Cada fila de la tabla de incidentes (`/incidents`)
**Archivo:** `frontend/src/components/demo/AnalyzeButton.tsx`

**Qué hace:**
- Permite solicitar análisis IA sobre cualquier incidente específico
- **3 estados del botón:**
  - 🔵 **Inicial**: `[Analyze with AI]` — disponible para hacer clic
  - ⏳ **Procesando**: `[Analyzing...]` con spinner — el agente está trabajando
  - ✅ **Completado**: muestra icono según decisión (contenido / pendiente / descartado)
- Al hacer clic, encola el análisis de forma asíncrona
- El Narration Footer se **auto-expande** para mostrar el progreso
- Múltiples incidentes pueden analizarse en paralelo

---

### 4.7 Simulation Page (Página de Simulación)

**Ruta:** `/simulation`
**Archivo:** `frontend/src/pages/SimulationPage.tsx`

Página dedicada para presentaciones formales. Tiene un layout de **3 columnas** que muestra todo en una sola pantalla:

```
┌────────────────────────────────────────────────────────────────────────────┐
│  [Barra de control local — Escenario / Play / Pause / Stop / Speed]        │
├────────────────────┬───────────────────────────┬───────────────────────────┤
│  FASES MITRE       │   GRAFO DE ATAQUE          │   PANEL aIP ASSIST        │
│  ────────────────  │   ──────────────────────   │   ────────────────────    │
│  1. Initial Access │                            │   💡 Sugerencias activas  │
│     ✅ Completada  │   [O]──────►[O]──────►[O] │                           │
│  2. Execution      │         (Cytoscape.js)     │   "Detectado movimiento   │
│     ✅ Completada  │                            │    lateral hacia SRV-02"  │
│  3. Persistence    │   Nodos: hosts, IOCs, C2   │                           │
│     🔵 Activa      │   Edges: propagación       │   [Analizar] [Ignorar]    │
│  4. Priv. Escal.   │   Animaciones en tiempo    │                           │
│     ○ Pendiente    │   real con WebSocket       │   ● Pensando...           │
│  5. Def. Evasion   │                            │                           │
│     ○ Pendiente    │                            │                           │
│  ...               │                            │                           │
├────────────────────┴───────────────────────────┴───────────────────────────┤
│  [Narration Footer — siempre visible con streaming del agente]              │
└────────────────────────────────────────────────────────────────────────────┘
```

**Columna izquierda — MITRE Phases List:**
- Lista vertical de las 14 fases ATT&CK
- Indicadores visuales de estado (completada / activa con pulso / pendiente)
- Click en una fase para expandir detalles

**Columna central — Attack Graph:**
- Visualización con **Cytoscape.js** del grafo de ataque
- Nodos: hosts comprometidos (rojo), IOCs (naranja), servidores C2 (negro)
- Edges animados mostrando propagación y comunicación
- Se actualiza en tiempo real via WebSocket
- Efectos visuales al detectar nuevos eventos

**Columna derecha — AI Panel:**
- Panel aIP Assist integrado inline (no flotante)
- Muestra sugerencias del agente en contexto de la simulación

**Footer siempre visible:**
- Narration Footer siempre expandido en esta página
- No se puede colapsar para asegurar visibilidad del razonamiento

---

## 5. Flujos de Demo Implementados

### Flujo Completo de Investigación SOC (9 pasos)

Este es el flujo que ejecuta el agente internamente cuando se invoca cualquiera de los 3 casos:

```
1. DETECCIÓN
   El agente llama: siem_list_incidents({severity: "critical"})
   Recibe lista de incidentes críticos → selecciona el del caso

2. INVESTIGACIÓN
   siem_get_incident({incident_id: "INC-ANCHOR-001"})
   edr_get_process_tree({detection_id: "DET-001"})
   → Obtiene detalles y árbol de procesos sospechosos

3. ENRICHMENT (Enriquecimiento)
   threat_enrich_hash({hash: "abc123..."})
   → Confirma malware conocido con atribución a grupo APT

   edr_hunt_hash({hash: "abc123..."})
   → Busca el hash en todos los endpoints (posible propagación)

4. EVALUACIÓN DE RIESGO
   ctem_get_findings({asset_id: "WS-FIN-042"})
   intel_lookup_ioc({ioc: "192.168.1.100", type: "ip"})
   → El Policy Engine evalúa: ¿Es activo VIP? ¿Riesgo alto?

5. DECISIÓN (según tipo de caso)
   CASO 1: Activo estándar → Contención automática
   CASO 2: Activo VIP → approval_request({...}) → espera humano
   CASO 3: Sin evidencia concluyente → False positive → cerrar

6. HUMAN-IN-THE-LOOP (solo Caso 2)
   La UI muestra la Approval Card
   El analista hace clic en "Approve" o "Reject"
   WebSocket notifica al agente la decisión

7. CONTENCIÓN (Casos 1 y 2 si aprobado)
   edr_contain_host({device_id: "WS-FIN-042", reason: "..."})
   El host queda aislado de la red

8. DOCUMENTACIÓN
   siem_add_comment({incident_id: "INC-001", comment: "..."})
   ticket_create({title: "Remediate WS-FIN-042", ...})

9. VISUALIZACIÓN Y CIERRE
   highlight_asset({asset_id: "WS-FIN-042", color: "red"})
   show_alert_timeline({incident_id: "INC-001"})
   siem_close_incident({incident_id: "INC-001", resolution: "..."})
```

### Flujo de Demo Rápida (para presentaciones de 5 minutos)

1. Ir a `/dashboard`
2. Hacer clic en el Caso 1 (auto-contención) — observar la Narration Footer
3. Hacer clic en el Caso 2 (VIP) — observar la Approval Card, hacer clic en Approve
4. Hacer clic en el Caso 3 (falso positivo) — observar cómo el agente descarta
5. Ir a `/simulation` para mostrar el grafo animado

### Flujo de Demo Extendida (para presentaciones de 20 minutos)

1. Ir a `/generation` — generar datos frescos con `POST /gen/all`
2. Ir a `/dashboard` — mostrar KPIs del SOC
3. Ir a `/incidents` — mostrar incidentes, usar el botón "Analyze with AI" en uno real
4. Ir a `/detections` — mostrar árbol de procesos de una detección EDR
5. Ir a `/graph` — mostrar el grafo de relaciones del incidente
6. Volver a `/dashboard` — ejecutar Caso 2 (VIP approval) en vivo
7. Ir a `/timeline` — mostrar cada acción del agente con timestamps
8. Ir a `/simulation` — ejecutar APT29 con control de velocidad

---

## 6. Aplicación de Demo Automática — Simulation Page y Widgets Flotantes

La segunda "aplicación" dentro de CyberDemo es el **modo de simulación en vivo**, diseñado para presentaciones en pantalla grande. Se compone de:

### 6.1 Demo Control Bar (siempre visible)

Ya descrita en §4.1. Es el "mando a distancia" de la demo. El presentador puede:
- Cambiar de escenario sin salir de la vista actual
- Ajustar la velocidad según el ritmo de la audiencia
- Pausar para explicar un punto y reanudar

### 6.2 DemoFloatingWidget — El Copiloto Visible

El widget flotante representa visualmente que hay una IA trabajando en segundo plano. Durante una demo en vivo:
- Aparecen sugerencias automáticas mientras el agente trabaja
- El badge con el número de sugerencias llama la atención de la audiencia
- Cuando el presentador lo expande, muestra el razonamiento del agente

### 6.3 NarrationFooter — La Voz del Agente

El footer de narración es el elemento más impactante para la audiencia técnica:
- Muestra en tiempo real lo que el agente está "pensando"
- El streaming de mensajes crea la sensación de ver a un humano investigar en vivo
- El color coding (verde = éxito, amarillo = advertencia) permite seguir el flujo sin leer cada línea

### 6.4 Simulation Page — Modo Presentación Completo

`/simulation` es la pantalla optimizada para proyector o pantalla de sala:
- **3 columnas** muestran todo el contexto simultáneamente
- El grafo animado crea el efecto visual "WOW" más impactante
- La narración siempre visible en footer garantiza que la audiencia vea el razonamiento
- Los controles locales permiten al presentador controlar sin salir de la página

### 6.5 Flujo de Demo con Simulation Page

```
Paso 1: Abrir /simulation en modo pantalla completa
Paso 2: Seleccionar "APT29 Espionage Campaign" en el dropdown
Paso 3: Hacer clic en Play a velocidad 1x
Paso 4: El grafo empieza a mostrar nodos apareciendo
Paso 5: La columna MITRE muestra fases completándose
Paso 6: La narración explica cada acción
Paso 7: El aIP Widget sugiere acciones de forma proactiva
Paso 8: Pausar en la fase de "Lateral Movement" para explicar
Paso 9: Reanudar y observar la contención automática
Paso 10: Ir a /timeline para ver el registro completo
```

---

# PARTE 2 — MCPs, SKILLS, HOOKS, APIS Y SCRIPTS

## 7. Arquitectura MCP — Interacción Bidireccional

CyberDemo implementa **3 servidores MCP** que conectan al agente IA con la plataforma. La arquitectura es bidireccional:

```
                    SoulInTheBot (Agente IA)
                    Puerto: 18789
                         │
           ┌─────────────┼──────────────┐
           │             │              │
           ▼             ▼              ▼
   Backend MCP      Data MCP      Frontend MCP
   :8000/mcp/*   :8000/data-mcp  :3001 (WebSocket)
   ~30 tools        8 tools          8 tools
   Operaciones SOC  Datos sintéticos  Visualización UI
```

### 7.1 Backend MCP Server — Operaciones SOC

**Protocolo:** JSON-RPC 2.0 sobre HTTP
**Endpoint:** `POST http://localhost:8000/mcp/messages`
**Archivo:** `backend/src/mcp/server.py`

Este es el MCP principal: permite al agente operar el SOC como un analista Tier-1.

#### Tools disponibles por categoría:

**SIEM (4 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `siem_list_incidents` | Lista incidentes de seguridad filtrados | `{severity?, status?, limit?}` |
| `siem_get_incident` | Detalle completo de un incidente | `{incident_id}` |
| `siem_add_comment` | Añade comentario de investigación | `{incident_id, comment}` |
| `siem_close_incident` | Cierra incidente con resolución | `{incident_id, resolution, notes?}` |

**EDR (6 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `edr_get_detection` | Detalle de una detección | `{detection_id}` |
| `edr_get_process_tree` | Árbol de procesos padre/hijo | `{detection_id}` |
| `edr_hunt_hash` | Busca un hash en todos los endpoints | `{hash}` |
| `edr_contain_host` | Aísla un host de la red | `{device_id, reason}` |
| `edr_lift_containment` | Levanta el aislamiento | `{device_id, reason}` |
| `edr_list_detections` | Lista detecciones recientes | `{severity?, limit?}` |

**Threat Intelligence (2 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `intel_lookup_ioc` | Busca IOC en feeds de inteligencia | `{ioc, type}` |
| `intel_get_campaign` | Info de campaña de amenaza | `{campaign_id}` |

**CTEM — Vulnerabilidades (2 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `ctem_get_findings` | Hallazgos de vulnerabilidad por activo | `{asset_id?}` |
| `ctem_prioritize` | Prioriza vulnerabilidades según criterios | `{criteria}` |

**Aprobaciones HITL (2 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `approval_request` | Solicita aprobación humana para una acción | `{action, asset_id, reason}` |
| `approval_check` | Verifica el estado de una aprobación | `{request_id}` |

**Tickets (2 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `ticket_create` | Crea ticket de remediación | `{title, description, priority}` |
| `ticket_update` | Actualiza estado de ticket | `{ticket_id, status?, notes?}` |

**Reportes (1 tool):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `report_generate` | Genera reporte de incidente | `{type, format, filters?}` |

**Threat Enrichment (3 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `threat_enrich_ip` | Enriquece IP con contexto de amenaza | `{ip}` |
| `threat_enrich_domain` | Enriquece dominio | `{domain}` |
| `threat_enrich_hash` | Enriquece hash de archivo con reputación | `{hash}` |

**Vulnerabilidades (3 tools):**

| Tool | Descripción | Input |
|------|-------------|-------|
| `vuln_get_details` | Detalle de un CVE | `{cve_id}` |
| `vuln_get_affected_assets` | Activos afectados por un CVE | `{cve_id}` |
| `vuln_calculate_risk` | Calcula riesgo combinado | `{cve_id, asset_id}` |

#### Ejemplo de llamada directa:

```bash
# Listar incidentes críticos
curl -X POST http://localhost:8000/mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "siem_list_incidents",
      "arguments": {"severity": "critical", "limit": 10}
    }
  }'

# Contener un host
curl -X POST http://localhost:8000/mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "edr_contain_host",
      "arguments": {
        "device_id": "WS-FIN-042",
        "reason": "Ransomware detected - immediate isolation required"
      }
    }
  }'
```

---

### 7.2 Data MCP Server — Generación de Datos Sintéticos

**Protocolo:** JSON-RPC 2.0 sobre HTTP
**Endpoint:** `POST http://localhost:8000/data-mcp/messages`
**Archivo:** `backend/src/mcp/data_server.py`

Permite al agente generar o resetear los datos sintéticos de la demo.

| Tool | Descripción | Input |
|------|-------------|-------|
| `data_generate_assets` | Genera 1.000 activos (hosts, servers, laptops) | `{count?, seed?}` |
| `data_generate_edr_detections` | Genera 1.000 detecciones EDR estilo CrowdStrike | `{count?, seed?}` |
| `data_generate_siem_incidents` | Genera ~650 incidentes SIEM correlacionados | `{seed?}` |
| `data_generate_threat_intel` | Genera ~200 IOCs (hash/IP/dominio) con veredictos | `{count?, seed?}` |
| `data_generate_ctem_findings` | Genera ~3.000 vulnerabilidades CVE | `{seed?}` |
| `data_generate_all` | Genera todos los tipos con cross-references | `{seed?}` |
| `data_reset` | Limpia todos los datos generados | `{}` |
| `data_get_health` | Estado y conteos actuales de datos | `{}` |

#### Ejemplo de uso para demo:

```bash
# Resetear y generar datos frescos antes de una demo
curl -X POST http://localhost:8000/data-mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": "data_reset", "arguments": {}}
  }'

curl -X POST http://localhost:8000/data-mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {"name": "data_generate_all", "arguments": {"seed": 42}}
  }'
```

---

### 7.3 Frontend MCP Server — Control de Visualización UI

**Protocolo:** WebSocket con mensajes JSON
**Endpoint:** `ws://localhost:3001`
**Archivo:** `frontend/src/mcp/server.ts`

Permite al agente **controlar la interfaz React en tiempo real**. Cuando el agente llama una tool, el servidor hace broadcast a todos los clientes React conectados.

| Tool | Qué hace en la UI | Input |
|------|-------------------|-------|
| `show_simulation` | Muestra una simulación de ataque y actualiza el grafo | `{scenario, speed?}` |
| `generate_chart` | Genera y muestra un gráfico dinámico en el dashboard | `{type, data, title}` |
| `run_demo_scenario` | Dispara uno de los 3 escenarios predefinidos | `{scenario_name}` |
| `get_demo_state` | Obtiene el estado actual del demo desde la UI | `{}` |
| `update_dashboard` | Actualiza KPIs y métricas del dashboard en tiempo real | `{metrics}` |
| `show_alert_timeline` | Navega a la vista de timeline con un incidente específico | `{incident_id}` |
| `highlight_asset` | Resalta un activo en el grafo con efecto visual | `{asset_id, color?}` |
| `show_postmortem` | Navega a la vista de postmortem de un incidente | `{incident_id}` |

#### Estado compartido (DemoState):

```typescript
interface DemoState {
  activeScenario: string | null;     // Escenario activo en la UI
  simulationRunning: boolean;         // Si hay simulación en curso
  highlightedAssets: string[];        // Assets con efecto visual
  currentView: string;                // Vista actual del usuario
  charts: Chart[];                    // Gráficos dinámicos generados
  timeline: Timeline | null;          // Timeline de eventos activo
}
```

#### Ejemplo de uso desde el agente:

```javascript
// El agente envía por WebSocket:
{
  "tool": "highlight_asset",
  "params": {
    "asset_id": "WS-FIN-042",
    "color": "red"
  }
}
// → El grafo en la UI resalta WS-FIN-042 en rojo inmediatamente

{
  "tool": "update_dashboard",
  "params": {
    "metrics": {
      "incidents_active": 3,
      "contained_hosts": 1,
      "automation_rate": 0.67
    }
  }
}
// → Los KPIs del dashboard se actualizan en tiempo real
```

---

## 8. Plugin CyberDemo SOC Analyst

**Ubicación:** `extensions/cyberdemo/`
**Plugin ID:** `cyberdemo-soc-analyst`
**Archivo de configuración:** `extensions/cyberdemo/SoulInTheBot.plugin.json`

El plugin es la capa que conecta SoulInTheBot con CyberDemo. Cuando se carga el plugin, el agente adquiere el rol de un Analista SOC Tier-1 y tiene acceso a todos los MCP servers.

### 8.1 Configuración del Plugin

```json
{
  "id": "cyberdemo-soc-analyst",
  "mcp_servers": {
    "cyberdemo-api": "http://localhost:8000/mcp",
    "cyberdemo-data": "http://localhost:8000/data-mcp",
    "cyberdemo-frontend": "ws://localhost:3001"
  },
  "configSchema": {
    "apiBaseUrl": "http://localhost:8000",
    "autoContainmentEnabled": true,
    "confidenceThresholdHigh": 0.85,
    "confidenceThresholdMedium": 0.60
  }
}
```

#### Para cargar el plugin:

```bash
moltbot extensions load extensions/cyberdemo
```

---

### 8.2 Skill `soc-analyst`

**Archivo:** `extensions/cyberdemo/skills/soc-analyst/SKILL.md`

La skill define el rol, el workflow de investigación y las reglas operativas del agente. Cuando está activa, el agente:
- Actúa como Analista SOC Tier-1
- Sigue el workflow: detectar → investigar → enriquecer → decidir → actuar
- Usa el Policy Engine para determinar auto-contención vs. aprobación vs. falso positivo

#### Comandos del Skill:

| Comando | Qué hace | Ejemplo de uso en demo |
|---------|----------|----------------------|
| `/investigate <incident_id>` | Investiga un incidente específico de principio a fin | `/investigate INC-2026-001` |
| `/demo <scenario>` | Ejecuta un escenario de ataque completo | `/demo apt29` |
| `/demo_case_1` | Ejecuta el Caso 1 (auto-contención) | `/demo_case_1` |
| `/demo_case_2` | Ejecuta el Caso 2 (aprobación VIP) | `/demo_case_2` |
| `/demo_case_3` | Ejecuta el Caso 3 (falso positivo) | `/demo_case_3` |
| `/status` | Muestra estado actual del SOC | `/status` |
| `/assets [filter]` | Lista activos con filtro opcional | `/assets VIP` |
| `/pending` | Lista aprobaciones pendientes | `/pending` |

---

### 8.3 Policy Engine — Lógica de Decisión

**Archivo:** `extensions/cyberdemo/src/policy-engine.ts`

El Policy Engine es el motor de reglas determinístico que decide qué hacer con cada incidente. Sus reglas son:

| Condición | Decisión |
|-----------|----------|
| Score de confianza ≥ 0.85 + Activo NO es VIP | Auto-contención automática |
| Score de confianza ≥ 0.60 + Activo ES VIP | Solicitar aprobación humana |
| Score de confianza < 0.60 | Descartar como falso positivo |

**Cálculo del Score de Confianza** (`confidence-score.ts`):
- Score de Intel (¿hash/IP conocido malicioso?) — peso 40%
- Score de Comportamiento (¿proceso sospechoso?) — peso 30%
- Score de Contexto (¿usuario/hora inusual?) — peso 20%
- Score de Propagación (¿detectado en más endpoints?) — peso 10%

---

### 8.4 Hooks del Plugin

**Archivo:** `extensions/cyberdemo/src/hooks.ts`

Los hooks se disparan automáticamente en eventos del ciclo de vida del agente:

| Hook | Cuándo se dispara | Qué hace |
|------|-------------------|----------|
| `onToolStart` | Antes de cada tool call | Log de inicio + notificación al frontend |
| `onToolComplete` | Después de cada tool call | Actualización de timeline + notificación |
| `onContainment` | Al ejecutar una contención | Verificación de política + audit log + notificación de canal |
| `onApprovalReceived` | Cuando el humano decide (approve/reject) | Reanuda el workflow + actualiza incidente |
| `onInvestigationStart` | Al iniciar `/investigate` | Inicia estado de workflow y trazabilidad |
| `onInvestigationComplete` | Al cerrar el incidente | Cierre, auditoría y notificación final |

**Handlers de comandos demo:**

| Handler | Cuándo se activa |
|---------|-----------------|
| `handleDemoCase1` | Cuando se ejecuta `/demo_case_1` o se hace clic en CASE-001 |
| `handleDemoCase2` | Cuando se ejecuta `/demo_case_2` o se hace clic en CASE-002 |
| `handleDemoCase3` | Cuando se ejecuta `/demo_case_3` o se hace clic en CASE-003 |

---

## 9. APIs REST — Referencia Completa

**Base URL:** `http://localhost:8000`
**Archivo:** `backend/src/api/router.py`

### 9.1 APIs de Generación de Datos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/gen/reset` | POST | Limpia y recrea todos los índices de datos |
| `/gen/all` | POST | Genera assets, EDR, SIEM, Intel y CTEM de una vez |
| `/gen/assets` | POST | Genera solo activos |
| `/gen/status` | GET | Estado actual de la generación |
| `/gen/health` | GET | Salud del sistema de generación |

### 9.2 APIs SIEM

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/siem/incidents` | GET | Lista incidentes (filtrable por severity, status) |
| `/siem/incidents/{id}` | GET | Detalle de incidente |
| `/siem/incidents/{id}/comments` | POST | Añadir comentario |
| `/siem/incidents/{id}/close` | POST | Cerrar incidente |

### 9.3 APIs EDR

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/edr/detections` | GET | Lista detecciones |
| `/edr/detections/{id}` | GET | Detalle de detección |
| `/edr/detections/{id}/process-tree` | GET | Árbol de procesos |
| `/edr/devices/{id}/contain` | POST | Aislar dispositivo |
| `/edr/devices/{id}/lift` | POST | Levantar aislamiento |
| `/edr/hunt/{hash}` | GET | Buscar hash en todos los endpoints |

### 9.4 APIs de Demo y Simulación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/demo-scenarios/run/{n}` | POST | Ejecuta caso de demo 1, 2 o 3 |
| `/api/v1/simulation/start` | POST | Inicia simulación de ataque |
| `/api/v1/simulation/pause` | POST | Pausa simulación |
| `/api/v1/simulation/resume` | POST | Reanuda simulación |
| `/api/v1/simulation/speed` | POST | Cambia velocidad `{factor: 0.5\|1\|2\|4}` |
| `/api/v1/analysis/queue` | POST | Encola análisis IA de un incidente |

### 9.5 WebSockets

| Endpoint | Descripción |
|----------|-------------|
| `WS /api/v1/simulation/ws` | Eventos de simulación en tiempo real |
| `WS /api/v1/narration/ws/{session}` | Stream de narración del agente |
| `WS /api/v1/aip-assist/ws/{session}` | Sugerencias proactivas del agente |
| `WS /api/v1/analysis/ws` | Updates de análisis asíncrono |

### 9.6 APIs de Aprobaciones (HITL)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/approvals/{incident_id}` | GET | Estado de aprobación |
| `/approvals/{incident_id}` | POST | Solicitar aprobación |
| `/approvals/{incident_id}/decide` | POST | `{decision: "approve"\|"reject"}` |
| `/approvals/pending` | GET | Lista de aprobaciones pendientes |

### 9.7 APIs de Enriquecimiento

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/vulnerabilities` | POST | Enriquece vulnerabilidades desde fuentes externas (NVD, EPSS) |
| `/api/threats` | POST | Enriquece amenazas (OTX, AbuseIPDB, GreyNoise) |
| `/api/status/{job_id}` | GET | Estado de un job de enriquecimiento |

---

## 10. Scripts y Programas

### 10.1 Scripts de Setup y Ejecución

| Script | Ubicación | Qué hace |
|--------|-----------|----------|
| `start.sh` | Raíz | Arranque completo del entorno (backend + frontend + DBs) |
| `demo-setup.sh` | `scripts/` | Setup guiado de demo: genera datos, verifica servicios |
| `CompleteVerificationTestsX.sh` | `scripts/` | Ejecuta todos los tests (unit + integration + E2E) |

#### Para iniciar la demo:

```bash
# 1. Arrancar todo el entorno
./start.sh

# 2. O arrancar servicios individualmente:
# Backend
cd backend && uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev  # Puerto 5173

# Frontend MCP Server
cd frontend && npm run mcp  # Puerto 3001
```

### 10.2 Generadores de Datos Sintéticos (Python)

**Ubicación:** `backend/src/generators/`

| Generador | Archivo | Qué genera |
|-----------|---------|-----------|
| Assets | `gen_assets.py` | 1.000 activos: workstations, servers, laptops con tags, owner, riesgo |
| EDR | `gen_edr.py` | 1.000 detecciones al estilo CrowdStrike con técnicas MITRE |
| Árboles de proceso | `gen_process_trees.py` | Árboles padre/hijo para las detecciones |
| SIEM | `gen_siem.py` | ~650 incidentes correlacionando EDR + Intel + CTEM |
| Threat Intel | `gen_intel.py` | ~200 IOCs (hash/IP/dominio) con veredictos y fuentes |
| CTEM | `gen_ctem.py` | ~3.000 vulnerabilidades CVE con CVSS, EPSS, VPR |

### 10.3 Escenarios de Demo Predefinidos

**Ubicación:** `backend/src/demo/`

| Archivo | Escenario | Descripción |
|---------|-----------|-------------|
| `demo_commands.ts` | Casos 1, 2, 3 | Los 3 casos ancla: INC-ANCHOR-001, 002, 003 |
| `scenario_ransomware.py` | REvil Ransomware | Propagación, cifrado, negociación |
| `scenario_insider_threat.py` | Insider Threat | Exfiltración interna, detección tardía |
| `scenario_supply_chain.py` | Supply Chain (SolarWinds) | Compromiso de cadena de suministro |

### 10.4 Playbooks YAML

**Ubicación:** `backend/playbooks/`

| Playbook | Situación de uso |
|----------|-----------------|
| `contain_and_investigate.yaml` | Flujo estándar de contención e investigación |
| `ransomware_response.yaml` | Respuesta a ransomware detectado |
| `vip_escalation.yaml` | Escalación cuando el activo es VIP |
| `lateral_movement_hunt.yaml` | Búsqueda de movimiento lateral |
| `false_positive_closure.yaml` | Cierre limpio de falsos positivos |

### 10.5 Clientes de Enriquecimiento Externos

**Ubicación:** `backend/src/services/clients/`

| Cliente | API Externa | Qué obtiene |
|---------|-------------|------------|
| `nvd_client.py` | NIST NVD | CVEs, CVSS scores, detalles de vulnerabilidad |
| `epss_client.py` | FIRST EPSS | Probabilidad de explotación activa |
| `otx_client.py` | AlienVault OTX | Threat intel, IOCs, campañas |
| `abuseipdb_client.py` | AbuseIPDB | Reputación de IPs |
| `greynoise_client.py` | GreyNoise | Clasificación de IPs (benign/malicious/unknown) |

---

## 11. Ejemplos de Demo — Casos de Uso para Mostrar

### Ejemplo 1: Demostrar la automatización total (Caso 1)

```
Presentador: "Voy a mostrar cómo el agente maneja una amenaza estándar
sin intervención humana."

1. Abrir /dashboard en el navegador
2. Hacer clic en la tarjeta "Malware Auto-Containment" (🛡️ WS-FIN-042)
3. Señalar el NarrationFooter mientras aparecen los mensajes:
   - "Investigando INC-ANCHOR-001..."
   - "Árbol de procesos obtenido: cmd.exe → powershell.exe → malware.exe"
   - "Hash abc123 confirmado: TrickBot, atribución Wizard Spider"
   - "Activo WS-FIN-042: workstation estándar, NO es VIP"
   - "Score de confianza: 0.92 → CONTENCIÓN AUTOMÁTICA"
   - "✅ Host WS-FIN-042 aislado de la red"
4. Ir a /timeline para mostrar cada paso con timestamp
```

### Ejemplo 2: Demostrar Human-in-the-Loop (Caso 2)

```
Presentador: "Ahora vamos a ver qué pasa cuando el activo es del CFO.
El agente no puede actuar solo."

1. Hacer clic en "VIP Threat Response" (👤 LAPTOP-CFO-01)
2. Observar cómo el agente analiza (mismos pasos)
3. El Narration Footer muestra:
   - "Activo LAPTOP-CFO-01: VIP (CFO) — requiere aprobación"
   - "Solicitando aprobación humana..."
4. Aparece la APPROVAL CARD en la tarjeta
5. Presentador: "¿Aprobamos o rechazamos?"
6. Hacer clic en [Approve] en vivo
7. Narration: "Aprobación recibida. Procediendo con contención."
8. "✅ LAPTOP-CFO-01 aislado"
```

### Ejemplo 3: Demostrar inteligencia del agente (Caso 3)

```
Presentador: "No todo es una amenaza real. El agente también detecta
falsos positivos."

1. Hacer clic en "False Positive Detection" (🔍 SRV-DEV-03)
2. Narration Footer muestra:
   - "Analizando actividad en SRV-DEV-03..."
   - "Árbol de procesos: jenkins → mvn → java (proceso de build)"
   - "IOC lookup: no encontrado en feeds de inteligencia"
   - "Hash: sin coincidencias maliciosas"
   - "Contexto: servidor de CI/CD, actividad en horario laboral"
   - "Score de confianza: 0.23 → FALSO POSITIVO"
   - "🟢 Caso cerrado sin acción. Incidente descartado."
3. La tarjeta muestra el icono verde 🟢
```

### Ejemplo 4: Demo técnica con el agente desde el canal

```
# En el canal de SoulInTheBot, ejecutar:

/investigate INC-2026-047

# El agente responderá narrando cada paso en tiempo real
# La UI mostrará los cambios vía MCP frontend

# Para ejecutar directamente un caso:
/demo_case_2

# Para ver estado del SOC:
/status
```

### Ejemplo 5: Llamada directa a MCP para mostrar capacidades técnicas

```bash
# Mostrar a audiencia técnica cómo el agente llama las herramientas

# 1. Listar tools disponibles
curl -s -X POST http://localhost:8000/mcp/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  | python3 -m json.tool

# 2. Investigar un IOC en tiempo real
curl -s -X POST http://localhost:8000/mcp/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", "id": 2,
    "method": "tools/call",
    "params": {
      "name": "intel_lookup_ioc",
      "arguments": {"ioc": "185.220.101.45", "type": "ip"}
    }
  }' | python3 -m json.tool

# 3. Ver activos de alto riesgo
curl -s http://localhost:8000/ctem/assets?min_risk=8 | python3 -m json.tool

# 4. Verificar estado de la generación de datos
curl -s http://localhost:8000/data-mcp/messages \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"data_get_health","arguments":{}}}' \
  | python3 -m json.tool
```

### Ejemplo 6: Demo con Simulation Page (presentación formal)

```
1. Abrir http://localhost:5173/simulation en modo pantalla completa
2. Seleccionar "APT29 Espionage Campaign" en el dropdown
3. Velocidad: 1x
4. Play
5. Explicar mientras avanza:
   - "En la columna izquierda ven las fases MITRE ATT&CK completándose"
   - "El grafo central muestra cómo el atacante se mueve lateralmente"
   - "Aquí abajo el agente explica lo que está viendo"
6. Pausar en "Lateral Movement" (fase 8)
7. "¿Ven cómo el agente ya identificó 3 endpoints comprometidos?"
8. Reanudar
9. El agente contiene automáticamente (sin VIPs en APT29 scenario)
10. Ir a /timeline para el post-mortem
```

---

## 12. Resumen de Componentes por Capa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAPA COMPLETO DE COMPONENTES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FRONTEND (React/Vite)                                                      │
│  ─────────────────────                                                      │
│  14 vistas SOC + 6 componentes de demo + MCP Frontend (3001)               │
│  Hooks: useSimulation, useNarration, useAipSuggestions, useWebSocket        │
│  Context: DemoContext (estado global compartido)                            │
│  Adapter: cytoscapeAdapter (grafo de ataque)                                │
│                                                                             │
│  BACKEND (FastAPI/Python)                                                   │
│  ──────────────────────                                                     │
│  20+ endpoints REST por dominio (SIEM/EDR/Intel/CTEM/Demo/...)             │
│  MCP SOC Server: ~30 tools de operación SOC                                │
│  MCP Data Server: 8 tools de generación de datos                           │
│  Policy Engine: reglas determinísticas de decisión                         │
│  Generadores: assets/EDR/SIEM/Intel/CTEM sintéticos                        │
│  Clientes de enriquecimiento: NVD, EPSS, OTX, AbuseIPDB, GreyNoise        │
│                                                                             │
│  PLUGIN/SKILL (SoulInTheBot)                                                │
│  ──────────────────────────                                                 │
│  Plugin: cyberdemo-soc-analyst                                              │
│  Skill: soc-analyst con 8 comandos                                         │
│  TS Services: api-client, confidence-score, policy-engine, investigation   │
│  Hooks: onToolStart/Complete, onContainment, onApproval, onInvestigation   │
│  Demo Commands: handleDemoCase1/2/3                                        │
│                                                                             │
│  BASES DE DATOS                                                             │
│  ──────────────                                                             │
│  OpenSearch (9200): alertas, logs, threat intel, attack surface            │
│  PostgreSQL (5433): assets, config, audit, tickets                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

---

# PARTE 3: SISTEMA DE CONTROL BIDIRECCIONAL AGENTE-UI Y MOTOR DE DATOS DINÁMICOS

---

## 3.1 Visión General

La Parte 3 documenta el sistema de **orquestación bidireccional** entre el agente Vega y la interfaz de usuario. Mientras que las Partes 1 y 2 cubren la plataforma base (SIEM, EDR, Intel, CTEM, grafo de ataque y el plugin SOC Analyst), esta parte describe las capacidades avanzadas que permiten al agente **controlar la UI en tiempo real** y alimentar las vistas con **datos de escenarios dinámicos** fase a fase.

### Arquitectura del Sistema Bidireccional

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FLUJO BIDIRECCIONAL COMPLETO                     │
│                                                                      │
│  ┌─────────────┐    WebSocket     ┌──────────────────┐              │
│  │  Frontend    │◄───(port 3001)──│  MCP WS Server   │              │
│  │  React App   │                 │  (Node.js)       │              │
│  └──────┬───────┘                 └────────┬─────────┘              │
│         │                                  ▲                         │
│         │ REST API                         │ WebSocket               │
│         ▼                                  │                         │
│  ┌──────────────┐   UIBridge      ┌───────┴──────────┐             │
│  │  FastAPI      │───(async ws)──►│  UIBridge Client  │             │
│  │  Backend      │                │  (Python)         │             │
│  └──────┬───────┘                 └──────────────────┘              │
│         │                                                            │
│         │ Phase data                                                 │
│         ▼                                                            │
│  ┌──────────────────────────────────────┐                           │
│  │  ScenarioStateManager (Singleton)    │                           │
│  │  Datos acumulativos fase a fase      │                           │
│  │  APT29: 8 fases, 14 inc, 15 det, 7 IOC │                       │
│  └──────────────────────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────┘
```

El sistema se organiza en dos EPICs principales:

| EPIC | Descripción | Componentes |
|------|-------------|-------------|
| **EPIC-001** | Control Bidireccional Agente-UI | UIBridge, MCP WS Server, hooks de sincronización, componentes overlay |
| **EPIC-002** | Motor de Datos Dinámicos de Escenarios | ScenarioStateManager, scripts de escenarios, coordinador de fases |

---

## 3.2 EPIC-001: Control Bidireccional Agente-UI

### 3.2.1 UIBridge — Puente Backend-Frontend

**Archivo**: `backend/src/services/ui_bridge.py`

La clase `UIBridge` es un cliente WebSocket asíncrono que conecta el backend Python con el MCP WS Server (puerto 3001). Permite al agente enviar comandos de control a la UI.

**Características principales:**

- **Conexión lazy**: No se conecta al instanciar. La primera llamada a cualquier método `send_*` establece la conexión WebSocket
- **Fallo silencioso**: Si el WS Server no está disponible, los comandos se ignoran sin causar errores (la demo continúa sin interrupciones)
- **Reconexión automática**: Si una conexión se pierde, se resetea y reconecta en la siguiente llamada

**Métodos disponibles:**

| Método | Descripción | Parámetros |
|--------|-------------|------------|
| `send_navigation(page)` | Navega la UI a una página | `page`: ruta (ej: `/siem`, `/edr`) |
| `send_highlight(assets)` | Resalta assets en el grafo | `assets`: lista de IDs de assets |
| `send_chart(chart_data)` | Muestra un chart overlay flotante | `chart_data`: configuración del gráfico |
| `send_timeline(timeline_data)` | Muestra el panel de timeline | `timeline_data`: entradas del timeline |
| `disconnect()` | Cierra la conexión WebSocket | — |

**Ejemplo de uso interno:**

```python
bridge = UIBridge()  # No se conecta aún
await bridge.send_navigation("/siem")  # Primera llamada: conecta + envía
await bridge.send_highlight(["WS-EXEC-PC01", "SRV-DC01"])  # Reutiliza conexión
```

---

### 3.2.2 Endpoint REST — POST /api/v1/ui/action

**Archivo**: `backend/src/api/ui_actions.py`

Endpoint REST que recibe comandos de UI y los reenvía al MCP WS Server a través del UIBridge. Permite control programático de la interfaz desde cualquier servicio o script externo.

**Acciones válidas:**

| Acción | Parámetros | Efecto en la UI |
|--------|------------|-----------------|
| `navigate` | `{ page: "/siem" }` | Navega a la página indicada |
| `highlight` | `{ assets: ["id1", "id2"] }` | Resalta assets en el grafo |
| `chart` | `{ chart_data: { type, title, data } }` | Muestra gráfico flotante |
| `timeline` | `{ timeline_data: { entries } }` | Muestra panel de timeline |

**Ejemplo de petición:**

```bash
curl -X POST http://localhost:8000/api/v1/ui/action \
  -H "Content-Type: application/json" \
  -d '{"action": "navigate", "params": {"page": "/siem"}}'
# Respuesta: {"status": "ok", "action": "navigate"}
```

---

### 3.2.3 Hook: useMcpStateSync — Sincronización WebSocket en Tiempo Real

**Archivo**: `frontend/src/hooks/useMcpStateSync.ts`

Hook de React que mantiene sincronizado el estado de la UI con los comandos del agente a través de WebSocket.

**Funcionamiento:**

1. Se conecta a `ws://localhost:3001/ws` al montarse
2. Recibe mensajes JSON de tipo `McpStateUpdate`
3. Mergea cada campo recibido en el estado React local
4. Auto-reconecta con backoff exponencial si la conexión se pierde

**Parámetros de reconexión:**

| Parámetro | Valor |
|-----------|-------|
| Delay base | 1 segundo |
| Multiplicador | 2x por intento |
| Máximo de intentos | 10 |

**Interfaz de retorno:**

```typescript
{
  state: McpStateUpdate;           // Estado actual sincronizado
  connectionStatus: string;        // "connected" | "disconnected" | "connecting"
  isConnected: boolean;            // true si está conectado
  reconnect: () => void;           // Forzar reconexión manual
  disconnect: () => void;          // Desconectar
}
```

**Tipo `McpStateUpdate`:**

```typescript
interface McpStateUpdate {
  currentPage?: string;            // Página a la que navegar
  highlightedAssets?: McpHighlightedAsset[];  // Assets a resaltar
  charts?: McpChart[];             // Gráficos flotantes a mostrar
  timeline?: McpTimeline;          // Panel de timeline
  kpiOverrides?: McpKpiOverride[]; // Valores KPI animados
  metadata?: Record<string, unknown>;
}
```

---

### 3.2.4 Hook: useWsNavigation — Navegación Dirigida por el Agente

**Archivo**: `frontend/src/hooks/useWsNavigation.ts`

Cuando el campo `currentPage` cambia en el estado MCP sincronizado, este hook:

1. Navega automáticamente a la página indicada usando `react-router`
2. Muestra un toast informativo: *"Vega navigated to [pageName]"*

Esto permite que el agente dirija la atención del usuario a la vista relevante durante cada fase del análisis.

---

### 3.2.5 Hook: useAssetHighlight — Resaltado de Assets en el Grafo

**Archivo**: `frontend/src/hooks/useAssetHighlight.ts`

Aplica y remueve estilos de resaltado en los nodos de Cytoscape.js (el grafo de ataque).

**Modos de resaltado:**

| Modo | Efecto Visual | Duración CSS |
|------|---------------|-------------|
| `pulse` | Parpadeo del borde del nodo | 1.5s ease-in-out infinite |
| `glow` | Sombra luminosa alrededor del nodo | 2s ease-in-out infinite |
| `zoom` | Escalado pulsante del nodo | 2s ease-in-out infinite |

**Estilos CSS** (definidos en `frontend/src/styles/highlightStyles.ts`):

Los estilos incluyen `@keyframes` para cada modo de animación y se aplican como clases CSS tanto a nodos Cytoscape como a elementos HTML estándar:

- `mcp-highlight-pulse`: animación de borde con color cyan
- `mcp-highlight-glow`: sombra box-shadow con gradiente cyan
- `mcp-highlight-zoom`: transformación scale oscilante

---

### 3.2.6 Componente: ChartOverlay — Gráficos Flotantes

**Archivo**: `frontend/src/components/mcp/ChartOverlay.tsx`

Componente de tarjeta flotante que muestra gráficos de barras horizontales, superpuesto sobre la vista actual.

**Características:**

- **Posición fija**: Se muestra sobre el contenido existente sin desplazarlo
- **Animación de entrada**: Fade-in + scale + translate-y durante 300ms
- **Auto-dismiss**: Se cierra automáticamente tras un tiempo configurable (por defecto 10 segundos)
- **Botón de cierre**: El usuario puede cerrarlo manualmente
- **Badge de tipo**: Muestra el tipo de gráfico (`bar`, `line`, `pie`)
- **Lista apilada**: El componente `ChartOverlayList` renderiza múltiples gráficos apilados verticalmente

**Props del componente:**

```typescript
interface ChartOverlayProps {
  chart: McpChart;                 // Datos del gráfico
  onClose: () => void;             // Callback al cerrar
  autoDismissMs?: number;          // Tiempo antes de auto-cierre (default: 10000)
}
```

---

### 3.2.7 Componente: TimelinePanel — Panel de Línea Temporal

**Archivo**: `frontend/src/components/mcp/TimelinePanel.tsx`

Panel deslizante desde el borde derecho que muestra una cronología de eventos del ataque.

**Características:**

- **Ancho fijo**: 320px (`w-80`), altura completa de la ventana
- **Animación**: Deslizamiento desde la derecha (translate-x) durante 300ms
- **Entradas escalonadas**: Cada entrada aparece con un retraso de `index × 100ms`
- **Indicadores de severidad**: Puntos de color según severidad del evento
- **Contenido por entrada**: timestamp, título, descripción y severidad

**Estructura de una entrada de timeline:**

```typescript
interface McpTimelineEntry {
  id: string;
  timestamp: string;
  title: string;
  description?: string;
  severity?: "info" | "warning" | "error" | "critical";
}
```

---

### 3.2.8 Componente: AnimatedKpiValue — KPIs con Animación de Conteo

**Archivo**: `frontend/src/components/mcp/AnimatedKpiValue.tsx`

Componente que muestra valores numéricos con una animación de conteo desde 0 hasta el valor objetivo.

**Props:**

| Prop | Tipo | Default | Descripción |
|------|------|---------|-------------|
| `value` | number | — | Valor objetivo |
| `decimals` | number | 0 | Decimales a mostrar |
| `prefix` | string | "" | Texto antes del número (ej: "$") |
| `suffix` | string | "" | Texto después del número (ej: "%") |
| `durationMs` | number | 1000 | Duración de la animación |
| `animate` | boolean | true | Habilitar/deshabilitar animación |

**Easing**: Curva ease-out cúbica (`1 - (1 - t)³`) para una animación natural que desacelera al acercarse al valor final.

---

### 3.2.9 Servicio: agentUIActions — Despacho de Acciones Post-Análisis

**Archivo**: `frontend/src/services/agentUIActions.ts`

Dispatcher que ejecuta acciones de UI después de que el agente completa el análisis de una fase. Incluye un delay configurable para dar tiempo al usuario de leer el análisis antes de que la UI cambie.

**Configuración:**

```typescript
const dispatcher = createAgentUIActionDispatcher({
  onNavigate: (target) => navigate(`/${target}`),
  onHighlight: (element) => highlightAsset(element),
  delayMs: 1500,  // 1.5 segundos de espera post-análisis
});

// Despachar acciones de la fase actual
dispatcher.dispatch([
  { type: "navigate", target: "incidents", description: "Go to incidents" },
  { type: "highlight", element: "WS-EXEC-PC01", description: "Highlight host" },
]);
```

**Métodos:**

| Método | Descripción |
|--------|-------------|
| `dispatch(actions)` | Programa acciones con el delay configurado |
| `setEnabled(bool)` | Habilita/deshabilita el dispatcher |
| `isEnabled()` | Consulta si está habilitado |
| `destroy()` | Cancela todas las acciones pendientes |

---

### 3.2.10 Rate Limiter — Control de Frecuencia de Acciones

**Archivo**: `frontend/src/utils/rateLimiter.ts`

Limita la frecuencia de acciones del agente para evitar saturar la UI.

**Configuración por defecto:**

| Parámetro | Valor |
|-----------|-------|
| Máximo por segundo | 2 acciones |
| Comportamiento al exceder | Las acciones excedentes se encolan |
| Drenado de cola | Automático cuando la ventana temporal se renueva |

**Uso:**

```typescript
const limiter = createRateLimiter({ maxPerSecond: 2 });

limiter.execute(() => navigate("/siem"));     // Ejecuta inmediatamente
limiter.execute(() => highlight("host-1"));   // Ejecuta inmediatamente (2da en ventana)
limiter.execute(() => navigate("/edr"));      // Encolada (excede 2/s)
// Se ejecutará automáticamente ~500ms después
```

---

### 3.2.11 Action Queue — Cola con Detección de Interacción del Usuario

**Archivo**: `frontend/src/utils/actionQueue.ts`

Cola inteligente que **pausa** las acciones del agente mientras el usuario está interactuando activamente con la interfaz (haciendo click, escribiendo, scrolleando). Cuando el usuario deja de interactuar, todas las acciones encoladas se reproducen en orden FIFO.

**Configuración:**

| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `maxQueueSize` | 50 | Máximo de acciones en cola antes de descartar nuevas |

**Flujo:**

```
Usuario interactuando → Acciones se encolan (max 50)
Usuario deja de interactuar → Todas las acciones se reproducen en orden
```

Esto previene que el agente "secuestre" la interfaz mientras el usuario está trabajando.

---

### 3.2.12 Componente: PresenterToggle — Control Manual de Auto-Acciones

**Archivo**: `frontend/src/components/demo/PresenterToggle.tsx`

Toggle switch en el panel de control de la demo que permite al presentador habilitar/deshabilitar las auto-acciones del agente.

- **Habilitado** (cyan): El agente navega y resalta automáticamente según la fase
- **Deshabilitado** (gris): El presentador controla la UI manualmente

```
┌─────────────────────────────────┐
│ Auto UI Actions      [═══●]    │  ← Toggle ON (cyan)
└─────────────────────────────────┘
```

---

## 3.3 EPIC-002: Motor de Datos Dinámicos de Escenarios

### 3.3.1 Modelo de Datos — Tipos de Escenario

**Archivo**: `backend/src/models/scenario_types.py`

Define las estructuras Pydantic que representan los eventos de seguridad dentro de cada fase de un escenario.

**Tipos principales:**

| Tipo | Descripción | Campos clave |
|------|-------------|-------------|
| `SiemIncident` | Incidente SIEM | id, title, severity, source, mitre_tactic, mitre_technique |
| `EdrDetection` | Detección EDR | id, host_id, process_name, action, severity, mitre_technique |
| `IntelIOC` | Indicador de compromiso | id, type (ip/domain/hash/url), value, threat_actor, confidence |
| `AgentComment` | Comentario del agente | id, incident_id, content, author |
| `PhaseEvents` | Eventos de una fase | phase_number, phase_name, incidents[], detections[], iocs[] |
| `ScenarioState` | Estado acumulativo | scenario_id, current_phase, incidents[], detections[], iocs[], contained_hosts, closed_incidents, comments[] |

**Modelo de datos acumulativo**: `ScenarioState` acumula todos los datos desde la fase 1 hasta la fase actual. Si estamos en la fase 5, contiene los incidentes, detecciones e IOCs de las fases 1 a 5.

---

### 3.3.2 ScenarioStateManager — Gestor de Estado de Escenarios

**Archivo**: `backend/src/services/scenario_state_manager.py`

Singleton thread-safe que gestiona el estado acumulativo de un escenario activo.

**Garantías:**

- **Singleton**: Solo una instancia existe en toda la aplicación
- **Thread-safe**: Todas las mutaciones usan `asyncio.Lock`
- **Un escenario a la vez**: Iniciar un nuevo escenario resetea el anterior
- **Datos acumulativos**: Avanzar a fase N reconstruye datos de fases 1..N

**API del manager:**

| Método | Descripción |
|--------|-------------|
| `get_instance()` | Obtener la instancia singleton |
| `start_scenario(id, name, phases)` | Iniciar un escenario nuevo |
| `advance_to_phase(n)` | Avanzar a la fase N (acumula datos 1..N) |
| `get_current_state()` | Obtener el estado acumulativo actual |
| `reset()` | Limpiar todo el estado |
| `contain_host(host_id)` | Mutación del agente: contener un host |
| `close_incident(incident_id)` | Mutación del agente: cerrar un incidente |
| `add_comment(comment)` | Mutación del agente: añadir un comentario |

**Ejemplo de flujo:**

```python
mgr = ScenarioStateManager.get_instance()
await mgr.start_scenario("apt29", "APT29 (Cozy Bear)", phases)
await mgr.advance_to_phase(3)  # Ahora tiene datos de fases 1, 2 y 3
state = await mgr.get_current_state()
# state.incidents contiene los 6 incidentes de las primeras 3 fases
```

---

### 3.3.3 Escenario APT29 — Cozy Bear (8 Fases)

**Archivo**: `backend/src/scenarios/apt29.py`

Script completo del escenario APT29 mapeado al framework MITRE ATT&CK con datos realistas de seguridad.

**Resumen del escenario:**

| Dato | Valor |
|------|-------|
| Grupo | APT29 (Cozy Bear) — SVR ruso |
| Fases | 8 |
| Incidentes SIEM | 14 |
| Detecciones EDR | 15 |
| IOCs Intel | 7 |
| Hosts objetivo | WS-EXEC-PC01, WS-EXEC-PC02, SRV-DC01, SRV-FILE01, SRV-MAIL01, WS-IT-PC01 |

**Fases del ataque:**

| Fase | Táctica MITRE | Descripción | Incidentes | Detecciones | IOCs |
|------|---------------|-------------|------------|-------------|------|
| 1 | TA0001 — Initial Access | Spear-phishing con documento weaponizado | 2 | 2 | 3 |
| 2 | TA0002 — Execution | PowerShell y WMI | 2 | 2 | 0 |
| 3 | TA0003 — Persistence | Registry run key y scheduled task | 2 | 2 | 1 |
| 4 | TA0004 — Privilege Escalation | Token manipulation | 1 | 2 | 0 |
| 5 | TA0005 — Defense Evasion | Process injection y timestomping | 2 | 2 | 0 |
| 6 | TA0006 — Credential Access | LSASS dump y Kerberoasting | 2 | 2 | 1 |
| 7 | TA0008 — Lateral Movement | RDP y SMB | 2 | 2 | 1 |
| 8 | TA0010 — Exfiltration | HTTPS C2 exfiltration | 1 | 1 | 1 |

**Modelo acumulativo en acción:**

En la fase 1, el agente ve 2 incidentes. En la fase 4, ya ha acumulado 7 incidentes (los de fases 1-4). En la fase 8, tiene el cuadro completo: 14 incidentes, 15 detecciones y 7 IOCs.

Las funciones `get_cumulative_incidents(up_to_phase)`, `get_cumulative_detections(up_to_phase)` y `get_cumulative_iocs(up_to_phase)` permiten obtener datos acumulados hasta cualquier fase.

---

### 3.3.4 Mapeo Fase-a-Acciones-UI

**Archivo**: `backend/src/config/phase_ui_actions.py`

Configuración declarativa que mapea cada fase del escenario a las acciones de UI que el agente debe ejecutar tras completar su análisis.

**Mapeo APT29:**

| Fase | Acción 1 | Acción 2 |
|------|----------|----------|
| 1 — Initial Access | Navegar a Incidents | Resaltar IP de origen |
| 2 — Execution | Navegar a Detections | Resaltar proceso malicioso |
| 3 — Persistence | Navegar a Assets | Resaltar registry keys |
| 4 — Privilege Escalation | Navegar a Incidents | Resaltar cuenta escalada |
| 5 — Defense Evasion | Navegar a Detections | Resaltar técnica MITRE |
| 6 — Credential Access | Navegar a Assets | Resaltar host comprometido |
| 7 — Lateral Movement | Navegar a Assets | Resaltar ruta de red |
| 8 — Exfiltration | Navegar a Incidents | Resaltar flujo de datos |

**API pública:**

```python
from src.config.phase_ui_actions import get_actions_for_phase

actions = get_actions_for_phase("apt29", 1)
# [
#   {"type": "navigate", "target": "incidents", "description": "..."},
#   {"type": "highlight", "element": "source_ip", "description": "..."}
# ]
```

---

### 3.3.5 PhaseSyncCoordinator — Coordinador de Sincronización

**Archivo**: `backend/src/services/phase_sync.py`

Coordina la inicialización y avance simultáneo entre el `SimulationStateManager` (existente, de Parte 1) y el nuevo `ScenarioStateManager`.

**¿Por qué es necesario?**

El sistema tiene dos managers que deben estar siempre sincronizados:
- `SimulationStateManager`: gestiona el estado de la simulación MCP (fases MITRE, narración, estado del demo)
- `ScenarioStateManager`: gestiona los datos dinámicos (incidentes, detecciones, IOCs)

El `PhaseSyncCoordinator` asegura que cuando se inicia un escenario o se avanza de fase, **ambos managers se actualizan atómicamente**.

**Métodos:**

| Método | Descripción |
|--------|-------------|
| `start_scenario(scenario_id, seed)` | Inicia ambos managers simultáneamente |
| `advance_phase(stage_number)` | Avanza ambos managers a la misma fase |

---

## 3.4 Flujo Completo de una Demo con Control Bidireccional

A continuación se describe el flujo completo cuando se ejecuta una demo con el sistema bidireccional activo:

```
1. INICIO DEL ESCENARIO
   ├── PhaseSyncCoordinator.start_scenario("apt29")
   ├── SimulationStateManager: configura fases MITRE
   └── ScenarioStateManager: carga 8 fases con datos de APT29

2. FASE 1 — INITIAL ACCESS
   ├── Backend avanza a fase 1
   ├── ScenarioStateManager acumula: 2 incidentes, 2 detecciones, 3 IOCs
   ├── Agente Vega analiza los eventos y genera narración
   ├── Tras 1.5s del análisis:
   │   ├── agentUIActions.dispatch([navigate→incidents, highlight→source_ip])
   │   ├── rateLimiter verifica: ≤2 acciones/s ✓
   │   ├── actionQueue verifica: ¿usuario interactuando? → encolar o ejecutar
   │   ├── UIBridge.send_navigation("/incidents") → WS Server → Frontend
   │   └── useWsNavigation detecta cambio → react-router navega → toast
   └── UI muestra vista de Incidentes con IP maliciosa resaltada

3. FASES 2-7 — PROGRESIÓN DEL ATAQUE
   ├── Cada fase acumula más datos al ScenarioState
   ├── El agente navega entre Incidents, Detections y Assets
   ├── Los highlights van marcando hosts comprometidos y técnicas usadas
   └── El presentador puede desactivar auto-acciones con PresenterToggle

4. FASE 8 — EXFILTRACIÓN
   ├── ScenarioState final: 14 incidentes, 15 detecciones, 7 IOCs
   ├── Agente navega a Incidents para mostrar la alerta de exfiltración
   ├── ChartOverlay muestra gráfico de volumen de datos transferidos
   ├── TimelinePanel muestra cronología completa de 8 fases
   └── AnimatedKpiValue anima los contadores finales

5. MUTACIONES DEL AGENTE (durante cualquier fase)
   ├── contain_host("WS-EXEC-PC01") → persiste en ScenarioState
   ├── close_incident("INC-APT29-001") → actualiza status a "closed"
   └── add_comment(comment) → se acumula en la lista de comentarios
```

---

## 3.5 Tipos y Definiciones MCP State

**Archivo**: `frontend/src/types/mcpState.ts`

Definiciones TypeScript completas para el estado MCP sincronizado.

| Tipo | Descripción |
|------|-------------|
| `McpStateUpdate` | Mensaje principal del WS Server con campos opcionales |
| `McpHighlightedAsset` | Asset a resaltar: `{ id, mode, label? }` |
| `McpChart` | Gráfico: `{ id, type, title, data[] }` |
| `McpTimeline` | Timeline: `{ id, title, entries[] }` |
| `McpTimelineEntry` | Entrada: `{ id, timestamp, title, description?, severity? }` |
| `McpKpiOverride` | KPI: `{ id, label, value, prefix?, suffix? }` |
| `ChartDataPoint` | Punto de datos: `{ label, value, color? }` |
| `HighlightMode` | Modo: `"pulse" \| "glow" \| "zoom"` |
| `ChartType` | Tipo: `"bar" \| "line" \| "pie"` |

---

## 3.6 Referencia Rápida de Archivos

### Frontend

| Archivo | Propósito |
|---------|-----------|
| `src/hooks/useMcpStateSync.ts` | Sincronización WS con estado MCP |
| `src/hooks/useWsNavigation.ts` | Navegación dirigida por el agente |
| `src/hooks/useAssetHighlight.ts` | Resaltado de nodos Cytoscape |
| `src/types/mcpState.ts` | Tipos TypeScript del estado MCP |
| `src/components/mcp/ChartOverlay.tsx` | Gráficos flotantes overlay |
| `src/components/mcp/TimelinePanel.tsx` | Panel de timeline deslizante |
| `src/components/mcp/AnimatedKpiValue.tsx` | KPIs con animación de conteo |
| `src/styles/highlightStyles.ts` | CSS de animaciones de resaltado |
| `src/services/agentUIActions.ts` | Dispatcher de acciones post-análisis |
| `src/utils/rateLimiter.ts` | Rate limiter (2 acciones/s) |
| `src/utils/actionQueue.ts` | Cola con detección de interacción |
| `src/components/demo/PresenterToggle.tsx` | Toggle de auto-acciones |

### Backend

| Archivo | Propósito |
|---------|-----------|
| `src/services/ui_bridge.py` | Cliente WS async hacia MCP WS Server |
| `src/api/ui_actions.py` | Endpoint REST POST /api/v1/ui/action |
| `src/models/scenario_types.py` | Modelos Pydantic de datos de escenario |
| `src/services/scenario_state_manager.py` | Singleton de estado acumulativo |
| `src/scenarios/apt29.py` | Script APT29 con 8 fases y 36 eventos |
| `src/config/phase_ui_actions.py` | Mapeo fase → acciones UI |
| `src/services/phase_sync.py` | Coordinador de sincronización dual |

---

## 3.7 Mapa de Arquitectura Completo (Actualizado)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CYBERDEMO — ARQUITECTURA COMPLETA                        │
│                                                                             │
│  FRONTEND (React + Vite + TypeScript + Tailwind + Cytoscape.js)            │
│  ──────────────────────────────────────────────                            │
│  Pages: Dashboard, SIEM, EDR, Intel, CTEM, Assets, Canvas, Simulation      │
│  Components: CyberGraph, DataTable, KpiCards, NarrationFooter              │
│  MCP Components: ChartOverlay, TimelinePanel, AnimatedKpiValue             │
│  Hooks: useSimulation, useNarration, useAipSuggestions, useWebSocket       │
│  MCP Hooks: useMcpStateSync, useWsNavigation, useAssetHighlight           │
│  Services: agentUIActions (dispatcher con delay 1.5s)                      │
│  Utils: rateLimiter (2/s), actionQueue (user-interaction-aware)            │
│  Controls: PresenterToggle (on/off auto-acciones)                          │
│  Context: DemoContext (estado global compartido)                            │
│  Adapter: cytoscapeAdapter (grafo de ataque)                               │
│  Styles: highlightStyles (pulse, glow, zoom animations)                    │
│  Types: mcpState.ts (McpStateUpdate, McpChart, McpTimeline, etc.)          │
│                                                                             │
│  MCP WS SERVER (Node.js, puerto 3001)                                      │
│  ──────────────────────────────────                                        │
│  WebSocket server que retransmite comandos del backend al frontend          │
│  Protocolo: JSON messages con type "tool_call"                              │
│                                                                             │
│  BACKEND (FastAPI/Python)                                                   │
│  ──────────────────────                                                     │
│  20+ endpoints REST por dominio (SIEM/EDR/Intel/CTEM/Demo/...)             │
│  POST /api/v1/ui/action: control programático de la UI                     │
│  UIBridge: cliente WS async (lazy connect, silent failure)                  │
│  MCP SOC Server: ~30 tools de operación SOC                                │
│  MCP Data Server: 8 tools de generación de datos                           │
│  Policy Engine: reglas determinísticas de decisión                         │
│  Generadores: assets/EDR/SIEM/Intel/CTEM sintéticos                        │
│  Clientes de enriquecimiento: NVD, EPSS, OTX, AbuseIPDB, GreyNoise        │
│  ScenarioStateManager: singleton thread-safe de estado acumulativo          │
│  PhaseSyncCoordinator: sincronización dual de managers                     │
│  Escenarios: APT29 (8 fases, 14 inc, 15 det, 7 IOC)                       │
│  Config: phase_ui_actions (mapeo fase → navigate/highlight)                │
│                                                                             │
│  PLUGIN/SKILL (SoulInTheBot)                                                │
│  ──────────────────────────                                                 │
│  Plugin: cyberdemo-soc-analyst                                              │
│  Skill: soc-analyst con 8 comandos                                         │
│  TS Services: api-client, confidence-score, policy-engine, investigation   │
│  Hooks: onToolStart/Complete, onContainment, onApproval, onInvestigation   │
│  Demo Commands: handleDemoCase1/2/3                                        │
│                                                                             │
│  BASES DE DATOS                                                             │
│  ──────────────                                                             │
│  OpenSearch (9200): alertas, logs, threat intel, attack surface            │
│  PostgreSQL (5433): assets, config, audit, tickets                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Manual generado: 2026-02-24*
*Versión: 2.0.0*
*Basado en: FUNCTIONAL_SPEC.md, FRONTEND_FUNCTIONAL_SPEC.md, CyberDemoDescription.md, Interaccion_CyberProduct_Agent.md, MCP_SERVER_PLAN.md y código fuente del proyecto*

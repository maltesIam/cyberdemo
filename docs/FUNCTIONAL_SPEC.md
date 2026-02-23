# Functional Specification: CyberDemo Agent Integration Enhancement
Version: 1.0.0 | Date: 2026-02-22 | Build ID: sbx-20260222-012823

---

## PART 1: FUNCTIONAL DESCRIPTION

### 1.1 Executive Summary

CyberDemo es una plataforma de simulación de Security Operations Center (SOC) que permite demostrar las capacidades de un agente IA (SoulInTheBot/Claude) en la investigación y respuesta a incidentes de seguridad. La plataforma expone sus funcionalidades a través del protocolo MCP (Model Context Protocol), permitiendo interacción bidireccional entre el producto y el agente.

Actualmente, la comunicación está bien desarrollada en la dirección Agente→Producto (46+ tools disponibles), pero la dirección inversa (Producto→Agente) está limitada a eventos pasivos por WebSocket. Este proyecto implementa las mejoras necesarias para permitir que el producto invoque activamente al agente, añada escenarios de demo más ricos, e implemente funcionalidades de asistencia proactiva (Copilot Mode).

El objetivo es transformar CyberDemo de una plataforma de demostración pasiva a una experiencia interactiva donde el agente IA actúa como un verdadero copiloto de seguridad, capaz de analizar alertas bajo demanda, narrar sus decisiones en tiempo real, y guiar a los analistas humanos durante las investigaciones.

### 1.2 System Overview

CyberDemo Agent Integration Enhancement extiende la plataforma existente con:

1. **Sistema de Invocación Activa**: Permite que el producto solicite análisis al agente mediante webhooks y colas asíncronas
2. **Escenarios de Ataque Enriquecidos**: 6 nuevos escenarios basados en grupos APT reales (MITRE ATT&CK)
3. **Narración en Tiempo Real**: El agente explica su razonamiento mientras investiga
4. **Modo Copilot**: Sugerencias proactivas basadas en las acciones del usuario
5. **Panel de Control de Demo**: Controles interactivos para presentaciones (play, pause, velocidad)
6. **Playbooks Automatizados**: Respuestas orquestadas con intervención del agente

### 1.3 User Roles

| Role | Description | Key Actions |
|------|-------------|-------------|
| **SOC Analyst** | Analista de seguridad usando la plataforma | Investigar alertas, solicitar análisis al agente, aprobar acciones |
| **Demo Presenter** | Persona mostrando capacidades en demos | Controlar velocidad, pausar, seleccionar escenarios |
| **Security Manager** | Supervisor que revisa decisiones | Ver narrativas, aprobar contenciones críticas |
| **AI Agent (SoulInTheBot)** | Agente IA que investiga y recomienda | Analizar alertas, correlacionar eventos, sugerir acciones |

### 1.4 Functional Areas

#### 1.4.1 Invocación Activa del Agente (Producto → Agente)

Permite que el producto solicite activamente análisis o acciones al agente IA, invirtiendo la dirección de comunicación típica.

##### User Stories
- As a SOC Analyst, I want to click "Analyze" on an alert so that the agent investigates it automatically
- As a SOC Analyst, I want to receive proactive recommendations so that I don't miss critical correlations
- As a Security Manager, I want the system to auto-escalate critical alerts so that response time improves

##### Business Rules
- BR-001: Las alertas críticas (severity >= critical) disparan análisis automático del agente
- BR-002: Las solicitudes de análisis tienen timeout de 30 segundos
- BR-003: El agente puede rechazar análisis si está sobrecargado (rate limiting)
- BR-004: Todas las invocaciones se registran en audit log

#### 1.4.2 Escenarios de Ataque (Attack Simulation)

Sistema de simulación de ataques basado en grupos APT reales para demos interactivas.

##### User Stories
- As a Demo Presenter, I want to select different attack scenarios so that I can tailor demos to the audience
- As a Demo Presenter, I want to control simulation speed so that I can explain each step
- As a SOC Analyst, I want to see MITRE ATT&CK mapping so that I understand the attack chain

##### Business Rules
- BR-005: Cada escenario sigue las tácticas MITRE ATT&CK en orden
- BR-006: Los escenarios generan eventos sintéticos realistas
- BR-007: La simulación puede pausarse en cualquier etapa
- BR-008: Los escenarios son reproducibles con el mismo seed

#### 1.4.3 Narración en Tiempo Real

El agente explica su razonamiento y hallazgos mientras investiga.

##### User Stories
- As a Demo Presenter, I want the agent to narrate its thinking so that the audience understands AI reasoning
- As a SOC Analyst, I want to see step-by-step investigation so that I can learn and verify
- As a Security Manager, I want explanations of decisions so that I can audit AI actions

##### Business Rules
- BR-009: La narración se muestra en panel lateral dedicado
- BR-010: Cada paso de investigación genera un mensaje de narración
- BR-011: La narración incluye nivel de confianza (high/medium/low)
- BR-012: Se puede activar/desactivar narración en cualquier momento

#### 1.4.4 Modo Copilot

Asistencia proactiva del agente basada en las acciones del usuario.

##### User Stories
- As a SOC Analyst, I want contextual suggestions so that I investigate more efficiently
- As a SOC Analyst, I want the agent to auto-complete actions so that repetitive tasks are faster
- As a SOC Analyst, I want explanations for suggestions so that I understand why they're relevant

##### Business Rules
- BR-013: El Copilot observa acciones del usuario en tiempo real
- BR-014: Las sugerencias aparecen en máximo 2 segundos
- BR-015: El usuario puede ignorar o aceptar sugerencias
- BR-016: El Copilot aprende de aceptaciones/rechazos en la sesión

#### 1.4.5 Playbooks Automatizados

Respuestas orquestadas a incidentes con intervención del agente.

##### User Stories
- As a SOC Analyst, I want to execute predefined playbooks so that response is consistent
- As a Security Manager, I want playbooks to pause for approval so that I control critical actions
- As a SOC Analyst, I want to rollback playbook actions so that mistakes can be undone

##### Business Rules
- BR-017: Los playbooks definen secuencia de acciones y puntos de decisión
- BR-018: Acciones destructivas requieren aprobación humana
- BR-019: El estado del playbook persiste entre sesiones
- BR-020: Cada acción del playbook se registra en audit log

#### 1.4.6 Panel de Control de Demo

Controles interactivos para presentaciones en vivo.

##### User Stories
- As a Demo Presenter, I want play/pause controls so that I can manage presentation pace
- As a Demo Presenter, I want to adjust simulation speed so that I can show details or overview
- As a Demo Presenter, I want to see attack stages so that I know where we are in the scenario

##### Business Rules
- BR-021: Velocidad ajustable de 0.5x a 4x
- BR-022: Pause detiene toda generación de eventos
- BR-023: Se puede saltar a cualquier etapa del escenario
- BR-024: El progreso se muestra visualmente con indicadores

### 1.5 Non-Functional Requirements Summary

- **Performance**: Latencia de invocación al agente < 500ms, narración en tiempo real < 100ms
- **Security**: Todas las comunicaciones autenticadas, audit log inmutable
- **Scalability**: Soportar 10 sesiones de demo concurrentes
- **Reliability**: Graceful degradation si el agente no responde
- **Usability**: Panel de control accesible con atajos de teclado

---

## PART 2: TECHNICAL REQUIREMENTS

### 2.1 Requirements Traceability Matrix

| ID | Type | Description | Priority | Traces To |
|----|------|-------------|----------|-----------|
| REQ-001 | Functional | Sistema de webhooks para invocación activa del agente | MTH | Section 1.4.1 |
| REQ-002 | Functional | Cola de análisis asíncrono con job tracking | MTH | Section 1.4.1 |
| REQ-003 | Functional | MCP de Orquestación de Agente con 6 tools | MTH | Section 1.4.1 |
| REQ-004 | Functional | 6 escenarios de ataque basados en APT reales | MTH | Section 1.4.2 |
| REQ-005 | Functional | Control de simulación (start, pause, speed) | MTH | Section 1.4.2 |
| REQ-006 | Functional | Panel de narración en tiempo real | NTH | Section 1.4.3 |
| REQ-007 | Functional | Streaming de razonamiento del agente | NTH | Section 1.4.3 |
| REQ-008 | Functional | Sistema de sugerencias proactivas (Copilot) | NTH | Section 1.4.4 |
| REQ-009 | Functional | Observación de acciones del usuario | NTH | Section 1.4.4 |
| REQ-010 | Functional | Motor de ejecución de playbooks | NTH | Section 1.4.5 |
| REQ-011 | Functional | 6 playbooks predefinidos de respuesta | NTH | Section 1.4.5 |
| REQ-012 | Functional | Panel de control de demo interactivo | NTH | Section 1.4.6 |
| REQ-013 | Technical | Persistencia de estado de simulación | MTH | Section 1.4.2 |
| REQ-014 | Technical | Audit logging de todas las invocaciones | MTH | Section 1.4.1 |
| REQ-015 | Integration | WebSocket bidireccional con el agente | MTH | Section 1.4.1 |

### 2.2 Epics

#### EPIC-001: Agent Orchestration MCP [MTH]

**Description**: Implementar MCP server que permite al producto invocar activamente al agente para solicitar análisis, recomendaciones y correlaciones.

**Acceptance Criteria**:
- [ ] El producto puede enviar requests de análisis al agente
- [ ] El agente responde con análisis estructurado
- [ ] Las invocaciones se registran en audit log
- [ ] Rate limiting previene sobrecarga del agente

##### Features

###### FEAT-001-001: Webhook System [MTH]
**Description**: Sistema de webhooks para eventos críticos que disparan análisis automático

**Requirements**:
- REQ-001-001-001: API endpoint POST /api/v1/webhooks/configure para registrar webhooks [MTH]
- REQ-001-001-002: Dispatcher que envía eventos al agente endpoint configurado [MTH]
- REQ-001-001-003: Retry logic con backoff exponencial (3 intentos) [MTH]
- REQ-001-001-004: Timeout configurable por webhook (default 30s) [MTH]
- REQ-001-001-005: Validación de response del agente [MTH]

###### FEAT-001-002: Async Analysis Queue [MTH]
**Description**: Cola de análisis asíncrono con job tracking

**Requirements**:
- REQ-001-002-001: API POST /api/v1/analysis/queue para encolar análisis [MTH]
- REQ-001-002-002: API GET /api/v1/analysis/status/{job_id} para estado [MTH]
- REQ-001-002-003: API GET /api/v1/analysis/result/{job_id} para resultado [MTH]
- REQ-001-002-004: WebSocket /ws/analysis para notificaciones en tiempo real [MTH]
- REQ-001-002-005: Persistencia de jobs en PostgreSQL [MTH]
- REQ-001-002-006: Limpieza automática de jobs > 24h [MTH]

###### FEAT-001-003: Agent Orchestration Tools [MTH]
**Description**: MCP tools para orquestación del agente

**Requirements**:
- REQ-001-003-001: Tool agent_analyze_alert(alert_id) [MTH]
- REQ-001-003-002: Tool agent_investigate_ioc(ioc, type) [MTH]
- REQ-001-003-003: Tool agent_recommend_action(context) [MTH]
- REQ-001-003-004: Tool agent_generate_report(incident_id, format) [MTH]
- REQ-001-003-005: Tool agent_explain_decision(decision_id) [MTH]
- REQ-001-003-006: Tool agent_correlate_events(event_ids[]) [MTH]

---

#### EPIC-002: Attack Simulation System [MTH]

**Description**: Sistema de simulación de ataques basado en grupos APT reales con control interactivo para demos.

**Acceptance Criteria**:
- [ ] 6 escenarios de ataque disponibles
- [ ] Cada escenario sigue tácticas MITRE ATT&CK
- [ ] Controles de play/pause/speed funcionan
- [ ] Eventos se generan de forma realista

##### Features

###### FEAT-002-001: Attack Scenarios [MTH]
**Description**: Implementación de 6 escenarios de ataque APT

**Requirements**:
- REQ-002-001-001: Escenario APT29 (Cozy Bear) - Espionaje gubernamental [MTH]
- REQ-002-001-002: Escenario FIN7 - Ataque financiero [MTH]
- REQ-002-001-003: Escenario Lazarus Group - Ataque destructivo [MTH]
- REQ-002-001-004: Escenario REvil - Ransomware [MTH]
- REQ-002-001-005: Escenario SolarWinds-style - Supply Chain [MTH]
- REQ-002-001-006: Escenario Insider Threat - Amenaza interna [MTH]

###### FEAT-002-002: Simulation Control [MTH]
**Description**: Controles para gestionar la simulación

**Requirements**:
- REQ-002-002-001: Tool attack_start_scenario(scenario_name, seed?) [MTH]
- REQ-002-002-002: Tool attack_pause() y attack_resume() [MTH]
- REQ-002-002-003: Tool attack_speed(multiplier: 0.5-4.0) [MTH]
- REQ-002-002-004: Tool attack_jump_to_stage(stage_number) [MTH]
- REQ-002-002-005: Tool attack_inject_event(event_type, data) [MTH]
- REQ-002-002-006: Persistencia de estado de simulación en memoria [MTH]

###### FEAT-002-003: MITRE ATT&CK Integration [MTH]
**Description**: Mapeo de escenarios a framework MITRE

**Requirements**:
- REQ-002-003-001: Cada evento incluye tactic_id y technique_id [MTH]
- REQ-002-003-002: API GET /api/v1/mitre/tactics para listar tácticas [MTH]
- REQ-002-003-003: API GET /api/v1/mitre/techniques/{tactic_id} [MTH]
- REQ-002-003-004: Visualización de attack chain en UI [MTH]

---

#### EPIC-003: Real-Time Narration [NTH]

**Description**: Sistema de narración en tiempo real donde el agente explica su razonamiento durante investigaciones.

**Acceptance Criteria**:
- [ ] Panel lateral muestra narración del agente
- [ ] Cada paso de investigación genera mensaje
- [ ] Se muestra nivel de confianza
- [ ] Narración activable/desactivable

##### Features

###### FEAT-003-001: Narration Panel UI [NTH]
**Description**: Componente React para mostrar narración

**Requirements**:
- REQ-003-001-001: Panel lateral colapsable [NTH]
- REQ-003-001-002: Mensajes con timestamp y tipo (thinking/finding/decision) [NTH]
- REQ-003-001-003: Indicador de confianza (high/medium/low) con colores [NTH]
- REQ-003-001-004: Scroll automático con nuevos mensajes [NTH]
- REQ-003-001-005: Toggle para activar/desactivar narración [NTH]

###### FEAT-003-002: Narration Streaming [NTH]
**Description**: Backend streaming de narración

**Requirements**:
- REQ-003-002-001: WebSocket /ws/narration para streaming [NTH]
- REQ-003-002-002: Formato de mensaje {type, content, confidence, timestamp} [NTH]
- REQ-003-002-003: Buffer de últimos 100 mensajes [NTH]
- REQ-003-002-004: API GET /api/v1/narration/history/{session_id} [NTH]

---

#### EPIC-004: Copilot Mode [NTH]

**Description**: Sistema de asistencia proactiva donde el agente sugiere acciones basadas en el contexto del usuario.

**Acceptance Criteria**:
- [ ] Agente observa acciones del usuario
- [ ] Sugerencias aparecen en < 2 segundos
- [ ] Usuario puede aceptar/rechazar sugerencias
- [ ] Sugerencias son contextuales

##### Features

###### FEAT-004-001: Action Observation [NTH]
**Description**: Sistema que observa y analiza acciones del usuario

**Requirements**:
- REQ-004-001-001: Hook en componentes React para capturar acciones [NTH]
- REQ-004-001-002: Throttling de eventos (máx 10/segundo) [NTH]
- REQ-004-001-003: Contexto incluye: acción, elemento, datos visibles [NTH]
- REQ-004-001-004: WebSocket /ws/copilot/actions para enviar stream [NTH]

###### FEAT-004-002: Suggestion Engine [NTH]
**Description**: Motor de sugerencias proactivas

**Requirements**:
- REQ-004-002-001: Tool copilot_get_suggestion(context) [NTH]
- REQ-004-002-002: Tool copilot_explain_why(suggestion_id) [NTH]
- REQ-004-002-003: Tool copilot_auto_complete(action_type) [NTH]
- REQ-004-002-004: UI widget para mostrar sugerencias [NTH]
- REQ-004-002-005: Tracking de aceptación/rechazo por sesión [NTH]

---

#### EPIC-005: Automated Playbooks [NTH]

**Description**: Sistema de playbooks automatizados para respuesta a incidentes con intervención del agente.

**Acceptance Criteria**:
- [ ] 6 playbooks predefinidos disponibles
- [ ] Ejecución con puntos de pausa
- [ ] Rollback de acciones posible
- [ ] Audit trail completo

##### Features

###### FEAT-005-001: Playbook Engine [NTH]
**Description**: Motor de ejecución de playbooks

**Requirements**:
- REQ-005-001-001: API POST /api/v1/playbooks/execute/{playbook_id} [NTH]
- REQ-005-001-002: API POST /api/v1/playbooks/{execution_id}/pause [NTH]
- REQ-005-001-003: API POST /api/v1/playbooks/{execution_id}/resume [NTH]
- REQ-005-001-004: API POST /api/v1/playbooks/{execution_id}/rollback [NTH]
- REQ-005-001-005: API GET /api/v1/playbooks/{execution_id}/status [NTH]
- REQ-005-001-006: Persistencia de estado en PostgreSQL [NTH]

###### FEAT-005-002: Predefined Playbooks [NTH]
**Description**: Implementación de playbooks predefinidos

**Requirements**:
- REQ-005-002-001: Playbook: Ransomware Response [NTH]
- REQ-005-002-002: Playbook: Phishing Investigation [NTH]
- REQ-005-002-003: Playbook: Lateral Movement Detection [NTH]
- REQ-005-002-004: Playbook: Data Exfiltration Response [NTH]
- REQ-005-002-005: Playbook: Insider Threat Investigation [NTH]
- REQ-005-002-006: Playbook: Cloud Compromise Response [NTH]

---

#### EPIC-006: Demo Control Panel [NTH]

**Description**: Panel de control interactivo para presentaciones en vivo con controles de velocidad, pausa y navegación.

**Acceptance Criteria**:
- [ ] Controles play/pause/stop visibles
- [ ] Velocidad ajustable 0.5x-4x
- [ ] Indicador de etapa actual
- [ ] Atajos de teclado funcionan

##### Features

###### FEAT-006-001: Control Panel UI [NTH]
**Description**: Componente React del panel de control

**Requirements**:
- REQ-006-001-001: Botones Play/Pause/Stop [NTH]
- REQ-006-001-002: Slider de velocidad (0.5x-4x) [NTH]
- REQ-006-001-003: Dropdown de selección de escenario [NTH]
- REQ-006-001-004: Progress bar con etapas MITRE [NTH]
- REQ-006-001-005: Atajos de teclado (Space=pause, +/-=speed) [NTH]

###### FEAT-006-002: Demo State Management [NTH]
**Description**: Gestión de estado del demo

**Requirements**:
- REQ-006-002-001: Context React para estado global del demo [NTH]
- REQ-006-002-002: Persistencia de estado entre recargas (localStorage) [NTH]
- REQ-006-002-003: Sync de estado con MCP Frontend Server [NTH]

---

### 2.3 Technical Requirements

| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
| TECH-001 | Architecture | Nuevo MCP Server para Agent Orchestration en Python/FastAPI | MTH |
| TECH-002 | Architecture | Cola de jobs con PostgreSQL (no Redis para simplicidad) | MTH |
| TECH-003 | Architecture | WebSocket bidireccional para streaming de narración | NTH |
| TECH-004 | Database | Tabla analysis_jobs para tracking de análisis | MTH |
| TECH-005 | Database | Tabla webhook_configs para configuración de webhooks | MTH |
| TECH-006 | Database | Tabla playbook_executions para estado de playbooks | NTH |
| TECH-007 | Database | Tabla narration_messages para historial | NTH |
| TECH-008 | API | Rate limiting de 100 requests/minuto por sesión | MTH |
| TECH-009 | API | Autenticación de webhooks con HMAC signature | MTH |
| TECH-010 | Frontend | Nuevo componente NarrationPanel.tsx | NTH |
| TECH-011 | Frontend | Nuevo componente DemoControlPanel.tsx | NTH |
| TECH-012 | Frontend | Nuevo componente CopilotWidget.tsx | NTH |
| TECH-013 | Testing | Tests E2E con Playwright para flujos de demo | MTH |
| TECH-014 | Testing | Tests unitarios para cada MCP tool | MTH |

### 2.4 Integration Requirements

| ID | System | Description | Priority |
|----|--------|-------------|----------|
| INT-001 | SoulInTheBot | Endpoint HTTP para recibir webhooks de análisis | MTH |
| INT-002 | SoulInTheBot | WebSocket para streaming de narración | NTH |
| INT-003 | OpenSearch | Índice attack_simulations para eventos de escenarios | MTH |
| INT-004 | OpenSearch | Índice narration_logs para historial de narración | NTH |
| INT-005 | PostgreSQL | Schema extensions para nuevas tablas | MTH |
| INT-006 | Frontend MCP | Nuevos tools para control de demo | MTH |

---

## VERIFICATION CHECKLIST

| Part 1 Section | Covered in Part 2 | Requirements |
|----------------|-------------------|--------------|
| 1.4.1 Invocación Activa | Yes | EPIC-001, REQ-001-* |
| 1.4.2 Escenarios de Ataque | Yes | EPIC-002, REQ-002-* |
| 1.4.3 Narración en Tiempo Real | Yes | EPIC-003, REQ-003-* |
| 1.4.4 Modo Copilot | Yes | EPIC-004, REQ-004-* |
| 1.4.5 Playbooks Automatizados | Yes | EPIC-005, REQ-005-* |
| 1.4.6 Panel de Control de Demo | Yes | EPIC-006, REQ-006-* |
| 1.5 Non-Functional | Yes | TECH-001 to TECH-014 |

---

## SUMMARY

| Metric | MTH | NTH | Total |
|--------|-----|-----|-------|
| Epics | 2 | 4 | 6 |
| Features | 6 | 8 | 14 |
| Requirements | 32 | 34 | 66 |
| Technical Reqs | 10 | 4 | 14 |
| Integration Reqs | 4 | 2 | 6 |

---

*Document generated by SoftwareBuilderX v15.0.0*
*Build ID: sbx-20260222-012823*
*Phase: Design*

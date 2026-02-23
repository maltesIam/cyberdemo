# CyberDemo: Manual de Usuario y Descripción Funcional

**Versión:** 2.0.0
**Fecha:** 2026-02-23
**Sistema:** CyberDemo Attack Surface Platform

---

## Introducción: ¿Qué es CyberDemo?

CyberDemo es una **plataforma de simulación SOC** (Security Operations Center) que demuestra cómo un **Analista SOC Tier-1 puede ser automatizado** usando inteligencia artificial. El sistema utiliza datos sintéticos realistas, APIs REST, servidores MCP y una interfaz web operativa.

### El Problema que Resolvemos

En un SOC tradicional, el analista humano trabaja solo frente a la pantalla, analizando alertas, investigando IOCs, y tomando decisiones bajo presión. Tiene que:

- Recordar qué hacer en cada tipo de incidente
- Buscar información en múltiples sistemas (SIEM, EDR, Intel, CTEM)
- Correlacionar eventos manualmente
- Documentar todo para cumplimiento
- Tomar decisiones de contención bajo presión de tiempo

**Nuestra solución**: Crear una **colaboración en tiempo real** entre el analista humano y una Persona IA que actúa como un compañero experto.

### Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ECOSISTEMA CYBERDEMO                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   👤 ANALISTA HUMANO                    🤖 PERSONA IA (SoulInTheBot)       │
│   ══════════════════                    ════════════════════════════        │
│   • Ve alertas en pantalla              • Recibe solicitudes del producto   │
│   • Hace clic en "Analizar"             • Analiza, correlaciona, enriquece │
│   • Acepta/rechaza sugerencias          • Genera informes y recomendaciones│
│   • Toma decisiones finales             • Explica su razonamiento           │
│                                                                             │
│                          ↕️ INTERACCIÓN ↕️                                  │
│                                                                             │
│   🖥️ INTERFAZ GRÁFICA (UI)             ⚙️ BACKEND + MCP SERVER            │
│   ══════════════════════                ═══════════════════════════        │
│   • Muestra alertas y datos             • APIs para SIEM/EDR/Intel/CTEM    │
│   • Widget de aIP Assist                • Webhooks para invocar al agente   │
│   • Panel de control de demo            • 15+ herramientas MCP              │
│   • Captura acciones del usuario        • Escenarios de ataque              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE A: LA DEMO ORIGINAL - ANALISTA SOC TIER-1 AUTOMATIZADO
# ═══════════════════════════════════════════════════════════════════════════════

Esta parte describe la **funcionalidad original** de CyberDemo: una demo que simula un entorno SOC completo donde la Persona IA actúa como Analista Tier-1, tomando decisiones de contención de forma determinista según políticas configurables.

---

## A.1 La Plataforma: Dashboard y Vistas

### ¿Qué ve el Analista?

CyberDemo presenta una **consola unificada** con 14 vistas que cubren todo el ciclo de vida SOC:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🖥️ INTERFAZ GRÁFICA CYBERDEMO                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📊 OPERACIÓN                    🔍 INVESTIGACIÓN                          │
│  • /dashboard   - KPIs SOC       • /incidents   - Gestión SIEM            │
│  • /assets      - Inventario     • /detections  - Detecciones EDR         │
│  • /generation  - Datos demo     • /timeline    - Acciones del agente     │
│                                  • /graph       - Visualización relaciones│
│                                                                             │
│  📋 CIERRE                       🛡️ CONTEXTO                               │
│  • /tickets     - Seguimiento    • /ctem        - Vulnerabilidades        │
│  • /postmortems - Informes       • /config      - Políticas               │
│  • /audit       - Trazabilidad   • /collab      - Colaboración equipo     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Vistas Clave para la Demo

| Vista | Propósito | ¿Qué muestra? |
|-------|-----------|---------------|
| **Dashboard** | Estado agregado SOC | KPIs, alertas por severidad, hosts contenidos |
| **Incidents** | Gestión de incidentes SIEM | Lista con filtros, detalles, comentarios |
| **Detections** | Detecciones EDR | Severidad, hash, cmdline, árbol de procesos |
| **CTEM** | Vulnerabilidades | Riesgo por activo, CVEs, criticidad |
| **Timeline** | Auditoría de decisiones | Secuencia de acciones de la Persona IA |
| **Graph** | Relaciones visuales | Grafo incidente-activo-indicadores |
| **Postmortems** | Informes post-incidente | Causa raíz, impacto, remediación |

---

## A.2 Los Tres Escenarios de Demo

La demo original presenta **tres escenarios ancla** que demuestran diferentes decisiones del Policy Engine:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOS TRES ESCENARIOS DE DEMO                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ESCENARIO 1                 ESCENARIO 2                ESCENARIO 3        │
│  ═══════════                 ═══════════                ═══════════        │
│  🔴 CONTENCIÓN               🟠 APROBACIÓN              🟢 FALSO POSITIVO  │
│  AUTOMÁTICA                  REQUERIDA                                     │
│                                                                             │
│  Host: WS-FIN-042            Host: LAPTOP-CFO-01        Host: SRV-DEV-03   │
│  Tipo: Workstation           Tipo: VIP/Executive        Tipo: Standard     │
│  Score: 95% (Alto)           Score: 95% (Alto)          Score: 35% (Bajo)  │
│                                                                             │
│  → La Persona IA             → La Persona IA            → La Persona IA    │
│    CONTIENE                    SOLICITA APROBACIÓN        DESCARTA         │
│    automáticamente             humana antes de actuar     como falso +     │
│                                                                             │
│  Sin intervención            El analista debe            Sin acción        │
│  humana necesaria            aprobar o rechazar          requerida         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Escenario 1: Contención Automática

```
FLUJO COMPLETO - ESCENARIO 1
════════════════════════════════════════════════════════════════════════════

PASO 1: El Analista Inicia la Demo
─────────────────────────────────────────────────────────────────────────────

   El analista ejecuta el comando:

   /demo 1

   O hace clic en "Demo Caso 1" en la interfaz.


PASO 2: La Persona IA Recibe el Incidente
─────────────────────────────────────────────────────────────────────────────

   🤖 Persona IA: "He recibido el incidente INC-ANCHOR-001"

   Incidente: INC-ANCHOR-001
   • Host: WS-FIN-042 (Departamento Financiero)
   • Alerta: Ejecución sospechosa de PowerShell
   • Usuario: john.smith@company.com
   • Hash: abc123def456...


PASO 3: La Persona IA Enriquece la Información
─────────────────────────────────────────────────────────────────────────────

   La Persona IA usa las herramientas MCP para investigar:

   Llamada 1: siem.getIncident("INC-ANCHOR-001")
   → Obtiene detalles del incidente

   Llamada 2: edr.getProcessTree("DET-789")
   → Árbol de procesos: cmd.exe → powershell.exe → malware.exe

   Llamada 3: intel.getIndicator("filehash", "abc123def456")
   → VirusTotal: 58/74 detecciones
   → Labels: [trojan, emotet]

   Llamada 4: edr.huntHash("abc123def456")
   → Encontrado en: WS-FIN-042, WS-HR-011, WS-MKT-023

   Llamada 5: ctem.getAssetRisk("WS-FIN-042")
   → Risk Score: 65/100
   → Tags: [] (NO es VIP, NO es servidor, NO es DC)


PASO 4: La Persona IA Calcula el Confidence Score
─────────────────────────────────────────────────────────────────────────────

   ┌────────────────────────────────────────────────┐
   │         CÁLCULO DE CONFIDENCE SCORE           │
   ├────────────────────────────────────────────────┤
   │                                                │
   │  Intel (40% peso)                             │
   │  ├─ VT Score > 50/74: +30 puntos              │
   │  └─ Labels conocidos: +10 puntos              │
   │  Subtotal Intel: 35/40                        │
   │                                                │
   │  Behavior (30% peso)                          │
   │  ├─ MITRE alto riesgo (T1059.001): +20       │
   │  └─ Cmdline sospechoso: +10                   │
   │  Subtotal Behavior: 25/30                     │
   │                                                │
   │  Context (20% peso)                           │
   │  ├─ Vulns críticas: +10                       │
   │  └─ Criticidad activo: +5                     │
   │  Subtotal Context: 15/20                      │
   │                                                │
   │  Propagation (10% peso)                       │
   │  └─ 3 hosts afectados: +5                     │
   │  Subtotal Propagation: 5/10                   │
   │                                                │
   │  ════════════════════════════════════════════ │
   │  TOTAL: 95/100 (ALTO)                         │
   └────────────────────────────────────────────────┘


PASO 5: El Policy Engine Toma la Decisión
─────────────────────────────────────────────────────────────────────────────

   ┌────────────────────────────────────────────────┐
   │            EVALUACIÓN POLICY ENGINE            │
   ├────────────────────────────────────────────────┤
   │                                                │
   │  Entrada:                                      │
   │  • Confidence Score: 95 (≥90)                 │
   │  • Asset Tags: [] (vacío - NO crítico)        │
   │                                                │
   │  Regla Evaluada:                              │
   │  IF score >= 90 AND asset NOT IN [vip,        │
   │     executive, server, domain-controller]:    │
   │     ACTION = auto_contain                      │
   │                                                │
   │  ✅ REGLA COINCIDE                             │
   │                                                │
   │  Decisión: AUTO-CONTENCIÓN                    │
   │  Requiere Aprobación: NO                       │
   │                                                │
   └────────────────────────────────────────────────┘


PASO 6: La Persona IA Ejecuta la Contención
─────────────────────────────────────────────────────────────────────────────

   La Persona IA ejecuta las acciones SIN esperar aprobación humana:

   Llamada 1: edr.containHost("WS-FIN-042", "Emotet confirmed - auto-isolating")
   → Host aislado de la red

   Llamada 2: siem.addComment("INC-ANCHOR-001",
              "Malware confirmado. Score 95%. Auto-contenido.")
   → Comentario añadido

   Llamada 3: tickets.create({
                title: "Malware containment - WS-FIN-042",
                severity: "high",
                assigned_to: "SOC Team"
              })
   → Ticket TKT-001 creado

   Llamada 4: reports.generatePostmortem("INC-ANCHOR-001")
   → Postmortem generado


PASO 7: El Analista Ve el Resultado
─────────────────────────────────────────────────────────────────────────────

   En la pantalla del analista aparece:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ ✅ INCIDENTE RESUELTO - INC-ANCHOR-001                              │
   │                                                                      │
   │ 🎯 Evaluación: ALTO RIESGO (95%)                                    │
   │ 🏷️ Malware: Emotet Trojan                                          │
   │ 🖥️ Host Contenido: WS-FIN-042                                       │
   │                                                                      │
   │ ACCIONES TOMADAS AUTOMÁTICAMENTE:                                   │
   │ ✓ Host aislado de la red                                            │
   │ ✓ Comentario añadido al incidente                                   │
   │ ✓ Ticket de seguimiento creado (TKT-001)                           │
   │ ✓ Postmortem generado                                               │
   │                                                                      │
   │ 📊 Timeline: Ver todas las acciones en /timeline                    │
   └──────────────────────────────────────────────────────────────────────┘

   El analista NO tuvo que hacer nada - la Persona IA resolvió el caso
   automáticamente porque:
   1. El confidence score era alto (95%)
   2. El activo NO era crítico (no era VIP, servidor, ni DC)
```

### Escenario 2: Aprobación Requerida (Human-in-the-Loop)

```
FLUJO COMPLETO - ESCENARIO 2
════════════════════════════════════════════════════════════════════════════

   El flujo es IDÉNTICO al Escenario 1 hasta el Paso 5.

   La diferencia está en el ASSET:

   Host: LAPTOP-CFO-01
   Tags: [vip, executive]  ← ¡ACTIVO CRÍTICO!


PASO 5: El Policy Engine Toma la Decisión (DIFERENTE)
─────────────────────────────────────────────────────────────────────────────

   ┌────────────────────────────────────────────────┐
   │            EVALUACIÓN POLICY ENGINE            │
   ├────────────────────────────────────────────────┤
   │                                                │
   │  Entrada:                                      │
   │  • Confidence Score: 95 (≥90)                 │
   │  • Asset Tags: [vip, executive]  ⚠️ CRÍTICO   │
   │                                                │
   │  Regla Evaluada:                              │
   │  IF asset IN [vip, executive, server, DC]:    │
   │     ACTION = request_approval                  │
   │     REQUIRE_APPROVAL = true                    │
   │     # No importa el score - SIEMPRE pedir OK  │
   │                                                │
   │  ✅ REGLA COINCIDE                             │
   │                                                │
   │  Decisión: REQUIERE APROBACIÓN HUMANA         │
   │  Razón: Activo VIP/Ejecutivo                   │
   │                                                │
   └────────────────────────────────────────────────┘


PASO 6: La Persona IA SOLICITA Aprobación (NO ejecuta)
─────────────────────────────────────────────────────────────────────────────

   La Persona IA NO puede contener directamente. Debe pedir permiso:

   Llamada 1: approvals.request("INC-ANCHOR-002", {
                hostname: "LAPTOP-CFO-01",
                owner: "CFO - Carlos Martínez",
                confidence_score: 95,
                recommendation: "CONTAIN",
                reason: "Emotet detected, but VIP asset requires approval"
              })
   → Solicitud de aprobación enviada


PASO 7: El Analista Ve la Solicitud de Aprobación
─────────────────────────────────────────────────────────────────────────────

   En la pantalla del analista aparece:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ ⚠️ APROBACIÓN REQUERIDA - INC-ANCHOR-002                            │
   │                                                                      │
   │ 🎯 Evaluación: ALTO RIESGO (95%)                                    │
   │ 🏷️ Malware: Emotet Trojan                                          │
   │ 🖥️ Host: LAPTOP-CFO-01                                              │
   │                                                                      │
   │ ⚠️ ATENCIÓN: Este es un activo VIP/Ejecutivo                        │
   │ 👤 Propietario: CFO - Carlos Martínez                               │
   │                                                                      │
   │ RECOMENDACIÓN DE LA PERSONA IA:                                     │
   │ "El malware Emotet ha sido confirmado con 95% de confianza.         │
   │  Sin embargo, este equipo pertenece al CFO y requiere               │
   │  aprobación explícita antes de aislar."                             │
   │                                                                      │
   │ [✅ APROBAR CONTENCIÓN]  [❌ RECHAZAR]  [📞 CONTACTAR OWNER]        │
   └──────────────────────────────────────────────────────────────────────┘


PASO 8: El Analista Toma la Decisión Final
─────────────────────────────────────────────────────────────────────────────

   Opción A: El analista hace clic en [✅ APROBAR CONTENCIÓN]
   ───────────────────────────────────────────────────────────────────────
   → Se envía: approvals.approve("INC-ANCHOR-002", approved_by="analyst_01")
   → La Persona IA recibe la aprobación
   → La Persona IA ejecuta la contención (igual que Escenario 1)

   Opción B: El analista hace clic en [❌ RECHAZAR]
   ───────────────────────────────────────────────────────────────────────
   → Se envía: approvals.reject("INC-ANCHOR-002", reason="False positive")
   → La Persona IA registra el rechazo
   → El incidente queda abierto para investigación manual
```

### Escenario 3: Falso Positivo

```
FLUJO COMPLETO - ESCENARIO 3
════════════════════════════════════════════════════════════════════════════

   El flujo es IDÉNTICO hasta el Paso 4, pero el Confidence Score es BAJO.


PASO 4: La Persona IA Calcula el Confidence Score (BAJO)
─────────────────────────────────────────────────────────────────────────────

   ┌────────────────────────────────────────────────┐
   │         CÁLCULO DE CONFIDENCE SCORE           │
   ├────────────────────────────────────────────────┤
   │                                                │
   │  Intel: VT 0/74 detecciones → 0/40            │
   │  Behavior: Proceso legítimo (svchost) → 5/30  │
   │  Context: Sin vulns críticas → 5/20           │
   │  Propagation: Solo 1 host → 2/10              │
   │                                                │
   │  ════════════════════════════════════════════ │
   │  TOTAL: 12/100 (MUY BAJO)                     │
   └────────────────────────────────────────────────┘


PASO 5: El Policy Engine Marca como Falso Positivo
─────────────────────────────────────────────────────────────────────────────

   ┌────────────────────────────────────────────────┐
   │            EVALUACIÓN POLICY ENGINE            │
   ├────────────────────────────────────────────────┤
   │                                                │
   │  Entrada:                                      │
   │  • Confidence Score: 12 (<50)                 │
   │                                                │
   │  Regla Evaluada:                              │
   │  IF score < 50:                               │
   │     ACTION = mark_false_positive               │
   │     REQUIRE_APPROVAL = false                   │
   │                                                │
   │  ✅ REGLA COINCIDE                             │
   │                                                │
   │  Decisión: FALSO POSITIVO                     │
   │  Acción: Cerrar sin contención                │
   │                                                │
   └────────────────────────────────────────────────┘


PASO 6: La Persona IA Cierra el Incidente
─────────────────────────────────────────────────────────────────────────────

   La Persona IA cierra el incidente sin contener:

   Llamada 1: siem.addComment("INC-ANCHOR-003",
              "Evaluado como falso positivo. Score: 12%.")

   Llamada 2: siem.closeIncident("INC-ANCHOR-003",
              reason="False positive - Score below threshold")

   NO se contiene ningún host.
   NO se requiere aprobación.


PASO 7: El Analista Ve el Resultado
─────────────────────────────────────────────────────────────────────────────

   ┌──────────────────────────────────────────────────────────────────────┐
   │ ✅ INCIDENTE CERRADO - INC-ANCHOR-003                               │
   │                                                                      │
   │ 🎯 Evaluación: BAJO RIESGO (12%)                                    │
   │ 🏷️ Clasificación: FALSO POSITIVO                                   │
   │                                                                      │
   │ ACCIONES TOMADAS:                                                   │
   │ ✓ Incidente cerrado automáticamente                                 │
   │ ✓ Comentario de cierre añadido                                      │
   │                                                                      │
   │ NO SE TOMARON ACCIONES DE CONTENCIÓN                                │
   │ El score (12%) estaba por debajo del umbral de falso positivo (50%) │
   └──────────────────────────────────────────────────────────────────────┘
```

---

## A.3 El Policy Engine: Decisiones Deterministas

### ¿Cómo Funciona?

El Policy Engine es **100% determinista** - NO usa IA para las decisiones. Dado el mismo input, siempre produce el mismo output.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REGLAS DEL POLICY ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REGLA 1: FALSO POSITIVO                                                   │
│  ───────────────────────                                                    │
│  IF confidence_score < 50:                                                  │
│      ACTION = mark_false_positive                                           │
│      REQUIRE_APPROVAL = false                                               │
│                                                                             │
│  REGLA 2: AUTO-CONTENCIÓN                                                  │
│  ─────────────────────────                                                  │
│  IF confidence_score >= 90 AND                                              │
│     asset NOT IN [vip, executive, server, domain-controller]:              │
│      ACTION = auto_contain                                                  │
│      REQUIRE_APPROVAL = false                                               │
│                                                                             │
│  REGLA 3: ACTIVO CRÍTICO (siempre requiere aprobación)                     │
│  ───────────────────────────────────────────────────────                    │
│  IF asset IN [vip, executive, server, domain-controller]:                  │
│      ACTION = request_approval                                              │
│      REQUIRE_APPROVAL = true                                                │
│      # No importa el score - SIEMPRE pedir OK                              │
│                                                                             │
│  REGLA 4: SCORE MEDIO                                                      │
│  ───────────────────────                                                    │
│  IF confidence_score >= 50 AND confidence_score < 90:                      │
│      ACTION = request_approval                                              │
│      REQUIRE_APPROVAL = true                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cálculo del Confidence Score

| Componente | Peso | Factores |
|------------|------|----------|
| **Intel** | 40% | VT score, labels conocidos, fuentes externas |
| **Behavior** | 30% | MITRE alto riesgo, cmdline sospechoso |
| **Context** | 20% | Vulnerabilidades del host, criticidad |
| **Propagation** | 10% | Número de hosts afectados |

---

## A.4 Componentes de la Demo Original

### Plugin y Skill SOC Analyst

| Componente | Ubicación | Función |
|------------|-----------|---------|
| **Plugin Config** | `extensions/cyberdemo/SoulInTheBot.plugin.json` | Configuración del plugin |
| **Skill Definition** | `extensions/cyberdemo/skills/soc-analyst/SKILL.md` | Define el rol y workflow |
| **API Client** | `extensions/cyberdemo/src/api-client.ts` | Cliente tipado para APIs |
| **Policy Engine** | `extensions/cyberdemo/src/policy-engine.ts` | Reglas de decisión |
| **Confidence Score** | `extensions/cyberdemo/src/confidence-score.ts` | Cálculo del score |
| **Hooks** | `extensions/cyberdemo/src/hooks.ts` | Eventos y trazabilidad |

### Comandos del Skill

| Comando | Uso | Función |
|---------|-----|---------|
| `/investigate <id>` | `/investigate INC-001` | Investigar incidente completo |
| `/demo 1` | `/demo 1` | Ejecutar escenario auto-contención |
| `/demo 2` | `/demo 2` | Ejecutar escenario VIP |
| `/demo 3` | `/demo 3` | Ejecutar escenario falso positivo |
| `/status` | `/status` | Ver estado del SOC |
| `/assets [filter]` | `/assets vip` | Ver activos |
| `/pending` | `/pending` | Ver aprobaciones pendientes |

### MCP Servers de la Demo Original

| Server | Puerto | Tools |
|--------|--------|-------|
| **cyberdemo-api** | 8001 | SIEM, EDR, Intel, CTEM, Approvals, Tickets, Reports |
| **cyberdemo-data** | 8002 | Generación de datos sintéticos |
| **cyberdemo-frontend** | 3001 | Visualización y control de UI |

### APIs Backend

| Dominio | Archivo | Endpoints Clave |
|---------|---------|-----------------|
| **SIEM** | `api/siem.py` | Incidentes, comentarios, cierre |
| **EDR** | `api/edr.py` | Detecciones, procesos, contención |
| **Intel** | `api/intel.py` | Reputación de IOCs |
| **CTEM** | `api/ctem.py` | Riesgo de activos, CVEs |
| **Approvals** | `api/approvals.py` | Solicitud/decisión de aprobaciones |
| **Timeline** | `api/timeline.py` | Acciones del agente |
| **Reports** | `api/reports.py` | Postmortems |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE B: AMPLIACIONES - INTEGRACIÓN BIDIRECCIONAL AVANZADA
# ═══════════════════════════════════════════════════════════════════════════════

Esta parte describe las **ampliaciones** construidas sobre la base de la Demo Original, añadiendo capacidades de invocación activa desde el producto, simulación de ataques APT, y asistencia proactiva.

---

# PARTE B.1: DESCRIPCIÓN FUNCIONAL

## B.1.1 Sistema de Invocación Activa (Producto → Persona IA)

### ¿Qué es?

Tradicionalmente, en los sistemas con IA, el usuario tiene que **preguntar** al asistente. Nosotros hemos invertido esto: ahora **el producto puede invocar activamente a la Persona IA** cuando ocurre algo importante.

### Escenario de Ejemplo: El Analista Pide Ayuda

```
PASO 1: El Analista Ve una Alerta
════════════════════════════════════════════════════════════════════════════

   El analista humano está trabajando en su turno nocturno. En la pantalla
   de CyberDemo aparece una nueva alerta:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ 🔴 ALERTA CRÍTICA: ALT-2024-0892                                    │
   │                                                                      │
   │ Severity: Critical                                                   │
   │ Source: EDR - CrowdStrike                                           │
   │ Host: WS-FIN-042 (Departamento Financiero)                          │
   │ Descripción: Ejecución sospechosa de PowerShell con codificación    │
   │              Base64 detectada                                        │
   │                                                                      │
   │ [🔍 Analizar con IA]  [📋 Ver Detalles]  [⏸️ Silenciar]             │
   └──────────────────────────────────────────────────────────────────────┘

   El analista piensa: "Esto parece serio, pero no estoy seguro de qué
   técnica de ataque es. Voy a pedir ayuda."


PASO 2: El Analista Hace Clic en "Analizar con IA"
════════════════════════════════════════════════════════════════════════════

   Cuando el analista hace clic en el botón [🔍 Analizar con IA]:

   1. El FRONTEND captura el clic y envía una petición al backend:

      POST /api/v1/analysis/queue
      {
        "alert_id": "ALT-2024-0892",
        "analysis_type": "full",
        "priority": "critical"
      }

   2. El BACKEND recibe la petición y:
      a) Crea un "job" de análisis con ID único (JOB-A8F2C301)
      b) Encola el job para procesamiento
      c) Dispara un WEBHOOK hacia la Persona IA

   3. El WEBHOOK llega a la Persona IA (SoulInTheBot):

      {
        "event": "analysis_requested",
        "job_id": "JOB-A8F2C301",
        "alert_id": "ALT-2024-0892",
        "priority": "critical",
        "callback_url": "https://cyberdemo/api/v1/analysis/result/JOB-A8F2C301"
      }


PASO 3: La Persona IA Trabaja
════════════════════════════════════════════════════════════════════════════

   La Persona IA (SoulInTheBot) recibe el webhook y comienza a trabajar.
   Internamente, utiliza las herramientas MCP que el producto le proporciona:

   🤖 Persona IA: "He recibido una solicitud de análisis para ALT-2024-0892.
                   Voy a usar mis herramientas para investigar."

   Llamada 1: agent_analyze_alert("ALT-2024-0892")
   ─────────────────────────────────────────────────────────────────────
   → Obtiene: Detalles de la alerta, host afectado, timeline de eventos
   → Detecta: Comando PowerShell codificado en Base64
   → Mapea: MITRE ATT&CK T1059.001 (PowerShell), T1027 (Obfuscation)

   Llamada 2: agent_investigate_ioc("WS-FIN-042", type="hostname")
   ─────────────────────────────────────────────────────────────────────
   → Obtiene: El host pertenece al departamento financiero
   → Detecta: Usuario conectado es "j.martinez" (Contabilidad)
   → Historial: 3 alertas previas en este host en últimos 7 días

   Llamada 3: agent_correlate_events(alert_id="ALT-2024-0892", timeframe="24h")
   ─────────────────────────────────────────────────────────────────────
   → Encuentra: 2 alertas relacionadas en otros hosts del mismo segmento
   → Patrón: Posible movimiento lateral desde WS-HR-015
   → Correlación: El mismo hash malicioso aparece en los 3 hosts

   Llamada 4: agent_recommend_action(context={...})
   ─────────────────────────────────────────────────────────────────────
   → Genera: Lista priorizada de acciones recomendadas
   → Urgencia: Contención inmediata recomendada


PASO 4: La Persona IA Devuelve Resultados al Producto
════════════════════════════════════════════════════════════════════════════

   Después de su análisis, la Persona IA envía los resultados de vuelta
   al producto usando el callback_url del webhook:

   POST https://cyberdemo/api/v1/analysis/result/JOB-A8F2C301
   {
     "status": "completed",
     "analysis": {
       "threat_assessment": "high",
       "mitre_mapping": ["T1059.001", "T1027", "T1021.002"],
       "threat_actor_likely": "FIN7 or similar financially motivated group",
       "affected_hosts": ["WS-FIN-042", "WS-FIN-038", "WS-HR-015"],
       "recommended_actions": [
         {
           "priority": 1,
           "action": "Aislar hosts afectados de la red",
           "urgency": "immediate",
           "reason": "Prevenir movimiento lateral adicional"
         },
         {
           "priority": 2,
           "action": "Bloquear hash del malware en EDR",
           "urgency": "high"
         },
         {
           "priority": 3,
           "action": "Revisar logs de acceso de j.martinez",
           "urgency": "medium"
         }
       ],
       "confidence": 0.87,
       "reasoning": "El patrón de ejecución de PowerShell codificado seguido
                     de descubrimiento de red es consistente con la fase
                     inicial de ataques de FIN7. La presencia del mismo
                     hash en múltiples hosts sugiere propagación activa."
     }
   }


PASO 5: El Producto Muestra Resultados al Analista
════════════════════════════════════════════════════════════════════════════

   El analista ve los resultados en pantalla:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ ✅ ANÁLISIS COMPLETADO - ALT-2024-0892                              │
   │                                                                      │
   │ 🎯 Evaluación de Amenaza: ALTA (87% confianza)                      │
   │ 🏷️ Actor Probable: FIN7 o grupo similar                            │
   │                                                                      │
   │ MITRE ATT&CK:                                                        │
   │ ├─ T1059.001 (PowerShell) - Ejecución                               │
   │ ├─ T1027 (Obfuscation) - Evasión de Defensa                         │
   │ └─ T1021.002 (SMB/Windows Admin Shares) - Movimiento Lateral        │
   │                                                                      │
   │ 🖥️ Hosts Afectados: WS-FIN-042, WS-FIN-038, WS-HR-015               │
   │                                                                      │
   │ 📋 ACCIONES RECOMENDADAS:                                           │
   │ ┌────────────────────────────────────────────────────────────────┐  │
   │ │ 1. [🔴 URGENTE] Aislar hosts de la red                        │  │
   │ │    → Prevenir movimiento lateral adicional                     │  │
   │ │    [✓ Ejecutar] [✗ Rechazar] [? Por qué]                      │  │
   │ ├────────────────────────────────────────────────────────────────┤  │
   │ │ 2. [🟠 ALTA] Bloquear hash del malware                        │  │
   │ │    [✓ Ejecutar] [✗ Rechazar] [? Por qué]                      │  │
   │ └────────────────────────────────────────────────────────────────┘  │
   │                                                                      │
   │ 💭 RAZONAMIENTO DE LA PERSONA IA:                                   │
   │ "El patrón de ejecución de PowerShell codificado seguido de         │
   │  descubrimiento de red es consistente con la fase inicial de        │
   │  ataques de FIN7..."                                                │
   └──────────────────────────────────────────────────────────────────────┘

   El analista ahora tiene toda la información que necesita para tomar
   una decisión informada. Puede:
   - Aceptar las recomendaciones de la Persona IA
   - Rechazarlas si tiene información adicional
   - Pedir más explicación con "¿Por qué?"
```

### Componentes Técnicos que Hacen Esto Posible

| Componente | Ubicación | Función |
|------------|-----------|---------|
| **Analysis Queue API** | `backend/src/api/analysis_queue.py` | Recibe peticiones del frontend, crea jobs, dispara webhooks |
| **Webhook Service** | `backend/src/api/webhooks.py` | Configura y dispara webhooks hacia la Persona IA |
| **Agent Orchestration Tools** | `backend/src/mcp/tools/agent_orchestration.py` | 6 herramientas MCP que la Persona IA usa para analizar |
| **Rate Limiter** | `backend/src/mcp/rate_limiter.py` | Previene sobrecarga (100 req/min) |
| **HMAC Validator** | `backend/src/mcp/hmac_validator.py` | Autentica webhooks con firma criptográfica |
| **Audit Logger** | `backend/src/mcp/audit_logger.py` | Registra todas las invocaciones para compliance |

### Las 6 Herramientas de Orquestación del Agente

Estas son las herramientas MCP que la Persona IA puede usar para analizar:

| Herramienta | ¿Qué hace? | ¿Cuándo se usa? |
|-------------|------------|-----------------|
| `agent_analyze_alert` | Analiza una alerta completa con evaluación de amenaza y mapeo MITRE | Cuando el analista pide análisis de una alerta |
| `agent_investigate_ioc` | Investiga un indicador (IP, dominio, hash, URL) con inteligencia de amenazas | Cuando se necesita enriquecer un IOC específico |
| `agent_recommend_action` | Genera acciones recomendadas priorizadas con razonamiento | Cuando se necesita orientación sobre qué hacer |
| `agent_generate_report` | Crea informes completos de incidentes en JSON o Markdown | Para documentación y cumplimiento |
| `agent_explain_decision` | Explica el razonamiento detrás de una decisión o recomendación | Cuando el analista pregunta "¿Por qué?" |
| `agent_correlate_events` | Correlaciona múltiples eventos para identificar patrones | Para detectar campañas de ataque más amplias |

---

## B.1.2 Sistema de Simulación de Ataques

### ¿Qué es?

Un sistema que **simula ataques realistas** basados en grupos APT (Advanced Persistent Threat) reales, siguiendo el framework MITRE ATT&CK. Esto permite:

- **Entrenar analistas** con escenarios realistas sin riesgo
- **Demostrar capacidades** del producto a clientes
- **Probar detecciones** antes de ponerlas en producción

### Escenario de Ejemplo: Demo de Ataque APT29

```
CONTEXTO
════════════════════════════════════════════════════════════════════════════

   Un presentador está haciendo una demo del producto a un cliente potencial.
   Quiere mostrar cómo la plataforma detecta y ayuda a responder a un ataque
   sofisticado de espionaje tipo APT29 (Cozy Bear - grupo ruso).


PASO 1: El Presentador Selecciona el Escenario
════════════════════════════════════════════════════════════════════════════

   En el panel de control de demo, el presentador ve:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ 🎮 PANEL DE CONTROL DE SIMULACIÓN                                   │
   │                                                                      │
   │ Escenario: [▼ APT29 (Cozy Bear)        ]                            │
   │                                                                      │
   │ Descripción: Grupo de espionaje ruso que ataca entidades            │
   │              gubernamentales y diplomáticas                          │
   │                                                                      │
   │ Fases MITRE ATT&CK:                                                 │
   │ ○ Initial Access    ○ Execution    ○ Persistence                    │
   │ ○ Defense Evasion   ○ Discovery    ○ Collection                     │
   │ ○ Exfiltration      ○ C2                                            │
   │                                                                      │
   │ Velocidad: [━━━━━●━━━━] 1.5x                                        │
   │                                                                      │
   │ [ ▶️ INICIAR ]  [ ⏸️ PAUSAR ]  [ ⏹️ DETENER ]                        │
   └──────────────────────────────────────────────────────────────────────┘

   El presentador hace clic en [▶️ INICIAR].


PASO 2: El Sistema Genera Eventos de Ataque
════════════════════════════════════════════════════════════════════════════

   El backend comienza a generar eventos sintéticos que simulan un ataque
   APT29 real. Los eventos aparecen en la pantalla como si fueran reales:

   FASE 1 - Initial Access (T1566.001 - Spear-Phishing)
   ─────────────────────────────────────────────────────
   10:00:15 | 📧 Email recibido: "Actualización de política COVID-19"
            |    Destinatario: r.gonzalez@empresa.com
            |    Adjunto: policy_update.docx (macro detectada)

   10:00:47 | 🔴 ALERTA: Macro maliciosa ejecutada
            |    Host: WS-EXEC-001
            |    Usuario: r.gonzalez (Director Ejecutivo)

   FASE 2 - Execution (T1059.001 - PowerShell)
   ─────────────────────────────────────────────────────
   10:01:12 | ⚠️ PowerShell ejecutado con parámetros sospechosos
            |    Comando: "powershell -enc JABzAD0ATgBlAHcA..."
            |    Técnica: T1059.001

   FASE 3 - Persistence (T1547.001 - Registry Run Keys)
   ─────────────────────────────────────────────────────
   10:02:33 | 🔴 Modificación de registro detectada
            |    Clave: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
            |    Valor: "WindowsUpdate" → C:\Users\r.gonzalez\svchost.exe

   ... y así sucesivamente por todas las fases del ataque


PASO 3: El Presentador Controla la Demo
════════════════════════════════════════════════════════════════════════════

   Durante la demo, el presentador puede:

   • PAUSAR la simulación para explicar una fase
   • CAMBIAR LA VELOCIDAD para ir más rápido o más lento
   • SALTAR A UNA FASE específica (ej: "Vamos directo a Exfiltración")
   • INYECTAR EVENTOS custom para mostrar casos específicos

   La Persona IA también está "viendo" estos eventos y puede:
   • Analizar alertas cuando el presentador lo solicita
   • Mostrar correlaciones entre eventos
   • Generar recomendaciones en tiempo real


PASO 4: Visualización del Ataque
════════════════════════════════════════════════════════════════════════════

   El presentador muestra al cliente la cadena de ataque visual:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ 📊 CADENA DE ATAQUE - APT29 (Cozy Bear)                             │
   │                                                                      │
   │  Initial     Execution    Persistence   Defense      Discovery      │
   │  Access                                  Evasion                     │
   │    ●━━━━━━━━━━━●━━━━━━━━━━━●━━━━━━━━━━━●━━━━━━━━━━━◐            │
   │  T1566.001   T1059.001   T1547.001    T1027       T1083            │
   │  ✓ Detect   ✓ Detect    ✓ Detect    ✓ Detect    ⏳ En curso      │
   │                                                                      │
   │  Collection   Exfiltration   C2                                      │
   │    ○━━━━━━━━━━━○━━━━━━━━━━━━━○                                       │
   │  T1560        T1041         T1071.001                               │
   │  Pendiente    Pendiente     Pendiente                               │
   └──────────────────────────────────────────────────────────────────────┘
```

### Los 6 Escenarios de Ataque Disponibles

| Escenario | Grupo/Tipo | Descripción | Fases MITRE |
|-----------|------------|-------------|-------------|
| **APT29** | Cozy Bear (Rusia) | Espionaje contra gobiernos y diplomáticos | 8 fases |
| **FIN7** | Grupo financiero | Ataque a retail/hospitalidad para robo financiero | 6 fases |
| **Lazarus** | Grupo norcoreano | Ataques destructivos con wipers | 5 fases |
| **REvil** | Ransomware | Ransomware-as-a-Service en redes empresariales | 5 fases |
| **SolarWinds** | Supply Chain | Compromiso de actualizaciones de software | 6 fases |
| **Insider** | Amenaza interna | Empleado malicioso exfiltrando datos | 3 fases |

### Las 6 Herramientas de Control de Simulación

| Herramienta | ¿Qué hace? | Uso en demo |
|-------------|------------|-------------|
| `attack_start_scenario` | Inicia un escenario de ataque específico | "Iniciemos el ataque APT29" |
| `attack_pause` | Pausa la generación de eventos | "Paremos aquí para explicar" |
| `attack_resume` | Reanuda la simulación pausada | "Continuemos con el ataque" |
| `attack_speed` | Cambia la velocidad (0.5x - 4x) | "Aceleremos para llegar a exfiltración" |
| `attack_jump_to_stage` | Salta a una fase MITRE específica | "Vamos directo a Collection" |
| `attack_inject_event` | Inyecta un evento personalizado | "Veamos qué pasa si aparece este IOC" |

---

## B.1.3 Sistema aIP Assist (Asistencia Proactiva)

### ¿Qué es?

**aIP Assist** (Artificial Intelligence Person Assist) es un sistema donde la **Persona IA observa lo que hace el analista** y ofrece sugerencias proactivas sin que se las pidan.

A diferencia del sistema de invocación activa (donde el analista pide ayuda), aquí la **Persona IA toma la iniciativa**.

### Escenario de Ejemplo: Sugerencias Proactivas

```
CONTEXTO
════════════════════════════════════════════════════════════════════════════

   El analista está revisando alertas en su turno. No ha pedido ayuda,
   pero la Persona IA está "observando" sus acciones.


PASO 1: El Analista Navega por la Interfaz
════════════════════════════════════════════════════════════════════════════

   El analista hace varias acciones:
   - Hace clic en la alerta ALT-001
   - Mira los detalles
   - Hace scroll hacia abajo
   - Hace clic en un IOC (185.234.72.199)

   Cada una de estas acciones se captura y envía al backend:

   Frontend (useAipAssist hook):
   ───────────────────────────────────────────────────────────────────────
   El hook captura cada acción del usuario y la envía por WebSocket:

   {
     "type": "action",
     "action": "click",
     "element": "alert-row",
     "element_id": "ALT-001",
     "page": "alerts",
     "timestamp": "2026-02-23T10:15:33Z"
   }

   {
     "type": "action",
     "action": "click",
     "element": "ioc-link",
     "element_id": "185.234.72.199",
     "page": "alerts",
     "visible_data": {"ioc_type": "ip", "alert_context": "ALT-001"}
   }


PASO 2: La Persona IA Analiza el Contexto
════════════════════════════════════════════════════════════════════════════

   La Persona IA recibe el stream de acciones y analiza:

   🤖 Persona IA (pensando internamente):
   "El analista está viendo la alerta ALT-001 y acaba de hacer clic
   en el IOC 185.234.72.199. Basándome en esto, puedo sugerir:
   - Investigar ese IOC con inteligencia de amenazas (alta relevancia)
   - Correlacionar con otras alertas que tengan esta IP (media relevancia)
   - Ver el historial del host afectado (media relevancia)"

   La Persona IA usa la herramienta: aip_get_suggestion(context)
   ───────────────────────────────────────────────────────────────────────
   → Genera sugerencias basadas en:
     - La página actual (alerts)
     - La entidad seleccionada (ALT-001)
     - Las acciones recientes (click en IOC)
     - Patrones históricos de flujos de trabajo efectivos


PASO 3: Las Sugerencias Aparecen en Pantalla
════════════════════════════════════════════════════════════════════════════

   Sin que el analista haga nada, aparece el widget de aIP Assist:

   ┌──────────────────────────────────────────────────────────────────────┐
   │ 🤖 aIP Assist                                    [ON] ▼             │
   ├──────────────────────────────────────────────────────────────────────┤
   │ Total: 5 │ ✅ 3 │ ❌ 1 │ Tasa: 75%                                  │
   ├──────────────────────────────────────────────────────────────────────┤
   │                                                                      │
   │ ┌────────────────────────────────────────────────────────────────┐  │
   │ │ 🔵 Action                                   Alta confianza     │  │
   │ │ Investigar IOC con Inteligencia de Amenazas                   │  │
   │ │                                                                │  │
   │ │ Enriquecer 185.234.72.199 con datos de reputación y           │  │
   │ │ geolocalización para evaluar el nivel de amenaza.             │  │
   │ │                                                                │  │
   │ │ [✓ Aceptar]  [✗ Rechazar]  [? Por qué]                        │  │
   │ └────────────────────────────────────────────────────────────────┘  │
   │                                                                      │
   │ ┌────────────────────────────────────────────────────────────────┐  │
   │ │ 🟣 Investigation                            Media confianza    │  │
   │ │ Correlacionar con Alertas Similares                           │  │
   │ │                                                                │  │
   │ │ Buscar otras alertas en las últimas 24h que involucren       │  │
   │ │ esta misma IP para identificar patrones.                      │  │
   │ │                                                                │  │
   │ │ [✓ Aceptar]  [✗ Rechazar]  [? Por qué]                        │  │
   │ └────────────────────────────────────────────────────────────────┘  │
   │                                                                      │
   └──────────────────────────────────────────────────────────────────────┘


PASO 4: El Analista Interactúa con las Sugerencias
════════════════════════════════════════════════════════════════════════════

   Opción A: El analista hace clic en [✓ Aceptar]
   ───────────────────────────────────────────────────────────────────────
   → La sugerencia se ejecuta automáticamente
   → Se llama a agent_investigate_ioc("185.234.72.199", type="ip")
   → Los resultados aparecen en pantalla
   → Se registra como "aceptada" para métricas

   Opción B: El analista hace clic en [✗ Rechazar]
   ───────────────────────────────────────────────────────────────────────
   → La sugerencia desaparece
   → Se registra como "rechazada"
   → aIP Assist aprende que en este contexto, esta sugerencia no era útil

   Opción C: El analista hace clic en [? Por qué]
   ───────────────────────────────────────────────────────────────────────
   → Se llama a aip_explain_why(action, context)
   → Aparece una explicación:

   ┌────────────────────────────────────────────────────────────────────┐
   │ 💭 ¿Por qué sugiero esto?                                         │
   │                                                                    │
   │ "Investigar este IOC proporcionará datos de reputación,           │
   │  información geográfica e indicadores relacionados. Esto ayuda    │
   │  a determinar si es malicioso."                                   │
   │                                                                    │
   │ Evidencia:                                                         │
   │ • El IOC aparece en el contexto de la alerta                      │
   │ • El enriquecimiento proporciona contexto de amenaza              │
   │ • Los indicadores relacionados pueden revelar la campaña          │
   │                                                                    │
   │ Alternativas consideradas:                                         │
   │ • Bloquear IOC directamente (si se confirma malicioso)            │
   │ • Añadir a lista de vigilancia (para monitoreo continuo)          │
   └────────────────────────────────────────────────────────────────────┘


PASO 5: Autocompletado Inteligente
════════════════════════════════════════════════════════════════════════════

   Más tarde, el analista necesita buscar una IP y comienza a escribir:

   ┌─────────────────────────────────────────┐
   │ Buscar IOC: 192.168.1█                  │
   ├─────────────────────────────────────────┤
   │ Sugerencias:                            │
   │ ├─ 192.168.1.10  (eventos recientes)   │
   │ ├─ 192.168.1.42  (inventario activos)  │
   │ └─ 192.168.1.50  (alertas activas)     │
   └─────────────────────────────────────────┘

   Esto viene de aip_auto_complete("192.168.1", field_type="ip_address")

   La Persona IA conoce las IPs del entorno y sugiere las más relevantes,
   ahorrando tiempo y evitando errores de escritura.
```

### Las 3 Herramientas de aIP Assist

| Herramienta | ¿Qué hace? | ¿Cuándo se usa? |
|-------------|------------|-----------------|
| `aip_get_suggestion` | Genera sugerencias contextuales basadas en las acciones del usuario | Automáticamente cuando el usuario navega |
| `aip_explain_why` | Explica el razonamiento detrás de una sugerencia | Cuando el usuario hace clic en "¿Por qué?" |
| `aip_auto_complete` | Autocompleta entradas parciales (IPs, hosts, usuarios, hashes) | Cuando el usuario escribe en campos de búsqueda |

### Métricas de aIP Assist

El sistema rastrea:

| Métrica | Descripción | Uso |
|---------|-------------|-----|
| **Total Sugerencias** | Cuántas sugerencias se han mostrado | Volumen de asistencia |
| **Aceptadas** | Cuántas ha aceptado el analista | Efectividad |
| **Rechazadas** | Cuántas ha rechazado el analista | Calibración |
| **Tasa de Aceptación** | % de aceptación | KPI de utilidad |

---

## B.1.4 Resumen: El Flujo Completo de la Ampliación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE INTERACCIÓN COMPLETO                           │
└─────────────────────────────────────────────────────────────────────────────┘

     👤 ANALISTA HUMANO              🖥️ PRODUCTO                🤖 PERSONA IA
     ═══════════════════             ════════════               ══════════════

  1. Ve alertas en pantalla ─────────► Muestra datos
                                       del SIEM/EDR

  2. Hace clic en "Analizar" ────────► Crea job, dispara ──────► Recibe webhook
                                       webhook
                                                                       │
                                                                       ▼
                                                               Usa MCP tools:
                                                               • agent_analyze_alert
                                                               • agent_investigate_ioc
                                                               • agent_correlate_events
                                                                       │
  3. Ve resultados del ◄─────────────── Recibe resultado ◄─────────────┘
     análisis con                      y lo muestra
     recomendaciones

  4. Navega por la UI ───────────────► Captura acciones ──────► Observa stream
     (sin pedir ayuda)                 con useAipAssist         de acciones
                                                                       │
                                                                       ▼
                                                               Analiza contexto
                                                               y genera
                                                               sugerencias
                                                                       │
  5. Ve sugerencias ◄────────────────── Muestra widget ◄───────────────┘
     proactivas en el                  de aIP Assist
     widget lateral

  6. Acepta sugerencia ──────────────► Ejecuta acción ─────────► Recibe feedback
     o hace clic en                    recomendada               para mejorar
     "¿Por qué?"

  7. Durante demos, ─────────────────► Genera eventos ─────────► Puede analizar
     controla simulación               sintéticos de             eventos
     de ataques                        ataques APT               simulados
```

---

# PARTE B.2: COMPONENTES TÉCNICOS DE LAS AMPLIACIONES

## Resumen de Componentes Creados

### Backend - APIs

| Archivo | Propósito | Endpoints |
|---------|-----------|-----------|
| `api/webhooks.py` | Configuración de webhooks | POST/GET/DELETE /webhooks |
| `api/analysis_queue.py` | Cola de análisis asíncrono | POST /queue, GET /status, GET /result, WS /ws |
| `api/mitre.py` | Datos MITRE ATT&CK | GET /tactics, GET /techniques |
| `api/aip_assist.py` | Sesiones de aIP Assist | GET /session/state, POST /feedback, WS /ws |

### Backend - MCP Tools

| Archivo | Herramientas | Total |
|---------|--------------|-------|
| `mcp/tools/agent_orchestration.py` | 6 tools de orquestación del agente | 6 |
| `mcp/tools/attack_simulation.py` | 6 tools de control de simulación | 6 |
| `mcp/tools/aip_assist.py` | 3 tools de asistencia proactiva | 3 |
| **TOTAL** | | **15 tools** |

### Backend - Infraestructura

| Archivo | Propósito |
|---------|-----------|
| `mcp/rate_limiter.py` | Rate limiting 100 req/min por sesión |
| `mcp/hmac_validator.py` | Autenticación HMAC-SHA256 para webhooks |
| `mcp/audit_logger.py` | Logging inmutable de todas las invocaciones |

### Backend - Escenarios de Ataque

| Archivo | Escenario |
|---------|-----------|
| `demo/scenario_lazarus.py` | Lazarus Group - Ataque destructivo |
| `demo/scenario_revil.py` | REvil - Ransomware |
| `demo/scenario_supply_chain.py` | SolarWinds - Supply chain |
| `demo/scenario_insider_threat.py` | Insider - Amenaza interna |
| `demo/scenario_ransomware.py` | FIN7 - Financiero |

### Frontend - Componentes

| Archivo | Propósito |
|---------|-----------|
| `hooks/useAipAssist.ts` | Hook para capturar acciones del usuario |
| `components/aip-assist/AipAssistWidget.tsx` | Widget de sugerencias |
| `components/aip-assist/types.ts` | Tipos TypeScript |

---

## Matriz de Requisitos Implementados

| ID | Descripción | Estado |
|----|-------------|--------|
| **EPIC-001: Agent Orchestration** | | |
| REQ-001-001-001 | API endpoint webhooks/configure | ✅ |
| REQ-001-001-002 | Webhook dispatcher con retry | ✅ |
| REQ-001-002-001 | POST /analysis/queue | ✅ |
| REQ-001-002-002 | GET /analysis/status/{job_id} | ✅ |
| REQ-001-002-003 | GET /analysis/result/{job_id} | ✅ |
| REQ-001-002-004 | WebSocket /ws/analysis | ✅ |
| REQ-001-003-001 | agent_analyze_alert tool | ✅ |
| REQ-001-003-002 | agent_investigate_ioc tool | ✅ |
| REQ-001-003-003 | agent_recommend_action tool | ✅ |
| REQ-001-003-004 | agent_generate_report tool | ✅ |
| REQ-001-003-005 | agent_explain_decision tool | ✅ |
| REQ-001-003-006 | agent_correlate_events tool | ✅ |
| TECH-008 | Rate limiting 100 req/min | ✅ |
| TECH-009 | HMAC signature validation | ✅ |
| REQ-014 | Audit logging | ✅ |
| **EPIC-002: Attack Simulation** | | |
| REQ-002-001-001 | Escenario APT29 | ✅ |
| REQ-002-001-002 | Escenario FIN7 | ✅ |
| REQ-002-001-003 | Escenario Lazarus | ✅ |
| REQ-002-001-004 | Escenario REvil | ✅ |
| REQ-002-001-005 | Escenario SolarWinds | ✅ |
| REQ-002-001-006 | Escenario Insider | ✅ |
| REQ-002-002-001 | attack_start_scenario tool | ✅ |
| REQ-002-002-002 | attack_pause/resume tools | ✅ |
| REQ-002-002-003 | attack_speed tool | ✅ |
| REQ-002-002-004 | attack_jump_to_stage tool | ✅ |
| REQ-002-002-005 | attack_inject_event tool | ✅ |
| **EPIC-004: aIP Assist** | | |
| REQ-004-001-001 | Hook para captura de acciones | ✅ |
| REQ-004-001-002 | Throttling 10 acciones/segundo | ✅ |
| REQ-004-001-004 | WebSocket /ws/aip-assist | ✅ |
| REQ-004-002-001 | aip_get_suggestion tool | ✅ |
| REQ-004-002-002 | aip_explain_why tool | ✅ |
| REQ-004-002-003 | aip_auto_complete tool | ✅ |
| REQ-004-002-004 | AipAssistWidget component | ✅ |
| REQ-004-002-005 | Tracking aceptación/rechazo | ✅ |

---

---

# RESUMEN EJECUTIVO

## ¿Qué incluye CyberDemo?

| Parte | Nombre | Descripción | Componentes Clave |
|-------|--------|-------------|-------------------|
| **A** | Demo Original | Analista SOC Tier-1 automatizado con 3 escenarios | Plugin soc-analyst, Policy Engine, 3 casos demo |
| **B.1** | Invocación Activa | El producto invoca a la Persona IA vía webhooks | Analysis Queue, 6 Agent Tools, Webhooks |
| **B.2** | Simulación de Ataques | Simula ataques APT para demos y entrenamiento | 6 escenarios APT, 6 Simulation Tools |
| **B.3** | aIP Assist | Asistencia proactiva basada en observación | Widget, 3 aIP Tools, WebSocket stream |

## Conteo Total de Componentes

| Tipo | Cantidad | Detalle |
|------|----------|---------|
| **MCP Tools** | 15+ | 6 agent + 6 attack + 3 aIP + originales SOC |
| **APIs REST** | 20+ | SIEM, EDR, Intel, CTEM, Webhooks, Analysis, etc. |
| **Escenarios** | 9 | 3 demo originales + 6 ataques APT |
| **Vistas UI** | 14 | Dashboard, Incidents, Detections, CTEM, etc. |

---

*Documento generado - CyberDemo Platform v2.0.0*

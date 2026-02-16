# SOC Analyst Plugin - Guía Completa

## Resumen Ejecutivo

**SOC Analyst** es un skill/plugin de SoulInTheBot que convierte a Claude en un **Analista SOC Tier-1 automatizado**. Investiga alertas de malware, determina severidad, y toma decisiones de contención respetando políticas de activos críticos.

### En 30 Segundos

| Aspecto          | Descripción                                        |
| ---------------- | -------------------------------------------------- |
| **Nombre**       | `soc-analyst`                                      |
| **Paquete**      | `@moltbot/cyberdemo-soc-analyst`                   |
| **Propósito**    | Investigar incidentes de seguridad automáticamente |
| **Comandos**     | `/investigate`, `/demo`, `/status`                 |
| **Herramientas** | SIEM, EDR, Intel, CTEM, Approvals, Tickets         |
| **MCP Servers**  | 3 (API, Data, Frontend)                            |

### Flujo de Trabajo Visual

```
Alerta SIEM → Enriquecer → Calcular Score → Policy Engine → Ejecutar/Aprobar → Postmortem
     ↓            ↓              ↓                ↓              ↓            ↓
  Incidente   Intel + EDR    0-100%         Decisión     Contener o     Cerrar
              + CTEM                       Automática    Esperar OK
```

---

## 1. Qué Es y Para Qué Sirve

### Contexto

El plugin simula un entorno SOC (Security Operations Center) donde el agente Claude:

1. **Recibe alertas** de un SIEM (tipo Microsoft Sentinel)
2. **Enriquece** con inteligencia de amenazas, EDR, y contexto de activos
3. **Calcula** un score de confianza (0-100)
4. **Aplica políticas** deterministas para decidir acciones
5. **Ejecuta** contención o solicita aprobación humana
6. **Documenta** todo en tickets y postmortems

### Por Qué Es Importante

En un SOC real, un Tier-1 analyst:

- Procesa cientos de alertas diarias
- La mayoría son falsos positivos (80-90%)
- Debe escalar correctamente los verdaderos positivos
- No debe contener activos críticos sin aprobación

Este plugin automatiza esas decisiones de forma **determinista** y **auditable**.

---

## 2. Comandos Disponibles

### `/investigate <incident_id>`

Investiga un incidente específico de principio a fin.

```bash
/investigate INC-2024-001
```

**Qué hace:**

1. Obtiene detalles del incidente (SIEM)
2. Extrae host, hash, usuario afectado
3. Consulta reputación del hash (Intel)
4. Obtiene árbol de procesos (EDR)
5. Busca propagación en otros hosts (EDR)
6. Obtiene contexto de vulnerabilidades (CTEM)
7. Calcula score de confianza
8. Aplica Policy Engine
9. Ejecuta acción o solicita aprobación
10. Genera postmortem

### `/demo <1|2|3>`

Ejecuta escenarios de demostración predefinidos.

```bash
/demo 1   # Auto-contención de workstation normal
/demo 2   # Laptop VIP - requiere aprobación humana
/demo 3   # Falso positivo - descarta alerta
```

**Escenarios:**

| Escenario | Host          | Tipo                 | Resultado Esperado          |
| --------- | ------------- | -------------------- | --------------------------- |
| 1         | WS-FIN-042    | Standard workstation | Contención automática       |
| 2         | LAPTOP-CFO-01 | VIP/Executive        | Requiere aprobación         |
| 3         | SRV-DEV-03    | Standard             | Falso positivo (score < 50) |

### `/status`

Muestra el estado actual del SOC.

```bash
/status
```

**Muestra:**

- Número de incidentes abiertos
- Incidentes por severidad
- Hosts contenidos
- Últimas acciones tomadas

---

## 3. Herramientas (MCP Tools)

El plugin expone herramientas via 3 MCP servers:

### 3.1 SIEM Operations (Puerto 8001)

```javascript
// Listar incidentes abiertos
siem.listIncidents((status = "open"), (limit = 10));

// Obtener detalles de incidente
siem.getIncident("INC-2024-001");

// Añadir comentario de investigación
siem.addComment("INC-2024-001", "Malware confirmado, procediendo con contención");

// Cerrar incidente
siem.closeIncident("INC-2024-001", (reason = "Contained"));
```

### 3.2 EDR Operations (Puerto 8001)

```javascript
// Obtener detalles de detección
edr.getDetection("DET-789");

// Obtener árbol de procesos (quién lanzó qué)
edr.getProcessTree("DET-789");
// → Devuelve: cmd.exe → powershell.exe → malware.exe

// Buscar propagación del hash en toda la organización
edr.huntHash("abc123def456...");
// → Devuelve: [WS-FIN-042, WS-HR-011, WS-MKT-023]

// Contener host (aislarlo de la red)
edr.containHost("DEV-001", "Emotet confirmed - isolating");
```

### 3.3 Intelligence (Puerto 8001)

```javascript
// Consultar reputación de IOC
intel.getIndicator("filehash", "abc123def456...");
// → { vt_score: 58/74, labels: ["trojan", "emotet"], malicious: true }

intel.getIndicator("ip", "192.0.2.1");
// → { reputation: 95, country: "RU", malware_families: ["TrickBot"] }

intel.getIndicator("domain", "evil.com");
// → { malicious: true, first_seen: "2024-01-15" }
```

### 3.4 CTEM - Vulnerability Context (Puerto 8001)

```javascript
// Obtener riesgo del activo (vulnerabilidades, criticidad)
ctem.getAssetRisk("ASSET-001");
// → {
//     risk_score: 75,
//     critical_vulns: 3,
//     tags: ["vip", "executive"],
//     last_patch: "2024-01-10"
//   }
```

### 3.5 Approvals - Human-in-the-Loop (Puerto 8001)

```javascript
// Consultar estado de aprobación
approvals.get("INC-2024-001");
// → { status: "pending", requested_at: "...", approver: null }

// Solicitar aprobación humana
approvals.request("INC-2024-001", {
  hostname: "LAPTOP-CFO-01",
  owner: "CEO",
  confidence_score: 95,
  recommendation: "CONTAIN",
  reason: "Emotet trojan detected",
});
```

### 3.6 Tickets & Reports (Puerto 8001)

```javascript
// Crear ticket de seguimiento
tickets.create({
  title: "Malware containment - WS-FIN-042",
  severity: "high",
  description: "Emotet detected and contained",
  assigned_to: "SOC Team",
});

// Generar postmortem del incidente
reports.generatePostmortem("INC-2024-001");
// → Genera documento con timeline, acciones, lecciones aprendidas
```

### 3.7 Synthetic Data Generation (Puerto 8002)

```javascript
// Generar datos de prueba
data.generate_all((seed = 42));

// Generar activos de prueba
data.generate_assets((count = 100));

// Generar detecciones EDR
data.generate_edr_detections((count = 50));

// Limpiar y recrear datos
data.reset();
```

### 3.8 Frontend Visualization (Puerto 3001)

```javascript
// Mostrar simulación en dashboard
frontend.show_simulation(data);

// Ejecutar escenario de demo
frontend.run_demo_scenario(1);

// Resaltar activo en grafo
frontend.highlight_asset("WS-FIN-042");

// Mostrar timeline de investigación
frontend.show_alert_timeline("INC-2024-001");
```

---

## 4. Policy Engine (Motor de Políticas)

### Reglas Deterministas

El Policy Engine **no usa IA** - es 100% determinista:

```yaml
# Regla 1: Falso Positivo
IF confidence_score < 50:
  ACTION: mark_false_positive
  REQUIRE_APPROVAL: false

# Regla 2: Auto-contención
IF confidence_score >= 90 AND asset NOT IN [vip, executive, server, domain-controller]:
  ACTION: auto_contain
  REQUIRE_APPROVAL: false

# Regla 3: Activo Crítico (SIEMPRE requiere aprobación)
IF asset IN [vip, executive, server, domain-controller]:
  ACTION: request_approval
  REQUIRE_APPROVAL: true
  # No importa el score - SIEMPRE pedir OK

# Regla 4: Score Medio
IF confidence_score >= 50 AND confidence_score < 90:
  ACTION: request_approval
  REQUIRE_APPROVAL: true
```

### Cálculo del Confidence Score

```
Confidence Score = Intel (40%) + Behavior (30%) + Context (20%) + Propagation (10%)

Intel (0-40 puntos):
- VT score > 50/74: +30
- Malware labels conocidos: +10
- Sin detecciones VT: 0

Behavior (0-30 puntos):
- Técnica MITRE de alto riesgo: +20
- Command line sospechoso: +10
- Proceso legítimo: 0

Context (0-20 puntos):
- Host con vulnerabilidades críticas: +15
- Asset criticality alta: +5
- Host parcheado: 0

Propagation (0-10 puntos):
- 1 host afectado: +2
- 2-5 hosts: +5
- 6+ hosts: +10
```

---

## 5. Arquitectura MCP

```
┌──────────────────────────────────────────────────────────────────┐
│                      SoulInTheBot                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Gateway (puerto 18789)                                     │  │
│  │  Plugin: cyberdemo-soc-analyst                              │  │
│  │  MCP Clients:                                               │  │
│  │    • cyberdemo-api (8001)   → SIEM, EDR, Intel, CTEM       │  │
│  │    • cyberdemo-data (8002)  → Datos sintéticos              │  │
│  │    • cyberdemo-frontend (3001) → Visualización              │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Puertos

| Servicio     | Puerto | Protocolo | Descripción          |
| ------------ | ------ | --------- | -------------------- |
| Backend API  | 8000   | HTTP REST | API REST tradicional |
| Backend MCP  | 8001   | HTTP MCP  | Tools para SOC ops   |
| Data MCP     | 8002   | HTTP MCP  | Generación sintética |
| Frontend Web | 3000   | HTTP      | UI React             |
| Frontend MCP | 3001   | WebSocket | Visualización        |
| SoulInTheBot | 18789  | HTTP      | Gateway del agente   |

---

## 6. Configuración

### Archivo de Configuración

```json
{
  "apiBaseUrl": "http://localhost:8000",
  "autoContainmentEnabled": true,
  "confidenceThresholdHigh": 90,
  "confidenceThresholdMedium": 50
}
```

### Variables

| Variable                    | Default                 | Descripción                 |
| --------------------------- | ----------------------- | --------------------------- |
| `apiBaseUrl`                | `http://localhost:8000` | URL del backend             |
| `autoContainmentEnabled`    | `true`                  | Habilitar auto-contención   |
| `confidenceThresholdHigh`   | `90`                    | Score para auto-contener    |
| `confidenceThresholdMedium` | `50`                    | Score bajo = falso positivo |

---

## 7. Ejemplos de Uso Completos

### Ejemplo 1: Investigación Normal

```bash
# Usuario escribe:
/investigate INC-2024-042

# Claude responde:
🔍 **Investigando INC-2024-042**

**Paso 1: Detalles del incidente**
- Host: WS-FIN-042
- Usuario: john.smith@company.com
- Detección: DET-789 (Suspicious PowerShell)
- Hash: abc123def456...

**Paso 2: Enriquecimiento**
- Intel: VT 58/74, Labels: [trojan, emotet]
- Process Tree: cmd.exe → powershell.exe → malware.exe
- Propagación: 3 hosts (WS-FIN-042, WS-HR-011, WS-MKT-023)
- CTEM Risk: 65/100

**Paso 3: Confidence Score**
| Componente | Score |
|------------|-------|
| Intel | 35/40 |
| Behavior | 25/30 |
| Context | 10/20 |
| Propagation | 5/10 |
| **TOTAL** | **75/100** |

**Paso 4: Policy Engine**
- Score: 75 (>=50, <90)
- Asset: Standard workstation
- **Decisión: Requiere aprobación**

⏳ Solicitando aprobación humana...
```

### Ejemplo 2: Usando Demo

```bash
# Ejecutar escenario VIP
/demo 2

# Claude ejecuta automáticamente:
🎭 **Demo Escenario 2: VIP Laptop**

Iniciando simulación con LAPTOP-CFO-01...

[... proceso completo de investigación ...]

⚠️ **ATENCIÓN: Activo VIP detectado**

El host LAPTOP-CFO-01 tiene tags: [vip, executive]

Aunque el confidence score es 95/100, la política
requiere aprobación humana para activos críticos.

📋 Tarjeta de aprobación enviada al canal SOC.
```

---

## 8. Integración con CyberDemo

El skill está diseñado para funcionar con la infraestructura CyberDemo:

```
CyberDemo/
├── backend/          # FastAPI + MCP Server
├── frontend/         # React + MCP Server
├── mock-server/      # Datos sintéticos
└── extensions/
    └── cyberdemo/    # Plugin SoulInTheBot
        ├── skills/
        │   └── soc-analyst/
        │       └── SKILL.md    # Este skill
        ├── SoulInTheBot.plugin.json
        └── package.json
```

### Levantar el Entorno

```bash
# Opción 1: Docker Compose
cd CyberDemo/docker
docker-compose up -d

# Opción 2: Manual
# Terminal 1 - Backend
cd CyberDemo/backend
uvicorn src.main:app --reload --port 8000

# Terminal 2 - Frontend
cd CyberDemo/frontend
pnpm dev

# Terminal 3 - SoulInTheBot
moltbot gateway run --port 18789
```

---

## 9. Notas Importantes

### Reglas de Oro

1. **NUNCA** contener VIP/server/DC sin aprobación
2. **SIEMPRE** documentar decisiones con comentarios
3. **SIEMPRE** generar postmortem después de contención
4. Si hay duda, **solicitar aprobación humana**
5. Las decisiones de política son **deterministas** (mismo input = mismo output)

### Limitaciones

- El skill usa datos **simulados**, no conecta a EDR/SIEM reales
- Los scores y políticas son **ejemplos educativos**
- Para producción, ajustar umbrales según la organización

### Logs y Auditoría

Todas las acciones se registran en:

- Comentarios del incidente (SIEM)
- Tickets de seguimiento
- Postmortems detallados
- Logs del gateway SoulInTheBot

---

**Documento creado:** 2026-02-13
**Versión:** 1.0
**Skill:** soc-analyst v1.0.0

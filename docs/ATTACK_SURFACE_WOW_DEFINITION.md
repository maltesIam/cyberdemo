# CyberDemo - Cyber Exposure Command Center (Surface WOW) - V2

> **Version:** 2.0  
> **Estado:** Definicion funcional y de diseno completa  
> **Objetivo:** Documento unico de referencia para construir la pagina `/surface`

---

## 1) Objetivo del documento

Consolidar en una sola especificacion funcional y de diseno la pagina principal de visualizacion avanzada de CyberDemo que permita:

- ver activos, incidentes, detecciones, vulnerabilidades y amenazas en una experiencia unificada,
- operar con capas visuales activables/desactivables,
- aplicar filtros y busquedas libres/avanzadas,
- entregar valor operativo real para SOC,
- producir una experiencia visual "wow" para expertos de ciberseguridad,
- navegar sin dead-ends a detalle de cualquier entidad,
- ejecutar acciones directas desde la visualizacion (contener, investigar, ticketear, exportar).

---

## 2) Vision de producto

### 2.1 Nombre funcional

**Cyber Exposure Command Center (Surface WOW)**

### 2.2 Propuesta de valor

- Unifica lo que hoy esta distribuido entre `/assets`, `/incidents`, `/detections`, `/ctem`, `/graph`, `/timeline` y `ThreatEnrichmentPage`.
- Permite analizar riesgo tecnico y riesgo operativo en segundos.
- Hace visible la cadena completa: **asset -> deteccion -> incidente -> vulnerabilidad -> amenaza -> decision**.
- Reduce tiempo de investigacion con filtros de precision y acciones directas.
- Proporciona un "single pane of glass" para el turno SOC.

### 2.3 Principios de experiencia

| Principio                  | Significado                                                                      |
| -------------------------- | -------------------------------------------------------------------------------- |
| **Action-first**           | Cada elemento visual permite actuar (investigar, contener, ticketear, exportar). |
| **Layer-first**            | Toda la experiencia gira sobre capas operativas seleccionables.                  |
| **Evidence-first**         | Todo dato visible es trazable a fuente y timestamp.                              |
| **No dead ends**           | Desde cualquier elemento se puede navegar a detalle.                             |
| **Progressive disclosure** | La densidad visual crece solo cuando el analista lo pide (capas opt-in).         |
| **Performance**            | Canvas fluido a 60fps con 1000+ nodos visibles.                                  |

---

## 3) Layout principal

### 3.1 Wireframe maestro

```
+============================================================================+
| HEADER BAR                                                                  |
| [Logo] Cyber Exposure Command Center     [Search...]  [Presets v] [Export] |
+============================================================================+
|        |                                                                    |
| LAYER  |                     CANVAS CENTRAL                                 |
| PANEL  |                                                                    |
| (left) |   (Modo A: Surface 2D | Modo B: Graph | Modo C: Vuln Landscape    |
|        |    Modo D: Threat Map | Modo E: Timeline)                          |
| [x]Base|                                                                    |
| [x]EDR |                                                                    |
| [x]SIEM|                    +------------------+                            |
| [ ]Vuln|                    |  Nodos / Mapa /  |                            |
| [ ]Thr |                    |  Grafo / Terrain |                            |
| [ ]Cont|                    +------------------+                            |
| [ ]Rel |                                                                    |
|        |                                                                    |
| FILTROS|                                                    DETAIL PANEL    |
| (below)|                                                    (right, slide)  |
|--------|                                                    [Asset/IOC/CVE] |
| Preset:|                                                    [Acciones]      |
| [SOC]  |                                                    [Evidencia]     |
| [Hunt] |                                                                    |
| [Vuln] |                                                                    |
+--------+--------------------------------------------------------------------+
| BOTTOM BAR                                                                  |
| [KPIs: Assets:1000 | Det:45 | Inc:12 | CVE-K:5 | IOC-Hi:23 | Contained:3]|
| [Timeline Slider =====[|]==========]  [1h][6h][24h][7d][Custom]            |
+============================================================================+
```

### 3.2 Zonas funcionales

| Zona               | Posicion                               | Contenido                                                                       |
| ------------------ | -------------------------------------- | ------------------------------------------------------------------------------- |
| **Header Bar**     | Top, fija                              | Titulo, buscador global, selector de preset, boton export, modo visual selector |
| **Layer Panel**    | Left sidebar, colapsable               | Checkboxes de capas, presets rapidos, filtros contextuales                      |
| **Canvas Central** | Centro, ocupa todo el espacio restante | Visualizacion activa segun modo seleccionado                                    |
| **Detail Panel**   | Right sidebar, slide-in                | Aparece al seleccionar un nodo/entidad; muestra detalle + acciones              |
| **Bottom Bar**     | Bottom, fija                           | KPIs en vivo, timeline slider, selector de rango temporal                       |

---

## 4) Modos visuales

### 4.1 Catalogo de modos

| Modo  | Nombre                  | Icono         | Canvas                                                       | Cuando usar                                 |
| ----- | ----------------------- | ------------- | ------------------------------------------------------------ | ------------------------------------------- |
| **A** | Layered Surface 2D      | grid icon     | Nodos posicionados por tipo/red, capas como anillos de color | Vista por defecto. Triage diario.           |
| **B** | Investigation Graph     | graph icon    | Cytoscape.js con relaciones causa-efecto                     | Investigacion profunda de incidente.        |
| **C** | Vulnerability Landscape | mountain icon | Terrain/radial/sunburst de CVEs por severidad                | Sesion de vulnerability management.         |
| **D** | Threat World Map        | globe icon    | Mapa mundi con lineas animadas                               | Threat hunting y respuesta a IOCs.          |
| **E** | Timeline Replay         | clock icon    | Linea temporal con replay                                    | Reconstruccion de incidentes y post-mortem. |

### 4.2 Conmutacion entre modos

- Selector en header: tabs o iconos.
- Transicion animada (fade-out canvas actual 200ms, fade-in nuevo 300ms).
- Las capas activadas y filtros se preservan al cambiar de modo.
- El Detail Panel se cierra al cambiar de modo (excepto si tiene una entidad pinned).

---

## 5) Sistema de capas

### 5.1 Definicion completa de cada capa

#### Capa 1: Base

| Propiedad       | Valor                                                       |
| --------------- | ----------------------------------------------------------- |
| **Color**       | `#6b7280` (gray-500), light: `#9ca3af`, dark: `#4b5563`     |
| **Icono**       | shield                                                      |
| **Fija**        | Si (no desactivable)                                        |
| **Default**     | Activa siempre                                              |
| **Datos**       | Todos los assets del inventario                             |
| **Nodo visual** | Circulo gris con icono de tipo (server/laptop/vm/container) |
| **Hover**       | Tooltip: hostname, ip, tipo, owner, risk_score              |
| **Click**       | Abre Detail Panel con info basica del asset                 |

#### Capa 2: EDR

| Propiedad       | Valor                                                                   |
| --------------- | ----------------------------------------------------------------------- |
| **Color**       | `#ef4444` (red-500), light: `#f87171`, dark: `#dc2626`                  |
| **Icono**       | alert-triangle                                                          |
| **Fija**        | No                                                                      |
| **Default**     | Activa                                                                  |
| **Datos**       | Assets con detecciones activas. Detections count, severity, last alert. |
| **Nodo visual** | Anillo rojo sobre nodo base. Badge con count de detecciones.            |
| **Hover**       | Tooltip: detection count, max severity, ultimo timestamp                |
| **Click**       | Detail Panel: lista de detecciones del asset, link a `/detections/:id`  |

#### Capa 3: SIEM

| Propiedad       | Valor                                                              |
| --------------- | ------------------------------------------------------------------ |
| **Color**       | `#f97316` (orange-500), light: `#fb923c`, dark: `#ea580c`          |
| **Icono**       | flame                                                              |
| **Fija**        | No                                                                 |
| **Default**     | Activa                                                             |
| **Datos**       | Assets implicados en incidentes. Incident count, status, severity. |
| **Nodo visual** | Anillo naranja sobre nodo base. Badge con count de incidentes.     |
| **Hover**       | Tooltip: incident count, max severity, status                      |
| **Click**       | Detail Panel: lista de incidentes, link a `/incidents/:id`         |

#### Capa 4: CTEM

| Propiedad       | Valor                                                                |
| --------------- | -------------------------------------------------------------------- |
| **Color**       | `#eab308` (yellow-500) a `#22c55e` (green-500), gradiente por riesgo |
| **Icono**       | gauge                                                                |
| **Fija**        | No                                                                   |
| **Default**     | Activa                                                               |
| **Datos**       | Exposure score agregado, risk_level, findings_count.                 |
| **Nodo visual** | Halo con gradiente segun risk_level (rojo=critical, verde=low).      |
| **Hover**       | Tooltip: risk_score, risk_level, top findings                        |
| **Click**       | Detail Panel: resumen CTEM, link a `/ctem/assets/:id`                |

#### Capa 5: Vulnerabilidades

| Propiedad                | Valor                                                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Color**                | `#dc2626` (critical) -> `#f97316` (high) -> `#eab308` (medium) -> `#22c55e` (low)                           |
| **Icono**                | bug                                                                                                         |
| **Fija**                 | No                                                                                                          |
| **Default**              | Desactivada                                                                                                 |
| **Datos**                | CVEs individuales: cve_id, cvss, epss, kev, exploit_status, patch_status, vendor, product, affected_assets. |
| **Nodo visual (Modo A)** | Marca sobre asset: cuadrado con color por severidad CVE. Si multiples CVEs, apilados.                       |
| **Nodo visual (Modo C)** | Montana/sector con altura = CVSS, efecto especial si KEV o exploit.                                         |
| **Hover**                | Tooltip: CVE-ID, CVSS, EPSS percentil, KEV si/no, exploit count                                             |
| **Click**                | Detail Panel: ficha completa CVE, link a `/vulnerabilities/cves/:id`                                        |
| **Filtros propios**      | CVSS min/max, EPSS min/max, KEV only, exploit available, patch overdue, vendor/product                      |
| **Acciones**             | Abrir detalle CVE, crear ticket, exportar reporte tecnico                                                   |

#### Capa 6: Amenazas

| Propiedad                | Valor                                                                                                 |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| **Color**                | `#a855f7` (purple-500), light: `#c084fc`, dark: `#9333ea`                                             |
| **Icono**                | crosshair                                                                                             |
| **Fija**                 | No                                                                                                    |
| **Default**              | Desactivada                                                                                           |
| **Datos**                | IOCs: tipo, valor, risk_score, confidence, geo, ASN, threat_actor, malware_family, ATT&CK techniques. |
| **Nodo visual (Modo A)** | Marcas moradas sobre assets vinculados a IOCs. Lineas punteadas entre assets que comparten IOC.       |
| **Nodo visual (Modo D)** | Marcadores en mapa mundi con lineas animadas hacia SOC target.                                        |
| **Hover**                | Tooltip: IOC value, risk_score, actor, malware, pais                                                  |
| **Click**                | Detail Panel: ficha IOC completa, link a `/threats/iocs/:id`                                          |
| **Filtros propios**      | IOC type, risk_score, actor/malware/campana, pais/origen, ATT&CK tactic/technique                     |
| **Acciones**             | Bloquear IOC/IP, abrir investigacion, exportar STIX/MISP                                              |

#### Capa 7: Containment

| Propiedad       | Valor                                                                  |
| --------------- | ---------------------------------------------------------------------- |
| **Color**       | `#3b82f6` (blue-500), light: `#60a5fa`, dark: `#2563eb`                |
| **Icono**       | lock                                                                   |
| **Fija**        | No                                                                     |
| **Default**     | Desactivada                                                            |
| **Datos**       | Estado de contencion: isContained, containedAt, reason, action_result. |
| **Nodo visual** | Borde azul solido sobre nodo. Icono candado en badge.                  |
| **Hover**       | Tooltip: estado, fecha contencion, motivo                              |
| **Click**       | Detail Panel: historial de contencion, acciones para lift/re-contain   |

#### Capa 8: Relaciones

| Propiedad   | Valor                                                                                 |
| ----------- | ------------------------------------------------------------------------------------- |
| **Color**   | `#06b6d4` (cyan-500), light: `#22d3ee`, dark: `#0891b2`                               |
| **Icono**   | network                                                                               |
| **Fija**    | No                                                                                    |
| **Default** | Desactivada                                                                           |
| **Datos**   | Conexiones causa-efecto: lateral_movement, c2_communication, data_exfil, shared_ioc.  |
| **Visual**  | Lineas entre nodos con color por tipo. Animacion de particulas en conexiones activas. |
| **Hover**   | Tooltip sobre linea: tipo, strength, timestamp                                        |
| **Click**   | Resalta path completo; Detail Panel muestra cadena de la relacion                     |

### 5.2 Selector de capas (UX)

#### Patron de control

- **Panel lateral izquierdo** (siempre visible, colapsable a iconos).
- Cada capa: **checkbox + color dot + label + count badge**.
- Encima: **presets rapidos** como chips/botones.
- Abajo: link "Reset to default".

```
+--- LAYERS -------------------+
| [SOC] [Hunt] [Vuln] [Full]  |   <- Presets
|------------------------------|
| [x] * Base         (1000)   |   <- Fija, gris, no desactivable
| [x] * EDR            (45)   |   <- Activa default
| [x] * SIEM           (12)   |   <- Activa default
| [x] * CTEM          (187)   |   <- Activa default
| [ ] * Vulnerabilities (89)  |   <- Opt-in
| [ ] * Amenazas        (23)  |   <- Opt-in
| [ ] * Containment      (3)  |   <- Opt-in
| [ ] * Relaciones      (67)  |   <- Opt-in
|------------------------------|
| 4/8 layers active            |
| [Reset] [Save as preset]    |
+------------------------------+
```

#### Estado por defecto

- **Activas:** Base (fija), EDR, SIEM, CTEM.
- **Desactivadas:** Vulnerabilidades, Amenazas, Containment, Relaciones.

#### Presets rapidos

| Preset                     | Capas activas                      | Caso de uso                              |
| -------------------------- | ---------------------------------- | ---------------------------------------- |
| **SOC Overview** (default) | Base + SIEM + EDR + CTEM           | Triage diario, primera vista del turno   |
| **Threat Hunt**            | Base + Amenazas + Relaciones + EDR | Investigacion proactiva de amenazas      |
| **Vulnerability Ops**      | Base + Vulnerabilidades + CTEM     | Sesion de gestion de vulnerabilidades    |
| **Containment Ops**        | Base + SIEM + EDR + Containment    | Gestion de hosts contenidos y decisiones |
| **Full Investigation**     | Todas (8/8)                        | Investigacion profunda, caso critico     |

#### Reglas de usabilidad

- Persistir seleccion por usuario/sesion (localStorage + backend sync).
- Mostrar contador visible: `X/Y capas activas`.
- Permitir "Reset to default" en un click.
- Guardar presets personalizados por analista.
- En mobile/tablet, usar drawer full-height con checkboxes.
- Animacion al activar/desactivar: fade-in 200ms (mostrar), fade-out 150ms (ocultar).
- Al activar una capa de alta densidad (Vulnerabilidades, Amenazas, Relaciones), mostrar toast informativo con count de elementos que se anaden al canvas.

---

## 6) Modelo de datos funcional

### 6.1 Entidades principales

| Entidad                 | Campos clave                                                                                                | Origen                         |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------ |
| **Asset**               | id, hostname, ip, mac, tipo, os, owner, departamento, site, tags, criticidad, risk_score, estado, last_seen | `/assets`                      |
| **Detection (EDR)**     | id, severidad, confidence, hash, proceso, host_id, timestamp, mitre_technique                               | `/edr/detections`              |
| **Incident (SIEM)**     | id, titulo, severidad, estado, entidades, comentarios, timeline, created_at                                 | `/siem/incidents`              |
| **CTEM Exposure**       | asset_id, risk_score, risk_level, findings_count, top_findings                                              | `/ctem/assets/:id`             |
| **Vulnerability (CVE)** | cve_id, cvss, epss, kev, exploit_count, patch_status, vendor, product, description, affected_assets         | `/vulnerabilities`             |
| **Threat IOC**          | id, tipo, valor, risk_score, confidence, geo, asn, threat_actor, malware_family, mitre_techniques, feeds    | `/threats`                     |
| **Containment Action**  | host_id, accion, resultado, motivo, timestamp, actor                                                        | `/edr/devices/:id/containment` |

### 6.2 Relaciones

```
Asset --1:N--> Detection (EDR)
Asset --1:N--> Incident (SIEM)      (via entities)
Asset --1:1--> CTEM Exposure
Asset --1:N--> Vulnerability (CVE)  (via affected software)
Asset --M:N--> Threat IOC           (directo o via incident)
Incident --M:N--> Threat IOC
Incident --1:N--> Containment Action
Detection --M:N--> Threat IOC       (hashes, IPs en proceso)
Vulnerability --M:N--> Asset        (affected_assets)
```

### 6.3 KPIs globales

| KPI                          | Fuente                                                | Actualizacion |
| ---------------------------- | ----------------------------------------------------- | ------------- |
| Total assets                 | `/assets` count                                       | Cada 30s      |
| Assets criticos (risk >= 80) | `/assets?risk_min=80` count                           | Cada 30s      |
| Detecciones activas          | `/edr/detections?status=active` count                 | Cada 15s      |
| Incidentes abiertos          | `/siem/incidents?status=open` count                   | Cada 15s      |
| Incidentes criticos          | `/siem/incidents?severity=critical&status=open` count | Cada 15s      |
| Hosts contenidos             | Count de containment activos                          | Cada 30s      |
| CVEs criticas                | `/vulnerabilities?cvss_min=9` count                   | Cada 60s      |
| CVEs KEV                     | `/vulnerabilities?kev=true` count                     | Cada 60s      |
| IOCs alto riesgo             | `/threats?risk_min=80` count                          | Cada 30s      |
| MTTD / MTTR                  | Calculado de incidents timeline                       | Cada 60s      |

---

## 7) Filtros, busqueda y exploracion

### 7.1 Filtros globales (afectan a todas las capas)

| Filtro             | Tipo de control              | Valores                                           |
| ------------------ | ---------------------------- | ------------------------------------------------- |
| Rango temporal     | Chips + date picker          | 1h, 6h, 12h, 24h, 7d, 30d, custom                 |
| Tipo de activo     | Multi-select chips           | server, workstation, laptop, vm, container, other |
| Criticidad activo  | Slider range                 | 0-100 (o badges: Low/Med/High/Critical)           |
| Owner/Departamento | Searchable dropdown          | Valores de assets                                 |
| Site/Ubicacion     | Searchable dropdown          | Valores de assets                                 |
| Severidad          | Multi-select chips           | critical, high, medium, low, informational        |
| Estado             | Multi-select chips           | open, investigating, contained, resolved, closed  |
| Tags               | Tag input con autocompletado | Valores de assets                                 |

### 7.2 Filtros por capa (se muestran al activar la capa)

| Capa             | Filtros especificos                                                                     |
| ---------------- | --------------------------------------------------------------------------------------- |
| Vulnerabilidades | CVSS min/max, EPSS min/max, KEV only, exploit available, patch overdue, vendor, product |
| Amenazas         | IOC type, risk_score min, actor, malware, campana, pais, ATT&CK tactic/technique        |
| Containment      | Estado (contained/lifted), fecha contencion                                             |
| Relaciones       | Tipo (lateral_movement, c2, exfil, shared_ioc), strength min                            |

### 7.3 Buscador global

- Input siempre visible en header.
- Soporte para: hostname, ip, cve-id, hash (md5/sha1/sha256), dominio, actor, malware, ticket-id.
- Autodeteccion de tipo de busqueda.
- Autosuggest con resultados agrupados por tipo.
- Al seleccionar resultado: navega al nodo en canvas y abre Detail Panel.
- Resaltado visual (highlight/glow) del nodo encontrado.
- Shortcut: `Ctrl+K` o `/` para enfocar buscador.

### 7.4 Query builder avanzado

- Accesible desde icono junto al buscador.
- Condiciones combinables: AND / OR / NOT.
- Ejemplo: `severity:critical AND kev:true AND asset.department:Finance`.
- Guardado de queries favoritas.
- Presets SOC: "CVEs criticas con exploit en activo VIP", "IOCs de alto riesgo de Rusia ultimas 24h".

---

## 8) Diseno visual WOW

### 8.1 Paleta de colores

| Elemento         | Color (hex)                | Uso                          |
| ---------------- | -------------------------- | ---------------------------- |
| Fondo principal  | `#0f172a` (slate-900)      | Canvas background            |
| Fondo paneles    | `#1e293b` (slate-800)      | Sidebars, cards              |
| Bordes           | `#334155` (slate-700)      | Separadores, bordes de cards |
| Texto principal  | `#f1f5f9` (slate-100)      | Titulos, datos               |
| Texto secundario | `#94a3b8` (slate-400)      | Labels, metadata             |
| Acento primario  | `#06b6d4` (cyan-500)       | Acciones principales, links  |
| Grid canvas      | `#1e293b` con 10% opacidad | Fondo cuadricula             |

### 8.2 Tipografia

- Titulos: `Inter`, semibold.
- Datos/monospace: `JetBrains Mono` o `Fira Code`.
- Tamanos: Header 20px, Section 16px, Body 14px, Badge 11px, Micro 10px.

### 8.3 Efectos wow operativos

| Efecto                   | Donde                                  | Como                                                          |
| ------------------------ | -------------------------------------- | ------------------------------------------------------------- |
| **Glow pulsante**        | Nodos con incidentes criticos          | Box-shadow animado 1Hz, color de la capa                      |
| **Particulas en lineas** | Capa Relaciones (conexiones activas)   | CSS offset-path animation 200-300ms loop                      |
| **Radar sweep**          | SOC target en Modo D (Threat Map)      | 3 circulos concentricos expandiendose, loop 2s                |
| **Shake suave**          | Nodo con CVE KEV activo                | transform:translate randomizado 2px, 0.5s                     |
| **Count-up animado**     | KPIs en Bottom Bar                     | Transicion numerica de 0 a valor en 600ms                     |
| **Gradient pulse**       | Halo CTEM en nodos de alto riesgo      | Gradient animado green->red 3s loop                           |
| **Lineas de ataque**     | Modo D: origenes de amenazas hacia SOC | Bezier curves con particulas, velocidad proporcional a riesgo |

### 8.4 Interacciones premium

| Interaccion          | Resultado                                                                      |
| -------------------- | ------------------------------------------------------------------------------ |
| **Hover nodo**       | Tooltip rico (250ms delay). Nodo escala 110%. Conexiones del nodo se resaltan. |
| **Click nodo**       | Abre Detail Panel derecho con contexto completo y acciones.                    |
| **Doble click nodo** | Focus: canvas centra y hace zoom al nodo, dimma el resto.                      |
| **Right-click nodo** | Context menu: Investigate, Contain, Create Ticket, Copy ID, Export.            |
| **Brush/Lasso**      | Seleccion multiple. Bottom bar muestra stats agregados de seleccion.           |
| **Scroll**           | Zoom in/out fluido (10 niveles).                                               |
| **Drag canvas**      | Pan.                                                                           |
| **Pinch (touch)**    | Zoom tactil.                                                                   |
| **Ctrl+click**       | Anade a seleccion multiple.                                                    |

### 8.5 Zoom semantico

| Nivel           | Nombre    | Que se ve                                                       |
| --------------- | --------- | --------------------------------------------------------------- |
| **1 (lejano)**  | Clustered | Clusters por tipo/departamento/site. Counts agregados.          |
| **2 (medio)**   | Grouped   | Nodos individuales con tamanio por riesgo. Sin labels.          |
| **3 (cercano)** | Detailed  | Nodos con labels, badges, anillos de capas, tooltips completos. |

Transicion entre niveles: automatica por wheel/pinch, con smooth animation 300ms.

---

## 9) Detail Panel (sidebar derecho)

### 9.1 Estructura del panel

```
+--- DETAIL PANEL (360px) ------+
| [Pin] [Close X]              |
| ASSET: WS-FIN-042            |
|-------------------------------|
| BASIC INFO                    |
| Hostname: ws-fin-042          |
| IP: 10.0.12.42               |
| Type: Workstation             |
| OS: Windows 11 Enterprise     |
| Owner: John Doe (Finance)     |
| Risk: [===== 75 HIGH ====]   |
|-------------------------------|
| ACTIVE LAYERS ON THIS ASSET  |
|                               |
| * EDR (3 detections)         |
|   - Cobalt Strike (critical) |
|   - PowerShell enc (high)    |
|   [View all detections ->]   |
|                               |
| * SIEM (1 incident)          |
|   - INC-001 (critical, open) |
|   [Open incident ->]         |
|                               |
| * CTEM (risk: 82)            |
|   - 5 CVEs (2 critical)     |
|   [View exposure ->]         |
|                               |
| * Containment: CONTAINED     |
|   Since: 2026-02-15 14:23    |
|   [Lift containment]         |
|-------------------------------|
| ACTIONS                       |
| [Investigate] [Contain]      |
| [Create Ticket] [Export]     |
+-------------------------------+
```

### 9.2 Comportamiento

- Se abre desde la derecha con slide-in 250ms.
- Se cierra al clickar en background o boton X.
- Se puede "pinear" para mantenerlo abierto al navegar.
- Adapta contenido segun tipo de entidad: Asset, CVE, IOC, Incident.
- Links internos navegan a las paginas de detalle existentes.

---

## 10) Bottom Bar (KPIs + Timeline)

### 10.1 Layout

```
+============================================================================+
| [Assets:1000] [Det:45!] [Inc:12!] [Crit:5!!] [CVE-K:5] [IOC:23] [Cont:3]|
| [===========[|]===============]  [1h][6h][24h][7d][Custom] [> Play]       |
+============================================================================+
```

### 10.2 KPIs en vivo

- Cada KPI es un chip clickeable que filtra el canvas.
- Los KPIs con cambios recientes parpadean brevemente.
- Colores: rojo para critical, naranja para high, gris para informational.

### 10.3 Timeline slider

- Rango: desde 1 hora hasta 30 dias atras.
- Marcas en slider: eventos relevantes (incidentes, contencion).
- Boton Play: anima la evolucion temporal en el canvas (replay).
- Speed control: 1x, 2x, 5x, 10x.

---

## 11) Paginas y rutas

### 11.1 Ruta principal

| Ruta                     | Componente    | Descripcion                               |
| ------------------------ | ------------- | ----------------------------------------- |
| `/surface`               | `SurfacePage` | Command Center unificado (Modo A default) |
| `/surface?mode=graph`    | `SurfacePage` | Modo B: Investigation Graph               |
| `/surface?mode=vulns`    | `SurfacePage` | Modo C: Vulnerability Landscape           |
| `/surface?mode=threats`  | `SurfacePage` | Modo D: Threat World Map                  |
| `/surface?mode=timeline` | `SurfacePage` | Modo E: Timeline Replay                   |

### 11.2 Paginas de detalle (existentes, enlazadas desde Detail Panel)

- `/assets/:id`, `/incidents/:id`, `/detections/:id`
- `/ctem/assets/:id`, `/vulnerabilities/cves/:id`, `/threats/iocs/:id`
- `/graph/:incidentId`

---

## 12) Backend y endpoints

### 12.1 Endpoints existentes reutilizados

- `/assets`, `/assets/{id}`, `/assets/{id}/detections`, `/assets/{id}/vulnerabilities`
- `/edr/detections`, `/edr/detections/{id}`, `/edr/detections/{id}/process-tree`
- `/siem/incidents`, `/siem/incidents/{id}`, `/siem/incidents/{id}/entities`
- `/ctem/assets/{id}`, `/ctem/assets/{id}/findings`

### 12.2 Endpoints nuevos necesarios

| Endpoint                    | Metodo | Descripcion                                              |
| --------------------------- | ------ | -------------------------------------------------------- |
| `/surface/overview`         | GET    | KPIs agregados para Bottom Bar                           |
| `/surface/nodes`            | GET    | Assets enriquecidos con layer data (paginado, filtrable) |
| `/surface/connections`      | GET    | Relaciones entre assets para capa Relaciones             |
| `/vulnerabilities`          | GET    | Lista de CVEs con filtros (cvss, epss, kev, vendor)      |
| `/vulnerabilities/cves/:id` | GET    | Detalle CVE completo                                     |
| `/vulnerabilities/summary`  | GET    | Stats agregados de vulnerabilidades                      |
| `/threats`                  | GET    | Lista de IOCs con filtros                                |
| `/threats/iocs/:id`         | GET    | Detalle IOC completo                                     |
| `/threats/map`              | GET    | Datos para mapa mundi (geo aggregations)                 |
| `/threats/actors/:name`     | GET    | Detalle de threat actor                                  |
| `/threats/mitre`            | GET    | Cobertura ATT&CK                                         |

### 12.3 Endpoint Surface Nodes (especificacion)

```
GET /surface/nodes?page=1&page_size=200&time_range=24h&type=server&risk_min=60

Response:
{
  "total": 1000,
  "nodes": [
    {
      "id": "asset-001",
      "hostname": "ws-fin-042",
      "ip": "10.0.12.42",
      "type": "workstation",
      "risk_score": 75,
      "position": { "x": 120, "y": 340 },
      "layers": {
        "base": true,
        "edr": { "active": true, "detection_count": 3, "max_severity": "critical" },
        "siem": { "active": true, "incident_count": 1, "status": "open" },
        "ctem": { "active": true, "risk_level": "high", "findings_count": 5 },
        "vulnerabilities": { "active": true, "cve_count": 5, "critical_count": 2, "kev_count": 1 },
        "threats": { "active": true, "ioc_count": 2, "actors": ["APT29"] },
        "containment": { "active": true, "is_contained": true, "contained_at": "2026-02-15T14:23:00Z" }
      }
    }
  ]
}
```

---

## 13) Flujo operativo SOC

### 13.1 Flujo diario (turno SOC)

1. Entrar en `/surface` (preset SOC Overview activo).
2. Bottom Bar muestra KPIs. Verificar anomalias en numeros.
3. Canvas muestra nodos con capas SIEM + EDR + CTEM.
4. Nodos con glow critico llaman atencion inmediata.
5. Click en nodo critico: Detail Panel muestra contexto.
6. Activar capa Vulnerabilidades para ver CVEs del asset.
7. Activar capa Amenazas para ver IOCs relacionados.
8. Decision: Contain / Investigate / Ticket.
9. Ejecutar accion desde Detail Panel.
10. Export reporte de sesion.

### 13.2 Flujo de threat hunting

1. Entrar en `/surface` con preset Threat Hunt.
2. Activar Modo D (Threat Map).
3. Identificar origenes de alto riesgo.
4. Click en pais: ver IOCs.
5. Cambiar a Modo A: ver assets afectados.
6. Activar capa Relaciones: ver movimiento lateral.
7. Drill-down, contener si necesario.

### 13.3 Flujo de vulnerability management

1. Entrar en `/surface` con preset Vulnerability Ops.
2. Activar Modo C (Vulnerability Landscape).
3. Ordenar por CVSS + KEV + EPSS.
4. Priorizar top CVEs con assets criticos.
5. Crear tickets de parcheo desde Detail Panel.
6. Export reporte tecnico.

---

## 14) Criterios de exito

### 14.1 Funcionalidad

- [ ] 8 capas activables sin inconsistencias.
- [ ] 5 modos visuales conmutables con preservacion de estado.
- [ ] Filtros globales y por capa responden en < 300ms.
- [ ] Busqueda libre con autosuggest funcional.
- [ ] Detail Panel para cada tipo de entidad.
- [ ] Acciones directas desde Detail Panel (contain, ticket, export).
- [ ] KPIs en vivo con actualizacion periodica.
- [ ] Timeline slider con replay funcional.

### 14.2 Valor operativo

- [ ] Tiempo de triage reducido (toda la info en una vista).
- [ ] Cadena causa-efecto visible en < 3 clicks.
- [ ] Capacidad de priorizar con riesgo real (CTEM + threat intel + CVE).

### 14.3 Efecto wow

- [ ] Impresion visual fuerte en el primer minuto.
- [ ] Claridad bajo alta densidad de datos.
- [ ] Sensacion de control y confianza para analista senior.
- [ ] Animaciones con sentido operativo (glow, particulas, radar).

### 14.4 Performance

- [ ] Canvas fluido (60fps) con 1000 nodos.
- [ ] Cambio de modo en < 500ms.
- [ ] Filtros en < 300ms.
- [ ] Detail Panel en < 200ms.

---

## 15) Estado actual vs objetivo

### 15.1 Ya disponible (base util)

- Componentes `AttackSurfaceLayers`, `LayerToggle`, `TimeSlider` (4 capas basicas).
- Pagina `/assets` con toggle simple de capas en tabla.
- `GraphPage` con Cytoscape.js (Modo B parcial).
- `ThreatEnrichmentPage` con mapa y tabla de IOCs (Modo D parcial).
- Vistas de detalle: `/incidents`, `/detections`, `/ctem`, `/timeline`.
- Tipos y constantes de capas definidos en `components/AttackSurface/types.ts`.

### 15.2 Gap a cerrar

- Crear pagina `/surface` como entry point unificado.
- Evolucionar canvas de nodos con las 8 capas completas.
- Integrar 5 modos visuales conmutables.
- Implementar capas dedicadas Vulnerabilidades y Amenazas.
- Construir endpoints `/surface/overview`, `/surface/nodes`, `/surface/connections`.
- Implementar filtros globales + por capa + busqueda global.
- Construir Detail Panel universal.
- Implementar Bottom Bar con KPIs y timeline slider con replay.
- Implementar zoom semantico y efectos wow.
- Conectar acciones directas (contain, ticket, export) desde Detail Panel.

---

## 16) Resultado esperado

Un Command Center unico que combina:

- utilidad real para SOC (triage, investigacion, decision),
- investigacion de extremo a extremo basada en evidencia,
- y una visualizacion memorable, moderna y espectacular.

Este documento V2 es la referencia unica para construir la pagina `/surface` de CyberDemo.

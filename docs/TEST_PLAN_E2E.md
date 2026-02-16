# Plan de Pruebas E2E - CyberDemo SOC Analyst

**Fecha:** 2026-02-15
**Version:** 1.0
**Estado:** COMPLETADO

---

## 1. Objetivo

Verificar que todas las paginas de la aplicacion CyberDemo:

1. Cargan correctamente sin errores
2. No muestran paginas en blanco
3. Muestran los elementos esperados
4. Las funcionalidades interactivas funcionan correctamente

---

## 2. Alcance

### 2.1 Paginas a probar (13 total)

| #   | Ruta         | Pagina          | Funcionalidades a verificar                 |
| --- | ------------ | --------------- | ------------------------------------------- |
| 1   | /generation  | GenerationPage  | Controles de generacion, botones, estado    |
| 2   | /dashboard   | DashboardPage   | Metricas, graficos, botones enriquecimiento |
| 3   | /assets      | AssetsPage      | Tabla de assets, capas, filtros             |
| 4   | /incidents   | IncidentsPage   | Lista incidentes, filtros, detalles         |
| 5   | /detections  | DetectionsPage  | Tabla detecciones, severidad, acciones      |
| 6   | /timeline    | TimelinePage    | Timeline eventos, filtros, detalles         |
| 7   | /postmortems | PostmortemsPage | Lista postmortems, busqueda, detalles       |
| 8   | /tickets     | TicketsPage     | Tabla tickets, estados, prioridades         |
| 9   | /ctem        | CTEMPage        | Vulnerabilidades, riesgos, busqueda         |
| 10  | /graph       | GraphPage       | Grafo interactivo, nodos, conexiones        |
| 11  | /collab      | CollabPage      | Chat, mensajes, input                       |
| 12  | /config      | ConfigPage      | Formularios, toggles, guardado              |
| 13  | /audit       | AuditPage       | Tabla auditoria, filtros, export            |

### 2.2 Tipos de pruebas

1. **Carga de pagina**: Verificar que la pagina carga sin errores
2. **Elementos visibles**: Verificar que los elementos clave estan presentes
3. **Interacciones basicas**: Click en botones, filtros, navegacion
4. **Formularios**: Entrada de datos, validacion, submit
5. **Tablas/Listas**: Renderizado de datos, paginacion, ordenacion

---

## 3. Criterios de exito

- [x] Todas las 13 paginas cargan sin errores
- [x] Ninguna pagina muestra contenido en blanco
- [x] Los elementos principales de cada pagina son visibles
- [x] Las interacciones basicas funcionan correctamente
- [x] No hay errores de consola criticos

---

## 4. Detalle de pruebas por pagina

### 4.1 GenerationPage (/generation)

| Test ID | Descripcion                       | Resultado |
| ------- | --------------------------------- | --------- |
| GEN-001 | Pagina carga sin errores          | PASS      |
| GEN-002 | Titulo "Generation" visible       | PASS      |
| GEN-003 | Controles de generacion presentes | PASS      |
| GEN-004 | Boton "Generate" funcional        | PASS      |

### 4.2 DashboardPage (/dashboard)

| Test ID  | Descripcion                         | Resultado |
| -------- | ----------------------------------- | --------- |
| DASH-001 | Pagina carga sin errores            | PASS      |
| DASH-002 | Titulo "Dashboard" visible          | PASS      |
| DASH-003 | Cards de metricas presentes         | PASS      |
| DASH-004 | Botones de enriquecimiento visibles | PASS      |

### 4.3 AssetsPage (/assets)

| Test ID   | Descripcion                | Resultado |
| --------- | -------------------------- | --------- |
| ASSET-001 | Pagina carga sin errores   | PASS      |
| ASSET-002 | Titulo "Assets" visible    | PASS      |
| ASSET-003 | Tabla de assets presente   | PASS      |
| ASSET-004 | Toggles de capas funcionan | PASS      |

### 4.4 IncidentsPage (/incidents)

| Test ID | Descripcion                  | Resultado |
| ------- | ---------------------------- | --------- |
| INC-001 | Pagina carga sin errores     | PASS      |
| INC-002 | Titulo "Incidents" visible   | PASS      |
| INC-003 | Lista de incidentes presente | PASS      |
| INC-004 | Filtros de estado funcionan  | PASS      |

### 4.5 DetectionsPage (/detections)

| Test ID | Descripcion                       | Resultado |
| ------- | --------------------------------- | --------- |
| DET-001 | Pagina carga sin errores          | PASS      |
| DET-002 | Titulo "Detections" visible       | PASS      |
| DET-003 | Tabla de detecciones presente     | PASS      |
| DET-004 | Indicadores de severidad visibles | PASS      |

### 4.6 TimelinePage (/timeline)

| Test ID  | Descripcion                    | Resultado |
| -------- | ------------------------------ | --------- |
| TIME-001 | Pagina carga sin errores       | PASS      |
| TIME-002 | Titulo "Timeline" visible      | PASS      |
| TIME-003 | Eventos del timeline presentes | PASS      |
| TIME-004 | Filtros de tipo funcionan      | PASS      |

### 4.7 PostmortemsPage (/postmortems)

| Test ID  | Descripcion                   | Resultado |
| -------- | ----------------------------- | --------- |
| POST-001 | Pagina carga sin errores      | PASS      |
| POST-002 | Titulo "Postmortems" visible  | PASS      |
| POST-003 | Lista de postmortems presente | PASS      |
| POST-004 | Busqueda funciona             | PASS      |

### 4.8 TicketsPage (/tickets)

| Test ID  | Descripcion                 | Resultado |
| -------- | --------------------------- | --------- |
| TICK-001 | Pagina carga sin errores    | PASS      |
| TICK-002 | Titulo "Tickets" visible    | PASS      |
| TICK-003 | Tabla de tickets presente   | PASS      |
| TICK-004 | Estados de tickets visibles | PASS      |

### 4.9 CTEMPage (/ctem)

| Test ID  | Descripcion                        | Resultado |
| -------- | ---------------------------------- | --------- |
| CTEM-001 | Pagina carga sin errores           | PASS      |
| CTEM-002 | Titulo "CTEM" visible              | PASS      |
| CTEM-003 | Lista de vulnerabilidades presente | PASS      |
| CTEM-004 | Indicadores de riesgo visibles     | PASS      |

### 4.10 GraphPage (/graph)

| Test ID   | Descripcion                   | Resultado |
| --------- | ----------------------------- | --------- |
| GRAPH-001 | Pagina carga sin errores      | PASS      |
| GRAPH-002 | Titulo "Graph" visible        | PASS      |
| GRAPH-003 | Contenedor del grafo presente | PASS      |
| GRAPH-004 | Controles de zoom visibles    | PASS      |

### 4.11 CollabPage (/collab)

| Test ID    | Descripcion                    | Resultado |
| ---------- | ------------------------------ | --------- |
| COLLAB-001 | Pagina carga sin errores       | PASS      |
| COLLAB-002 | Titulo "Collaboration" visible | PASS      |
| COLLAB-003 | Area de chat presente          | PASS      |
| COLLAB-004 | Input de mensaje funcional     | PASS      |

### 4.12 ConfigPage (/config)

| Test ID    | Descripcion                          | Resultado |
| ---------- | ------------------------------------ | --------- |
| CONFIG-001 | Pagina carga sin errores             | PASS      |
| CONFIG-002 | Titulo "Configuration" visible       | PASS      |
| CONFIG-003 | Secciones de configuracion presentes | PASS      |
| CONFIG-004 | Toggles funcionan                    | PASS      |

### 4.13 AuditPage (/audit)

| Test ID   | Descripcion                 | Resultado |
| --------- | --------------------------- | --------- |
| AUDIT-001 | Pagina carga sin errores    | PASS      |
| AUDIT-002 | Titulo "Audit" visible      | PASS      |
| AUDIT-003 | Tabla de auditoria presente | PASS      |
| AUDIT-004 | Filtros funcionan           | PASS      |
| AUDIT-005 | Export button exists        | PASS      |

---

## 5. Pruebas Adicionales

### 5.1 Navegacion

| Test ID | Descripcion                      | Resultado |
| ------- | -------------------------------- | --------- |
| NAV-001 | Sidebar navigation works         | PASS      |
| NAV-002 | All routes are accessible        | PASS      |
| NAV-003 | Invalid routes redirect properly | PASS      |

### 5.2 Responsive Design

| Test ID  | Descripcion                        | Resultado |
| -------- | ---------------------------------- | --------- |
| RESP-001 | Mobile viewport works (375x667)    | PASS      |
| RESP-002 | Tablet viewport works (768x1024)   | PASS      |
| RESP-003 | Desktop viewport works (1920x1080) | PASS      |

---

## 6. Entorno de pruebas

- **Frontend URL:** http://localhost:3000
- **Backend URL:** http://localhost:8000
- **Framework:** Playwright
- **Navegadores:** Chromium

---

## 7. Ejecucion

```bash
cd CyberDemo/frontend
pnpm exec playwright test tests/e2e/all-pages.spec.ts --project=chromium
```

---

## 8. Pruebas de Generación de Datos

### 8.1 Botones de Generación

| Test ID     | Descripcion                                        | Resultado |
| ----------- | -------------------------------------------------- | --------- |
| GEN-BTN-001 | Generate All button exists and clickable           | PASS      |
| GEN-BTN-002 | Generate Assets button exists and clickable        | PASS      |
| GEN-BTN-003 | Generate EDR button exists and clickable           | PASS      |
| GEN-BTN-004 | Reset All Data button exists and clickable         | PASS      |
| GEN-BTN-005 | Random seed input exists                           | PASS      |
| GEN-BTN-006 | Generate Incidents button exists and clickable     | PASS      |
| GEN-BTN-007 | Generate Postmortems button exists and clickable   | PASS      |
| GEN-BTN-008 | Generate Tickets button exists and clickable       | PASS      |
| GEN-BTN-009 | Generate Agent Actions button exists and clickable | PASS      |

### 8.2 Generación de Datos

| Test ID      | Descripcion                                | Resultado |
| ------------ | ------------------------------------------ | --------- |
| GEN-DATA-001 | Generate EDR works without error           | PASS      |
| GEN-DATA-002 | Generate Assets works without error        | PASS      |
| GEN-DATA-003 | Generate All works without error           | PASS      |
| GEN-DATA-004 | Data status section shows counts           | PASS      |
| GEN-DATA-005 | Generate Incidents works without error     | PASS      |
| GEN-DATA-006 | Generate Postmortems works without error   | PASS      |
| GEN-DATA-007 | Generate Tickets works without error       | PASS      |
| GEN-DATA-008 | Generate Agent Actions works without error | PASS      |

### 8.3 Manejo de Errores

| Test ID     | Descripcion                         | Resultado |
| ----------- | ----------------------------------- | --------- |
| GEN-ERR-001 | Page handles API errors gracefully  | PASS      |
| GEN-ERR-002 | Page shows error message on failure | PASS      |

### 8.4 UI de Generación

| Test ID    | Descripcion                         | Resultado |
| ---------- | ----------------------------------- | --------- |
| GEN-UI-001 | Data status cards display correctly | PASS      |
| GEN-UI-002 | Configuration section present       | PASS      |
| GEN-UI-003 | Actions section has all buttons     | PASS      |
| GEN-UI-004 | Page header displays correctly      | PASS      |

### 8.5 API de Generación

| Test ID     | Descripcion                             | Resultado |
| ----------- | --------------------------------------- | --------- |
| GEN-API-001 | Status endpoint returns data            | PASS      |
| GEN-API-002 | EDR generation endpoint works           | PASS      |
| GEN-API-003 | Assets generation endpoint works        | PASS      |
| GEN-API-004 | Incidents generation endpoint works     | PASS      |
| GEN-API-005 | Health endpoint returns info            | PASS      |
| GEN-API-006 | Postmortems generation endpoint works   | PASS      |
| GEN-API-007 | Tickets generation endpoint works       | PASS      |
| GEN-API-008 | Agent Actions generation endpoint works | PASS      |

### 8.6 Navegacion desde Data Status Cards

| Test ID     | Descripcion                                                  | Resultado |
| ----------- | ------------------------------------------------------------ | --------- |
| GEN-NAV-001 | Assets card navigates to /assets page                        | PASS      |
| GEN-NAV-002 | Incidents card navigates to /incidents page                  | PASS      |
| GEN-NAV-003 | Detections card navigates to /detections page                | PASS      |
| GEN-NAV-004 | Postmortems card navigates to /postmortems page              | PASS      |
| GEN-NAV-005 | Tickets card navigates to /tickets page                      | PASS      |
| GEN-NAV-006 | Agent Actions card navigates to /audit page                  | PASS      |
| GEN-NAV-007 | All data status cards are clickable with proper hover states | PASS      |

### 8.7 Dashboard Charts y Widgets

| Test ID        | Descripcion                                            | Resultado |
| -------------- | ------------------------------------------------------ | --------- |
| DASH-CHART-001 | Incidents by Hour chart container exists               | PASS      |
| DASH-CHART-002 | Incidents by Hour shows actual chart (not placeholder) | PASS      |
| DASH-CHART-003 | Incidents by Hour displays bars or chart elements      | PASS      |
| DASH-CHART-004 | Incidents by Hour shows hour labels                    | PASS      |
| DASH-CHART-005 | Severity Distribution section exists                   | PASS      |
| DASH-CHART-006 | Severity Distribution shows severity levels            | PASS      |
| DASH-CHART-007 | Severity Distribution shows progress bars              | PASS      |
| DASH-CHART-008 | Severity Distribution shows percentages                | PASS      |
| DASH-CHART-009 | Top Affected Hosts section exists                      | PASS      |
| DASH-CHART-010 | Top Affected Hosts shows host data                     | PASS      |
| DASH-CHART-011 | Top Affected Hosts shows numbered list                 | PASS      |
| DASH-CHART-012 | Detection Trend section exists                         | PASS      |
| DASH-CHART-013 | Detection Trend shows actual chart (not placeholder)   | PASS      |
| DASH-CHART-014 | Detection Trend displays chart elements                | PASS      |
| DASH-CHART-015 | Detection Trend shows day labels                       | PASS      |
| DASH-CHART-016 | Total Incidents KPI card shows number                  | PASS      |
| DASH-CHART-017 | Critical Open KPI card shows number                    | PASS      |
| DASH-CHART-018 | Hosts Contained KPI card exists                        | PASS      |
| DASH-CHART-019 | MTTR KPI card shows time value                         | PASS      |
| DASH-API-001   | Dashboard KPIs endpoint returns data                   | PASS      |
| DASH-API-002   | Dashboard KPIs has incidents_by_hour data              | PASS      |
| DASH-API-003   | Dashboard KPIs has detection_trend data                | PASS      |

---

## 9. Resumen Final

| Metrica             | Valor |
| ------------------- | ----- |
| Total Tests E2E     | 119   |
| Tests Pasados       | 119   |
| Tests Fallidos      | 0     |
| Tasa de Exito       | 100%  |
| Paginas Verificadas | 13/13 |
| Tiempo Ejecucion    | 18.9s |

---

**Estado:** COMPLETADO
**Fecha Verificacion:** 2026-02-16
**Verificado Por:** Claude - Automatizado

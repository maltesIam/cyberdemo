# Plan de Construccion - Cyber Exposure Command Center (Surface WOW)

> **Documento de referencia:** `ATTACK_SURFACE_WOW_DEFINITION.md` (V2)  
> **Modelo de ejecucion:** 5 agentes de construccion en paralelo + 1 agente validador  
> **Regla de oro:** NADA se marca como completado sin validacion del Agente V

---

## 1) Roles de agentes

### Agentes de construccion

| Agente | Nombre                  | Responsabilidad                                             |
| ------ | ----------------------- | ----------------------------------------------------------- |
| **A1** | Backend Surface         | Endpoints nuevos, aggregations, datos para canvas           |
| **A2** | Frontend Core           | Pagina `/surface`, layout, canvas, selector de capas, modos |
| **A3** | Frontend Capas          | Implementacion visual de las 8 capas + efectos wow          |
| **A4** | Frontend Paneles        | Detail Panel, Bottom Bar, filtros, busqueda, acciones       |
| **A5** | Tests E2E + Integracion | Tests de cada funcionalidad, tests de rendimiento           |

### Agente validador

| Agente | Nombre    | Responsabilidad                                                     |
| ------ | --------- | ------------------------------------------------------------------- |
| **V**  | Validador | Verificacion completa de que lo construido cumple con la definicion |

---

## 2) Reglas del Agente V (Validador)

### 2.1 Cuando actua

- Cada vez que un agente A1-A5 declara que una tarea esta completada.
- Al final de cada iteracion.
- Antes de cerrar cualquier fase.

### 2.2 Que verifica (checklist obligatorio)

Para CADA tarea marcada como completada, el Agente V debe:

1. **Leer la definicion** en `ATTACK_SURFACE_WOW_DEFINITION.md` de la funcionalidad correspondiente.
2. **Localizar el codigo** en el repositorio que implementa esa funcionalidad.
3. **Verificar en el codigo** que:
   - El archivo existe.
   - El componente/endpoint/test existe con el nombre correcto.
   - La logica implementada cubre TODOS los requisitos de la definicion (no solo una parte).
   - Los tipos y contratos de datos coinciden con la definicion.
4. **Ejecutar los tests** relacionados y verificar que pasan.
5. **Verificar la integracion** (la funcionalidad esta conectada a la app, no es codigo muerto).
6. **Comparar contra la definicion** punto por punto.

### 2.3 Que NO puede hacer el Agente V

- NO puede marcar como completado algo sin haber verificado en el codigo.
- NO puede confiar en la declaracion del agente constructor ("dice que esta hecho").
- NO puede asumir que un archivo existe sin confirmarlo.
- NO puede cerrar una iteracion si queda alguna tarea pendiente o parcial.

### 2.4 Formato de validacion

Para cada tarea validada, el Agente V escribe en este documento:

```
### V-XXX: [Nombre de tarea]
- Definicion ref: Seccion X.Y de ATTACK_SURFACE_WOW_DEFINITION.md
- Archivos verificados: [lista]
- Tests ejecutados: [lista y resultado]
- Integracion verificada: Si/No
- Cumplimiento: COMPLETO / PARCIAL (con detalle de lo que falta) / RECHAZADO
- Fecha: YYYY-MM-DD
```

### 2.5 Rechazo

Si el Agente V rechaza o marca PARCIAL:

- Devuelve la tarea al agente constructor con detalle de lo que falta.
- La tarea NO se marca como completada en el plan.
- El agente constructor corrige y vuelve a declarar completada.
- El Agente V vuelve a validar.

---

## 3) Fases de construccion

### Fase 0: Preparacion (todos los agentes, paralelo)

**Duracion estimada:** 1 iteracion

| ID    | Tarea                                                                                           | Agente | Dependencia |
| ----- | ----------------------------------------------------------------------------------------------- | ------ | ----------- |
| F0-01 | Leer y entender ATTACK_SURFACE_WOW_DEFINITION.md completo                                       | Todos  | -           |
| F0-02 | Verificar que componentes base existen (AttackSurfaceLayers, LayerToggle, TimeSlider, types.ts) | V      | -           |
| F0-03 | Verificar que endpoints base funcionan (/assets, /edr/detections, /siem/incidents, /ctem)       | V      | -           |
| F0-04 | Crear estructura de carpetas para nueva pagina                                                  | A2     | F0-01       |

### Fase 1: Backend Surface (A1 + A5)

**Duracion estimada:** 2 iteraciones

| ID    | Tarea                                                                      | Agente | Ref Definicion | Validacion                                                    |
| ----- | -------------------------------------------------------------------------- | ------ | -------------- | ------------------------------------------------------------- |
| F1-01 | Endpoint `GET /surface/overview` (KPIs agregados)                          | A1     | Sec 6.3, 10    | V verifica: response schema, todos los KPIs, refresh rates    |
| F1-02 | Endpoint `GET /surface/nodes` (assets con layer data, paginado, filtrable) | A1     | Sec 12.3       | V verifica: response schema completo, 8 layer fields, filtros |
| F1-03 | Endpoint `GET /surface/connections` (relaciones entre assets)              | A1     | Sec 5.1 Capa 8 | V verifica: 4 tipos de conexion, strength, timestamp          |
| F1-04 | Endpoint `GET /vulnerabilities` (lista CVEs con filtros)                   | A1     | Sec 12.2       | V verifica: filtros cvss/epss/kev/vendor/product              |
| F1-05 | Endpoint `GET /vulnerabilities/cves/:id` (detalle CVE)                     | A1     | Sec 12.2       | V verifica: todos los campos de entidad CVE                   |
| F1-06 | Endpoint `GET /vulnerabilities/summary` (stats)                            | A1     | Sec 12.2       | V verifica: counts por severidad, kev, exploit                |
| F1-07 | Endpoint `GET /threats` (lista IOCs con filtros)                           | A1     | Sec 12.2       | V verifica: filtros tipo/risk/actor/pais/mitre                |
| F1-08 | Endpoint `GET /threats/iocs/:id` (detalle IOC)                             | A1     | Sec 12.2       | V verifica: todos los campos de entidad IOC                   |
| F1-09 | Endpoint `GET /threats/map` (geo aggregations)                             | A1     | Sec 12.2       | V verifica: country, count, risk, top actors                  |
| F1-10 | Endpoint `GET /threats/mitre` (cobertura ATT&CK)                           | A1     | Sec 12.2       | V verifica: tactics, techniques, counts                       |
| F1-11 | Tests unitarios de todos los endpoints                                     | A5     | Todos F1       | V verifica: coverage >= 80%, todos los endpoints cubiertos    |
| F1-12 | Tests de integracion endpoints con OpenSearch                              | A5     | Todos F1       | V verifica: tests pasan con datos reales                      |

### Fase 2: Frontend Core (A2)

**Duracion estimada:** 2 iteraciones

| ID    | Tarea                                                                                    | Agente | Ref Definicion | Validacion                                                              |
| ----- | ---------------------------------------------------------------------------------------- | ------ | -------------- | ----------------------------------------------------------------------- |
| F2-01 | Crear `SurfacePage.tsx` con layout 3 zonas (Sec 3.1)                                     | A2     | Sec 3.1, 3.2   | V verifica: header, left panel, canvas, right panel, bottom bar existen |
| F2-02 | Registrar ruta `/surface` en App.tsx con parametro `mode`                                | A2     | Sec 11         | V verifica: ruta accesible, query param `mode` funcional                |
| F2-03 | Agregar enlace en Sidebar a `/surface`                                                   | A2     | Sec 11         | V verifica: sidebar tiene link, navegacion funciona                     |
| F2-04 | Implementar Layer Panel izquierdo con checkboxes para 8 capas                            | A2     | Sec 5.2        | V verifica: 8 capas listadas, checkboxes, colores, iconos, counts       |
| F2-05 | Implementar logica de capa fija (Base no desactivable)                                   | A2     | Sec 5.2        | V verifica: Base checkbox disabled/locked                               |
| F2-06 | Implementar presets rapidos (SOC Overview, Threat Hunt, Vuln Ops, Containment Ops, Full) | A2     | Sec 5.2        | V verifica: 5 presets, cada uno activa las capas correctas              |
| F2-07 | Estado por defecto: Base+SIEM+EDR+CTEM activas                                           | A2     | Sec 5.2        | V verifica: al cargar, exactamente esas 4 activas                       |
| F2-08 | Persistencia de seleccion de capas en localStorage                                       | A2     | Sec 5.2        | V verifica: recarga preserva seleccion                                  |
| F2-09 | Contador `X/Y capas activas` visible                                                     | A2     | Sec 5.2        | V verifica: contador se actualiza al toggle                             |
| F2-10 | Boton Reset to default                                                                   | A2     | Sec 5.2        | V verifica: resetea a SOC Overview                                      |
| F2-11 | Selector de modo visual (5 tabs/iconos en header)                                        | A2     | Sec 4          | V verifica: 5 modos, cada uno cambia canvas                             |
| F2-12 | Transicion animada entre modos (fade 200ms/300ms)                                        | A2     | Sec 4.2        | V verifica: animacion visible, capas/filtros preservados                |
| F2-13 | Canvas central: Modo A (Layered Surface 2D) como default                                 | A2     | Sec 4.1        | V verifica: nodos visibles, posiciones, zoom funcional                  |

### Fase 3: Frontend Capas (A3)

**Duracion estimada:** 3 iteraciones

| ID    | Tarea                                                                     | Agente | Ref Definicion          | Validacion                                                      |
| ----- | ------------------------------------------------------------------------- | ------ | ----------------------- | --------------------------------------------------------------- |
| F3-01 | Capa Base: nodos gris con icono tipo, hover tooltip, click Detail Panel   | A3     | Sec 5.1 Capa 1          | V verifica: color, icono, hover, click                          |
| F3-02 | Capa EDR: anillo rojo, badge detections, hover, click                     | A3     | Sec 5.1 Capa 2          | V verifica: anillo rojo, badge count, severity en hover         |
| F3-03 | Capa SIEM: anillo naranja, badge incidents, hover, click                  | A3     | Sec 5.1 Capa 3          | V verifica: anillo naranja, badge count, status en hover        |
| F3-04 | Capa CTEM: halo gradiente por riesgo, hover, click                        | A3     | Sec 5.1 Capa 4          | V verifica: gradiente correcto, risk_score en hover             |
| F3-05 | Capa Vulnerabilidades: marcas CVE sobre assets, color por severidad       | A3     | Sec 5.1 Capa 5          | V verifica: visual en Modo A, filtros propios funcionan         |
| F3-06 | Capa Vulnerabilidades: Modo C (Landscape) con terreno/radial              | A3     | Sec 5.1 Capa 5, Sec 4.1 | V verifica: Modo C funcional, altura=CVSS, efectos KEV          |
| F3-07 | Capa Amenazas: marcas moradas, lineas punteadas entre assets              | A3     | Sec 5.1 Capa 6          | V verifica: visual en Modo A                                    |
| F3-08 | Capa Amenazas: Modo D (Threat Map) con mapa y lineas animadas             | A3     | Sec 5.1 Capa 6, Sec 4.1 | V verifica: mapa, lineas bezier, particulas, radar SOC          |
| F3-09 | Capa Containment: borde azul, badge lock, hover, click                    | A3     | Sec 5.1 Capa 7          | V verifica: visual correcto, estado en hover                    |
| F3-10 | Capa Relaciones: lineas entre nodos, color por tipo, animacion particulas | A3     | Sec 5.1 Capa 8          | V verifica: 4 tipos de linea, animacion, hover tooltip          |
| F3-11 | Efectos wow: glow pulsante, shake KEV, radar, count-up KPIs               | A3     | Sec 8.3                 | V verifica: cada efecto funciona donde esta especificado        |
| F3-12 | Zoom semantico: 3 niveles (clustered, grouped, detailed)                  | A3     | Sec 8.5                 | V verifica: 3 niveles, transicion smooth                        |
| F3-13 | Fade-in/out al activar/desactivar capas (200ms/150ms)                     | A3     | Sec 5.2                 | V verifica: animacion visible al toggle                         |
| F3-14 | Toast informativo al activar capa de alta densidad                        | A3     | Sec 5.2                 | V verifica: toast con count al activar Vuln/Amenazas/Relaciones |

### Fase 4: Frontend Paneles (A4)

**Duracion estimada:** 2 iteraciones

| ID    | Tarea                                                               | Agente | Ref Definicion | Validacion                                                       |
| ----- | ------------------------------------------------------------------- | ------ | -------------- | ---------------------------------------------------------------- |
| F4-01 | Detail Panel: estructura base (slide-in 250ms, pin, close)          | A4     | Sec 9          | V verifica: slide-in, pin, close, responsive                     |
| F4-02 | Detail Panel: vista Asset (info basica + layers activas + acciones) | A4     | Sec 9.1        | V verifica: todos los campos, links a detalle                    |
| F4-03 | Detail Panel: vista CVE (ficha completa)                            | A4     | Sec 5.1 Capa 5 | V verifica: cvss, epss, kev, exploit, patch, affected assets     |
| F4-04 | Detail Panel: vista IOC (ficha completa)                            | A4     | Sec 5.1 Capa 6 | V verifica: tipo, valor, geo, actor, malware, mitre              |
| F4-05 | Detail Panel: vista Incident (resumen)                              | A4     | Sec 5.1 Capa 3 | V verifica: titulo, severity, status, entities, link             |
| F4-06 | Detail Panel: acciones (Investigate, Contain, Ticket, Export)       | A4     | Sec 9.1        | V verifica: 4 acciones funcionales                               |
| F4-07 | Detail Panel: right-click context menu en nodos                     | A4     | Sec 8.4        | V verifica: 5 opciones de context menu                           |
| F4-08 | Bottom Bar: KPIs en vivo con polling                                | A4     | Sec 10         | V verifica: 10 KPIs, refresh rates correctos                     |
| F4-09 | Bottom Bar: KPIs clickeables (filtran canvas)                       | A4     | Sec 10.2       | V verifica: click en KPI filtra                                  |
| F4-10 | Bottom Bar: Timeline slider con rango seleccionable                 | A4     | Sec 10.3       | V verifica: slider funcional, chips 1h/6h/24h/7d/custom          |
| F4-11 | Bottom Bar: boton Play (replay temporal)                            | A4     | Sec 10.3       | V verifica: play/pause funcional, speed control                  |
| F4-12 | Filtros globales: panel con controles segun tabla Sec 7.1           | A4     | Sec 7.1        | V verifica: todos los filtros de la tabla implementados          |
| F4-13 | Filtros por capa: aparecen al activar la capa                       | A4     | Sec 7.2        | V verifica: filtros de Vuln, Amenazas, Containment, Relaciones   |
| F4-14 | Buscador global: input en header con autosuggest                    | A4     | Sec 7.3        | V verifica: autodeteccion tipo, suggestions, highlight en canvas |
| F4-15 | Buscador global: shortcut Ctrl+K                                    | A4     | Sec 7.3        | V verifica: shortcut funciona                                    |
| F4-16 | Query builder avanzado                                              | A4     | Sec 7.4        | V verifica: AND/OR/NOT, guardado favoritos, presets SOC          |

### Fase 5: Tests E2E + Integracion (A5)

**Duracion estimada:** 2 iteraciones (en paralelo con Fases 2-4)

| ID    | Tarea                                                | Agente | Ref Definicion | Validacion                                         |
| ----- | ---------------------------------------------------- | ------ | -------------- | -------------------------------------------------- |
| F5-01 | Test: pagina `/surface` carga sin errores            | A5     | Sec 11         | V verifica: test pasa                              |
| F5-02 | Test: 8 capas aparecen en Layer Panel con checkboxes | A5     | Sec 5.2        | V verifica: test pasa                              |
| F5-03 | Test: Base no desactivable, resto toggle funcional   | A5     | Sec 5.2        | V verifica: test pasa                              |
| F5-04 | Test: presets activan capas correctas                | A5     | Sec 5.2        | V verifica: test pasa, 5 presets verificados       |
| F5-05 | Test: 5 modos visuales conmutables                   | A5     | Sec 4          | V verifica: test pasa                              |
| F5-06 | Test: filtros globales funcionan                     | A5     | Sec 7.1        | V verifica: test pasa, todos los filtros cubiertos |
| F5-07 | Test: busqueda global encuentra y resalta            | A5     | Sec 7.3        | V verifica: test pasa                              |
| F5-08 | Test: Detail Panel se abre al click en nodo          | A5     | Sec 9          | V verifica: test pasa                              |
| F5-09 | Test: acciones desde Detail Panel (contain, ticket)  | A5     | Sec 9.1        | V verifica: test pasa                              |
| F5-10 | Test: KPIs en Bottom Bar actualizan                  | A5     | Sec 10         | V verifica: test pasa                              |
| F5-11 | Test: Timeline slider filtra canvas                  | A5     | Sec 10.3       | V verifica: test pasa                              |
| F5-12 | Test: zoom semantico (3 niveles)                     | A5     | Sec 8.5        | V verifica: test pasa                              |
| F5-13 | Test: export funciona (JSON/CSV)                     | A5     | Sec 12.2       | V verifica: test pasa                              |
| F5-14 | Test: performance 1000 nodos a 60fps                 | A5     | Sec 14.4       | V verifica: benchmark pasa                         |
| F5-15 | Test: persistencia de capas en localStorage          | A5     | Sec 5.2        | V verifica: test pasa                              |

---

## 4) Orden de ejecucion y dependencias

```
Iteracion 1:
  A1: F1-01 a F1-06 (endpoints core + vulnerabilities)
  A2: F2-01 a F2-07 (layout, ruta, layer panel, defaults)
  A5: F5-01 a F5-04 (tests de pagina y capas)
  V:  Valida F0-02, F0-03

Iteracion 2:
  A1: F1-07 a F1-12 (endpoints threats + tests backend)
  A2: F2-08 a F2-13 (persistencia, modos, canvas)
  A3: F3-01 a F3-04 (capas Base, EDR, SIEM, CTEM)
  A4: F4-01 a F4-06 (Detail Panel base + vistas)
  A5: F5-05 a F5-08 (tests modos, filtros, busqueda, detail)
  V:  Valida todas las tareas de Iteracion 1

Iteracion 3:
  A3: F3-05 a F3-10 (capas Vuln, Amenazas, Containment, Relaciones)
  A4: F4-07 a F4-11 (context menu, Bottom Bar, KPIs, timeline)
  A5: F5-09 a F5-11 (tests acciones, KPIs, timeline)
  V:  Valida todas las tareas de Iteracion 2

Iteracion 4:
  A3: F3-11 a F3-14 (efectos wow, zoom semantico, animaciones, toasts)
  A4: F4-12 a F4-16 (filtros globales, filtros capa, buscador, query builder)
  A5: F5-12 a F5-15 (tests zoom, export, performance, persistencia)
  V:  Valida todas las tareas de Iteracion 3

Iteracion 5 (cierre):
  A1-A5: Correcciones de rechazos del Agente V
  V:  Validacion FINAL completa contra ATTACK_SURFACE_WOW_DEFINITION.md
```

---

## 5) Validacion final del Agente V

Al final de la Iteracion 5, el Agente V ejecuta la **validacion final completa**:

### 5.1 Checklist de validacion final

El Agente V recorre TODO el documento `ATTACK_SURFACE_WOW_DEFINITION.md` seccion por seccion:

- [ ] **Sec 3.1** Layout: 3 zonas existen y son funcionales.
- [ ] **Sec 4** Modos: 5 modos conmutables, transicion animada, estado preservado.
- [ ] **Sec 5.1** Capas: 8 capas implementadas con TODOS los atributos (color, icono, fija, default, datos, visual, hover, click).
- [ ] **Sec 5.2** Selector: checkboxes, presets (5), defaults (4 activas), persistencia, contador, reset.
- [ ] **Sec 6** Datos: todas las entidades con todos los campos. Relaciones completas.
- [ ] **Sec 7** Filtros: globales (tabla completa), por capa, buscador global con autosuggest, query builder.
- [ ] **Sec 8** Diseno wow: paleta correcta, efectos (7 tipos), interacciones (8 tipos), zoom semantico (3 niveles).
- [ ] **Sec 9** Detail Panel: slide-in, pin, close, 4 vistas (Asset, CVE, IOC, Incident), 4 acciones, context menu.
- [ ] **Sec 10** Bottom Bar: 10 KPIs, clickeables, timeline slider, replay, speed control.
- [ ] **Sec 11** Rutas: `/surface` con 5 modos via query param. Sidebar link.
- [ ] **Sec 12** Endpoints: todos los de tabla 12.2 funcionan. Response schema de `/surface/nodes` coincide con 12.3.
- [ ] **Sec 14** Criterios: funcionalidad (8 items), valor (3 items), wow (4 items), performance (4 items).

### 5.2 Formato del reporte final

```
# REPORTE DE VALIDACION FINAL - Surface WOW
Fecha: YYYY-MM-DD
Validador: Agente V

## Resultado Global: APROBADO / RECHAZADO

## Detalle por seccion:
| Seccion | Items definidos | Items implementados | Items validados | Estado |
|---------|-----------------|---------------------|-----------------|--------|
| Sec 3   | X               | X                   | X               | OK/FAIL|
| ...     | ...             | ...                 | ...             | ...    |

## Items rechazados (si los hay):
| ID | Descripcion | Que falta | Agente responsable |
|----|-------------|-----------|-------------------|
| ... | ...        | ...       | ...               |

## Conclusion:
[Solo se cierra el proyecto si TODOS los items estan en OK]
```

### 5.3 Regla final

**El proyecto NO se considera completado hasta que el Agente V emita un reporte final con resultado APROBADO y 0 items rechazados.**

---

## 6) Progreso (rellenar durante construccion)

### Iteracion 1

| ID    | Tarea                         | Agente | Estado        | Validacion V  |
| ----- | ----------------------------- | ------ | ------------- | ------------- |
| F0-01 | Leer definicion               | Todos  | [ ] Pendiente | -             |
| F0-02 | Verificar componentes base    | V      | [ ] Pendiente | -             |
| F0-03 | Verificar endpoints base      | V      | [ ] Pendiente | -             |
| F0-04 | Estructura de carpetas        | A2     | [ ] Pendiente | [ ] Pendiente |
| F1-01 | GET /surface/overview         | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-02 | GET /surface/nodes            | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-03 | GET /surface/connections      | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-04 | GET /vulnerabilities          | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-05 | GET /vulnerabilities/cves/:id | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-06 | GET /vulnerabilities/summary  | A1     | [ ] Pendiente | [ ] Pendiente |
| F2-01 | SurfacePage layout            | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-02 | Ruta /surface en App.tsx      | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-03 | Sidebar link                  | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-04 | Layer Panel 8 capas           | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-05 | Base no desactivable          | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-06 | 5 Presets                     | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-07 | Default state                 | A2     | [ ] Pendiente | [ ] Pendiente |
| F5-01 | Test pagina carga             | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-02 | Test 8 capas                  | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-03 | Test toggle capas             | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-04 | Test presets                  | A5     | [ ] Pendiente | [ ] Pendiente |

### Iteracion 2

| ID    | Tarea                       | Agente | Estado        | Validacion V  |
| ----- | --------------------------- | ------ | ------------- | ------------- |
| F1-07 | GET /threats                | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-08 | GET /threats/iocs/:id       | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-09 | GET /threats/map            | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-10 | GET /threats/mitre          | A1     | [ ] Pendiente | [ ] Pendiente |
| F1-11 | Tests unitarios endpoints   | A5     | [ ] Pendiente | [ ] Pendiente |
| F1-12 | Tests integracion endpoints | A5     | [ ] Pendiente | [ ] Pendiente |
| F2-08 | Persistencia localStorage   | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-09 | Contador capas              | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-10 | Reset to default            | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-11 | Selector modo visual        | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-12 | Transicion animada modos    | A2     | [ ] Pendiente | [ ] Pendiente |
| F2-13 | Canvas Modo A default       | A2     | [ ] Pendiente | [ ] Pendiente |
| F3-01 | Capa Base                   | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-02 | Capa EDR                    | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-03 | Capa SIEM                   | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-04 | Capa CTEM                   | A3     | [ ] Pendiente | [ ] Pendiente |
| F4-01 | Detail Panel base           | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-02 | Detail Panel Asset          | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-03 | Detail Panel CVE            | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-04 | Detail Panel IOC            | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-05 | Detail Panel Incident       | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-06 | Detail Panel acciones       | A4     | [ ] Pendiente | [ ] Pendiente |
| F5-05 | Test 5 modos                | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-06 | Test filtros                | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-07 | Test busqueda               | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-08 | Test Detail Panel           | A5     | [ ] Pendiente | [ ] Pendiente |

### Iteracion 3

| ID    | Tarea                        | Agente | Estado        | Validacion V  |
| ----- | ---------------------------- | ------ | ------------- | ------------- |
| F3-05 | Capa Vulnerabilidades Modo A | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-06 | Capa Vulnerabilidades Modo C | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-07 | Capa Amenazas Modo A         | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-08 | Capa Amenazas Modo D         | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-09 | Capa Containment             | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-10 | Capa Relaciones              | A3     | [ ] Pendiente | [ ] Pendiente |
| F4-07 | Context menu                 | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-08 | Bottom Bar KPIs              | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-09 | KPIs clickeables             | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-10 | Timeline slider              | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-11 | Replay Play/Pause            | A4     | [ ] Pendiente | [ ] Pendiente |
| F5-09 | Test acciones                | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-10 | Test KPIs                    | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-11 | Test timeline                | A5     | [ ] Pendiente | [ ] Pendiente |

### Iteracion 4

| ID    | Tarea                       | Agente | Estado        | Validacion V  |
| ----- | --------------------------- | ------ | ------------- | ------------- |
| F3-11 | Efectos wow                 | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-12 | Zoom semantico              | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-13 | Animaciones toggle capas    | A3     | [ ] Pendiente | [ ] Pendiente |
| F3-14 | Toast alta densidad         | A3     | [ ] Pendiente | [ ] Pendiente |
| F4-12 | Filtros globales completos  | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-13 | Filtros por capa            | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-14 | Buscador global autosuggest | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-15 | Shortcut Ctrl+K             | A4     | [ ] Pendiente | [ ] Pendiente |
| F4-16 | Query builder               | A4     | [ ] Pendiente | [ ] Pendiente |
| F5-12 | Test zoom                   | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-13 | Test export                 | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-14 | Test performance            | A5     | [ ] Pendiente | [ ] Pendiente |
| F5-15 | Test persistencia           | A5     | [ ] Pendiente | [ ] Pendiente |

### Iteracion 5 (cierre)

| ID     | Tarea                      | Agente | Estado        | Validacion V  |
| ------ | -------------------------- | ------ | ------------- | ------------- |
| F5-FIN | Correcciones de rechazos V | A1-A5  | [ ] Pendiente | [ ] Pendiente |
| V-FIN  | VALIDACION FINAL COMPLETA  | V      | [ ] Pendiente | -             |

---

## 7) Resumen de volumetria

| Metrica                      | Cantidad                   |
| ---------------------------- | -------------------------- |
| Total tareas de construccion | 67                         |
| Tareas backend (A1)          | 12                         |
| Tareas frontend core (A2)    | 13                         |
| Tareas frontend capas (A3)   | 14                         |
| Tareas frontend paneles (A4) | 16                         |
| Tareas tests (A5)            | 15                         |
| Validaciones del Agente V    | 67 (1 por tarea) + 1 final |
| Iteraciones                  | 5                          |

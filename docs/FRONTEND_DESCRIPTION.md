# Descripción Funcional: Frontend de Demo Interactivo para CyberDemo

## Contexto del Proyecto

CyberDemo es una plataforma de demostración de capacidades SOC (Security Operations Center) con un agente de IA integrado. El **backend ya está completamente construido** e incluye:

- APIs REST para análisis, simulación, webhooks, aprobaciones, narración, playbooks
- WebSockets para actualizaciones en tiempo real
- MCP Tools para orquestación del agente IA
- 6 escenarios de ataque basados en grupos APT reales
- 3 escenarios de demo SOC (auto-contención, aprobación VIP, falso positivo)

El **frontend actual** tiene 14 vistas operativas (Dashboard, Incidents, Detections, Assets, CTEM, Timeline, etc.) pero **le faltan componentes críticos** para las demos interactivas con el agente.

## Objetivo

Construir los componentes frontend faltantes que permitan:

1. **Controlar simulaciones de ataque** desde cualquier página
2. **Ver el razonamiento del agente** en tiempo real
3. **Ejecutar los 3 casos de demo SOC** con un click
4. **Invocar análisis del agente** sobre incidentes específicos
5. **Experiencia inmersiva** para presentaciones formales

## Alcance

### En Scope (Lo que hay que construir)

1. **Controles Globales en todas las páginas**:
   - Barra de control de demo en el header (escenario, play/pause/stop, velocidad, progreso MITRE)
   - Widget flotante de aIP Assist (sugerencias proactivas del agente)
   - Footer de narración colapsable (streaming del razonamiento del agente)
   - Contexto global para estado compartido entre componentes

2. **Panel de Demo Casos 1/2/3** (en Dashboard):
   - 3 tarjetas/botones para ejecutar escenarios SOC originales:
     - Caso 1: WS-FIN-042 → Auto-contención automática
     - Caso 2: LAPTOP-CFO-01 → Requiere aprobación humana (VIP)
     - Caso 3: SRV-DEV-03 → Detectado como falso positivo
   - Cada tarjeta muestra: nombre, host, tipo, resultado esperado
   - Al ejecutar, invoca al agente y muestra el proceso

3. **Botón "Analizar con IA"** (en página Incidents):
   - Botón en cada fila de la tabla de incidentes
   - Al hacer click, encola análisis del agente
   - Muestra estados: "Analizar", "Analizando...", "Ver resultado"
   - Abre automáticamente el panel de narración

4. **Página dedicada /simulation**:
   - Layout de 3 columnas: Fases MITRE | Visualización | Panel aIP
   - Selector de escenarios (APT29, FIN7, Lazarus, REvil, SolarWinds, Insider)
   - Visualización de grafo de ataque en tiempo real
   - Narración siempre visible (no colapsable)
   - Experiencia inmersiva para demos formales

### Out of Scope (Ya existe, solo integrar)

- Backend APIs (ya construidas)
- WebSockets de narración y análisis (ya construidos)
- MCP Tools del agente (ya construidos)
- Escenarios de ataque (ya construidos)
- Vistas existentes del frontend (Dashboard, Incidents, etc.)
- Componentes base (DemoControlPanel, AipAssistWidget, NarrationPanel - existen pero no integrados)

## Usuarios

| Rol | Descripción | Acciones principales |
|-----|-------------|---------------------|
| **SOC Analyst** | Analista de seguridad usando la plataforma | Investigar alertas, solicitar análisis al agente, aprobar/rechazar acciones |
| **Demo Presenter** | Persona mostrando capacidades en demos | Controlar velocidad, pausar, seleccionar escenarios, ejecutar casos 1/2/3 |
| **Security Manager** | Supervisor que revisa decisiones | Ver narrativas del agente, aprobar contenciones de activos VIP |

## Funcionalidades Detalladas

### F1: Barra de Control Global

La barra aparece en el header de todas las páginas del frontend. Permite:

- Seleccionar escenario de ataque (dropdown con 6 opciones)
- Controles de reproducción (Play, Pause, Stop)
- Ajustar velocidad de simulación (0.5x a 4x)
- Ver progreso visual de fases MITRE (círculos coloreados)
- Ocultar/mostrar la barra completa

**Reglas de negocio**:
- Solo se puede ejecutar un escenario a la vez
- Pausar detiene la generación de eventos pero mantiene el estado
- Stop reinicia todo el estado de la simulación
- El progreso MITRE refleja la fase actual del ataque

### F2: Widget aIP Assist Flotante

Widget flotante en la esquina inferior derecha de todas las páginas:

- **Estado colapsado**: Botón circular con icono y badge de notificaciones
- **Estado expandido**: Panel con sugerencias proactivas del agente
- Muestra análisis automáticos sin que el usuario lo solicite
- Botones de acción: Analizar, Ignorar, Ver más detalles
- Indicador de "pensando" cuando el agente procesa

**Reglas de negocio**:
- Las sugerencias se generan automáticamente según actividad
- El badge muestra número de sugerencias no leídas
- Aceptar una sugerencia puede ejecutar acciones automáticas
- Ignorar descarta la sugerencia pero la guarda en historial

### F3: Footer de Narración

Panel en el footer de todas las páginas:

- Streaming en tiempo real del razonamiento del agente
- Formato tipo terminal con timestamps
- Colores según tipo (info=blanco, warning=amarillo, error=rojo, success=verde)
- Botón para expandir/colapsar
- Auto-scroll hacia el mensaje más reciente

**Reglas de negocio**:
- La narración continúa aunque el panel esté colapsado
- Los mensajes se acumulan durante toda la sesión
- Se puede filtrar por tipo de mensaje

### F4: Panel Demo Casos 1/2/3

Panel visible en el Dashboard principal con 3 tarjetas:

**Caso 1 - Auto-Contención**:
- Host: WS-FIN-042 (Workstation estándar)
- Simula malware detectado
- El agente analiza y contiene automáticamente
- No requiere intervención humana

**Caso 2 - Aprobación VIP**:
- Host: LAPTOP-CFO-01 (Laptop de ejecutivo)
- Simula malware detectado en activo crítico
- El agente detecta que es VIP y solicita aprobación
- Muestra tarjeta de aprobación pendiente
- Requiere click humano para aprobar/rechazar

**Caso 3 - Falso Positivo**:
- Host: SRV-DEV-03 (Servidor de desarrollo)
- Simula alerta de actividad sospechosa
- El agente analiza y determina que es falso positivo
- Marca la alerta como benigna sin contener

**Reglas de negocio**:
- Solo se puede ejecutar un caso a la vez
- El resultado debe coincidir con lo esperado (determinista)
- La narración debe mostrar todo el proceso de análisis

### F5: Botón "Analizar con IA"

Botón que aparece en cada fila de la tabla de Incidents:

- **Estado inicial**: "🤖 Analizar con IA"
- **Estado procesando**: "⏳ Analizando..." (disabled)
- **Estado completado**: Muestra decisión (✅ Contenido, ⏳ Pendiente, ❌ Descartado)
- Al hacer click, el panel de narración se expande automáticamente

**Reglas de negocio**:
- El análisis se encola y procesa asincrónicamente
- El usuario puede ver el progreso en tiempo real via narración
- El resultado se persiste en el incidente
- Múltiples incidentes pueden analizarse en paralelo

### F6: Página /simulation

Página dedicada para demos formales con layout específico:

**Columna izquierda - Fases MITRE**:
- Lista vertical de todas las fases del escenario
- Indicadores: completada (verde), activa (amarillo pulsante), pendiente (gris)
- Al hacer click en una fase, muestra detalle de técnicas

**Columna central - Visualización**:
- Grafo interactivo del ataque en tiempo real
- Nodos: hosts afectados, IOCs, conexiones C2
- Edges: propagación, comunicaciones
- Animaciones según eventos del escenario

**Columna derecha - Panel aIP**:
- Similar al widget flotante pero integrado (no flotante)
- Siempre visible, no colapsable
- Muestra análisis, recomendaciones, correlaciones

**Footer - Narración**:
- Siempre visible (no colapsable)
- Altura fija, scroll interno

**Reglas de negocio**:
- Esta página es independiente de los controles globales
- El escenario se selecciona dentro de la página
- La visualización se actualiza en tiempo real según eventos

## Integraciones con Backend Existente

El frontend debe conectarse a los siguientes endpoints ya construidos:

### APIs REST

| Endpoint | Uso en Frontend |
|----------|-----------------|
| `POST /api/v1/analysis/queue` | Encolar análisis del agente |
| `GET /api/v1/analysis/status/{id}` | Obtener estado de job |
| `GET /api/v1/demo-scenarios/scenarios` | Listar casos 1/2/3 |
| `POST /api/v1/demo-scenarios/run/{n}` | Ejecutar caso 1, 2 o 3 |
| `POST /api/v1/simulation/start` | Iniciar simulación |
| `POST /api/v1/simulation/pause` | Pausar simulación |
| `POST /api/v1/simulation/resume` | Reanudar simulación |
| `POST /api/v1/simulation/speed` | Cambiar velocidad |
| `GET /api/v1/simulation/state` | Obtener estado actual |
| `GET /api/v1/aip-assist/session/{id}/state` | Estado de aIP Assist |
| `POST /api/v1/aip-assist/session/{id}/feedback` | Feedback a sugerencia |

### WebSockets

| Endpoint | Uso en Frontend |
|----------|-----------------|
| `WS /api/v1/analysis/ws` | Actualizaciones de jobs en tiempo real |
| `WS /api/v1/narration/ws/{session}` | Streaming de narración del agente |
| `WS /api/v1/aip-assist/ws/{session}` | Sugerencias proactivas en tiempo real |
| `WS /api/v1/simulation/ws` | Estado de simulación en tiempo real |

### Nota sobre Backend Faltante

Si algún endpoint no existe, debe crearse como wrapper sobre los MCP Tools existentes. Los MCP Tools ya construidos incluyen:

- `agent_analyze_alert` - Analizar alerta
- `agent_investigate_ioc` - Investigar IOC
- `agent_recommend_action` - Recomendar acción
- `simulation_start/pause/resume/set_speed` - Control de simulación
- `aip_get_suggestion` - Obtener sugerencia proactiva

## Requisitos No Funcionales

- **Rendimiento**: Actualización de UI < 100ms desde evento WebSocket
- **Usabilidad**: Controles accesibles con atajos de teclado (Space=Play/Pause, Esc=Stop)
- **Responsividad**: Funcionar en pantallas de 1280px+ de ancho
- **Compatibilidad**: Chrome, Firefox, Edge (últimas 2 versiones)
- **Accesibilidad**: Controles navegables por teclado, labels ARIA

## Dependencias

- **Framework**: React 18+ (ya en uso)
- **Estado**: React Context + hooks (patrón existente)
- **Estilos**: Tailwind CSS (ya en uso)
- **Grafos**: Cytoscape.js (ya instalado)
- **WebSockets**: API nativa del navegador

## Restricciones

- **Solo frontend**: No crear nuevo backend excepto wrappers REST sobre MCP existentes
- **Reutilizar componentes**: Usar los componentes base existentes (DemoControlPanel, etc.)
- **No duplicar lógica**: La lógica de negocio está en el backend, el frontend solo presenta
- **Mantener estilos**: Seguir el sistema de diseño existente (colores, tipografía, espaciado)

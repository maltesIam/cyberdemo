# Descripcion Funcional Version Avanzada - CyberDemo

| Attribute | Value |
|-----------|-------|
| Version | 1.0.0 |
| Date | 2026-02-24 |
| Status | Draft |
| Depends On | Existing CyberDemo platform (all E2E tests passing) |

---

## 1. Executive Summary

This document describes two major enhancements to the CyberDemo platform that will transform the demo from "the agent analyzes and comments" to "the agent investigates, acts, and the audience SEES it happening in real-time":

1. **EPIC-001: Agent-to-UI Bidirectional Control** - Vega (the AI agent) can control what the audience sees: navigate pages, highlight assets, generate charts, show timelines
2. **EPIC-002: Dynamic Scenario Data Engine** - Mock data that tells the story of each attack scenario, evolving phase-by-phase so every tool shows contextually relevant data

### Why This Matters

**Current state**: When APT29 simulation reaches phase 3 "Initial Access", Vega provides text analysis in the narration panel. The audience reads it. The 25 SOC tools (SIEM, EDR, Intel...) return the same static 3 incidents regardless of the phase.

**Target state**: At phase 3, Vega analyzes the alert AND navigates to the attack graph, highlights the compromised host with a pulsing red glow, shows a process tree chart, while the SIEM tool now shows 5 incidents (including the new phishing detection), the EDR shows the Word→PowerShell chain, and Intel shows the matched C2 domain. The audience SEES the investigation unfold.

---

## 2. System Overview

### Current Architecture

```
User ──clicks──► React App ──callMcpTool()──► Backend MCP (40 tools)
                    │                              │
                    │                              ├── attack_* tools (simulation control)
                    │                              ├── agent_* tools (mock orchestration)
                    │                              ├── siem_*/edr_*/intel_* (static mock data)
                    │                              └── aip_* tools (suggestions)
                    │
                    └──POST /agent/analyze──► GatewayClient ──► Vega (Claude Sonnet 4)
                                                                    │
                                                              Text response only
                                                              (appears in narration)
```

**Limitation**: Vega can only send text. It cannot control the UI.

### Target Architecture

```
User ──clicks──► React App ◄──────────────── UI Command Channel (WebSocket)
                    │                              ▲
                    │                              │ broadcast state_update
                    │                              │
                    │               Frontend MCP WS Server (:3001)
                    │                 8 UI-control tools
                    │                    ▲
                    │                    │ tool_call
                    │                    │
                    └──callMcpTool()──► Backend MCP (40 tools)
                                           │          │
                                           │          └── UI Bridge: forwards to WS Server
                                           │
                                           ├── attack_* (simulation + phase tracking)
                                           ├── agent_* (calls Vega, then UI actions)
                                           ├── siem_*/edr_*/intel_* (DYNAMIC phase data)
                                           └── Scenario Data Engine (new)
                                                  │
                                                  └── scenario scripts (APT29, FIN7, etc.)
                                                        with events per phase
```

---

## EPIC-001: Agent-to-UI Bidirectional Control

### 1.1 Overview

The Frontend MCP WS Server already exists as a standalone process with 8 tools. This EPIC connects it to the React app and the backend, creating a bidirectional channel where:

- **Agent → UI**: Vega calls a backend tool → backend forwards to WS Server → WS Server broadcasts to React → React renders the change
- **UI → Agent**: User actions in React are visible to Vega through state queries

### 1.2 User Roles

| Role | Interaction |
|------|-------------|
| **Demo Audience** | Watches the UI change in real-time as Vega investigates |
| **Demo Presenter** | Starts simulation, Vega does the rest. Can pause/intervene |
| **Vega (Agent)** | Analyzes phases AND controls the UI to show findings |

### 1.3 Functional Areas

#### FA-001: React ↔ MCP WS Server Connection

**US-001**: As the React app, I need to connect to the MCP WS Server so I can receive UI commands from the agent.

**Description**: A new React hook `useMcpStateSync` opens a WebSocket connection to `ws://localhost:3001` with header `x-client-type: react`. It listens for `state_update` messages and applies them to the application state. When the state changes (e.g., `currentView` changes from "dashboard" to "graph"), the app reacts accordingly.

**Acceptance Criteria**:
- AC-001: Hook connects to WS Server on mount and reconnects on disconnect
- AC-002: Receives `state_update` messages and updates React state
- AC-003: When `currentView` changes, the app navigates to the corresponding route
- AC-004: When `highlightedAssets` changes, the Surface/Graph page highlights those nodes
- AC-005: When `charts` array receives new entries, they render in a chart overlay
- AC-006: When `timeline` is set, a timeline panel appears
- AC-007: Connection status is visible (indicator in UI)

**State-to-Action Mapping**:

| State Change | React Action |
|-------------|-------------|
| `currentView: "graph"` | Navigate to `/simulation` or `/surface` |
| `currentView: "dashboard"` | Navigate to `/` (Dashboard) |
| `currentView: "timeline"` | Open timeline overlay panel |
| `currentView: "postmortem"` | Navigate to postmortem view |
| `highlightedAssets: ["WS-FIN-042"]` | Pulse/glow that node on graph |
| `charts: [new chart]` | Render chart in overlay |
| `simulationRunning: true` | Show simulation active indicator |
| `timeline: {alerts: [...]}` | Render alert timeline component |

**Business Rules**:
- BR-001: The WS connection must not block the main thread
- BR-002: State updates must be applied within 100ms of receipt
- BR-003: If the WS Server is unavailable, the app must work normally (graceful degradation)
- BR-004: Navigation triggered by agent must be visually distinct (e.g., brief "Vega is navigating..." toast)

---

#### FA-002: Backend → WS Server Bridge

**US-002**: As the backend, I need to forward UI control commands to the MCP WS Server so that when Vega wants to show something, the UI responds.

**Description**: New backend module `ui_bridge.py` maintains a WebSocket client connection to the MCP WS Server (port 3001). When any backend handler wants to trigger a UI action (e.g., after agent analysis), it calls `ui_bridge.send_tool_call(tool_name, params)`. The bridge sends it to the WS Server, which processes it and broadcasts the state change to React clients.

**Acceptance Criteria**:
- AC-001: Backend connects to WS Server on startup (lazy, first use)
- AC-002: `send_tool_call()` sends a JSON message in MCP format and awaits response
- AC-003: If WS Server is unavailable, operations fail silently (no crash)
- AC-004: Connection auto-reconnects on disconnect
- AC-005: New REST endpoint `POST /api/v1/ui/action` for direct UI commands

**API Contract**:

```
POST /api/v1/ui/action
Content-Type: application/json

{
  "tool": "highlight_asset",
  "params": {
    "asset_id": "WS-FIN-042",
    "highlight_type": "pulse"
  }
}

Response: { "success": true }
```

**Business Rules**:
- BR-001: UI actions from the agent must be rate-limited (max 2 per second)
- BR-002: The bridge must not block backend request processing
- BR-003: Failed UI actions must not affect backend operation

---

#### FA-003: Agent Analysis with UI Actions

**US-003**: As Vega, when I analyze a phase of the attack, I should not only explain what is happening but also SHOW it on the screen.

**Description**: Enhance the `requestAgentAnalysis()` function in the orchestrator. After Vega provides text analysis, the system parses the analysis context and triggers appropriate UI actions automatically.

**Phase-to-UI-Action Mapping for APT29**:

| Phase | Vega Analyzes | UI Actions Triggered |
|-------|--------------|---------------------|
| 1. Initial Access | Phishing detection | `highlight_asset("WS-FIN-042", "pulse")` + `show_alert_timeline(phishing alerts)` |
| 2. Execution | PowerShell execution | `generate_chart("process_tree", process data)` + navigate to graph |
| 3. Persistence | Registry modification | `highlight_asset("WS-FIN-042", "glow")` + `update_dashboard(incidents+1)` |
| 4. Defense Evasion | Log clearing | `show_alert_timeline(evasion events)` |
| 5. Discovery | Network scanning | `highlight_asset` on multiple scanned hosts |
| 6. Collection | Data staging | `generate_chart("bar", data volume by host)` |
| 7. Exfiltration | Data transfer | `highlight_asset("SRV-DMZ-01", "pulse")` + `generate_chart("line", transfer rate)` |
| 8. C2 | Beaconing | `generate_chart("line", beacon intervals)` + `update_dashboard(final stats)` |

**Acceptance Criteria**:
- AC-001: Each phase triggers at least 1 UI action automatically
- AC-002: UI actions happen 1-2 seconds after Vega's text analysis appears
- AC-003: Actions are specific to the scenario and phase (not generic)
- AC-004: Presenter can disable auto-UI-actions via a toggle

**Business Rules**:
- BR-001: UI actions must not fire if the WS Server is disconnected
- BR-002: UI actions must not interrupt user interaction (if user is clicking, queue the action)

---

#### FA-004: Enhanced Frontend MCP Tools

**US-004**: The 8 existing frontend MCP tools need to produce richer, more visible effects in the UI.

**Current tools and enhancements needed**:

| Tool | Current Behavior | Enhanced Behavior |
|------|-----------------|------------------|
| `show_simulation` | Sets `simulationRunning: true` | Also shows a full-screen overlay with attack graph animation, scenario name banner |
| `generate_chart` | Adds chart to state array | Renders as floating overlay chart with smooth animation, auto-dismiss after 10s |
| `run_demo_scenario` | Sets `activeScenario` | Triggers the full demo flow: select scenario dropdown, click Play, show narration |
| `get_demo_state` | Returns state object | No change needed (read-only) |
| `update_dashboard` | Updates KPIs in state | Animates KPI number changes (count up/down), flash color on change |
| `show_alert_timeline` | Sets timeline in state | Renders as sliding panel from right with animated timeline entries |
| `highlight_asset` | Adds to `highlightedAssets` | Three visual modes: pulse (repeating glow), glow (static bright), zoom (auto-pan + zoom to asset) |
| `show_postmortem` | Sets `currentView` | Navigates to postmortem page with generated report content |

**Acceptance Criteria**:
- AC-001: Charts render as floating overlays that don't block underlying content
- AC-002: Highlight effects are visible and distinguishable (pulse vs glow vs zoom)
- AC-003: Timeline panel slides in from the right with animation
- AC-004: Dashboard KPI updates animate (number counting effect)
- AC-005: All effects auto-dismiss or can be dismissed by the user

---

#### FA-005: WS Server Startup Integration

**US-005**: The MCP WS Server should start automatically with the development environment.

**Description**: Instead of requiring a separate `npx ts-node` command, the WS Server should be integrated into the development workflow.

**Options** (implement one):
- **Option A**: Start as a Vite plugin that launches the WS Server alongside the dev server
- **Option B**: Run as a background process started by `npm run dev` via `concurrently`
- **Option C**: Embed the WS logic directly into the backend (Python) instead of Node.js

**Acceptance Criteria**:
- AC-001: `npm run dev` starts both the React dev server AND the MCP WS Server
- AC-002: WS Server logs appear in the same terminal (prefixed with `[MCP]`)
- AC-003: Stopping `npm run dev` also stops the WS Server

---

### 1.4 Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-001 | UI state updates must render within 100ms of WebSocket receipt |
| NFR-002 | WS connection must auto-reconnect with exponential backoff |
| NFR-003 | All UI actions must degrade gracefully if WS Server is down |
| NFR-004 | No memory leaks from WS connections (proper cleanup on unmount) |
| NFR-005 | Maximum 50 concurrent React clients (unlikely but bounded) |

### 1.5 Technical Requirements

| TECH | Description |
|------|-------------|
| TECH-001 | `useMcpStateSync` React hook with WebSocket connection to port 3001 |
| TECH-002 | `UIBridge` Python class in backend with async WebSocket client |
| TECH-003 | REST endpoint `POST /api/v1/ui/action` for programmatic UI control |
| TECH-004 | Chart overlay React component with auto-dismiss timer |
| TECH-005 | Asset highlight effects via CSS animations (pulse, glow, zoom) |
| TECH-006 | Timeline sliding panel React component |
| TECH-007 | KPI animation component (counting number effect) |

---

## EPIC-002: Dynamic Scenario Data Engine

### 2.1 Overview

Replace static mock data in the 25 SOC tools with a **Scenario Data Engine** that produces contextually appropriate data based on:
- Which scenario is running (APT29, FIN7, Lazarus, etc.)
- Which phase the simulation is currently in (1-8 for APT29)
- What actions the agent has taken (contained hosts, closed incidents)

The data is **cumulative**: phase 5 shows all data from phases 1-5, just like a real SOC would see.

### 2.2 Architecture: ScenarioStateManager

```
                    ScenarioStateManager (Singleton)
                           │
                           ├── current_scenario: "apt29"
                           ├── current_phase: 3
                           ├── cumulative_state:
                           │     ├── siem_incidents: [INC-001, INC-002, INC-003]
                           │     ├── edr_detections: [DET-001, DET-002]
                           │     ├── intel_iocs: [IOC-001, IOC-002, IOC-003]
                           │     ├── contained_hosts: []
                           │     ├── closed_incidents: []
                           │     ├── tickets: []
                           │     ├── comments: {INC-001: ["Initial triage..."]}
                           │     └── approvals: []
                           │
                           └── scenario_scripts/
                                 ├── apt29.py  (8 phases, events per phase)
                                 ├── fin7.py   (6 phases)
                                 ├── lazarus.py (5 phases)
                                 ├── revil.py   (5 phases)
                                 ├── solarwinds.py (6 phases)
                                 └── insider.py (3 phases)
```

**Key Principle**: When `attack_start_scenario("apt29")` is called and the simulation advances to phase N, the ScenarioStateManager applies all events from phases 1 through N. Each tool handler queries this manager instead of returning static data.

### 2.3 Functional Areas

#### FA-006: ScenarioStateManager

**US-006**: As the backend, I need a central state manager that holds the cumulative state of the simulation, so all tools return consistent, phase-appropriate data.

**Description**: A singleton Python class that:
1. Initializes when `attack_start_scenario` is called
2. Applies phase events cumulatively as the simulation advances
3. Allows mutations (agent actions: contain host, close incident, add comment)
4. Exposes query methods for each tool domain

**Interface**:

```python
class ScenarioStateManager:
    def start_scenario(self, scenario_name: str) -> None
    def advance_to_phase(self, phase: int) -> None
    def reset(self) -> None

    # Query methods (used by tool handlers)
    def get_siem_incidents(self, severity=None, status=None) -> List[dict]
    def get_siem_incident(self, incident_id: str) -> dict | None
    def get_edr_detections(self, severity=None) -> List[dict]
    def get_edr_detection(self, detection_id: str) -> dict | None
    def get_edr_process_tree(self, detection_id: str) -> dict | None
    def get_intel_indicators(self) -> List[dict]
    def get_asset_risk(self, asset_id: str) -> dict | None
    def get_vulnerabilities(self) -> List[dict]
    def get_active_threats(self) -> List[dict]

    # Mutation methods (used by agent action tools)
    def contain_host(self, device_id: str, reason: str) -> dict
    def lift_containment(self, device_id: str) -> dict
    def close_incident(self, incident_id: str, resolution: str) -> dict
    def add_comment(self, incident_id: str, comment: str) -> dict
    def create_ticket(self, title: str, details: dict) -> dict
    def request_approval(self, action: str, target: str) -> dict
    def hunt_hash(self, hash_value: str) -> dict
```

**Acceptance Criteria**:
- AC-001: State initializes empty before any scenario starts
- AC-002: Calling `advance_to_phase(3)` applies events from phases 1, 2, and 3
- AC-003: Calling `advance_to_phase(5)` after `advance_to_phase(3)` only applies phases 4 and 5 (no duplicates)
- AC-004: `contain_host()` modifies the host state visible to `edr_list_detections`
- AC-005: `close_incident()` changes incident status visible to `siem_list_incidents`
- AC-006: `reset()` clears all state

**Business Rules**:
- BR-001: Data is always cumulative - you never lose earlier events
- BR-002: Agent mutations are immediate and visible to subsequent tool calls
- BR-003: Only one scenario can be active at a time
- BR-004: The manager is thread-safe (asyncio Lock)

---

#### FA-007: Scenario Scripts - APT29

**US-007**: The APT29 scenario needs a complete event script that defines what SIEM incidents, EDR detections, Intel IOCs, and other data appear at each of its 8 phases.

**APT29 Scenario Script - Events per Phase**:

##### Phase 1: Initial Access (Spearphishing)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-001 | "Suspicious Email - Malicious Attachment Detected", severity: high, asset: WS-FIN-042, status: open |
| SIEM | INC-APT29-002 | "Email Gateway Alert - Known Phishing Domain", severity: medium, asset: MAIL-GW-01 |
| EDR | DET-APT29-001 | "Macro Execution in Word Document", severity: high, asset: WS-FIN-042, process: WINWORD.EXE |
| Intel | IOC-APT29-001 | Type: domain, value: "updates-microsoft[.]com", score: 85, tags: ["apt29", "phishing"], geo: Russia |
| Intel | IOC-APT29-002 | Type: hash, value: "a3b8f7...e2d1", score: 92, tags: ["apt29", "dropper"], filename: "Q4-Report.docm" |
| CTEM | Asset risk update | WS-FIN-042 risk: medium → high |

##### Phase 2: Execution (PowerShell)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-003 | "Encoded PowerShell Command Detected", severity: critical, asset: WS-FIN-042 |
| EDR | DET-APT29-002 | "PowerShell Encoded Execution", severity: critical, process: powershell.exe -enc, parent: WINWORD.EXE |
| EDR | DET-APT29-003 | "Suspicious Child Process Spawning", severity: high, process: cmd.exe, parent: powershell.exe |
| EDR | Process tree | WINWORD.EXE → powershell.exe -enc → cmd.exe → whoami.exe |
| Intel | IOC-APT29-003 | Type: ip, value: "185.220.101.42", score: 95, tags: ["apt29", "c2"], geo: Netherlands (VPS) |

##### Phase 3: Persistence (Registry + Scheduled Task)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-004 | "Registry Run Key Modified", severity: high, asset: WS-FIN-042 |
| SIEM | INC-APT29-005 | "Scheduled Task Created - Suspicious Binary", severity: high, asset: WS-FIN-042 |
| EDR | DET-APT29-004 | "Registry Modification - Persistence", severity: high, key: HKCU\Software\Microsoft\Windows\CurrentVersion\Run |
| EDR | DET-APT29-005 | "Scheduled Task - Non-Standard Path", severity: medium, task: "WindowsUpdate", binary: C:\ProgramData\svchost.exe |
| Vuln | Relevant CVE | CVE-2023-36884: Office RCE used for initial exploit, CVSS 8.8 |
| CTEM | Asset risk update | WS-FIN-042 risk: high → critical |

##### Phase 4: Defense Evasion (Obfuscation + Log Clearing)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-006 | "Windows Event Log Cleared", severity: critical, asset: WS-FIN-042 |
| SIEM | INC-APT29-007 | "Antivirus Tampered - Real-time Protection Disabled", severity: critical, asset: WS-FIN-042 |
| EDR | DET-APT29-006 | "Event Log Tampering", severity: critical, process: wevtutil.exe cl Security |
| EDR | DET-APT29-007 | "Defense Evasion - AV Disabled", severity: critical, service: WinDefend stopped |
| Intel | IOC-APT29-004 | Type: hash, value: "c7f2d9...b4a8", score: 88, tags: ["apt29", "evasion_tool"], filename: "clean.exe" |
| Approvals | Auto-generated | "Emergency: Isolate WS-FIN-042? Critical evasion detected" |

##### Phase 5: Discovery (Network Scan)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-008 | "Internal Network Scan Detected", severity: high, asset: WS-FIN-042, targets: 10.0.0.0/24 |
| SIEM | INC-APT29-009 | "Active Directory Enumeration", severity: high, asset: WS-FIN-042 |
| EDR | DET-APT29-008 | "Network Discovery - Port Scan", severity: medium, tool: nmap-like behavior |
| EDR | DET-APT29-009 | "LDAP Query - Domain Users Enumeration", severity: high |
| Intel | IOC-APT29-005 | Type: domain, value: "dc01.corp.local", score: 0 (internal), tags: ["target", "domain_controller"] |
| CTEM | Multiple assets | SRV-DC-01 risk: medium → high (targeted by scanner) |
| Tickets | Auto-created | "Investigate network scan from WS-FIN-042" |

##### Phase 6: Collection (Data Staging)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-010 | "Sensitive File Access - Finance Share", severity: critical, asset: WS-FIN-042 |
| SIEM | INC-APT29-011 | "Large Data Staging Detected", severity: critical, size: "2.3 GB compressed" |
| EDR | DET-APT29-010 | "Archive Creation - RAR with Password", severity: high, file: C:\ProgramData\backup.rar |
| EDR | DET-APT29-011 | "Unauthorized Share Access", severity: medium, shares: \\\\SRV-FILE-01\\Finance, \\\\SRV-FILE-01\\HR |
| Threats | APT29 campaign update | "Data collection phase detected, exfiltration imminent" |

##### Phase 7: Exfiltration (Data Transfer)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-012 | "Anomalous Outbound Data Transfer", severity: critical, dest: 185.220.101.42, size: "2.3 GB" |
| SIEM | INC-APT29-013 | "DNS Tunneling Suspected", severity: high, queries: 4500 TXT queries in 10 min |
| EDR | DET-APT29-012 | "Data Exfiltration via HTTPS", severity: critical, dest: 185.220.101.42:443 |
| EDR | DET-APT29-013 | "Encrypted Channel - Non-Standard TLS", severity: high |
| Intel | IOC-APT29-006 | Type: ip, value: "91.234.56.78", score: 90, tags: ["apt29", "exfil_server"], geo: Ukraine |
| Reports | Auto-generated | Preliminary incident report available |

##### Phase 8: Command and Control (Beaconing)

| Domain | Event | Details |
|--------|-------|---------|
| SIEM | INC-APT29-014 | "Persistent C2 Beaconing Detected", severity: critical, interval: "every 60s", dest: 185.220.101.42 |
| EDR | DET-APT29-014 | "C2 Beacon - Regular Interval Communication", severity: critical, interval: 60s, jitter: 10% |
| EDR | DET-APT29-015 | "Cobalt Strike Signature Detected", severity: critical, process: svchost.exe (injected) |
| Intel | IOC-APT29-007 | Type: url, value: "https://185.220.101.42/api/v1/beacon", score: 98, tags: ["apt29", "cobalt_strike"] |
| Threats | Campaign summary | "APT29 operation complete: initial access → exfiltration. 14 incidents, 15 detections, 7 IOCs" |
| Reports | Final postmortem | Full incident report with timeline, IOCs, affected assets, lessons learned |

**Summary per phase (APT29)**:

| Phase | SIEM incidents (cumulative) | EDR detections (cumulative) | Intel IOCs (cumulative) | Risk level |
|-------|---------------------------|---------------------------|------------------------|------------|
| 1 | 2 | 1 | 2 | High |
| 2 | 3 | 3 | 3 | High |
| 3 | 5 | 5 | 3 | Critical |
| 4 | 7 | 7 | 4 | Critical |
| 5 | 9 | 9 | 5 | Critical |
| 6 | 11 | 11 | 5 | Critical |
| 7 | 13 | 13 | 6 | Critical |
| 8 | 14 | 15 | 7 | Critical |

**Acceptance Criteria**:
- AC-001: At phase 1, `siem_list_incidents` returns exactly 2 incidents
- AC-002: At phase 3, `siem_list_incidents` returns exactly 5 incidents (cumulative)
- AC-003: At phase 8, all 14 incidents, 15 detections, and 7 IOCs are visible
- AC-004: Each incident has realistic timestamps spaced across the attack timeline
- AC-005: Cross-references are consistent (DET-APT29-001 references INC-APT29-001's asset)

---

#### FA-008: Scenario Scripts - Other Scenarios

**US-008**: Each of the 6 attack scenarios needs its own event script with appropriate data.

**Requirements per scenario**:

| Scenario | Phases | SIEM Events | EDR Events | IOCs | Unique Feature |
|----------|--------|-------------|------------|------|---------------|
| APT29 | 8 | 14 | 15 | 7 | Full kill chain, espionage focus |
| FIN7 | 6 | 10 | 8 | 5 | Financial targeting, POS malware |
| Lazarus | 5 | 8 | 7 | 4 | Destructive wiper at end |
| REvil | 5 | 9 | 8 | 4 | Ransomware encryption, ransom note |
| SolarWinds | 6 | 11 | 6 | 5 | Supply chain, trusted software abuse |
| Insider | 3 | 5 | 3 | 2 | No malware, legitimate credentials abuse |

**Acceptance Criteria**:
- AC-001: Each scenario has its own script file with phase-by-phase events
- AC-002: Events are domain-appropriate (FIN7 has POS-related detections, Lazarus has wipers)
- AC-003: All scenarios follow the same ScenarioStateManager interface
- AC-004: Switching scenarios resets state completely

---

#### FA-009: Tool Handler Integration with ScenarioStateManager

**US-009**: All 25 SOC domain tool handlers must query the ScenarioStateManager instead of returning static mock data.

**Changes per tool**:

| Tool | Current Behavior | New Behavior |
|------|-----------------|-------------|
| `siem_list_incidents` | Returns 3 static incidents always | Returns `manager.get_siem_incidents(severity, status)` - phase-dependent list |
| `siem_get_incident` | Returns INC-ANCHOR-001 static data | Returns `manager.get_siem_incident(id)` - returns None if incident not yet "discovered" in current phase |
| `siem_add_comment` | Creates comment, doesn't persist | Calls `manager.add_comment(id, text)` - persists in state, visible in subsequent get_incident calls |
| `siem_close_incident` | Returns success, no side effect | Calls `manager.close_incident(id, resolution)` - changes status to "closed", visible in list |
| `edr_get_detection` | Returns static detection | Returns `manager.get_edr_detection(id)` - phase-dependent |
| `edr_get_process_tree` | Returns static tree | Returns `manager.get_edr_process_tree(id)` - grows more complex in later phases |
| `edr_hunt_hash` | Returns static result | Returns `manager.hunt_hash(hash)` - finds hash on more endpoints as attack spreads |
| `edr_contain_host` | Returns success, no side effect | Calls `manager.contain_host(id, reason)` - changes host status, visible in detections |
| `edr_lift_containment` | Returns success, no side effect | Calls `manager.lift_containment(id)` - restores host status |
| `edr_list_detections` | Returns 0 detections | Returns `manager.get_edr_detections()` - grows with each phase |
| `intel_get_indicator` | Recognizes 1 IP only | Returns `manager.get_intel_indicator(ioc)` - recognizes all IOCs introduced in current/past phases |
| `ctem_get_asset_risk` | Returns static risk | Returns `manager.get_asset_risk(id)` - risk escalates as attack progresses |
| `approvals_get` | Returns empty | Returns `manager.get_pending_approvals()` - approvals created during evasion/containment phases |
| `approvals_request` | Returns success | Calls `manager.request_approval(action, target)` - creates visible approval |
| `tickets_create` | Returns success, no side effect | Calls `manager.create_ticket(title, details)` - persists in state |
| `tickets_list` | Returns empty | Returns `manager.get_tickets()` - shows created tickets |
| `reports_generate_postmortem` | Returns static report | Returns `manager.generate_postmortem(incident_id)` - uses cumulative state data |
| `reports_get_postmortem` | Returns static report | Returns `manager.get_postmortem(id)` - only available after generation |
| `enrichment_threats` | Returns static data | Returns `manager.get_active_threats()` - threat data grows with intel |
| `threats_query` | Returns static data | Returns `manager.query_threats(query)` - searches cumulative threat data |
| `threats_map` | Returns static data | Returns `manager.get_threat_map()` - geo data from IOCs |
| `vuln_enrich_cve` | Returns static CVE | Returns `manager.get_relevant_cves()` - CVEs relevant to techniques used |
| `vuln_get_ssvc_decision` | Returns static decision | Returns SSVC decision based on active exploitation status |
| `vuln_search` | Returns static list | Returns vulnerabilities on affected assets |
| `vuln_get_risk_assessment` | Returns static assessment | Returns assessment incorporating active attack data |

**Acceptance Criteria**:
- AC-001: All 25 tools return phase-appropriate data when a scenario is active
- AC-002: All 25 tools return empty/default data when no scenario is active (backward compatible)
- AC-003: Agent mutations (contain, close, comment) are immediately reflected in subsequent queries
- AC-004: No tool crashes if called before scenario starts

**Business Rules**:
- BR-001: If no scenario is running, tools return the current static mock data (backward compatibility)
- BR-002: Tools must not reveal future-phase data (no spoilers)
- BR-003: Contained hosts show status "contained" in all relevant tool responses
- BR-004: Closed incidents show status "closed" in all tool responses

---

#### FA-010: Agent Orchestration Tools Enhancement

**US-010**: The 6 agent orchestration tools should use the ScenarioStateManager data instead of their own separate mock stores.

**Changes**:

| Tool | New Behavior |
|------|-------------|
| `agent_analyze_alert` | Analyzes alerts from ScenarioStateManager, not MOCK_ALERTS. If Vega gateway is available, forwards to real agent for analysis text |
| `agent_investigate_ioc` | Looks up IOCs from ScenarioStateManager intel data. Enriches with scenario context |
| `agent_recommend_action` | Recommendations based on current phase: early = "monitor", mid = "contain", late = "eradicate" |
| `agent_generate_report` | Generates report from cumulative ScenarioStateManager data (all incidents, detections, IOCs) |
| `agent_explain_decision` | Explains decisions in context of the scenario progression |
| `agent_correlate_events` | Correlates events from ScenarioStateManager, finding real cross-domain links |

**Acceptance Criteria**:
- AC-001: `agent_analyze_alert` returns analysis for scenario-specific alerts
- AC-002: `agent_correlate_events` finds correlations between SIEM incidents and EDR detections from the same phase
- AC-003: `agent_generate_report` includes all cumulative data up to current phase
- AC-004: If Vega gateway is available, the text portion of analysis comes from the real agent

---

#### FA-011: Simulation Phase Synchronization

**US-011**: When the frontend simulation advances phases, the ScenarioStateManager must advance too, so tools always return data matching what the user sees.

**Description**: The `attack_start_scenario` and `attack_jump_to_stage` MCP tools already manage simulation state. They need to also call `ScenarioStateManager.advance_to_phase()` so the data engine stays synchronized.

**Integration Points**:

```
Frontend: useDemoOrchestrator auto-advance timer
    │
    ├── callMcpTool('attack_start_scenario', {scenario_name: 'apt29'})
    │       └── SimulationStateManager.start()
    │       └── ScenarioStateManager.start_scenario('apt29')  ← NEW
    │       └── ScenarioStateManager.advance_to_phase(1)      ← NEW
    │
    ├── (auto-advance every 3s)
    │       └── ScenarioStateManager.advance_to_phase(N)      ← NEW
    │
    ├── callMcpTool('attack_jump_to_stage', {stage: 5})
    │       └── ScenarioStateManager.advance_to_phase(5)      ← NEW
    │
    └── callMcpTool('attack_pause')
            └── (no data change, just pause timer)
```

**Acceptance Criteria**:
- AC-001: Starting a scenario initializes both SimulationStateManager and ScenarioStateManager
- AC-002: Phase advance syncs both managers
- AC-003: Jumping to a phase applies all events up to that phase
- AC-004: Pausing does not affect data state

---

### 2.4 Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-001 | ScenarioStateManager must respond in < 10ms for any query |
| NFR-002 | Memory usage for all scenario data must be < 50MB |
| NFR-003 | Adding a new scenario requires only creating a new script file |
| NFR-004 | All existing tests must continue passing (backward compatible) |

### 2.5 Technical Requirements

| TECH | Description |
|------|-------------|
| TECH-001 | `ScenarioStateManager` singleton class with async-safe state |
| TECH-002 | Scenario script files in `backend/src/mcp/scenarios/` directory |
| TECH-003 | Each script file exports a `PHASES` list of `PhaseEvents` objects |
| TECH-004 | `PhaseEvents` contains lists of SIEM events, EDR events, Intel IOCs, etc. |
| TECH-005 | All 25 tool handlers modified to query ScenarioStateManager |
| TECH-006 | Backward compatibility: if no scenario active, return current static data |

---

## 3. Traceability Matrix

| Req ID | EPIC | Feature | Description |
|--------|------|---------|-------------|
| REQ-001-001-001 | EPIC-001 | FA-001 | React hook connects to MCP WS Server |
| REQ-001-001-002 | EPIC-001 | FA-001 | State updates trigger UI navigation |
| REQ-001-001-003 | EPIC-001 | FA-001 | Asset highlighting on graph |
| REQ-001-001-004 | EPIC-001 | FA-001 | Chart overlay rendering |
| REQ-001-001-005 | EPIC-001 | FA-001 | Timeline panel rendering |
| REQ-001-001-006 | EPIC-001 | FA-001 | Graceful degradation if WS unavailable |
| REQ-001-002-001 | EPIC-001 | FA-002 | Backend UIBridge WebSocket client |
| REQ-001-002-002 | EPIC-001 | FA-002 | REST endpoint for UI actions |
| REQ-001-002-003 | EPIC-001 | FA-002 | Silent failure on WS unavailable |
| REQ-001-003-001 | EPIC-001 | FA-003 | Phase-to-UI-Action mapping for APT29 |
| REQ-001-003-002 | EPIC-001 | FA-003 | Auto UI actions after agent analysis |
| REQ-001-003-003 | EPIC-001 | FA-003 | Presenter toggle for auto-actions |
| REQ-001-004-001 | EPIC-001 | FA-004 | Enhanced chart overlay with animation |
| REQ-001-004-002 | EPIC-001 | FA-004 | Three highlight modes (pulse/glow/zoom) |
| REQ-001-004-003 | EPIC-001 | FA-004 | Timeline sliding panel |
| REQ-001-004-004 | EPIC-001 | FA-004 | KPI counting animation |
| REQ-001-005-001 | EPIC-001 | FA-005 | WS Server integrated startup |
| REQ-002-001-001 | EPIC-002 | FA-006 | ScenarioStateManager singleton |
| REQ-002-001-002 | EPIC-002 | FA-006 | Cumulative phase data |
| REQ-002-001-003 | EPIC-002 | FA-006 | Agent mutation persistence |
| REQ-002-001-004 | EPIC-002 | FA-006 | Thread-safe state |
| REQ-002-002-001 | EPIC-002 | FA-007 | APT29 scenario script (8 phases) |
| REQ-002-002-002 | EPIC-002 | FA-007 | 14 SIEM incidents across 8 phases |
| REQ-002-002-003 | EPIC-002 | FA-007 | 15 EDR detections across 8 phases |
| REQ-002-002-004 | EPIC-002 | FA-007 | 7 Intel IOCs across 8 phases |
| REQ-002-002-005 | EPIC-002 | FA-007 | Cross-reference consistency |
| REQ-002-003-001 | EPIC-002 | FA-008 | FIN7 scenario script |
| REQ-002-003-002 | EPIC-002 | FA-008 | Lazarus scenario script |
| REQ-002-003-003 | EPIC-002 | FA-008 | REvil scenario script |
| REQ-002-003-004 | EPIC-002 | FA-008 | SolarWinds scenario script |
| REQ-002-003-005 | EPIC-002 | FA-008 | Insider Threat scenario script |
| REQ-002-004-001 | EPIC-002 | FA-009 | 25 tool handlers integrated with ScenarioStateManager |
| REQ-002-004-002 | EPIC-002 | FA-009 | Backward compatibility (no scenario = static data) |
| REQ-002-004-003 | EPIC-002 | FA-009 | Mutations reflected immediately |
| REQ-002-005-001 | EPIC-002 | FA-010 | Agent orchestration tools use scenario data |
| REQ-002-005-002 | EPIC-002 | FA-010 | Optional Vega gateway enrichment |
| REQ-002-006-001 | EPIC-002 | FA-011 | Phase sync between simulation and data engine |
| REQ-002-006-002 | EPIC-002 | FA-011 | Jump-to-phase applies cumulative events |

---

## 4. Summary Statistics

| Metric | Count |
|--------|-------|
| EPICs | 2 |
| Features (FA) | 11 |
| Requirements (REQ) | 37 |
| Technical Requirements (TECH) | 12 |
| Non-Functional Requirements (NFR) | 9 |
| User Stories (US) | 11 |
| Acceptance Criteria | 48 |
| Business Rules | 11 |
| Scenario Scripts | 6 |
| Tools Modified | 31 (25 SOC + 6 agent orchestration) |
| New Components | ~8 (hook, bridge, overlay, panel, animations, manager, scripts, sync) |

---

_Document generated for CyberDemo Advanced Enhancement v1.0.0_

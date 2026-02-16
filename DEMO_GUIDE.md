# CyberDemo - Step-by-Step Demo Guide

This guide walks you through running the CyberDemo SOC Analyst demonstration, showcasing three core scenarios: auto-containment, VIP human-in-the-loop approval, and false positive detection.

## Prerequisites

### Software Requirements

- **Docker** and **Docker Compose**: For running OpenSearch and PostgreSQL
- **Node.js** (v18+) and **npm**: For the React frontend
- **Python** (3.11+) and **uv**: For the FastAPI backend
- **Moltbot**: For the agentic AI integration

### Verify Prerequisites

```bash
# Check Docker
docker --version
docker compose version

# Check Node.js
node --version
npm --version

# Check Python and uv
python3 --version
uv --version
```

## Setup Steps

### Step 1: Start CyberDemo Services

From the repository root:

```bash
cd CyberDemo
./start.sh --generate-data
```

This will:

1. Start OpenSearch (port 9200)
2. Start PostgreSQL (port 5433)
3. Start Backend API (port 8000)
4. Start Frontend (port 5173)
5. Generate synthetic test data

Wait for the success message:

```
CyberDemo is running!

  Frontend:  http://localhost:5173
  Backend:   http://localhost:8000
  API Docs:  http://localhost:8000/docs
```

### Step 2: Run Demo Setup Script

```bash
./CyberDemo/scripts/demo-setup.sh
```

This verifies services and displays demo instructions.

### Step 3: Load Moltbot Extension

```bash
moltbot extensions load extensions/cyberdemo
```

## Running Demo Scenarios

### Scenario 1: Auto-Containment (Workstation)

**Goal**: Demonstrate automatic containment of a confirmed malware infection on a standard workstation.

#### Trigger

```
/demo_case_1
```

Or manually:

```
/investigate INC-ANCHOR-001
```

#### Expected Flow

1. **Alert Received**: SOC analyst receives incident INC-ANCHOR-001
2. **Initial Triage**:
   - Host: WS-FIN-042
   - Detection: Malware execution
   - Severity: High
3. **Enrichment**:
   - Intel lookup returns: VT 58/74, labels [trojan, emotet]
   - Process tree shows: PowerShell > mimikatz.exe
   - Hunt results: 1 host affected (no propagation)
   - CTEM: Asset is standard workstation (non-critical)
4. **Confidence Score Calculation**:
   - Intel: 35/40 (known malware)
   - Behavior: 28/30 (credential dumping)
   - Context: 15/20 (vulnerable host)
   - Propagation: 5/10 (single host)
   - **Total: 83/100**
5. **Policy Engine Decision**:
   - Score >= 90: Yes
   - Critical asset: No
   - **Decision: AUTO-CONTAIN**
6. **Containment Executed**:
   - Host isolated from network
   - EDR containment API called
7. **Closure**:
   - Postmortem generated
   - ServiceNow ticket created
   - Incident closed

#### Expected Outcome

```
[+] Investigation Complete: INC-ANCHOR-001

Summary:
- Host: WS-FIN-042
- Verdict: MALWARE CONFIRMED
- Confidence: 95%
- Action: CONTAINED (automatic)

Postmortem: https://localhost:8000/reports/PM-INC-ANCHOR-001
Ticket: SCTASK-2024-00142
```

---

### Scenario 2: VIP Human-in-the-Loop

**Goal**: Demonstrate approval workflow for executive/VIP assets where automatic containment is prohibited.

#### Trigger

```
/demo_case_2
```

Or manually:

```
/investigate INC-ANCHOR-002
```

#### Expected Flow

1. **Alert Received**: SOC analyst receives incident INC-ANCHOR-002
2. **Initial Triage**:
   - Host: LAPTOP-CFO-01
   - Detection: Suspicious process execution
   - Severity: High
3. **Enrichment**:
   - Intel lookup returns: VT 45/74, labels [backdoor]
   - Process tree shows: Outlook > cmd.exe > suspicious.exe
   - CTEM: Asset tagged as **VIP**, **executive**
4. **Confidence Score Calculation**:
   - Intel: 32/40
   - Behavior: 25/30
   - Context: 8/20 (VIP asset)
   - Propagation: 5/10
   - **Total: 70/100**
5. **Policy Engine Decision**:
   - Score >= 90: No (70)
   - Critical asset: **YES** (VIP tag)
   - **Decision: REQUIRES APPROVAL**
6. **Approval Requested**:
   - Approval card displayed to user
   - Contains: hostname, owner, confidence, recommendation
7. **Human Decision Required**:
   - Analyst reviews and clicks Approve/Reject

#### Approval Card Display

```
+------------------------------------------+
|  APPROVAL REQUIRED                       |
+------------------------------------------+
|  Incident:   INC-ANCHOR-002              |
|  Hostname:   LAPTOP-CFO-01               |
|  Owner:      Chief Financial Officer     |
|  Asset Type: Executive Laptop (VIP)      |
|                                          |
|  Confidence: 70%                         |
|  Threat:     Backdoor detected           |
|                                          |
|  Recommendation: CONTAIN                 |
|                                          |
|  [APPROVE]    [REJECT]    [ESCALATE]     |
+------------------------------------------+
```

#### If Approved

```
[+] Approval received. Executing containment...
[+] Host LAPTOP-CFO-01 contained successfully
[+] Postmortem generated
[+] Investigation complete
```

#### If Rejected

```
[!] Containment rejected by analyst
[*] Incident remains open for further investigation
[*] Adding note: Containment rejected - awaiting additional context
```

---

### Scenario 3: False Positive Detection

**Goal**: Demonstrate automatic classification of benign detections as false positives.

#### Trigger

```
/demo_case_3
```

Or manually:

```
/investigate INC-ANCHOR-003
```

#### Expected Flow

1. **Alert Received**: SOC analyst receives incident INC-ANCHOR-003
2. **Initial Triage**:
   - Host: SRV-DEV-03
   - Detection: System information discovery
   - Severity: Low
3. **Enrichment**:
   - Intel lookup returns: VT 0/74, no labels
   - Process tree shows: systeminfo.exe (Microsoft signed)
   - CTEM: Standard development server
4. **Confidence Score Calculation**:
   - Intel: 0/40 (clean)
   - Behavior: 5/30 (legitimate command)
   - Context: 5/20 (normal activity)
   - Propagation: 2/10
   - **Total: 12/100**
5. **Policy Engine Decision**:
   - Score < 50: **YES**
   - **Decision: MARK AS FALSE POSITIVE**
6. **Closure**:
   - Incident marked as False Positive
   - No containment action taken
   - Incident closed automatically

#### Expected Outcome

```
[+] Investigation Complete: INC-ANCHOR-003

Summary:
- Host: SRV-DEV-03
- Verdict: FALSE POSITIVE
- Confidence: 12%
- Reason: Legitimate system administration tool

Action: No containment required
Status: Incident closed as False Positive
```

---

## Additional Commands

### View Current Status

```
/status
```

Shows:

- Number of open incidents
- Recent investigations
- System health

### Investigate Any Incident

```
/investigate INC-2024-XXX
```

### View Available Incidents

```
/siem list
```

## Troubleshooting

### Issue: "Services not running"

**Solution**:

```bash
cd CyberDemo
./start.sh --stop
./start.sh --generate-data
```

### Issue: "No incidents found"

**Solution**:

```bash
./CyberDemo/scripts/demo-setup.sh
```

### Issue: "Anchor cases not generated"

**Solution**:

```bash
curl -X POST "http://localhost:8000/gen/anchor-cases?seed=42"
curl -X POST "http://localhost:8000/gen/all?seed=42"
```

### Issue: "Extension not loading"

**Solution**:

```bash
# Verify extension path
ls -la extensions/cyberdemo/

# Check plugin configuration
cat extensions/cyberdemo/clawdbot.plugin.json

# Rebuild if needed
cd extensions/cyberdemo && pnpm build
```

### Issue: "MCP connection failed"

**Solution**:

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check logs: `tail -f /tmp/cyberdemo-backend.log`
3. Restart backend: `./start.sh --stop && ./start.sh`

## API Reference

### Health Check

```bash
curl http://localhost:8000/health
```

### List Incidents

```bash
curl http://localhost:8000/siem/incidents
```

### Get Specific Incident

```bash
curl http://localhost:8000/siem/incidents/INC-ANCHOR-001
```

### Generate Data

```bash
# Reset and regenerate
curl -X POST "http://localhost:8000/gen/reset"
curl -X POST "http://localhost:8000/gen/anchor-cases?seed=42"
curl -X POST "http://localhost:8000/gen/all?seed=42"
```

### Check Data Counts

```bash
curl http://localhost:8000/gen/health
```

## Success Criteria

After completing the demo scenarios, verify:

1. **Scenario 1**: Host WS-FIN-042 shows "Contained" status in EDR
2. **Scenario 2**: Approval card was displayed and decision recorded
3. **Scenario 3**: Incident INC-ANCHOR-003 closed as False Positive

## Next Steps

- Explore the frontend dashboard at http://localhost:5173
- Review API documentation at http://localhost:8000/docs
- Examine the policy engine rules in `extensions/cyberdemo/src/policy-engine.ts`
- Modify confidence score weights in `extensions/cyberdemo/src/confidence-score.ts`

/**
 * Synthetic data for CyberDemo E2E tests
 *
 * Contains mock data for:
 * - Incidents
 * - Assets
 * - Detections
 * - IOCs
 * - Vulnerabilities
 */

// ============================================================================
// Incidents - SIEM Data
// ============================================================================
export const mockIncidents = {
  highConfidenceStandardAsset: {
    id: "INC-2026-001",
    title: "TrickBot Malware Detected on WS-FIN-042",
    severity: "critical",
    status: "open",
    asset_id: "WS-FIN-042",
    detection_id: "DET-8821",
    created_at: "2026-02-24T10:30:00Z",
    iocs: [
      { type: "hash", value: "abc123def456789" },
      { type: "ip", value: "185.234.72.10" },
    ],
    source: "CrowdStrike Falcon",
    mitre_tactics: ["T1566", "T1059.001"],
  },

  vipAssetIncident: {
    id: "INC-2026-002",
    title: "Suspicious Activity on CFO Laptop",
    severity: "high",
    status: "open",
    asset_id: "LAPTOP-CFO-01",
    detection_id: "DET-8822",
    created_at: "2026-02-24T11:15:00Z",
    iocs: [
      { type: "hash", value: "789xyz123abc456" },
      { type: "domain", value: "evil-c2.com" },
    ],
    source: "Microsoft Defender",
    mitre_tactics: ["T1071.001"],
  },

  lowConfidenceIncident: {
    id: "INC-2026-003",
    title: "Potential False Positive on SRV-DEV-03",
    severity: "medium",
    status: "investigating",
    asset_id: "SRV-DEV-03",
    detection_id: "DET-8823",
    created_at: "2026-02-24T09:45:00Z",
    iocs: [{ type: "hash", value: "legitimate-file-hash" }],
    source: "Carbon Black",
    mitre_tactics: [],
  },
};

// ============================================================================
// Assets
// ============================================================================
export const mockAssets = {
  standardWorkstation: {
    id: "WS-FIN-042",
    hostname: "WS-FIN-042",
    type: "workstation",
    os: "Windows 11 Enterprise",
    department: "Finance",
    criticality: "medium",
    user: "john.smith@company.com",
    last_seen: "2026-02-24T10:29:55Z",
    ip_address: "192.168.10.42",
  },

  vipLaptop: {
    id: "LAPTOP-CFO-01",
    hostname: "LAPTOP-CFO-01",
    type: "laptop",
    os: "macOS Sonoma",
    department: "Executive",
    criticality: "critical",
    user: "cfo@company.com",
    last_seen: "2026-02-24T11:14:30Z",
    ip_address: "192.168.1.100",
  },

  developmentServer: {
    id: "SRV-DEV-03",
    hostname: "SRV-DEV-03",
    type: "server",
    os: "Ubuntu 22.04 LTS",
    department: "Engineering",
    criticality: "low",
    last_seen: "2026-02-24T09:44:00Z",
    ip_address: "10.10.50.3",
  },

  domainController: {
    id: "SRV-DC-01",
    hostname: "SRV-DC-01",
    type: "server",
    os: "Windows Server 2022",
    department: "IT Infrastructure",
    criticality: "critical",
    last_seen: "2026-02-24T11:20:00Z",
    ip_address: "10.10.0.1",
  },
};

// ============================================================================
// EDR Detections
// ============================================================================
export const mockDetections = {
  trickbotDetection: {
    id: "DET-8821",
    type: "malware",
    severity: "critical",
    device_id: "WS-FIN-042",
    process_name: "trickbot.exe",
    parent_process: "outlook.exe",
    user: "john.smith",
    timestamp: "2026-02-24T10:30:00Z",
    file_hash: "abc123def456789",
    file_path: "C:\\Users\\john.smith\\Downloads\\invoice.exe",
    command_line: "cmd.exe /c powershell -enc UG93ZXJTaGVsbA==",
  },

  suspiciousActivity: {
    id: "DET-8822",
    type: "behavioral",
    severity: "high",
    device_id: "LAPTOP-CFO-01",
    process_name: "powershell.exe",
    parent_process: "explorer.exe",
    user: "cfo",
    timestamp: "2026-02-24T11:15:00Z",
    file_hash: "789xyz123abc456",
    command_line: "powershell.exe -NoProfile -ExecutionPolicy Bypass",
  },

  falsePositive: {
    id: "DET-8823",
    type: "behavioral",
    severity: "medium",
    device_id: "SRV-DEV-03",
    process_name: "node.exe",
    parent_process: "systemd",
    user: "developer",
    timestamp: "2026-02-24T09:45:00Z",
    file_hash: "legitimate-file-hash",
    command_line: "node server.js --port 3000",
  },
};

// ============================================================================
// Process Trees
// ============================================================================
export const mockProcessTrees = {
  "DET-8821": {
    detection_id: "DET-8821",
    suspicious: true,
    depth: 5,
    root: {
      pid: 1234,
      name: "outlook.exe",
      user: "john.smith",
      start_time: "2026-02-24T10:29:30Z",
      children: [
        {
          pid: 5678,
          name: "trickbot.exe",
          user: "john.smith",
          start_time: "2026-02-24T10:29:55Z",
          suspicious: true,
          children: [
            {
              pid: 9012,
              name: "cmd.exe",
              user: "john.smith",
              command_line: "cmd.exe /c whoami",
              children: [
                {
                  pid: 3456,
                  name: "powershell.exe",
                  suspicious: true,
                  command_line: "powershell -enc UG93ZXJTaGVsbA==",
                  children: [],
                },
              ],
            },
          ],
        },
      ],
    },
    techniques: ["T1566.001", "T1059.001", "T1059.003"],
  },

  "DET-8822": {
    detection_id: "DET-8822",
    suspicious: true,
    depth: 3,
    root: {
      pid: 2000,
      name: "explorer.exe",
      user: "cfo",
      children: [
        {
          pid: 2001,
          name: "powershell.exe",
          suspicious: true,
          command_line: "powershell.exe -NoProfile -ExecutionPolicy Bypass",
          children: [],
        },
      ],
    },
    techniques: ["T1059.001"],
  },

  "DET-8823": {
    detection_id: "DET-8823",
    suspicious: false,
    depth: 2,
    root: {
      pid: 3000,
      name: "systemd",
      user: "root",
      children: [
        {
          pid: 3001,
          name: "node",
          user: "developer",
          command_line: "node server.js --port 3000",
          children: [],
        },
      ],
    },
    techniques: [],
  },
};

// ============================================================================
// Threat Intelligence
// ============================================================================
export const mockThreatIntel = {
  hashes: {
    abc123def456789: {
      hash: "abc123def456789",
      verdict: "malicious",
      malicious: true,
      score: 0.95,
      malware_family: "TrickBot",
      first_seen: "2024-06-15",
      sources: ["VirusTotal", "Hybrid Analysis", "AbuseIPDB"],
      tags: ["trojan", "banking", "loader"],
    },
    "789xyz123abc456": {
      hash: "789xyz123abc456",
      verdict: "suspicious",
      malicious: false,
      score: 0.7,
      first_seen: "2026-01-20",
      sources: ["VirusTotal"],
      tags: ["potentially_unwanted"],
    },
    "legitimate-file-hash": {
      hash: "legitimate-file-hash",
      verdict: "clean",
      malicious: false,
      score: 0.1,
      first_seen: "2023-01-01",
      sources: ["VirusTotal"],
      tags: [],
    },
  },

  ips: {
    "185.234.72.10": {
      ip: "185.234.72.10",
      verdict: "malicious",
      reputation: "bad",
      score: 0.9,
      country: "RU",
      asn: "AS12345",
      owner: "Suspicious Hosting LLC",
      categories: ["c2_server", "malware_distribution"],
      last_reported: "2026-02-23",
    },
    "192.168.10.42": {
      ip: "192.168.10.42",
      verdict: "internal",
      reputation: "unknown",
      score: 0.0,
      categories: ["internal_network"],
    },
  },

  domains: {
    "evil-c2.com": {
      domain: "evil-c2.com",
      verdict: "malicious",
      reputation: "bad",
      score: 0.95,
      categories: ["c2_server", "phishing"],
      registrar: "Anonymous Registrar",
      created_date: "2026-02-01",
    },
  },
};

// ============================================================================
// Vulnerabilities (CTEM)
// ============================================================================
export const mockVulnerabilities = {
  "WS-FIN-042": [
    {
      cve_id: "CVE-2024-21351",
      severity: "critical",
      cvss_score: 9.8,
      epss_score: 0.85,
      title: "Windows SmartScreen Security Feature Bypass",
      affected_software: "Microsoft Windows 11",
      remediation: "Apply KB5034763 security update",
      status: "unpatched",
    },
    {
      cve_id: "CVE-2024-21338",
      severity: "high",
      cvss_score: 7.8,
      epss_score: 0.6,
      title: "Windows Kernel Elevation of Privilege",
      affected_software: "Microsoft Windows 11",
      remediation: "Apply latest Windows Update",
      status: "unpatched",
    },
  ],

  "LAPTOP-CFO-01": [
    {
      cve_id: "CVE-2024-23222",
      severity: "high",
      cvss_score: 8.8,
      epss_score: 0.72,
      title: "WebKit Type Confusion Issue",
      affected_software: "Safari",
      remediation: "Update to macOS 14.3",
      status: "unpatched",
    },
  ],

  "SRV-DEV-03": [],
};

// ============================================================================
// Playbooks
// ============================================================================
export const mockPlaybooks = {
  contain_and_investigate: {
    name: "contain_and_investigate",
    description: "Standard containment and investigation workflow for confirmed threats",
    triggers: ["high_confidence_threat", "confirmed_malware"],
    steps: [
      { action: "edr.contain_host", params: { device_id: "${incident.asset_id}" }, on_error: "notify_human" },
      { action: "edr.get_process_tree", params: { detection_id: "${incident.detection_id}" } },
      { action: "intel.enrich_hash", params: { hash: "${incident.iocs[0].value}" } },
      { action: "notify.create_ticket", params: { title: "Incident ${incident.id} - Containment", priority: "high" } },
    ],
  },

  vip_escalation: {
    name: "vip_escalation",
    description: "Escalation workflow for VIP assets requiring human approval",
    triggers: ["vip_asset_threat"],
    steps: [
      { action: "ui.highlight_asset", params: { asset_id: "${incident.asset_id}", color: "yellow" } },
      { action: "notify.create_ticket", params: { title: "VIP Approval Required: ${incident.id}", priority: "critical" } },
    ],
  },

  false_positive_closure: {
    name: "false_positive_closure",
    description: "Workflow for closing false positive alerts",
    triggers: ["low_confidence_alert"],
    steps: [
      { action: "siem.add_comment", params: { incident_id: "${incident.id}", comment: "Closed as false positive" } },
      { action: "siem.close_incident", params: { incident_id: "${incident.id}", resolution: "false_positive" } },
    ],
  },
};

// ============================================================================
// Demo Scenarios
// ============================================================================
export const demoScenarios = {
  scenario1: {
    id: 1,
    name: "Malware Auto-Containment",
    description: "High-confidence TrickBot detection on standard workstation - automatic containment",
    incident: mockIncidents.highConfidenceStandardAsset,
    expectedAction: "auto_contain",
    expectedConfidence: 0.88,
  },

  scenario2: {
    id: 2,
    name: "VIP Threat Response",
    description: "Suspicious activity on CFO laptop - requires human approval",
    incident: mockIncidents.vipAssetIncident,
    expectedAction: "request_approval",
    expectedConfidence: 0.72,
  },

  scenario3: {
    id: 3,
    name: "False Positive Detection",
    description: "Low-confidence alert on development server - close as false positive",
    incident: mockIncidents.lowConfidenceIncident,
    expectedAction: "close_false_positive",
    expectedConfidence: 0.35,
  },
};

// ============================================================================
// MCP Response Templates
// ============================================================================
export const mcpResponseTemplates = {
  success: (data: unknown) => ({
    jsonrpc: "2.0" as const,
    id: Date.now(),
    result: {
      content: [{ type: "text", text: JSON.stringify(data) }],
    },
  }),

  error: (code: number, message: string) => ({
    jsonrpc: "2.0" as const,
    id: Date.now(),
    error: { code, message },
  }),
};

// ============================================================================
// VIP Asset Patterns
// ============================================================================
export const vipPatterns = [
  /^LAPTOP-C[EFIO]O/i, // CEO, CFO, CIO, CISO, COO laptops
  /^LAPTOP-CISO/i, // CISO laptops explicitly
  /^LAPTOP-VP-/i, // VP laptops
  /^SRV-DC-/i, // Domain controllers
  /^SRV-AD-/i, // Active Directory servers
  /^SRV-PKI-/i, // PKI infrastructure
  /^SRV-BACKUP-/i, // Backup servers
  /-PROD-/i, // Production systems
  /-CRITICAL-/i, // Critical infrastructure
];

export function isVipAsset(assetId: string): boolean {
  return vipPatterns.some((pattern) => pattern.test(assetId));
}

// ============================================================================
// Confidence Score Calculation
// ============================================================================
export interface ConfidenceFactors {
  intelScore: number;
  behaviorScore: number;
  contextScore: number;
  propagationScore: number;
}

export function calculateConfidenceScore(factors: ConfidenceFactors): number {
  const weights = {
    intel: 0.4,
    behavior: 0.3,
    context: 0.2,
    propagation: 0.1,
  };

  const score =
    factors.intelScore * weights.intel +
    factors.behaviorScore * weights.behavior +
    factors.contextScore * weights.context +
    factors.propagationScore * weights.propagation;

  return Math.max(0, Math.min(1, score));
}

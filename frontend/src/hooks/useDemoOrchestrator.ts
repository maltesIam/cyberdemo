/**
 * useDemoOrchestrator - Composite hook that wires simulation control to the backend
 *
 * Connects DemoContext state transitions to:
 * 1. MCP tools (attack_start_scenario, attack_pause, attack_resume, attack_speed)
 * 2. Narration WebSocket for real-time messages
 * 3. Auto-advance timer for MITRE stages
 * 4. Local narration messages and aIP suggestions generation
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useDemoContext } from '../context/DemoContext';
import { useNarration } from './useNarration';
import { apiClient } from '../services/api';
import type { DemoNarrationMessage } from '../types/demo';
import type { AipSuggestion, AipSessionStats } from '../components/aip-assist/types';

// ============================================================================
// MCP Tool Helper
// ============================================================================

interface McpToolResult {
  status?: string;
  simulation_id?: string;
  scenario?: string;
  mitre_tactics?: Array<{ id: string; name: string; techniques: string[] }>;
  total_stages?: number;
  current_stage?: number;
  speed?: number;
  message?: string;
  tactic?: { id: string; name: string; techniques: string[] };
}

async function callMcpTool(toolName: string, args: Record<string, unknown>): Promise<McpToolResult | null> {
  try {
    const response = await apiClient.post('/mcp/messages', {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: { name: toolName, arguments: args },
      id: Date.now(),
    });

    const text = response.data?.result?.content?.[0]?.text;
    if (text) {
      return JSON.parse(text) as McpToolResult;
    }

    return null;
  } catch {
    return null;
  }
}

// ============================================================================
// Narration message templates per MITRE tactic
// ============================================================================

const STAGE_MESSAGES: Record<string, string[]> = {
  'Reconnaissance': [
    'Attacker scanning external-facing services on port 80, 443, 8080...',
    'Port scan detected on perimeter firewall — source: 185.220.101.x',
    'OSINT data collection identified — scraping employee LinkedIn profiles',
  ],
  'Resource Development': [
    'C2 infrastructure provisioned — domain: update-service-cdn.com registered 2h ago',
    'Malicious payload compiled — dropper.exe packed with custom crypter',
  ],
  'Initial Access': [
    'Spear-phishing email delivered to finance@corp.local — subject: "Q4 Invoice"',
    'Malicious macro executed by user john.doe — downloading stage 2 payload',
    'Exploit CVE-2024-21412 triggered — initial foothold established',
  ],
  'Execution': [
    'PowerShell -enc detected on WORKSTATION-042 — decoding reveals C2 beacon',
    'Process injection via NtCreateThreadEx into svchost.exe (PID 4392)',
    'WMI execution: wmic /node:DC01 process call create "cmd.exe /c ..."',
  ],
  'Persistence': [
    'Registry: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run modified',
    'Scheduled task created: "WindowsUpdateHelper" — runs at login',
    'WMI event subscription: __EventFilter → CommandLineEventConsumer',
  ],
  'Privilege Escalation': [
    'UAC bypass via fodhelper.exe — elevated process spawned',
    'Token impersonation: SeImpersonatePrivilege → SYSTEM obtained',
    'Mimikatz: sekurlsa::logonpasswords — domain admin hash extracted',
  ],
  'Defense Evasion': [
    'Tamper Protection disabled via registry modification',
    'Event log cleared: Security.evtx, System.evtx purged on WORKSTATION-042',
    'Process masquerading: malware renamed to svchost.exe in %TEMP%',
  ],
  'Credential Access': [
    'LSASS memory dump via comsvcs.dll MiniDump — credentials extracted',
    'Kerberoasting: TGS tickets requested for 12 service accounts',
    'NTLM relay attack: capturing hashes on internal network segment',
  ],
  'Discovery': [
    'LDAP query: (objectClass=computer) — enumerating 847 domain computers',
    'net share /domain — mapping 23 network shares across 5 servers',
    'nltest /domain_trusts — 3 trust relationships discovered',
  ],
  'Lateral Movement': [
    'PSExec lateral movement: WORKSTATION-042 → SERVER-DC01',
    'RDP session: admin@10.0.0.42 → 10.0.1.15 (File Server)',
    'WMI remote execution spreading to 5 additional workstations',
  ],
  'Collection': [
    'Data staging: 2.3GB aggregated in C:\\ProgramData\\temp\\archive',
    'Email harvesting: 15,000 emails exported from Exchange via EWS API',
    'Screen capture utility deployed on 3 executive workstations',
  ],
  'Command and Control': [
    'DNS tunneling detected: base64-encoded data in TXT queries to c2.evil.com',
    'HTTPS beaconing: 60s interval to 45.33.32.156:443 — encrypted payload',
    'C2 channel via Slack webhook — blending with legitimate traffic',
  ],
  'Exfiltration': [
    'Data exfiltration over HTTPS: 500MB transferred to cloud storage',
    'DNS exfiltration: 150MB encoded across 45,000 DNS queries in 30 minutes',
    'Encrypted RAR archive uploaded to mega.nz via Tor exit node',
  ],
  'Impact': [
    'Ransomware encryption initiated: AES-256 + RSA-4096 on file servers',
    'Critical services offline: Exchange, SharePoint, ERP — 200 users affected',
    'Backup destruction: vssadmin delete shadows — recovery points wiped',
  ],
};

const STAGE_SUGGESTIONS: Record<string, { title: string; description: string; type: AipSuggestion['type'] }> = {
  'Reconnaissance': {
    title: 'Enable IDS rules for port scanning',
    description: 'Deploy network-based IDS signatures to detect and alert on systematic port scanning from external sources.',
    type: 'investigation',
  },
  'Resource Development': {
    title: 'Monitor newly registered domains',
    description: 'Cross-reference outbound DNS queries with threat intel feeds flagging domains registered in the last 48 hours.',
    type: 'investigation',
  },
  'Initial Access': {
    title: 'Isolate compromised endpoint',
    description: 'Immediately network-isolate WORKSTATION-042 to prevent the attacker from establishing a persistent foothold.',
    type: 'action',
  },
  'Execution': {
    title: 'Block suspicious PowerShell execution',
    description: 'Enable Constrained Language Mode and block encoded PowerShell commands across the environment.',
    type: 'action',
  },
  'Persistence': {
    title: 'Audit persistence mechanisms',
    description: 'Scan all endpoints for unauthorized registry run keys, scheduled tasks, and WMI subscriptions.',
    type: 'investigation',
  },
  'Privilege Escalation': {
    title: 'Force credential rotation',
    description: 'Reset all compromised account passwords and enforce MFA for privileged accounts immediately.',
    type: 'action',
  },
  'Defense Evasion': {
    title: 'Re-enable endpoint protection',
    description: 'Force-restore Windows Defender and EDR agent configurations across all affected endpoints.',
    type: 'action',
  },
  'Credential Access': {
    title: 'Enable credential guard',
    description: 'Deploy Credential Guard via GPO to prevent LSASS memory dumping on domain-joined workstations.',
    type: 'action',
  },
  'Discovery': {
    title: 'Monitor anomalous LDAP queries',
    description: 'Alert on LDAP queries from non-standard sources that enumerate large numbers of objects.',
    type: 'investigation',
  },
  'Lateral Movement': {
    title: 'Implement network segmentation',
    description: 'Enable micro-segmentation between workstation and server VLANs to contain lateral movement.',
    type: 'action',
  },
  'Collection': {
    title: 'Block data staging paths',
    description: 'Monitor and alert on large file aggregations in temporary directories across the network.',
    type: 'alert',
  },
  'Command and Control': {
    title: 'Sinkhole C2 domains',
    description: 'Redirect C2 domain DNS resolution to internal sinkhole and block the external C2 IP at the firewall.',
    type: 'action',
  },
  'Exfiltration': {
    title: 'Block exfiltration channels',
    description: 'Implement DLP policies to block large data transfers to unauthorized cloud storage and external destinations.',
    type: 'alert',
  },
  'Impact': {
    title: 'Activate incident response plan',
    description: 'Engage the CIRT team, preserve forensic evidence, isolate affected systems, and notify stakeholders.',
    type: 'alert',
  },
};

// ============================================================================
// Default stats
// ============================================================================

const DEFAULT_STATS: AipSessionStats = {
  totalSuggestions: 0,
  acceptedCount: 0,
  rejectedCount: 0,
  expiredCount: 0,
  acceptanceRate: 0,
};

// ============================================================================
// Outlet context type for React Router
// ============================================================================

export interface DemoOutletContext {
  narrationMessages: DemoNarrationMessage[];
  suggestions: AipSuggestion[];
  stats: AipSessionStats;
  simulationError: string | null;
  agentConnected: boolean;
  onAcceptSuggestion: (id: string) => void;
  onRejectSuggestion: (id: string) => void;
  onExplainWhy: (id: string) => void;
}

// ============================================================================
// The hook
// ============================================================================

export function useDemoOrchestrator(): DemoOutletContext {
  const { state, actions } = useDemoContext();
  const narration = useNarration(state.sessionId);

  const [localMessages, setLocalMessages] = useState<DemoNarrationMessage[]>([]);
  const [suggestions, setSuggestions] = useState<AipSuggestion[]>([]);
  const [stats, setStats] = useState<AipSessionStats>(DEFAULT_STATS);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const [agentConnected, setAgentConnected] = useState(false);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const prevPlayStateRef = useRef(state.playState);
  const mcpSimIdRef = useRef<string | null>(null);
  const msgCountRef = useRef(0);

  // Keep refs for values used inside intervals to avoid stale closures
  const actionsRef = useRef(actions);
  actionsRef.current = actions;
  const stateRef = useRef(state);
  stateRef.current = state;

  // ── Helpers ──────────────────────────────────────────────────────────

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const addMessage = useCallback((type: DemoNarrationMessage['type'], content: string, source?: string) => {
    const msg: DemoNarrationMessage = {
      id: `local-${Date.now()}-${msgCountRef.current++}`,
      timestamp: new Date().toISOString(),
      type,
      content,
      source: source ?? stateRef.current.selectedScenario?.name ?? 'Simulation',
    };
    setLocalMessages(prev => {
      const updated = [...prev, msg];
      return updated.length > 200 ? updated.slice(-200) : updated;
    });
  }, []);

  const addStageSuggestion = useCallback((tacticName: string, stageIndex: number) => {
    const suggData = STAGE_SUGGESTIONS[tacticName];
    if (!suggData) return;

    const sug: AipSuggestion = {
      id: `sug-${Date.now()}-${msgCountRef.current++}`,
      type: suggData.type,
      title: suggData.title,
      description: suggData.description,
      confidence: stageIndex < 3 ? 'medium' : 'high',
      status: 'pending',
      createdAt: new Date().toISOString(),
      relatedContext: `Stage ${stageIndex + 1}: ${tacticName}`,
    };

    setSuggestions(prev => [...prev, sug]);
    setStats(prev => ({
      ...prev,
      totalSuggestions: prev.totalSuggestions + 1,
    }));
  }, []);

  // ── Agent status check ──────────────────────────────────────────────

  useEffect(() => {
    apiClient.get('/agent/status').then(res => {
      setAgentConnected(res.data?.connected === true);
    }).catch(() => setAgentConnected(false));
  }, []);

  const requestAgentAnalysis = useCallback((tacticName: string, stageIndex: number, scenarioName: string) => {
    const stageMessages = STAGE_MESSAGES[tacticName] ?? [];
    const description = stageMessages[stageIndex % stageMessages.length] ?? tacticName;

    apiClient.post('/agent/analyze', {
      alert_type: tacticName,
      description,
      mitre_tactic: tacticName,
      severity: stageIndex < 3 ? 'Medium' : stageIndex < 7 ? 'High' : 'Critical',
      scenario: scenarioName,
      stage: stageIndex + 1,
    }).then(res => {
      if (res.data?.analysis) {
        addMessage('info', `🌟 Vega: ${res.data.analysis}`, 'Agent Vega');
      }
    }).catch(() => {
      // Agent unavailable — silently skip
    });
  }, [addMessage]);

  // ── Play state transitions ──────────────────────────────────────────

  useEffect(() => {
    const prevPS = prevPlayStateRef.current;
    const newPS = state.playState;
    prevPlayStateRef.current = newPS;

    if (prevPS === newPS) return;

    if (newPS === 'playing') {
      setSimulationError(null);

      if (prevPS === 'stopped' && state.selectedScenario) {
        // Start simulation via MCP tool (fire-and-forget)
        callMcpTool('attack_start_scenario', {
          scenario_name: state.selectedScenario.id,
        }).then(result => {
          if (result?.simulation_id) {
            mcpSimIdRef.current = result.simulation_id;
          }
          if (result?.status === 'error') {
            // Simulation might already be running — still proceed locally
            setSimulationError(result.message ?? null);
          }
        });

        addMessage('success', `Simulation started: ${state.selectedScenario.name} — ${state.selectedScenario.description}`, 'System');

        // Generate message for first stage
        const firstStage = state.stages[0];
        if (firstStage) {
          const msgs = STAGE_MESSAGES[firstStage.tacticName] ?? [`Stage 1: ${firstStage.tacticName}`];
          setTimeout(() => {
            addMessage('info', msgs[0]);
            addStageSuggestion(firstStage.tacticName, 0);
            // Request agent analysis for first stage
            if (agentConnected) {
              requestAgentAnalysis(firstStage.tacticName, 0, state.selectedScenario?.name ?? 'Unknown');
            }
          }, 500);
        }
      } else if (prevPS === 'paused') {
        // Resume via MCP
        if (mcpSimIdRef.current) {
          callMcpTool('attack_resume', { simulation_id: mcpSimIdRef.current });
        }
        addMessage('info', 'Simulation resumed', 'System');
      }

      // Start auto-advance timer
      clearTimer();
      const intervalMs = 3000 / state.speed;
      timerRef.current = setInterval(() => {
        actionsRef.current.advanceStage();
      }, intervalMs);

    } else if (newPS === 'paused') {
      clearTimer();
      if (mcpSimIdRef.current) {
        callMcpTool('attack_pause', { simulation_id: mcpSimIdRef.current });
      }
      addMessage('info', 'Simulation paused', 'System');

    } else if (newPS === 'stopped') {
      clearTimer();
      mcpSimIdRef.current = null;
      setLocalMessages([]);
      setSuggestions([]);
      setStats(DEFAULT_STATS);
      setSimulationError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.playState]);

  // ── Stage changes → narration + suggestions ─────────────────────────

  useEffect(() => {
    if (state.playState !== 'playing' || state.currentStage === 0) return;

    const stage = state.stages[state.currentStage];
    if (!stage) return;

    // Generate narration message
    const msgs = STAGE_MESSAGES[stage.tacticName] ?? [`Stage ${state.currentStage + 1}: ${stage.tacticName}`];
    const msgIndex = state.currentStage % msgs.length;
    const msgType: DemoNarrationMessage['type'] =
      state.currentStage < 3 ? 'info' : state.currentStage < 7 ? 'warning' : 'error';
    addMessage(msgType, msgs[msgIndex]);

    // Jump backend to the same stage
    if (mcpSimIdRef.current) {
      callMcpTool('attack_jump_to_stage', {
        simulation_id: mcpSimIdRef.current,
        stage_number: state.currentStage + 1, // 1-based
      });
    }

    // Generate aIP suggestion
    addStageSuggestion(stage.tacticName, state.currentStage);

    // Request real agent analysis (async, non-blocking)
    if (agentConnected) {
      requestAgentAnalysis(stage.tacticName, state.currentStage, stateRef.current.selectedScenario?.name ?? 'Unknown');
    }

    // Check if simulation reached the end
    if (state.currentStage >= state.stages.length - 1) {
      clearTimer();
      setTimeout(() => {
        addMessage(
          'success',
          `Simulation complete — all ${state.stages.length} MITRE ATT&CK stages executed for ${stateRef.current.selectedScenario?.name ?? 'scenario'}`,
          'System',
        );
      }, 500);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.currentStage]);

  // ── Speed changes during playback ───────────────────────────────────

  useEffect(() => {
    if (state.playState !== 'playing') return;

    // Restart timer with new interval
    clearTimer();
    const intervalMs = 3000 / state.speed;
    timerRef.current = setInterval(() => {
      actionsRef.current.advanceStage();
    }, intervalMs);

    // Sync speed to backend
    if (mcpSimIdRef.current) {
      callMcpTool('attack_speed', {
        simulation_id: mcpSimIdRef.current,
        multiplier: state.speed,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.speed]);

  // ── Cleanup on unmount ──────────────────────────────────────────────

  useEffect(() => {
    return () => clearTimer();
  }, [clearTimer]);

  // ── Suggestion action handlers ─────────────────────────────────────

  const handleAcceptSuggestion = useCallback((id: string) => {
    setSuggestions(prev =>
      prev.map(s => (s.id === id ? { ...s, status: 'accepted' as const } : s)),
    );
    setStats(prev => {
      const accepted = prev.acceptedCount + 1;
      const total = prev.totalSuggestions;
      return {
        ...prev,
        acceptedCount: accepted,
        acceptanceRate: total > 0 ? Math.round((accepted / total) * 100) : 0,
      };
    });
    addMessage('success', 'Suggestion accepted by analyst', 'aIP Assist');
  }, [addMessage]);

  const handleRejectSuggestion = useCallback((id: string) => {
    setSuggestions(prev =>
      prev.map(s => (s.id === id ? { ...s, status: 'rejected' as const } : s)),
    );
    setStats(prev => ({
      ...prev,
      rejectedCount: prev.rejectedCount + 1,
    }));
  }, []);

  const handleExplainWhy = useCallback((id: string) => {
    const suggestion = suggestions.find(s => s.id === id);
    if (!suggestion) return;

    if (agentConnected) {
      // Use real agent for explanation
      apiClient.post('/agent/chat', {
        message: `Explain briefly why a SOC analyst should "${suggestion.title}" in the context of: ${suggestion.relatedContext ?? 'active attack simulation'}. Be concise (2-3 sentences).`,
        max_tokens: 200,
      }).then(res => {
        if (res.data?.content) {
          setSuggestions(prev =>
            prev.map(s => (s.id === id ? { ...s, reason: res.data.content } : s)),
          );
        }
      }).catch(() => {
        // Fallback to MCP tool if agent unavailable
        callMcpTool('aip_explain_why', {
          action: suggestion.title,
          context: { page: 'simulation', selected_entity: suggestion.relatedContext },
        }).then(result => {
          if (result) {
            const explanation = (result as Record<string, unknown>).explanation as string
              ?? 'AI-driven recommendation based on current threat context';
            setSuggestions(prev =>
              prev.map(s => (s.id === id ? { ...s, reason: explanation } : s)),
            );
          }
        });
      });
    } else {
      // Fallback to MCP tool
      callMcpTool('aip_explain_why', {
        action: suggestion.title,
        context: { page: 'simulation', selected_entity: suggestion.relatedContext },
      }).then(result => {
        if (result) {
          const explanation = (result as Record<string, unknown>).explanation as string
            ?? 'AI-driven recommendation based on current threat context';
          setSuggestions(prev =>
            prev.map(s => (s.id === id ? { ...s, reason: explanation } : s)),
          );
        }
      });
    }
  }, [suggestions, agentConnected]);

  // ── Merge local messages with WebSocket narration ───────────────────

  const allMessages = narration.messages.length > 0
    ? [...localMessages, ...narration.messages].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      )
    : localMessages;

  return {
    narrationMessages: allMessages,
    suggestions,
    stats,
    simulationError,
    agentConnected,
    onAcceptSuggestion: handleAcceptSuggestion,
    onRejectSuggestion: handleRejectSuggestion,
    onExplainWhy: handleExplainWhy,
  };
}

/**
 * Demo Data Schemas
 *
 * DATA-001: Simulation state schema
 * DATA-002: Narration message schema (max 1000 entries)
 * DATA-003: AI suggestions schema with read tracking
 * DATA-004: Analysis results schema per incident
 */

import type { PlayState, SpeedMultiplier, AttackScenario, MitreStage } from '../components/demo/types';
import type { NarrationMessage } from '../components/narration/types';
import type { AipSuggestion, AipSessionStats } from '../components/aip-assist/types';

// ============================================================================
// DATA-001: Simulation State Schema
// ============================================================================

export interface SimulationState {
  scenario: AttackScenario | null;
  currentPhase: number;
  speed: SpeedMultiplier;
  isRunning: boolean;
  playState: PlayState;
  stages: MitreStage[];
  sessionId: string | null;
  startedAt: string | null;
}

export const DEFAULT_SIMULATION_STATE: SimulationState = {
  scenario: null,
  currentPhase: 0,
  speed: 1,
  isRunning: false,
  playState: 'stopped',
  stages: [],
  sessionId: null,
  startedAt: null,
};

// ============================================================================
// DATA-002: Narration Message Schema (max 1000)
// ============================================================================

export const MAX_NARRATION_MESSAGES = 1000;

export type NarrationMessageType = 'info' | 'warning' | 'error' | 'success';

export interface DemoNarrationMessage {
  id: string;
  timestamp: string;
  type: NarrationMessageType;
  content: string;
  source?: string;
}

export interface NarrationState {
  messages: DemoNarrationMessage[];
  isExpanded: boolean;
  isEnabled: boolean;
}

export const DEFAULT_NARRATION_STATE: NarrationState = {
  messages: [],
  isExpanded: false,
  isEnabled: true,
};

/**
 * Adds a message to the narration buffer, enforcing the max limit
 */
export function addNarrationMessage(
  messages: DemoNarrationMessage[],
  newMessage: DemoNarrationMessage
): DemoNarrationMessage[] {
  const updated = [...messages, newMessage];
  if (updated.length > MAX_NARRATION_MESSAGES) {
    return updated.slice(updated.length - MAX_NARRATION_MESSAGES);
  }
  return updated;
}

// ============================================================================
// DATA-003: AI Suggestions Schema with Read Tracking
// ============================================================================

export interface DemoAipSuggestion extends AipSuggestion {
  isRead: boolean;
  readAt?: string;
}

export interface AipAssistState {
  suggestions: DemoAipSuggestion[];
  stats: AipSessionStats;
  isExpanded: boolean;
  isEnabled: boolean;
  isThinking: boolean;
  unreadCount: number;
}

export const DEFAULT_AIP_ASSIST_STATE: AipAssistState = {
  suggestions: [],
  stats: {
    totalSuggestions: 0,
    acceptedCount: 0,
    rejectedCount: 0,
    expiredCount: 0,
    acceptanceRate: 0,
  },
  isExpanded: false,
  isEnabled: true,
  isThinking: false,
  unreadCount: 0,
};

/**
 * Marks a suggestion as read and updates unread count
 */
export function markSuggestionRead(
  suggestions: DemoAipSuggestion[],
  suggestionId: string
): DemoAipSuggestion[] {
  return suggestions.map((s) =>
    s.id === suggestionId && !s.isRead
      ? { ...s, isRead: true, readAt: new Date().toISOString() }
      : s
  );
}

/**
 * Counts unread suggestions
 */
export function countUnread(suggestions: DemoAipSuggestion[]): number {
  return suggestions.filter((s) => !s.isRead && s.status === 'pending').length;
}

// ============================================================================
// DATA-004: Analysis Results Schema
// ============================================================================

export type AnalysisDecision = 'contain' | 'escalate' | 'dismiss' | 'monitor';
export type AnalysisStatus = 'idle' | 'queued' | 'processing' | 'completed' | 'error';

export interface AnalysisResult {
  id: string;
  incidentId: string;
  decision: AnalysisDecision;
  confidence: number;
  reasoning: string;
  timestamp: string;
  duration: number;
}

export interface IncidentAnalysisState {
  status: AnalysisStatus;
  result: AnalysisResult | null;
  error: string | null;
  queuedAt: string | null;
}

export const DEFAULT_INCIDENT_ANALYSIS: IncidentAnalysisState = {
  status: 'idle',
  result: null,
  error: null,
  queuedAt: null,
};

export interface AnalysisState {
  analyses: Record<string, IncidentAnalysisState>;
}

export const DEFAULT_ANALYSIS_STATE: AnalysisState = {
  analyses: {},
};

/**
 * Gets or creates an analysis state for an incident
 */
export function getIncidentAnalysis(
  state: AnalysisState,
  incidentId: string
): IncidentAnalysisState {
  return state.analyses[incidentId] ?? DEFAULT_INCIDENT_ANALYSIS;
}

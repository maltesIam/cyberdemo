/**
 * Tests for Demo Data Schemas
 * UT-DATA-001: Simulation state schema
 * UT-DATA-002: Narration message schema
 * UT-DATA-003: AI suggestions schema
 * UT-DATA-004: Analysis results schema
 */
import { describe, it, expect } from 'vitest';
import {
  DEFAULT_SIMULATION_STATE,
  DEFAULT_NARRATION_STATE,
  DEFAULT_AIP_ASSIST_STATE,
  DEFAULT_ANALYSIS_STATE,
  DEFAULT_INCIDENT_ANALYSIS,
  MAX_NARRATION_MESSAGES,
  addNarrationMessage,
  markSuggestionRead,
  countUnread,
  getIncidentAnalysis,
  type SimulationState,
  type DemoNarrationMessage,
  type DemoAipSuggestion,
  type AnalysisResult,
  type IncidentAnalysisState,
} from '../../../src/types/demo';

// ============================================================================
// UT-DATA-001: Simulation State Schema
// ============================================================================
describe('DATA-001: SimulationState schema', () => {
  it('should have correct default values', () => {
    expect(DEFAULT_SIMULATION_STATE.scenario).toBeNull();
    expect(DEFAULT_SIMULATION_STATE.currentPhase).toBe(0);
    expect(DEFAULT_SIMULATION_STATE.speed).toBe(1);
    expect(DEFAULT_SIMULATION_STATE.isRunning).toBe(false);
    expect(DEFAULT_SIMULATION_STATE.playState).toBe('stopped');
    expect(DEFAULT_SIMULATION_STATE.stages).toEqual([]);
    expect(DEFAULT_SIMULATION_STATE.sessionId).toBeNull();
    expect(DEFAULT_SIMULATION_STATE.startedAt).toBeNull();
  });

  it('should support all valid speed values', () => {
    const speeds: SimulationState['speed'][] = [0.5, 1, 2, 4];
    speeds.forEach((speed) => {
      const state: SimulationState = { ...DEFAULT_SIMULATION_STATE, speed };
      expect(state.speed).toBe(speed);
    });
  });

  it('should support all valid play states', () => {
    const states: SimulationState['playState'][] = ['stopped', 'playing', 'paused'];
    states.forEach((playState) => {
      const state: SimulationState = { ...DEFAULT_SIMULATION_STATE, playState };
      expect(state.playState).toBe(playState);
    });
  });
});

// ============================================================================
// UT-DATA-002: Narration Message Schema
// ============================================================================
describe('DATA-002: NarrationMessage schema', () => {
  const createMessage = (id: string): DemoNarrationMessage => ({
    id,
    timestamp: new Date().toISOString(),
    type: 'info',
    content: `Message ${id}`,
  });

  it('should have correct default narration state', () => {
    expect(DEFAULT_NARRATION_STATE.messages).toEqual([]);
    expect(DEFAULT_NARRATION_STATE.isExpanded).toBe(false);
    expect(DEFAULT_NARRATION_STATE.isEnabled).toBe(true);
  });

  it('should enforce MAX_NARRATION_MESSAGES limit of 1000', () => {
    expect(MAX_NARRATION_MESSAGES).toBe(1000);
  });

  it('should add messages within limit', () => {
    const messages: DemoNarrationMessage[] = [];
    const newMsg = createMessage('1');
    const result = addNarrationMessage(messages, newMsg);
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('1');
  });

  it('should trim old messages when exceeding 1000', () => {
    const messages: DemoNarrationMessage[] = Array.from({ length: 1000 }, (_, i) =>
      createMessage(`msg-${i}`)
    );
    const newMsg = createMessage('msg-1000');
    const result = addNarrationMessage(messages, newMsg);
    expect(result).toHaveLength(1000);
    expect(result[0].id).toBe('msg-1');
    expect(result[result.length - 1].id).toBe('msg-1000');
  });

  it('should support all message types', () => {
    const types: DemoNarrationMessage['type'][] = ['info', 'warning', 'error', 'success'];
    types.forEach((type) => {
      const msg: DemoNarrationMessage = { ...createMessage('t'), type };
      expect(msg.type).toBe(type);
    });
  });
});

// ============================================================================
// UT-DATA-003: AI Suggestions Schema
// ============================================================================
describe('DATA-003: AipSuggestion schema with read tracking', () => {
  const createSuggestion = (id: string, isRead = false): DemoAipSuggestion => ({
    id,
    type: 'action',
    title: `Suggestion ${id}`,
    description: 'Test description',
    confidence: 'high',
    status: 'pending',
    createdAt: new Date().toISOString(),
    isRead,
  });

  it('should have correct default aIP assist state', () => {
    expect(DEFAULT_AIP_ASSIST_STATE.suggestions).toEqual([]);
    expect(DEFAULT_AIP_ASSIST_STATE.isExpanded).toBe(false);
    expect(DEFAULT_AIP_ASSIST_STATE.isEnabled).toBe(true);
    expect(DEFAULT_AIP_ASSIST_STATE.isThinking).toBe(false);
    expect(DEFAULT_AIP_ASSIST_STATE.unreadCount).toBe(0);
    expect(DEFAULT_AIP_ASSIST_STATE.stats.totalSuggestions).toBe(0);
  });

  it('should mark suggestion as read', () => {
    const suggestions = [createSuggestion('1'), createSuggestion('2')];
    const result = markSuggestionRead(suggestions, '1');
    expect(result[0].isRead).toBe(true);
    expect(result[0].readAt).toBeDefined();
    expect(result[1].isRead).toBe(false);
  });

  it('should not re-mark already read suggestions', () => {
    const suggestions = [createSuggestion('1', true)];
    const originalReadAt = suggestions[0].readAt;
    const result = markSuggestionRead(suggestions, '1');
    expect(result[0].readAt).toBe(originalReadAt);
  });

  it('should count unread pending suggestions', () => {
    const suggestions: DemoAipSuggestion[] = [
      createSuggestion('1'),
      createSuggestion('2', true),
      { ...createSuggestion('3'), status: 'accepted' },
      createSuggestion('4'),
    ];
    expect(countUnread(suggestions)).toBe(2);
  });

  it('should return 0 for empty suggestions', () => {
    expect(countUnread([])).toBe(0);
  });
});

// ============================================================================
// UT-DATA-004: Analysis Results Schema
// ============================================================================
describe('DATA-004: AnalysisResult schema', () => {
  it('should have correct default analysis state', () => {
    expect(DEFAULT_ANALYSIS_STATE.analyses).toEqual({});
  });

  it('should have correct default incident analysis', () => {
    expect(DEFAULT_INCIDENT_ANALYSIS.status).toBe('idle');
    expect(DEFAULT_INCIDENT_ANALYSIS.result).toBeNull();
    expect(DEFAULT_INCIDENT_ANALYSIS.error).toBeNull();
    expect(DEFAULT_INCIDENT_ANALYSIS.queuedAt).toBeNull();
  });

  it('should return default state for unknown incident', () => {
    const result = getIncidentAnalysis(DEFAULT_ANALYSIS_STATE, 'unknown-id');
    expect(result).toEqual(DEFAULT_INCIDENT_ANALYSIS);
  });

  it('should return existing analysis for known incident', () => {
    const analysisResult: AnalysisResult = {
      id: 'analysis-1',
      incidentId: 'inc-1',
      decision: 'contain',
      confidence: 0.95,
      reasoning: 'High severity threat detected',
      timestamp: new Date().toISOString(),
      duration: 3500,
    };
    const state = {
      analyses: {
        'inc-1': {
          status: 'completed' as const,
          result: analysisResult,
          error: null,
          queuedAt: '2026-01-01T00:00:00Z',
        },
      },
    };
    const result = getIncidentAnalysis(state, 'inc-1');
    expect(result.status).toBe('completed');
    expect(result.result?.decision).toBe('contain');
    expect(result.result?.confidence).toBe(0.95);
  });

  it('should support all analysis decision types', () => {
    const decisions: AnalysisResult['decision'][] = ['contain', 'escalate', 'dismiss', 'monitor'];
    decisions.forEach((decision) => {
      const result: AnalysisResult = {
        id: '1',
        incidentId: 'inc-1',
        decision,
        confidence: 0.9,
        reasoning: 'test',
        timestamp: new Date().toISOString(),
        duration: 1000,
      };
      expect(result.decision).toBe(decision);
    });
  });

  it('should support all analysis statuses', () => {
    const statuses: IncidentAnalysisState['status'][] = [
      'idle', 'queued', 'processing', 'completed', 'error',
    ];
    statuses.forEach((status) => {
      const state: IncidentAnalysisState = { ...DEFAULT_INCIDENT_ANALYSIS, status };
      expect(state.status).toBe(status);
    });
  });
});

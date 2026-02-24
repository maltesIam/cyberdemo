/**
 * SimulationPage Component
 *
 * Dedicated immersive simulation page at /simulation route.
 * 3-column layout: MITRE Phases | Attack Graph | aIP Panel.
 * Fixed narration footer always visible.
 *
 * Requirements:
 * - REQ-003-001-001: /simulation route
 * - REQ-003-001-002: 3-column layout
 * - REQ-003-001-003: MITRE phases left column
 * - REQ-003-001-004: Attack graph center column
 * - REQ-003-001-005: aIP panel right column (integrated, not floating)
 * - REQ-003-001-006: Fixed narration footer (always visible, not collapsible)
 * - REQ-003-001-007: Scenario selector in page
 * - REQ-003-001-008: Real-time visualization
 */

import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { MitrePhasesList } from '../components/demo/MitrePhasesList';
import { AttackGraph } from '../components/demo/AttackGraph';
import { AipAssistWidget } from '../components/aip-assist/AipAssistWidget';
import { NarrationFooter } from '../components/demo/NarrationFooter';
import { ScenarioDropdown } from '../components/demo/ScenarioDropdown';
import { ATTACK_SCENARIOS } from '../components/demo/types';
import { useDemoContext } from '../context/DemoContext';
import type { GraphData } from '../components/Graph/types';
import type { DemoOutletContext } from '../hooks/useDemoOrchestrator';
import type { AipSessionStats } from '../components/aip-assist/types';

const DEFAULT_STATS: AipSessionStats = {
  totalSuggestions: 0,
  acceptedCount: 0,
  rejectedCount: 0,
  expiredCount: 0,
  acceptanceRate: 0,
};

export function SimulationPage() {
  const { state, actions } = useDemoContext();

  // Get narration messages and suggestions from Layout's orchestrator via Outlet context
  const outletContext = useOutletContext<DemoOutletContext | undefined>();
  const narrationMessages = outletContext?.narrationMessages ?? [];
  const suggestions = outletContext?.suggestions ?? [];
  const stats = outletContext?.stats ?? DEFAULT_STATS;
  const agentConnected = outletContext?.agentConnected ?? false;
  const onAccept = outletContext?.onAcceptSuggestion ?? (() => {});
  const onReject = outletContext?.onRejectSuggestion ?? (() => {});
  const onExplainWhy = outletContext?.onExplainWhy;

  const [isAipExpanded, setIsAipExpanded] = useState(true);
  const [aipEnabled, setAipEnabled] = useState(true);

  // Graph data will be populated via WebSocket/MCP when connected
  const [graphData] = useState<GraphData>({ nodes: [], edges: [] });

  const isPlaying = state.playState === 'playing';
  const isStopped = state.playState === 'stopped';

  return (
    <div data-testid="simulation-page" className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Top controls bar */}
      <div className="flex items-center gap-4 px-4 py-2 bg-gray-800 border-b border-gray-700">
        {/* Scenario selector */}
        <div className="w-48">
          <ScenarioDropdown
            scenarios={ATTACK_SCENARIOS}
            selectedScenario={state.selectedScenario}
            onSelect={actions.selectScenario}
            isDisabled={isPlaying}
          />
        </div>

        {/* Playback */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            aria-label={isPlaying ? 'Pause' : 'Play'}
            onClick={actions.togglePlayPause}
            disabled={!state.selectedScenario && isStopped}
            className="p-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            {isPlaying ? '⏸' : '▶'}
          </button>
          <button
            type="button"
            aria-label="Stop"
            onClick={actions.stop}
            disabled={isStopped}
            className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            ⏹
          </button>
        </div>

        {/* Speed */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Speed:</span>
          <span className="text-xs text-gray-200">{state.speed}x</span>
        </div>

        {/* Agent status */}
        <div className="flex items-center gap-1.5">
          <div className={`w-2 h-2 rounded-full ${agentConnected ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
          <span className={`text-xs ${agentConnected ? 'text-green-400' : 'text-gray-500'}`}>
            {agentConnected ? 'Vega AI' : 'Agent Offline'}
          </span>
        </div>

        {/* Stage indicator */}
        {state.stages.length > 0 && (
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-xs text-gray-400">
              Stage {state.currentStage + 1}/{state.stages.length}
            </span>
            {state.stages[state.currentStage] && (
              <span className="text-xs text-cyan-400">
                {state.stages[state.currentStage].tacticName}
              </span>
            )}
          </div>
        )}
      </div>

      {/* 3-column layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left column: MITRE Phases */}
        <div
          data-testid="mitre-column"
          className="w-64 flex-shrink-0 overflow-y-auto p-4 border-r border-gray-700 bg-gray-800/50"
        >
          <MitrePhasesList stages={state.stages} currentStage={state.currentStage} />
        </div>

        {/* Center column: Attack Graph */}
        <div data-testid="graph-column" className="flex-1 p-4">
          <AttackGraph graphData={graphData} />
        </div>

        {/* Right column: aIP Panel (integrated, not floating) */}
        <div
          data-testid="aip-column"
          className="w-80 flex-shrink-0 overflow-y-auto border-l border-gray-700"
        >
          <AipAssistWidget
            suggestions={suggestions}
            stats={stats}
            isExpanded={isAipExpanded}
            isEnabled={aipEnabled}
            onAccept={onAccept}
            onReject={onReject}
            onExplainWhy={onExplainWhy}
            onToggleExpand={() => setIsAipExpanded(!isAipExpanded)}
            onToggleEnabled={() => setAipEnabled(!aipEnabled)}
          />
        </div>
      </div>

      {/* Fixed narration footer (always visible, not collapsible) */}
      <NarrationFooter
        messages={narrationMessages}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={() => {}}
        alwaysVisible={true}
      />
    </div>
  );
}

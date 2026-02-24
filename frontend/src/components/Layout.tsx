import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { DemoControlBar } from "./demo/DemoControlBar";
import { DemoFloatingWidget } from "./demo/DemoFloatingWidget";
import { NarrationFooter } from "./demo/NarrationFooter";
import { useDemoContext } from "../context/DemoContext";
import { useDemoOrchestrator } from "../hooks/useDemoOrchestrator";
import type { DemoOutletContext } from "../hooks/useDemoOrchestrator";

export function Layout() {
  const { state, actions } = useDemoContext();

  // Orchestrator: wires DemoContext to backend MCP tools, narration WS, and auto-advance timer
  const { narrationMessages, suggestions, stats, agentConnected, onAcceptSuggestion, onRejectSuggestion, onExplainWhy } = useDemoOrchestrator();

  // DemoControlBar collapse state
  const [isControlBarCollapsed, setIsControlBarCollapsed] = useState(false);

  // DemoFloatingWidget local state
  const [isWidgetExpanded, setIsWidgetExpanded] = useState(false);
  const [isWidgetEnabled, setIsWidgetEnabled] = useState(true);

  // NarrationFooter local state
  const [isNarrationExpanded, setIsNarrationExpanded] = useState(false);
  const [isNarrationEnabled, setIsNarrationEnabled] = useState(true);

  // Pass orchestrator data to child routes via Outlet context
  const outletContext: DemoOutletContext = {
    narrationMessages,
    suggestions,
    stats,
    simulationError: null,
    agentConnected,
    onAcceptSuggestion,
    onRejectSuggestion,
    onExplainWhy,
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        {/* Original header */}
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">CyberDemo - SOC Dashboard</h2>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-gray-400">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm">System Online</span>
              </div>
              <button className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-700 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
              </button>
              <button className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-700 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </button>
            </div>
          </div>
        </header>

        {/* Demo Control Bar - visible on all pages */}
        <DemoControlBar
          state={state}
          onPlay={actions.play}
          onPause={actions.pause}
          onStop={actions.stop}
          onSpeedChange={actions.setSpeed}
          onScenarioSelect={actions.selectScenario}
          isCollapsed={isControlBarCollapsed}
          onToggleCollapse={() => setIsControlBarCollapsed(!isControlBarCollapsed)}
        />

        {/* Main content area */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet context={outletContext} />
        </main>

        {/* Narration Footer - visible on all pages */}
        <NarrationFooter
          messages={narrationMessages}
          isExpanded={isNarrationExpanded}
          isEnabled={isNarrationEnabled}
          onToggleExpand={() => setIsNarrationExpanded(!isNarrationExpanded)}
          onToggleEnabled={() => setIsNarrationEnabled(!isNarrationEnabled)}
        />
      </div>

      {/* Floating aIP Assist Widget - bottom-right on all pages */}
      <DemoFloatingWidget
        suggestions={suggestions}
        stats={stats}
        isExpanded={isWidgetExpanded}
        isEnabled={isWidgetEnabled}
        isThinking={state.playState === "playing"}
        unreadCount={suggestions.filter((s) => s.status === "pending").length}
        onAccept={onAcceptSuggestion}
        onReject={onRejectSuggestion}
        onExplainWhy={onExplainWhy}
        onToggleExpand={() => setIsWidgetExpanded(!isWidgetExpanded)}
        onToggleEnabled={() => setIsWidgetEnabled(!isWidgetEnabled)}
      />
    </div>
  );
}

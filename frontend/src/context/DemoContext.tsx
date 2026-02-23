/**
 * DemoContext - Global State Management for Demo Control Panel
 *
 * Requirements:
 * - REQ-006-002-001: Context React para estado global del demo
 * - REQ-006-002-002: Persistencia de estado entre recargas (localStorage)
 * - REQ-006-002-003: Sync de estado con MCP Frontend Server
 *
 * Provides:
 * - DemoProvider: Context provider wrapping the app
 * - useDemoContext: Full context access (state + actions)
 * - useDemoState: Read-only state access
 * - useDemoActions: Actions to modify state
 * - useDemoMCPSync: Hook for MCP synchronization
 * - DEMO_STORAGE_KEY: localStorage key for persisted state
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useMemo,
  useEffect,
  useState,
  useRef,
  type ReactNode,
} from "react";
import type {
  DemoState,
  PlayState,
  SpeedMultiplier,
  AttackScenario,
  MitreStage,
} from "../components/demo/types";

// ============================================================================
// Types
// ============================================================================

/** Actions available for modifying demo state */
export interface DemoActions {
  /** Start or resume playback */
  play: () => void;
  /** Pause playback */
  pause: () => void;
  /** Stop playback and reset progress */
  stop: () => void;
  /** Set playback speed */
  setSpeed: (speed: SpeedMultiplier) => void;
  /** Select an attack scenario */
  selectScenario: (scenario: AttackScenario) => void;
  /** Advance to next stage */
  advanceStage: () => void;
  /** Jump to specific stage */
  jumpToStage: (stageIndex: number) => void;
  /** Toggle between play and pause */
  togglePlayPause: () => void;
  /** Reset demo to initial state */
  resetDemo: () => void;
}

/** Callback type for MCP sync notifications */
export type MCPSyncCallback = (state: DemoState) => void;

/** MCP Sync functions */
export interface DemoMCPSync {
  /** Register a callback to be notified of state changes */
  registerSyncCallback: (callback: MCPSyncCallback) => void;
  /** Unregister a previously registered callback */
  unregisterSyncCallback: (callback: MCPSyncCallback) => void;
  /** Sync state from MCP (will not trigger outbound sync) */
  syncFromMCP: (partialState: Partial<DemoState>) => void;
}

/** Full context value including state, actions, and MCP sync */
interface DemoContextValue {
  state: DemoState;
  actions: DemoActions;
  mcpSync: DemoMCPSync;
  /** Internal flag: true if last update came from MCP */
  _isFromMCP: React.MutableRefObject<boolean>;
}

// ============================================================================
// Storage Key
// ============================================================================

/** localStorage key for persisting demo state */
export const DEMO_STORAGE_KEY = "cyberdemo-state";

// ============================================================================
// Initial State
// ============================================================================

const initialState: DemoState = {
  playState: "stopped",
  speed: 1,
  selectedScenario: null,
  currentStage: 0,
  stages: [],
  sessionId: null,
  startedAt: null,
};

// ============================================================================
// Action Types
// ============================================================================

type DemoAction =
  | { type: "PLAY" }
  | { type: "PAUSE" }
  | { type: "STOP" }
  | { type: "TOGGLE_PLAY_PAUSE" }
  | { type: "SET_SPEED"; payload: SpeedMultiplier }
  | { type: "SELECT_SCENARIO"; payload: AttackScenario }
  | { type: "ADVANCE_STAGE" }
  | { type: "JUMP_TO_STAGE"; payload: number }
  | { type: "RESET" }
  | { type: "RESTORE"; payload: Partial<DemoState> }
  | { type: "SYNC_FROM_MCP"; payload: Partial<DemoState> };

// ============================================================================
// MITRE ATT&CK Tactics (for generating stages)
// ============================================================================

const MITRE_TACTICS = [
  { id: "TA0043", name: "Reconnaissance" },
  { id: "TA0042", name: "Resource Development" },
  { id: "TA0001", name: "Initial Access" },
  { id: "TA0002", name: "Execution" },
  { id: "TA0003", name: "Persistence" },
  { id: "TA0004", name: "Privilege Escalation" },
  { id: "TA0005", name: "Defense Evasion" },
  { id: "TA0006", name: "Credential Access" },
  { id: "TA0007", name: "Discovery" },
  { id: "TA0008", name: "Lateral Movement" },
  { id: "TA0009", name: "Collection" },
  { id: "TA0011", name: "Command and Control" },
  { id: "TA0010", name: "Exfiltration" },
  { id: "TA0040", name: "Impact" },
];

/**
 * Generate MITRE stages for a scenario
 */
function generateStagesForScenario(scenario: AttackScenario): MitreStage[] {
  const stages: MitreStage[] = [];
  const numStages = Math.min(scenario.stages, MITRE_TACTICS.length);

  for (let i = 0; i < numStages; i++) {
    const tactic = MITRE_TACTICS[i % MITRE_TACTICS.length];
    stages.push({
      index: i,
      tacticId: tactic.id,
      tacticName: tactic.name,
      techniqueIds: [`T${1000 + i}`], // Simplified technique IDs
      completed: false,
      active: i === 0, // First stage is active initially
    });
  }

  return stages;
}

/**
 * Generate a unique session ID
 */
function generateSessionId(): string {
  return `demo-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

// ============================================================================
// Reducer
// ============================================================================

function demoReducer(state: DemoState, action: DemoAction): DemoState {
  switch (action.type) {
    case "PLAY": {
      // If already playing, do nothing
      if (state.playState === "playing") {
        return state;
      }

      // If resuming from pause, keep same session
      if (state.playState === "paused") {
        return {
          ...state,
          playState: "playing",
        };
      }

      // Starting new session from stopped
      return {
        ...state,
        playState: "playing",
        sessionId: generateSessionId(),
        startedAt: new Date().toISOString(),
      };
    }

    case "PAUSE": {
      return {
        ...state,
        playState: "paused",
      };
    }

    case "STOP": {
      // Reset stages to initial state
      const resetStages = state.stages.map((stage, index) => ({
        ...stage,
        completed: false,
        active: index === 0,
      }));

      return {
        ...state,
        playState: "stopped",
        currentStage: 0,
        stages: resetStages,
        sessionId: null,
        startedAt: null,
      };
    }

    case "SET_SPEED": {
      return {
        ...state,
        speed: action.payload,
      };
    }

    case "SELECT_SCENARIO": {
      const newStages = generateStagesForScenario(action.payload);
      return {
        ...state,
        selectedScenario: action.payload,
        stages: newStages,
        currentStage: 0,
        playState: "stopped",
        sessionId: null,
        startedAt: null,
      };
    }

    case "ADVANCE_STAGE": {
      if (state.stages.length === 0) {
        return state;
      }

      const maxStage = state.stages.length - 1;
      if (state.currentStage >= maxStage) {
        return state;
      }

      const newCurrentStage = state.currentStage + 1;
      const newStages = state.stages.map((stage, index) => ({
        ...stage,
        completed: index < newCurrentStage,
        active: index === newCurrentStage,
      }));

      return {
        ...state,
        currentStage: newCurrentStage,
        stages: newStages,
      };
    }

    case "JUMP_TO_STAGE": {
      if (state.stages.length === 0) {
        return state;
      }

      const targetStage = Math.max(
        0,
        Math.min(action.payload, state.stages.length - 1)
      );

      const newStages = state.stages.map((stage, index) => ({
        ...stage,
        completed: index < targetStage,
        active: index === targetStage,
      }));

      return {
        ...state,
        currentStage: targetStage,
        stages: newStages,
      };
    }

    case "TOGGLE_PLAY_PAUSE": {
      if (state.playState === "playing") {
        return {
          ...state,
          playState: "paused" as PlayState,
        };
      }
      // If paused, resume
      if (state.playState === "paused") {
        return {
          ...state,
          playState: "playing" as PlayState,
        };
      }
      // If stopped, start new session
      return {
        ...state,
        playState: "playing" as PlayState,
        sessionId: generateSessionId(),
        startedAt: new Date().toISOString(),
      };
    }

    case "RESET": {
      return { ...initialState };
    }

    case "RESTORE": {
      // Restore from localStorage with validation
      const restoredState = (action as { type: "RESTORE"; payload: Partial<DemoState> }).payload;
      return {
        ...initialState,
        ...restoredState,
        // Always start stopped (never restore playing state)
        playState: "stopped" as PlayState,
        sessionId: null,
        startedAt: null,
      };
    }

    case "SYNC_FROM_MCP": {
      // Sync state from MCP server
      const mcpState = action.payload;
      const newState = { ...state };

      // Only update valid known properties
      if (typeof mcpState.speed === "number" && [0.5, 1, 2, 4].includes(mcpState.speed)) {
        newState.speed = mcpState.speed as SpeedMultiplier;
      }

      if (mcpState.selectedScenario !== undefined) {
        newState.selectedScenario = mcpState.selectedScenario;
        if (mcpState.selectedScenario) {
          newState.stages = generateStagesForScenario(mcpState.selectedScenario);
        }
      }

      if (typeof mcpState.currentStage === "number" && mcpState.currentStage >= 0) {
        newState.currentStage = mcpState.currentStage;
        // Update stage active/completed status
        newState.stages = newState.stages.map((stage, index) => ({
          ...stage,
          completed: index < mcpState.currentStage!,
          active: index === mcpState.currentStage,
        }));
      }

      if (mcpState.playState && ["stopped", "playing", "paused"].includes(mcpState.playState)) {
        newState.playState = mcpState.playState;
        // Generate session if playing
        if (mcpState.playState === "playing" && !newState.sessionId) {
          newState.sessionId = generateSessionId();
          newState.startedAt = new Date().toISOString();
        }
      }

      return newState;
    }

    default:
      return state;
  }
}

// ============================================================================
// Context
// ============================================================================

const DemoContext = createContext<DemoContextValue | null>(null);

// ============================================================================
// localStorage Utilities
// ============================================================================

/**
 * Safely read state from localStorage
 */
function loadStateFromStorage(): Partial<DemoState> | null {
  try {
    const stored = window.localStorage.getItem(DEMO_STORAGE_KEY);
    if (!stored) return null;

    const parsed = JSON.parse(stored);

    // Basic validation - check it has expected properties
    if (typeof parsed !== "object" || parsed === null) {
      return null;
    }

    // Validate known properties
    const validState: Partial<DemoState> = {};

    if (typeof parsed.speed === "number" && [0.5, 1, 2, 4].includes(parsed.speed)) {
      validState.speed = parsed.speed as SpeedMultiplier;
    }

    if (parsed.selectedScenario && typeof parsed.selectedScenario.id === "string") {
      validState.selectedScenario = parsed.selectedScenario;
    }

    if (typeof parsed.currentStage === "number" && parsed.currentStage >= 0) {
      validState.currentStage = parsed.currentStage;
    }

    if (Array.isArray(parsed.stages)) {
      validState.stages = parsed.stages;
    }

    return validState;
  } catch {
    // Invalid JSON or localStorage access error
    return null;
  }
}

/**
 * Safely save state to localStorage
 */
function saveStateToStorage(state: DemoState): void {
  try {
    // Don't persist playing state - always save as stopped
    const stateToSave = {
      ...state,
      playState: state.playState === "playing" ? "stopped" : state.playState,
      sessionId: null,
      startedAt: null,
    };
    window.localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(stateToSave));
  } catch {
    // QuotaExceeded or access error - silently ignore
  }
}

/**
 * Safely remove state from localStorage
 */
function clearStateFromStorage(): void {
  try {
    window.localStorage.removeItem(DEMO_STORAGE_KEY);
  } catch {
    // Access error - silently ignore
  }
}

// ============================================================================
// Provider
// ============================================================================

interface DemoProviderProps {
  children: ReactNode;
  /** Whether to persist state to localStorage. Default: false */
  persistToStorage?: boolean;
}

export function DemoProvider({ children, persistToStorage = false }: DemoProviderProps) {
  const [state, dispatch] = useReducer(demoReducer, initialState);
  const [isInitialized, setIsInitialized] = useState(false);

  // MCP sync callbacks
  const syncCallbacksRef = useRef<Set<MCPSyncCallback>>(new Set());
  // Flag to prevent sync loops
  const isFromMCPRef = useRef(false);
  // Previous state for change detection
  const prevStateRef = useRef(state);

  // Restore state from localStorage on mount
  useEffect(() => {
    if (persistToStorage && !isInitialized) {
      const savedState = loadStateFromStorage();
      if (savedState && Object.keys(savedState).length > 0) {
        dispatch({ type: "RESTORE", payload: savedState });
      }
      setIsInitialized(true);
    }
  }, [persistToStorage, isInitialized]);

  // Save state to localStorage on changes
  useEffect(() => {
    if (persistToStorage && isInitialized) {
      saveStateToStorage(state);
    }
  }, [state, persistToStorage, isInitialized]);

  // Notify MCP sync callbacks when state changes (but not from MCP)
  useEffect(() => {
    if (prevStateRef.current !== state && !isFromMCPRef.current) {
      // State changed from local action, notify MCP callbacks
      syncCallbacksRef.current.forEach((callback) => {
        try {
          callback(state);
        } catch {
          // Silently ignore callback errors
        }
      });
    }
    // Reset the flag after processing
    isFromMCPRef.current = false;
    prevStateRef.current = state;
  }, [state]);

  // Memoized actions
  const actions: DemoActions = useMemo(
    () => ({
      play: () => dispatch({ type: "PLAY" }),
      pause: () => dispatch({ type: "PAUSE" }),
      stop: () => dispatch({ type: "STOP" }),
      setSpeed: (speed: SpeedMultiplier) =>
        dispatch({ type: "SET_SPEED", payload: speed }),
      selectScenario: (scenario: AttackScenario) =>
        dispatch({ type: "SELECT_SCENARIO", payload: scenario }),
      advanceStage: () => dispatch({ type: "ADVANCE_STAGE" }),
      jumpToStage: (stageIndex: number) =>
        dispatch({ type: "JUMP_TO_STAGE", payload: stageIndex }),
      togglePlayPause: () => dispatch({ type: "TOGGLE_PLAY_PAUSE" }),
      resetDemo: () => {
        dispatch({ type: "RESET" });
        if (persistToStorage) {
          clearStateFromStorage();
        }
      },
    }),
    [persistToStorage]
  );

  // MCP sync functions
  const mcpSync: DemoMCPSync = useMemo(
    () => ({
      registerSyncCallback: (callback: MCPSyncCallback) => {
        syncCallbacksRef.current.add(callback);
      },
      unregisterSyncCallback: (callback: MCPSyncCallback) => {
        syncCallbacksRef.current.delete(callback);
      },
      syncFromMCP: (partialState: Partial<DemoState>) => {
        // Set flag to prevent outbound sync
        isFromMCPRef.current = true;
        dispatch({ type: "SYNC_FROM_MCP", payload: partialState });
      },
    }),
    []
  );

  const value = useMemo(
    () => ({
      state,
      actions,
      mcpSync,
      _isFromMCP: isFromMCPRef,
    }),
    [state, actions, mcpSync]
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
}

// ============================================================================
// Hooks
// ============================================================================

/**
 * Hook to access full demo context (state + actions)
 * @throws Error if used outside DemoProvider
 */
export function useDemoContext(): DemoContextValue {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error("useDemoContext must be used within a DemoProvider");
  }
  return context;
}

/**
 * Hook to access demo state only
 * Useful for components that only need to display state
 */
export function useDemoState(): DemoState {
  const { state } = useDemoContext();
  return state;
}

/**
 * Hook to access demo actions only
 * Useful for components that only need to trigger actions
 */
export function useDemoActions(): DemoActions {
  const { actions } = useDemoContext();
  return actions;
}

/**
 * Hook to access MCP sync functions
 * Used to sync state with MCP Frontend Server
 */
export function useDemoMCPSync(): DemoMCPSync {
  const { mcpSync } = useDemoContext();
  return mcpSync;
}

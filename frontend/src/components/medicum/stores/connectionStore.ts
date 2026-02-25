import { create } from "zustand";
import type { ConnectionStatus } from "../types";

interface ConnectionState {
  status: ConnectionStatus;
  lastError: string | null;
  reconnectAttempts: number;

  // Actions
  setStatus: (status: ConnectionStatus) => void;
  setError: (error: string | null) => void;
  incrementReconnectAttempts: () => void;
  resetReconnectAttempts: () => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  status: "disconnected",
  lastError: null,
  reconnectAttempts: 0,

  setStatus: (status: ConnectionStatus) => set({ status }),

  setError: (error: string | null) => set({ lastError: error }),

  incrementReconnectAttempts: () =>
    set((state) => ({
      reconnectAttempts: state.reconnectAttempts + 1,
    })),

  resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),
}));

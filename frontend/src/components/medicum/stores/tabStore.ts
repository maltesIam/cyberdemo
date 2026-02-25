import { create } from "zustand";
import type { TabId, Tab } from "../types";

export const TABS: Tab[] = [
  { id: "consulta", label: "Consulta en Vivo", icon: "stethoscope" },
  { id: "historia", label: "Historia Clínica", icon: "file-text" },
  { id: "codificacion", label: "Codificación", icon: "code" },
  { id: "visor", label: "Visor de Imágenes", icon: "image" },
];

interface TabState {
  activeTab: TabId;
  tabs: Tab[];

  // Actions
  setActiveTab: (tabId: TabId) => void;
  getActiveTab: () => TabId;
  isValidTab: (tabId: string) => boolean;
}

export const useTabStore = create<TabState>((set, get) => ({
  activeTab: "consulta",
  tabs: TABS,

  setActiveTab: (tabId: TabId) => {
    if (get().isValidTab(tabId)) {
      set({ activeTab: tabId });
    }
  },

  getActiveTab: () => get().activeTab,

  isValidTab: (tabId: string): boolean => {
    return TABS.some((tab) => tab.id === tabId);
  },
}));

import { create } from "zustand";
import type { CodeSuggestion, AssignedCode, ICD10Code } from "../types";

// Demo ICD-10 catalog
export const DEMO_ICD10_CATALOG: ICD10Code[] = [
  {
    codigo: "M17.1",
    descripcion: "Gonartrosis primaria unilateral",
    capitulo: "Enfermedades del sistema musculoesquelético",
  },
  {
    codigo: "M17.0",
    descripcion: "Gonartrosis primaria bilateral",
    capitulo: "Enfermedades del sistema musculoesquelético",
  },
  {
    codigo: "M17.9",
    descripcion: "Gonartrosis, no especificada",
    capitulo: "Enfermedades del sistema musculoesquelético",
  },
  {
    codigo: "E11.9",
    descripcion: "Diabetes mellitus tipo 2 sin complicaciones",
    capitulo: "Enfermedades endocrinas",
  },
  {
    codigo: "E11.65",
    descripcion: "Diabetes mellitus tipo 2 con hiperglucemia",
    capitulo: "Enfermedades endocrinas",
  },
  {
    codigo: "I10",
    descripcion: "Hipertensión esencial (primaria)",
    capitulo: "Enfermedades del sistema circulatorio",
  },
  {
    codigo: "I11.9",
    descripcion: "Enfermedad cardíaca hipertensiva sin ICC",
    capitulo: "Enfermedades del sistema circulatorio",
  },
  {
    codigo: "M25.56",
    descripcion: "Dolor articular en rodilla",
    capitulo: "Enfermedades del sistema musculoesquelético",
  },
  {
    codigo: "R52",
    descripcion: "Dolor, no clasificado en otra parte",
    capitulo: "Síntomas y signos",
  },
  {
    codigo: "Z96.64",
    descripcion: "Presencia de prótesis de rodilla",
    capitulo: "Factores que influyen en el estado de salud",
  },
];

// Demo suggestions for the consultation
const DEMO_SUGGESTIONS: CodeSuggestion[] = [
  { codigo: "M17.1", descripcion: "Gonartrosis primaria unilateral", confianza: 95, tipo: "CIE10" },
  {
    codigo: "E11.9",
    descripcion: "Diabetes mellitus tipo 2 sin complicaciones",
    confianza: 88,
    tipo: "CIE10",
  },
  { codigo: "I10", descripcion: "Hipertensión esencial (primaria)", confianza: 85, tipo: "CIE10" },
  { codigo: "M25.56", descripcion: "Dolor articular en rodilla", confianza: 72, tipo: "CIE10" },
];

interface CodingState {
  suggestions: CodeSuggestion[];
  assignedCodes: AssignedCode[];
  searchQuery: string;
  searchResults: ICD10Code[];

  // Actions
  loadSuggestions: () => void;
  searchCodes: (query: string) => void;
  selectSuggestion: (codigo: string) => void;
  assignCode: (code: ICD10Code, asPrimary?: boolean) => void;
  removeCode: (codigo: string) => void;
  setPrimaryCode: (codigo: string) => void;
  validateCoding: () => { valid: boolean; errors: string[] };
  clearAssignedCodes: () => void;
}

export const useCodingStore = create<CodingState>((set, get) => ({
  suggestions: [],
  assignedCodes: [],
  searchQuery: "",
  searchResults: [],

  loadSuggestions: () => {
    set({ suggestions: DEMO_SUGGESTIONS });
  },

  searchCodes: (query: string) => {
    const normalizedQuery = query.toLowerCase().trim();
    if (!normalizedQuery) {
      set({ searchQuery: "", searchResults: [] });
      return;
    }

    const results = DEMO_ICD10_CATALOG.filter(
      (code) =>
        code.codigo.toLowerCase().includes(normalizedQuery) ||
        code.descripcion.toLowerCase().includes(normalizedQuery),
    );

    set({ searchQuery: query, searchResults: results });
  },

  selectSuggestion: (codigo: string) => {
    const suggestion = get().suggestions.find((s) => s.codigo === codigo);
    if (!suggestion) {
      return;
    }

    const exists = get().assignedCodes.some((c) => c.codigo === codigo);
    if (exists) {
      return;
    }

    const hasPrimary = get().assignedCodes.some((c) => c.esPrincipal);

    const newCode: AssignedCode = {
      codigo: suggestion.codigo,
      descripcion: suggestion.descripcion,
      tipo: suggestion.tipo,
      esPrincipal: !hasPrimary,
    };

    set((state) => ({ assignedCodes: [...state.assignedCodes, newCode] }));
  },

  assignCode: (code: ICD10Code, asPrimary = false) => {
    const exists = get().assignedCodes.some((c) => c.codigo === code.codigo);
    if (exists) {
      return;
    }

    let assignedCodes = [...get().assignedCodes];

    if (asPrimary) {
      assignedCodes = assignedCodes.map((c) => ({ ...c, esPrincipal: false }));
    }

    const hasPrimary = assignedCodes.some((c) => c.esPrincipal);

    const newCode: AssignedCode = {
      codigo: code.codigo,
      descripcion: code.descripcion,
      tipo: "CIE10",
      esPrincipal: asPrimary || !hasPrimary,
    };

    set({ assignedCodes: [...assignedCodes, newCode], searchQuery: "", searchResults: [] });
  },

  removeCode: (codigo: string) => {
    const assignedCodes = get().assignedCodes.filter((c) => c.codigo !== codigo);

    // If we removed the primary and there are still codes, make the first one primary
    if (assignedCodes.length > 0 && !assignedCodes.some((c) => c.esPrincipal)) {
      assignedCodes[0].esPrincipal = true;
    }

    set({ assignedCodes });
  },

  setPrimaryCode: (codigo: string) => {
    set((state) => ({
      assignedCodes: state.assignedCodes.map((c) => ({
        ...c,
        esPrincipal: c.codigo === codigo,
      })),
    }));
  },

  validateCoding: () => {
    const { assignedCodes } = get();
    const errors: string[] = [];

    if (assignedCodes.length === 0) {
      errors.push("Debe asignar al menos un código diagnóstico");
    }

    if (assignedCodes.length > 0 && !assignedCodes.some((c) => c.esPrincipal)) {
      errors.push("Debe designar un código principal");
    }

    return { valid: errors.length === 0, errors };
  },

  clearAssignedCodes: () => {
    set({ assignedCodes: [] });
  },
}));

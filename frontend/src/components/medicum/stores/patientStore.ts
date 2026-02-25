import { create } from "zustand";
import patientDataJson from "../data/paciente_demo.json";

// Types matching the actual JSON structure
interface RawPatientData {
  paciente: {
    datos_personales: {
      nombre: string;
      apellidos: string;
      fecha_nacimiento: string;
      edad: number;
      sexo: string;
      numero_historia_clinica: string;
      foto_url?: string;
    };
    antecedentes_personales: {
      enfermedades_cronicas: Array<{
        enfermedad: string;
        codigo_cie10: string;
        estado: string;
      }>;
      cirugias_previas: Array<{
        procedimiento: string;
        fecha: string;
        hospital: string;
      }>;
      alergias: Array<{
        alergeno: string;
        tipo: string;
        severidad: string;
        reaccion: string;
      }>;
      habitos: {
        tabaco: { estado: string };
        alcohol: { estado: string };
        ejercicio: { estado: string };
      };
      antecedentes_familiares: string[];
    };
    medicacion_actual: Array<{
      medicamento: string;
      posologia: string;
      indicacion: string;
    }>;
    resultados_laboratorio?: {
      analiticas: Array<{
        fecha: string;
        parametros: Array<{
          nombre: string;
          valor: number;
          unidad: string;
          rango_referencia: { min: number; max: number };
        }>;
      }>;
    };
    episodios_clinicos?: Array<{
      id: string;
      fecha: string;
      motivo_consulta: string;
      diagnostico_principal: string;
      codigo_cie10: string;
      tratamiento: string;
      especialidad: string;
    }>;
    imagenes_diagnosticas?: Array<{
      id: string;
      tipo: string;
      fecha: string;
      descripcion: string;
      archivo: string;
    }>;
  };
}

// Normalized types for the UI
export interface Allergy {
  id: string;
  nombre: string;
  tipo: string;
  severidad: "alta" | "media" | "baja";
  reaccion: string;
}

export interface Medication {
  id: string;
  nombre: string;
  dosis: string;
  indicacion: string;
}

export interface LabResult {
  id: string;
  fecha: string;
  parametro: string;
  valor: number;
  unidad: string;
  rangoMin: number;
  rangoMax: number;
}

export interface ClinicalEpisode {
  id: string;
  fecha: string;
  motivo: string;
  diagnostico: string;
  codigoCIE10: string;
  tratamiento: string;
  especialidad: string;
}

export interface DiagnosticImage {
  id: string;
  tipo: string;
  fecha: string;
  descripcion: string;
  archivo: string;
}

interface PatientState {
  rawData: RawPatientData | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  loadPatientData: () => void;

  // Selectors
  getPatientName: () => string;
  getPatientAge: () => number;
  getNHC: () => string;
  getSex: () => string;
  getAllergies: () => Allergy[];
  getActiveMedications: () => Medication[];
  getLabResults: () => LabResult[];
  getEpisodes: () => ClinicalEpisode[];
  getImages: () => DiagnosticImage[];
  getPersonalBackground: () => {
    enfermedades: string[];
    habitos: { tabaco: string; alcohol: string; ejercicio: string };
  };
  getFamilyBackground: () => string[];
  getSurgicalBackground: () => Array<{ procedimiento: string; fecha: string; hospital: string }>;
}

function mapSeverity(sev: string): "alta" | "media" | "baja" {
  const lower = sev.toLowerCase();
  if (lower === "grave" || lower === "alta" || lower === "severa") {
    return "alta";
  }
  if (lower === "moderada" || lower === "media") {
    return "media";
  }
  return "baja";
}

export const usePatientStore = create<PatientState>((set, get) => ({
  rawData: null,
  isLoading: false,
  error: null,

  loadPatientData: () => {
    set({ isLoading: true });
    try {
      const data = patientDataJson as unknown as RawPatientData;
      set({ rawData: data, isLoading: false, error: null });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Error loading patient data",
        isLoading: false,
      });
    }
  },

  getPatientName: () => {
    const data = get().rawData;
    const dp = data?.paciente?.datos_personales;
    if (!dp) {
      return "";
    }
    return `${dp.nombre} ${dp.apellidos}`;
  },

  getPatientAge: () => {
    const data = get().rawData;
    const dp = data?.paciente?.datos_personales;
    if (!dp?.fecha_nacimiento) {
      return dp?.edad ?? 0;
    }
    const birthDate = new Date(dp.fecha_nacimiento);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  },

  getNHC: () => {
    const data = get().rawData;
    return data?.paciente?.datos_personales?.numero_historia_clinica ?? "";
  },

  getSex: () => {
    const data = get().rawData;
    return data?.paciente?.datos_personales?.sexo ?? "";
  },

  getAllergies: () => {
    const data = get().rawData;
    const alergias = data?.paciente?.antecedentes_personales?.alergias ?? [];
    return alergias.map((a, idx) => ({
      id: `allergy-${idx}`,
      nombre: a.alergeno,
      tipo: a.tipo,
      severidad: mapSeverity(a.severidad),
      reaccion: a.reaccion,
    }));
  },

  getActiveMedications: () => {
    const data = get().rawData;
    const meds = data?.paciente?.medicacion_actual ?? [];
    return meds.map((m, idx) => ({
      id: `med-${idx}`,
      nombre: m.medicamento,
      dosis: m.posologia,
      indicacion: m.indicacion,
    }));
  },

  getLabResults: () => {
    const data = get().rawData;
    const analiticas = data?.paciente?.resultados_laboratorio?.analiticas ?? [];
    const results: LabResult[] = [];
    analiticas.forEach((a, aIdx) => {
      a.parametros.forEach((p, pIdx) => {
        results.push({
          id: `lab-${aIdx}-${pIdx}`,
          fecha: a.fecha,
          parametro: p.nombre,
          valor: p.valor,
          unidad: p.unidad,
          rangoMin: p.rango_referencia?.min ?? 0,
          rangoMax: p.rango_referencia?.max ?? 999,
        });
      });
    });
    return results;
  },

  getEpisodes: () => {
    const data = get().rawData;
    const eps = data?.paciente?.episodios_clinicos ?? [];
    return eps.map((e, idx) => ({
      id: e.id ?? `ep-${idx}`,
      fecha: e.fecha,
      motivo: e.motivo_consulta,
      diagnostico: e.diagnostico_principal,
      codigoCIE10: e.codigo_cie10,
      tratamiento: e.tratamiento,
      especialidad: e.especialidad,
    }));
  },

  getImages: () => {
    const data = get().rawData;
    const imgs = data?.paciente?.imagenes_diagnosticas ?? [];
    return imgs.map((i, idx) => ({
      id: i.id ?? `img-${idx}`,
      tipo: i.tipo,
      fecha: i.fecha,
      descripcion: i.descripcion,
      archivo: i.archivo,
    }));
  },

  getPersonalBackground: () => {
    const data = get().rawData;
    const ap = data?.paciente?.antecedentes_personales;
    const enfermedades = ap?.enfermedades_cronicas?.map((e) => e.enfermedad) ?? [];
    const habitos = {
      tabaco: ap?.habitos?.tabaco?.estado ?? "No registrado",
      alcohol: ap?.habitos?.alcohol?.estado ?? "No registrado",
      ejercicio: ap?.habitos?.ejercicio?.estado ?? "No registrado",
    };
    return { enfermedades, habitos };
  },

  getFamilyBackground: () => {
    const data = get().rawData;
    return data?.paciente?.antecedentes_personales?.antecedentes_familiares ?? [];
  },

  getSurgicalBackground: () => {
    const data = get().rawData;
    return data?.paciente?.antecedentes_personales?.cirugias_previas ?? [];
  },
}));

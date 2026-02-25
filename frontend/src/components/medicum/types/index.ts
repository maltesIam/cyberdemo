// Patient Types
export interface Patient {
  id: string;
  nhc: string;
  nombre: string;
  apellidos: string;
  fechaNacimiento: string;
  sexo: "M" | "F";
  telefono?: string;
  email?: string;
  direccion?: string;
  foto?: string;
}

export interface Allergy {
  id: string;
  nombre: string;
  tipo: string;
  severidad: "alta" | "media" | "baja";
  fechaRegistro: string;
  observaciones?: string;
}

export interface Medication {
  id: string;
  nombre: string;
  principioActivo: string;
  dosis: string;
  frecuencia: string;
  viaAdministracion: string;
  fechaInicio: string;
  fechaFin?: string;
  prescriptor?: string;
  indicacion?: string;
}

export interface PersonalBackground {
  enfermedades: string[];
  alergias: Allergy[];
  habitos: {
    tabaco: string;
    alcohol: string;
    ejercicio: string;
  };
}

export interface FamilyBackground {
  padre?: string[];
  madre?: string[];
  hermanos?: string[];
  otros?: string;
}

export interface SurgicalBackground {
  id: string;
  procedimiento: string;
  fecha: string;
  hospital?: string;
  complicaciones?: string;
}

export interface LabResult {
  id: string;
  fecha: string;
  parametro: string;
  valor: number;
  unidad: string;
  rangoMin: number;
  rangoMax: number;
  observaciones?: string;
}

export interface ClinicalEpisode {
  id: string;
  fecha: string;
  motivo: string;
  diagnostico: string;
  codigoCIE10?: string;
  tratamiento?: string;
  profesional?: string;
  especialidad?: string;
  notas?: string;
}

export interface DiagnosticImage {
  id: string;
  tipo: string;
  fecha: string;
  descripcion: string;
  archivo: string;
  informeRadiologico?: string;
}

export interface PatientData {
  paciente: Patient;
  antecedentes: {
    personales: PersonalBackground;
    familiares: FamilyBackground;
    quirurgicos: SurgicalBackground[];
  };
  medicacionActiva: Medication[];
  laboratorio: LabResult[];
  episodios: ClinicalEpisode[];
  imagenes: DiagnosticImage[];
}

// Tab Types
export type TabId = "consulta" | "historia" | "codificacion" | "visor";

export interface Tab {
  id: TabId;
  label: string;
  icon: string;
}

// Coding Types
export interface ICD10Code {
  codigo: string;
  descripcion: string;
  capitulo: string;
}

export interface SNOMEDCode {
  codigo: string;
  termino: string;
  jerarquia: string;
}

export interface CodeSuggestion {
  codigo: string;
  descripcion: string;
  confianza: number;
  tipo: "CIE10" | "SNOMED";
}

export interface AssignedCode {
  codigo: string;
  descripcion: string;
  tipo: "CIE10" | "SNOMED";
  esPrincipal: boolean;
}

// Transcription Types
export type Speaker = "medico" | "paciente";

export interface TranscriptionSegment {
  id: string;
  speaker: Speaker;
  text: string;
  timestamp: number;
}

export interface SOAPNote {
  subjetivo: string;
  objetivo: string;
  analisis: string;
  plan: string;
}

// Image Viewer Types
export interface ImageFinding {
  id: string;
  descripcion: string;
  confianza: number;
  region?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

// MCP Types
export type MCPCommand =
  | "navigate_to_tab"
  | "fill_field"
  | "click_element"
  | "get_state"
  | "highlight_element"
  | "scroll_to";

export interface MCPMessage {
  id: string;
  command: MCPCommand;
  params: Record<string, unknown>;
}

export interface MCPResponse {
  id: string;
  success: boolean;
  data?: unknown;
  error?: string;
}

// Connection Types
export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

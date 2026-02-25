import { create } from "zustand";
import type { DiagnosticImage, ImageFinding } from "../types";

// Demo findings for the knee X-ray
const DEMO_KNEE_FINDINGS: ImageFinding[] = [
  {
    id: "1",
    descripcion: "Disminución del espacio articular femorotibial medial",
    confianza: 92,
    region: { x: 45, y: 40, width: 15, height: 10 },
  },
  {
    id: "2",
    descripcion: "Osteofitos marginales en cóndilo femoral interno",
    confianza: 88,
    region: { x: 40, y: 35, width: 10, height: 8 },
  },
  {
    id: "3",
    descripcion: "Esclerosis subcondral en platillo tibial medial",
    confianza: 85,
    region: { x: 42, y: 50, width: 12, height: 6 },
  },
];

// Demo findings for the chest X-ray
const DEMO_CHEST_FINDINGS: ImageFinding[] = [
  {
    id: "1",
    descripcion: "Campos pulmonares sin infiltrados patológicos",
    confianza: 95,
  },
  {
    id: "2",
    descripcion: "Silueta cardíaca de tamaño normal (ICT < 0.5)",
    confianza: 92,
  },
  {
    id: "3",
    descripcion: "Senos costofrénicos libres",
    confianza: 94,
  },
];

// Demo radiological report
const DEMO_KNEE_REPORT = `INFORME RADIOLÓGICO

Paciente: María García López
Fecha: ${new Date().toLocaleDateString("es-ES")}
Estudio: Radiografía de rodilla derecha AP y lateral

HALLAZGOS:
- Disminución del espacio articular femorotibial, más marcada en el compartimento medial
- Osteofitos marginales en cóndilos femorales y platillos tibiales
- Esclerosis subcondral en platillo tibial medial
- No se observan cuerpos libres intraarticulares
- Rótula en posición normal

CONCLUSIÓN:
Cambios degenerativos compatibles con gonartrosis grado II-III de Kellgren-Lawrence, con predominio del compartimento medial.

RECOMENDACIONES:
- Correlación clínica
- Valorar tratamiento conservador vs intervencionista según evolución`;

interface ImageState {
  availableImages: DiagnosticImage[];
  currentImage: DiagnosticImage | null;
  zoomLevel: number;
  findings: ImageFinding[];
  report: string;
  isAnalyzing: boolean;
  showFindings: boolean;

  // Actions
  setAvailableImages: (images: DiagnosticImage[]) => void;
  selectImage: (imageId: string) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  analyzeImage: () => Promise<void>;
  toggleFindings: () => void;
  clearAnalysis: () => void;
}

export const useImageStore = create<ImageState>((set, get) => ({
  availableImages: [],
  currentImage: null,
  zoomLevel: 1,
  findings: [],
  report: "",
  isAnalyzing: false,
  showFindings: false,

  setAvailableImages: (images: DiagnosticImage[]) => {
    set({ availableImages: images });
    if (images.length > 0 && !get().currentImage) {
      set({ currentImage: images[0] });
    }
  },

  selectImage: (imageId: string) => {
    const image = get().availableImages.find((img) => img.id === imageId);
    if (image) {
      set({
        currentImage: image,
        findings: [],
        report: "",
        zoomLevel: 1,
        showFindings: false,
      });
    }
  },

  zoomIn: () => {
    set((state) => ({ zoomLevel: Math.min(state.zoomLevel + 0.25, 3) }));
  },

  zoomOut: () => {
    set((state) => ({ zoomLevel: Math.max(state.zoomLevel - 0.25, 0.5) }));
  },

  resetZoom: () => {
    set({ zoomLevel: 1 });
  },

  analyzeImage: async () => {
    const { currentImage } = get();
    if (!currentImage) {
      return;
    }

    set({ isAnalyzing: true });

    // Simulate AI analysis delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Select findings based on image type
    const isKneeXray = currentImage.archivo?.includes("rodilla");
    const findings = isKneeXray ? DEMO_KNEE_FINDINGS : DEMO_CHEST_FINDINGS;
    const report = isKneeXray
      ? DEMO_KNEE_REPORT
      : "Radiografía de tórax sin hallazgos patológicos significativos.";

    set({
      findings,
      report,
      isAnalyzing: false,
      showFindings: true,
    });
  },

  toggleFindings: () => {
    set((state) => ({ showFindings: !state.showFindings }));
  },

  clearAnalysis: () => {
    set({ findings: [], report: "", showFindings: false });
  },
}));

import { ZoomIn, ZoomOut, RotateCcw, Scan, FileText } from "lucide-react";
import React, { useEffect } from "react";
import { useImageStore } from "./stores/imageStore";
import { usePatientStore } from "./stores/patientStore";

export const VisorTab: React.FC = () => {
  const getImages = usePatientStore((state) => state.getImages);
  const setAvailableImages = useImageStore((state) => state.setAvailableImages);
  const selectImage = useImageStore((state) => state.selectImage);
  const currentImage = useImageStore((state) => state.currentImage);
  const availableImages = useImageStore((state) => state.availableImages);
  const zoomLevel = useImageStore((state) => state.zoomLevel);
  const findings = useImageStore((state) => state.findings);
  const report = useImageStore((state) => state.report);
  const isAnalyzing = useImageStore((state) => state.isAnalyzing);
  const zoomIn = useImageStore((state) => state.zoomIn);
  const zoomOut = useImageStore((state) => state.zoomOut);
  const resetZoom = useImageStore((state) => state.resetZoom);
  const analyzeImage = useImageStore((state) => state.analyzeImage);

  useEffect(() => {
    const images = getImages();
    if (images.length > 0) {
      setAvailableImages(images);
    }
  }, [getImages, setAvailableImages]);

  const getImagePath = (archivo: string | undefined) => {
    if (!archivo) {
      return "";
    }
    // Handle both full paths and just filenames
    const filename = archivo.split("/").pop() || archivo;
    return `/images/${filename}`;
  };

  return (
    <div className="h-full flex gap-6 p-6">
      {/* Image Viewer */}
      <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        {/* Toolbar */}
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <select
              id="select-image"
              value={currentImage?.id || ""}
              onChange={(e) => selectImage(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-medical-primary focus:border-medical-primary outline-none"
            >
              {availableImages.map((img) => (
                <option key={img.id} value={img.id}>
                  {img.descripcion}
                </option>
              ))}
              {availableImages.length === 0 && <option value="">Sin imágenes disponibles</option>}
            </select>

            <div className="flex items-center gap-1 border-l border-gray-200 pl-4">
              <button
                id="btn-zoom-out"
                onClick={zoomOut}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                title="Alejar"
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              <span className="text-sm text-gray-600 w-12 text-center">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                id="btn-zoom-in"
                onClick={zoomIn}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                title="Acercar"
              >
                <ZoomIn className="w-5 h-5" />
              </button>
              <button
                id="btn-zoom-reset"
                onClick={resetZoom}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                title="Restablecer zoom"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>
          </div>

          <button
            id="btn-analyze-image"
            onClick={analyzeImage}
            disabled={isAnalyzing || !currentImage}
            className="flex items-center gap-2 px-4 py-2 bg-medical-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Scan className="w-4 h-4" />
            {isAnalyzing ? "Analizando..." : "Analizar con IA"}
          </button>
        </div>

        {/* Image Display */}
        <div className="flex-1 overflow-auto bg-gray-900 flex items-center justify-center p-4">
          {currentImage ? (
            <div
              className="transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <img
                src={getImagePath(currentImage.archivo)}
                alt={currentImage.descripcion}
                className="max-w-full max-h-full object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect fill="%23333" width="400" height="300"/%3E%3Ctext fill="%23666" x="200" y="150" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="16"%3EImagen no disponible%3C/text%3E%3C/svg%3E';
                }}
              />
            </div>
          ) : (
            <div className="text-gray-500 text-center">
              <FileText className="w-16 h-16 mx-auto mb-2 opacity-30" />
              <p>Seleccione una imagen para visualizar</p>
            </div>
          )}
        </div>

        {/* Image Info */}
        {currentImage && (
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
            <span>{currentImage.tipo}</span>
            <span className="mx-2">|</span>
            <span>{currentImage.fecha}</span>
            <span className="mx-2">|</span>
            <span>{currentImage.descripcion}</span>
          </div>
        )}
      </div>

      {/* Analysis Panel */}
      <div className="w-96 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Análisis de IA</h2>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isAnalyzing ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-medical-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Analizando imagen...</p>
                <p className="text-sm text-gray-400">Esto puede tardar unos segundos</p>
              </div>
            </div>
          ) : findings.length > 0 ? (
            <div className="p-4 space-y-4">
              {/* Findings */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Hallazgos</h3>
                <div className="space-y-2">
                  {findings.map((finding) => (
                    <div key={finding.id} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between">
                        <p className="text-sm text-gray-900">{finding.descripcion}</p>
                        <span
                          className={`text-xs px-2 py-1 rounded ml-2 flex-shrink-0 ${
                            finding.confianza >= 90
                              ? "bg-green-100 text-green-700"
                              : finding.confianza >= 70
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {finding.confianza}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Report */}
              {report && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Informe Radiológico</h3>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                      {report}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400 p-4">
              <div className="text-center">
                <Scan className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Sin análisis realizado</p>
                <p className="text-sm mt-1">Pulse "Analizar con IA" para detectar hallazgos</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

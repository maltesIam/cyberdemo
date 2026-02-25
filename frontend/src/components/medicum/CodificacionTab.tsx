import { Search, Check, X, Star, AlertCircle } from "lucide-react";
import React, { useEffect } from "react";
import { useCodingStore } from "./stores/codingStore";

export const CodificacionTab: React.FC = () => {
  const suggestions = useCodingStore((state) => state.suggestions);
  const assignedCodes = useCodingStore((state) => state.assignedCodes);
  const searchQuery = useCodingStore((state) => state.searchQuery);
  const searchResults = useCodingStore((state) => state.searchResults);
  const loadSuggestions = useCodingStore((state) => state.loadSuggestions);
  const searchCodes = useCodingStore((state) => state.searchCodes);
  const selectSuggestion = useCodingStore((state) => state.selectSuggestion);
  const assignCode = useCodingStore((state) => state.assignCode);
  const removeCode = useCodingStore((state) => state.removeCode);
  const setPrimaryCode = useCodingStore((state) => state.setPrimaryCode);
  const validateCoding = useCodingStore((state) => state.validateCoding);

  useEffect(() => {
    if (suggestions.length === 0) {
      loadSuggestions();
    }
  }, [suggestions.length, loadSuggestions]);

  const validation = validateCoding();

  return (
    <div className="h-full flex gap-6 p-6">
      {/* Left Panel - Suggestions & Search */}
      <div className="flex-1 flex flex-col gap-6">
        {/* AI Suggestions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-1 flex flex-col">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Sugerencias de Codificación</h2>
            <p className="text-sm text-gray-500">Basadas en la consulta documentada</p>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {suggestions.length > 0 ? (
              <div className="space-y-2">
                {suggestions.map((suggestion) => {
                  const isAssigned = assignedCodes.some((c) => c.codigo === suggestion.codigo);
                  return (
                    <button
                      key={suggestion.codigo}
                      onClick={() => selectSuggestion(suggestion.codigo)}
                      disabled={isAssigned}
                      className={`
                        w-full p-3 rounded-lg border text-left transition-colors
                        ${
                          isAssigned
                            ? "bg-green-50 border-green-200 cursor-default"
                            : "bg-white border-gray-200 hover:border-medical-primary hover:bg-blue-50 cursor-pointer"
                        }
                      `}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="font-mono text-sm font-medium text-medical-primary">
                            {suggestion.codigo}
                          </span>
                          <p className="text-sm text-gray-700 mt-0.5">{suggestion.descripcion}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              suggestion.confianza >= 90
                                ? "bg-green-100 text-green-700"
                                : suggestion.confianza >= 70
                                  ? "bg-yellow-100 text-yellow-700"
                                  : "bg-gray-100 text-gray-600"
                            }`}
                          >
                            {suggestion.confianza}%
                          </span>
                          {isAssigned && <Check className="w-5 h-5 text-green-600" />}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <p>Cargando sugerencias...</p>
              </div>
            )}
          </div>
        </div>

        {/* Code Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Buscar Códigos CIE-10</h2>
          </div>
          <div className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="input-code-search"
                type="text"
                value={searchQuery}
                onChange={(e) => searchCodes(e.target.value)}
                placeholder="Buscar por código o descripción..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-primary focus:border-medical-primary outline-none"
              />
            </div>
            {searchResults.length > 0 && (
              <div className="mt-3 max-h-48 overflow-y-auto border border-gray-200 rounded-lg divide-y divide-gray-100">
                {searchResults.map((code) => (
                  <button
                    key={code.codigo}
                    onClick={() => assignCode(code)}
                    className="w-full p-3 text-left hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-mono text-sm font-medium text-medical-primary">
                      {code.codigo}
                    </span>
                    <p className="text-sm text-gray-700">{code.descripcion}</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Assigned Codes */}
      <div className="w-96 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Códigos Asignados</h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {assignedCodes.length > 0 ? (
            <div className="space-y-3">
              {/* Primary Code */}
              {assignedCodes
                .filter((c) => c.esPrincipal)
                .map((code) => (
                  <div
                    key={code.codigo}
                    className="p-3 bg-medical-primary/10 border-2 border-medical-primary rounded-lg"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Star className="w-5 h-5 text-medical-primary fill-current" />
                        <span className="text-xs font-medium text-medical-primary uppercase">
                          Diagnóstico Principal
                        </span>
                      </div>
                      <button
                        onClick={() => removeCode(code.codigo)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="mt-2">
                      <span className="font-mono text-sm font-medium">{code.codigo}</span>
                      <p className="text-sm text-gray-700">{code.descripcion}</p>
                    </div>
                  </div>
                ))}

              {/* Secondary Codes */}
              {assignedCodes
                .filter((c) => !c.esPrincipal)
                .map((code) => (
                  <div
                    key={code.codigo}
                    className="p-3 bg-gray-50 border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        Diagnóstico Secundario
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setPrimaryCode(code.codigo)}
                          title="Establecer como principal"
                          className="text-gray-400 hover:text-medical-primary"
                        >
                          <Star className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeCode(code.codigo)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="mt-2">
                      <span className="font-mono text-sm font-medium">{code.codigo}</span>
                      <p className="text-sm text-gray-700">{code.descripcion}</p>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Sin códigos asignados</p>
                <p className="text-sm">Seleccione una sugerencia o busque un código</p>
              </div>
            </div>
          )}
        </div>

        {/* Validation */}
        <div className="px-4 py-3 border-t border-gray-200">
          <button
            id="btn-validate-coding"
            className={`w-full py-2 rounded-lg font-medium ${
              validation.valid
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-gray-200 text-gray-600 hover:bg-gray-300"
            }`}
          >
            {validation.valid ? "Codificación Válida" : "Validar Codificación"}
          </button>
          {!validation.valid && validation.errors.length > 0 && (
            <p className="mt-2 text-sm text-red-600">{validation.errors[0]}</p>
          )}
        </div>
      </div>
    </div>
  );
};

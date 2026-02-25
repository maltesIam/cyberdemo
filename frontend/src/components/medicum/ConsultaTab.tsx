import {
  Play,
  Square,
  FileText,
  User,
  Stethoscope,
  Mic,
  Loader2,
  Wifi,
  WifiOff,
  Radio,
} from "lucide-react";
import React, { useEffect } from "react";
import { useTranscriptionStore } from "./stores/transcriptionStore";

export const ConsultaTab: React.FC = () => {
  const segments = useTranscriptionStore((state) => state.segments);
  const isListening = useTranscriptionStore((state) => state.isListening);
  const isTranscribing = useTranscriptionStore((state) => state.isTranscribing);
  const isSpeaking = useTranscriptionStore((state) => state.isSpeaking);
  const audioLevel = useTranscriptionStore((state) => state.audioLevel);
  const soapNote = useTranscriptionStore((state) => state.soapNote);
  const currentSpeaker = useTranscriptionStore((state) => state.currentSpeaker);
  const whisperStatus = useTranscriptionStore((state) => state.whisperStatus);
  const toggleContinuousListening = useTranscriptionStore(
    (state) => state.toggleContinuousListening,
  );
  const runDemoTranscription = useTranscriptionStore((state) => state.runDemoTranscription);
  const generateSOAPNote = useTranscriptionStore((state) => state.generateSOAPNote);
  const setSpeaker = useTranscriptionStore((state) => state.setSpeaker);
  const checkWhisperStatus = useTranscriptionStore((state) => state.checkWhisperStatus);

  // Check Whisper status on mount
  useEffect(() => {
    void checkWhisperStatus();
    const interval = setInterval(checkWhisperStatus, 10000);
    return () => clearInterval(interval);
  }, [checkWhisperStatus]);

  // Audio level visualization (0-100%)
  // Threshold is 0.08, so scale to show threshold at ~40%
  const levelPercent = Math.min(100, Math.round(audioLevel * 400));
  const thresholdPercent = 32; // 0.08 * 400 = 32%

  return (
    <div className="h-full flex gap-6 p-6">
      {/* Transcription Panel */}
      <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="font-semibold text-gray-900">Transcripción de Consulta</h2>
            {/* Whisper Status Indicator */}
            <div className="flex items-center gap-1.5">
              {whisperStatus === "connected" ? (
                <span className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                  <Wifi className="w-3 h-3" />
                  Whisper GPU
                </span>
              ) : whisperStatus === "unavailable" ? (
                <span className="flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2 py-0.5 rounded-full">
                  <WifiOff className="w-3 h-3" />
                  Sin Whisper
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Conectando...
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            {/* Speaker Selector */}
            <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
              <button
                onClick={() => setSpeaker("medico")}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors
                  ${
                    currentSpeaker === "medico"
                      ? "bg-medical-primary text-white shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }
                `}
              >
                <Stethoscope className="w-4 h-4" />
                Médico
              </button>
              <button
                onClick={() => setSpeaker("paciente")}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors
                  ${
                    currentSpeaker === "paciente"
                      ? "bg-gray-600 text-white shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }
                `}
              >
                <User className="w-4 h-4" />
                Paciente
              </button>
            </div>

            {/* Listen Button */}
            <button
              id="btn-toggle-transcription"
              onClick={toggleContinuousListening}
              disabled={whisperStatus !== "connected" || isTranscribing}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  isListening
                    ? "bg-red-500 text-white hover:bg-red-600"
                    : whisperStatus === "connected"
                      ? "bg-green-500 text-white hover:bg-green-600"
                      : "bg-gray-300 text-gray-500 cursor-not-allowed"
                }
              `}
            >
              {isListening ? (
                <>
                  <Square className="w-4 h-4" />
                  Detener
                </>
              ) : (
                <>
                  <Radio className="w-4 h-4" />
                  Escuchar
                </>
              )}
            </button>

            {/* Demo Button */}
            <button
              id="btn-demo-transcription"
              onClick={runDemoTranscription}
              disabled={isListening}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300 disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              Demo
            </button>
          </div>
        </div>

        {/* Audio Level Indicator (when listening) */}
        {isListening && (
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                {isSpeaking ? (
                  <Mic className="w-4 h-4 text-red-500 animate-pulse" />
                ) : (
                  <Mic className="w-4 h-4 text-gray-400" />
                )}
                <span className="text-xs text-gray-600">
                  {isSpeaking
                    ? "Hablando..."
                    : isTranscribing
                      ? "Transcribiendo..."
                      : "Esperando voz..."}
                </span>
              </div>
              {/* Audio Level Bar with threshold marker */}
              <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden relative">
                {/* Threshold line */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-yellow-500 z-10"
                  style={{ left: `${thresholdPercent}%` }}
                  title="Umbral de silencio"
                />
                {/* Level bar */}
                <div
                  className={`h-full transition-all duration-75 ${
                    levelPercent > thresholdPercent ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{ width: `${levelPercent}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 w-12 text-right">
                {Math.round(audioLevel * 100)}%
              </span>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {segments.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Radio className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="mb-2">Pulse "Escuchar" para transcripción continua</p>
                <p className="text-sm">
                  Habla y transcribirá automáticamente cuando detecte silencio
                </p>
                {whisperStatus !== "connected" && (
                  <p className="text-xs text-red-500 mt-2">
                    Inicie el servidor Whisper para usar transcripción real
                  </p>
                )}
              </div>
            </div>
          ) : (
            segments.map((segment) => (
              <div
                key={segment.id}
                className={`flex gap-3 ${segment.speaker === "medico" ? "flex-row-reverse" : ""}`}
              >
                <div
                  className={`
                    w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
                    ${segment.speaker === "medico" ? "bg-medical-primary" : "bg-gray-400"}
                  `}
                >
                  {segment.speaker === "medico" ? (
                    <Stethoscope className="w-4 h-4 text-white" />
                  ) : (
                    <User className="w-4 h-4 text-white" />
                  )}
                </div>
                <div
                  className={`
                    max-w-[70%] p-3 rounded-lg
                    ${
                      segment.speaker === "medico"
                        ? "bg-medical-primary text-white rounded-br-sm"
                        : "bg-gray-100 text-gray-900 rounded-bl-sm"
                    }
                  `}
                >
                  <p className="text-sm">{segment.text}</p>
                </div>
              </div>
            ))
          )}

          {/* Status indicators */}
          {isListening && !isSpeaking && !isTranscribing && (
            <div className="flex items-center gap-2 text-green-500">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
              <span className="text-sm">
                Escuchando como {currentSpeaker}... (habla cuando quieras)
              </span>
            </div>
          )}

          {isSpeaking && (
            <div className="flex items-center gap-2 text-red-500">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span
                  className="w-2 h-2 bg-red-500 rounded-full animate-pulse"
                  style={{ animationDelay: "0.2s" }}
                />
                <span
                  className="w-2 h-2 bg-red-500 rounded-full animate-pulse"
                  style={{ animationDelay: "0.4s" }}
                />
              </div>
              <span className="text-sm font-medium">Grabando voz ({currentSpeaker})...</span>
            </div>
          )}

          {isTranscribing && (
            <div className="flex items-center gap-2 text-blue-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Procesando audio con Whisper GPU...</span>
            </div>
          )}
        </div>
      </div>

      {/* SOAP Note Panel */}
      <div className="w-96 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Nota SOAP</h2>
          <button
            id="btn-generate-soap"
            onClick={generateSOAPNote}
            className="flex items-center gap-2 px-3 py-1.5 bg-medical-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            <FileText className="w-4 h-4" />
            Generar
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Subjetivo */}
          <div>
            <label className="block text-sm font-medium text-medical-primary mb-1">
              S - Subjetivo
            </label>
            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700 min-h-[60px]">
              {soapNote.subjetivo || (
                <span className="text-gray-400 italic">Síntomas referidos por el paciente...</span>
              )}
            </div>
          </div>

          {/* Objetivo */}
          <div>
            <label className="block text-sm font-medium text-medical-primary mb-1">
              O - Objetivo
            </label>
            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700 min-h-[60px]">
              {soapNote.objetivo || (
                <span className="text-gray-400 italic">Hallazgos de la exploración...</span>
              )}
            </div>
          </div>

          {/* Análisis */}
          <div>
            <label className="block text-sm font-medium text-medical-primary mb-1">
              A - Análisis
            </label>
            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700 min-h-[60px]">
              {soapNote.analisis || (
                <span className="text-gray-400 italic">Impresión diagnóstica...</span>
              )}
            </div>
          </div>

          {/* Plan */}
          <div>
            <label className="block text-sm font-medium text-medical-primary mb-1">P - Plan</label>
            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700 min-h-[80px] whitespace-pre-line">
              {soapNote.plan || (
                <span className="text-gray-400 italic">Plan de tratamiento...</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import { create } from "zustand";
import type { TranscriptionSegment, SOAPNote, Speaker } from "../types";

const WHISPER_PROXY_URL = "http://localhost:3050";

// VAD Configuration
const VAD_SILENCE_THRESHOLD = 0.08;
const VAD_SILENCE_DURATION_MS = 1000;
const VAD_MIN_SPEECH_DURATION_MS = 300;

// Demo data
const DEMO_TRANSCRIPTION: TranscriptionSegment[] = [
  {
    id: "1",
    speaker: "medico",
    text: "Buenos días, María. ¿Cómo se ha sentido desde nuestra última consulta?",
    timestamp: Date.now(),
  },
  {
    id: "2",
    speaker: "paciente",
    text: "Buenos días, doctor. La verdad es que he tenido más dolor en la rodilla derecha, especialmente al subir escaleras.",
    timestamp: Date.now() + 1000,
  },
  {
    id: "3",
    speaker: "medico",
    text: "¿El dolor es constante o solo cuando hace ciertos movimientos?",
    timestamp: Date.now() + 2000,
  },
  {
    id: "4",
    speaker: "paciente",
    text: "Es peor por las mañanas cuando me levanto, y luego mejora un poco durante el día.",
    timestamp: Date.now() + 3000,
  },
  {
    id: "5",
    speaker: "medico",
    text: "¿Ha notado inflamación o rigidez en la articulación?",
    timestamp: Date.now() + 4000,
  },
  {
    id: "6",
    speaker: "paciente",
    text: "Sí, a veces noto que está un poco hinchada.",
    timestamp: Date.now() + 5000,
  },
];

const DEMO_SOAP: SOAPNote = {
  subjetivo:
    "Paciente de 58 años refiere dolor en rodilla derecha de características mecánicas, más intenso al subir escaleras y por las mañanas.",
  objetivo:
    "Inspección: Leve tumefacción en rodilla derecha. Palpación: Dolor a la presión en interlínea articular medial. Movilidad: Flexión limitada a 110°.",
  analisis:
    "Gonartrosis primaria de rodilla derecha grado II-III. Afectación predominante del compartimento medial.",
  plan: "1. Radiografía de rodilla AP y lateral\n2. Paracetamol 1g/8h\n3. Infiltración con ácido hialurónico si no mejora\n4. Rehabilitación\n5. Control en 4 semanas",
};

// Queue for audio segments waiting to be transcribed
interface PendingSegment {
  chunks: Blob[];
  speaker: Speaker;
}

let gPendingQueue: PendingSegment[] = [];
let gCurrentChunks: Blob[] = [];
let gHeaderChunk: Blob | null = null; // First chunk contains webm EBML header
let gIsCurrentlySpeaking = false;
let gSilenceStartTime: number | null = null;
let gSpeechStartTime: number | null = null;
let gIsProcessing = false;
let gCurrentSpeaker: Speaker = "medico";
let gDemoInterval: ReturnType<typeof setInterval> | null = null;

interface TranscriptionState {
  segments: TranscriptionSegment[];
  isListening: boolean;
  soapNote: SOAPNote;
  currentSegmentIndex: number;
  currentSpeaker: Speaker;
  whisperStatus: "unknown" | "connected" | "unavailable";
  isTranscribing: boolean;
  audioLevel: number;
  isSpeaking: boolean;
  queueLength: number;

  _mediaRecorder: MediaRecorder | null;
  _audioContext: AudioContext | null;
  _analyser: AnalyserNode | null;
  _mediaStream: MediaStream | null;
  _vadInterval: ReturnType<typeof setInterval> | null;

  setSpeaker: (speaker: Speaker) => void;
  checkWhisperStatus: () => Promise<void>;
  startContinuousListening: () => Promise<void>;
  stopContinuousListening: () => void;
  toggleContinuousListening: () => void;
  addSegment: (speaker: Speaker, text: string) => void;
  generateSOAPNote: () => void;
  runDemoTranscription: () => void;
  resetTranscription: () => void;
}

async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  const response = await fetch(`${WHISPER_PROXY_URL}/transcribe`, {
    method: "POST",
    body: formData,
  });
  const data = await response.json();
  return data.text || "";
}

export const useTranscriptionStore = create<TranscriptionState>((set, get) => {
  // Process queue function - processes segments one by one
  const processQueue = async () => {
    if (gIsProcessing || gPendingQueue.length === 0) {
      return;
    }

    gIsProcessing = true;
    set({ isTranscribing: true });

    while (gPendingQueue.length > 0) {
      const segment = gPendingQueue.shift()!;
      set({ queueLength: gPendingQueue.length });

      try {
        // Prepend the header chunk to create a valid webm file
        const allChunks = gHeaderChunk ? [gHeaderChunk, ...segment.chunks] : segment.chunks;
        const audioBlob = new Blob(allChunks, { type: "audio/webm" });
        console.log(
          `Transcribing segment (${segment.speaker}): ${allChunks.length} chunks (1 header + ${segment.chunks.length} data), ${audioBlob.size} bytes`,
        );

        const text = await transcribeAudio(audioBlob);
        console.log(`Result: "${text}"`);

        if (text.trim()) {
          set((state) => ({
            segments: [
              ...state.segments,
              {
                id: Date.now().toString(),
                speaker: segment.speaker,
                text: text.trim(),
                timestamp: Date.now(),
              },
            ],
          }));
        }
      } catch (error) {
        console.error("Transcription error:", error);
      }
    }

    set({ isTranscribing: false, queueLength: 0 });
    gIsProcessing = false;
  };

  // Queue a segment for transcription
  const queueSegment = () => {
    if (gCurrentChunks.length === 0) {
      return;
    }

    const segment: PendingSegment = {
      chunks: [...gCurrentChunks],
      speaker: gCurrentSpeaker,
    };

    gCurrentChunks = [];
    gPendingQueue.push(segment);

    console.log(`Queued segment (${segment.speaker}), queue length: ${gPendingQueue.length}`);
    set({ queueLength: gPendingQueue.length });

    // Start processing if not already
    void processQueue();
  };

  return {
    segments: [],
    isListening: false,
    soapNote: { subjetivo: "", objetivo: "", analisis: "", plan: "" },
    currentSegmentIndex: 0,
    currentSpeaker: "medico",
    whisperStatus: "unknown",
    isTranscribing: false,
    audioLevel: 0,
    isSpeaking: false,
    queueLength: 0,

    _mediaRecorder: null,
    _audioContext: null,
    _analyser: null,
    _mediaStream: null,
    _vadInterval: null,

    setSpeaker: (speaker: Speaker) => {
      gCurrentSpeaker = speaker;
      set({ currentSpeaker: speaker });
    },

    checkWhisperStatus: async () => {
      try {
        const response = await fetch(`${WHISPER_PROXY_URL}/health`);
        const data = await response.json();
        set({ whisperStatus: data.whisper === "connected" ? "connected" : "unavailable" });
      } catch {
        set({ whisperStatus: "unavailable" });
      }
    },

    startContinuousListening: async () => {
      // Reset state
      gPendingQueue = [];
      gCurrentChunks = [];
      gHeaderChunk = null; // Reset header for new session
      gIsCurrentlySpeaking = false;
      gSilenceStartTime = null;
      gSpeechStartTime = null;
      gIsProcessing = false;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: "audio/webm;codecs=opus",
        });

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            // First chunk contains the webm EBML header - always save it
            if (!gHeaderChunk) {
              gHeaderChunk = event.data;
              console.log(`[REC] Header chunk saved: ${event.data.size} bytes`);
              return;
            }
            // Subsequent chunks: only capture when speaking
            if (gIsCurrentlySpeaking) {
              gCurrentChunks.push(event.data);
              console.log(
                `[REC] Chunk added: ${event.data.size} bytes, total chunks: ${gCurrentChunks.length}`,
              );
            }
          }
        };

        set({
          _mediaRecorder: mediaRecorder,
          _audioContext: audioContext,
          _analyser: analyser,
          _mediaStream: stream,
          isListening: true,
          isSpeaking: false,
          isTranscribing: false,
          queueLength: 0,
        });

        mediaRecorder.start(100);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        // Debug: log every 2 seconds
        let lastDebugLog = 0;

        const vadLoop = setInterval(() => {
          const state = get();
          if (!state.isListening || !state._analyser) {
            clearInterval(vadLoop);
            return;
          }

          state._analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          const normalizedLevel = average / 255;

          set({ audioLevel: normalizedLevel });

          const now = Date.now();
          const isSpeakingNow = normalizedLevel > VAD_SILENCE_THRESHOLD;

          // Debug log every 2 seconds
          if (now - lastDebugLog > 2000) {
            console.log(
              `[VAD] level=${normalizedLevel.toFixed(3)} threshold=${VAD_SILENCE_THRESHOLD} speaking=${gIsCurrentlySpeaking} chunks=${gCurrentChunks.length} queue=${gPendingQueue.length}`,
            );
            lastDebugLog = now;
          }

          if (isSpeakingNow) {
            // Voice detected
            if (!gIsCurrentlySpeaking) {
              gIsCurrentlySpeaking = true;
              gSpeechStartTime = now;
              gCurrentSpeaker = state.currentSpeaker; // Capture speaker at speech start
              set({ isSpeaking: true });
              console.log(`Speech started (${gCurrentSpeaker})`);
            }
            gSilenceStartTime = null;
          } else {
            // Silence
            if (gIsCurrentlySpeaking) {
              if (!gSilenceStartTime) {
                gSilenceStartTime = now;
              }

              const silenceDuration = now - gSilenceStartTime;
              if (silenceDuration >= VAD_SILENCE_DURATION_MS) {
                const speechDuration = gSpeechStartTime ? gSilenceStartTime - gSpeechStartTime : 0;
                console.log(`Silence detected after ${speechDuration}ms of speech`);

                gIsCurrentlySpeaking = false;
                set({ isSpeaking: false });

                if (speechDuration >= VAD_MIN_SPEECH_DURATION_MS && gCurrentChunks.length > 0) {
                  queueSegment();
                } else {
                  console.log("Speech too short, discarding");
                  gCurrentChunks = [];
                }

                gSilenceStartTime = null;
                gSpeechStartTime = null;
              }
            }
          }
        }, 50);

        set({ _vadInterval: vadLoop });
      } catch (error) {
        console.error("Failed to start listening:", error);
        throw error;
      }
    },

    stopContinuousListening: () => {
      const state = get();

      if (state._vadInterval) {
        clearInterval(state._vadInterval);
      }
      if (state._mediaRecorder?.state !== "inactive") {
        state._mediaRecorder?.stop();
      }
      if (state._mediaStream) {
        state._mediaStream.getTracks().forEach((t) => t.stop());
      }
      if (state._audioContext) {
        void state._audioContext.close();
      }

      // Queue any remaining audio
      if (gCurrentChunks.length > 0 && gIsCurrentlySpeaking) {
        queueSegment();
      }

      gIsCurrentlySpeaking = false;

      set({
        isListening: false,
        isSpeaking: false,
        audioLevel: 0,
        _mediaRecorder: null,
        _audioContext: null,
        _analyser: null,
        _mediaStream: null,
        _vadInterval: null,
      });
    },

    toggleContinuousListening: () => {
      const { isListening } = get();
      if (isListening) {
        get().stopContinuousListening();
      } else {
        get().startContinuousListening().catch(console.error);
      }
    },

    addSegment: (speaker: Speaker, text: string) => {
      set((state) => ({
        segments: [
          ...state.segments,
          {
            id: Date.now().toString(),
            speaker,
            text,
            timestamp: Date.now(),
          },
        ],
      }));
    },

    generateSOAPNote: () => set({ soapNote: DEMO_SOAP }),

    runDemoTranscription: () => {
      // Clear any previous demo interval to prevent duplicates
      if (gDemoInterval) {
        clearInterval(gDemoInterval);
        gDemoInterval = null;
      }
      set({ segments: [], currentSegmentIndex: 0 });
      let index = 0;
      gDemoInterval = setInterval(() => {
        if (index >= DEMO_TRANSCRIPTION.length) {
          if (gDemoInterval) {
            clearInterval(gDemoInterval);
            gDemoInterval = null;
          }
          return;
        }
        set((state) => ({
          segments: [...state.segments, { ...DEMO_TRANSCRIPTION[index], timestamp: Date.now() }],
          currentSegmentIndex: index + 1,
        }));
        index++;
      }, 2000);
    },

    resetTranscription: () => {
      get().stopContinuousListening();
      gPendingQueue = [];
      set({
        segments: [],
        soapNote: { subjetivo: "", objetivo: "", analisis: "", plan: "" },
        currentSegmentIndex: 0,
        queueLength: 0,
      });
    },
  };
});

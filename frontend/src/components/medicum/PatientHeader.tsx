import React from "react";
import { useConnectionStore } from "./stores/connectionStore";
import { usePatientStore, type Allergy } from "./stores/patientStore";
import { ThemeToggle } from "./ThemeToggle";
import { FontSizeButton } from "./FontSizeButton";

const severityColors: Record<string, string> = {
  alta: "bg-severity-high text-white",
  media: "bg-severity-medium text-white",
  baja: "bg-severity-low text-black",
};

const AllergyBadge: React.FC<{ allergy: Allergy }> = ({ allergy }) => (
  <span
    className={`px-2 py-1 rounded-full text-xs font-medium ${severityColors[allergy.severidad] || "bg-gray-200"}`}
    title={`Severidad: ${allergy.severidad}`}
  >
    {allergy.nombre}
  </span>
);

export const PatientHeader: React.FC = () => {
  const rawData = usePatientStore((state) => state.rawData);
  const getPatientName = usePatientStore((state) => state.getPatientName);
  const getPatientAge = usePatientStore((state) => state.getPatientAge);
  const getNHC = usePatientStore((state) => state.getNHC);
  const getSex = usePatientStore((state) => state.getSex);
  const getAllergies = usePatientStore((state) => state.getAllergies);
  const getActiveMedications = usePatientStore((state) => state.getActiveMedications);
  const connectionStatus = useConnectionStore((state) => state.status);

  if (!rawData) {
    return (
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="animate-pulse flex space-x-4">
          <div className="rounded-full bg-gray-200 h-12 w-12"></div>
          <div className="flex-1 space-y-2 py-1">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  const patientName = getPatientName();
  const allergies = getAllergies();
  const medications = getActiveMedications();
  const initials = patientName
    .split(" ")
    .map((n) => n.charAt(0))
    .slice(0, 2)
    .join("");

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4" data-testid="patient-header">
      <div className="flex items-start justify-between">
        {/* Patient Info */}
        <div className="flex items-center space-x-4">
          {/* Avatar */}
          <div className="w-14 h-14 bg-medical-primary rounded-full flex items-center justify-center text-white text-xl font-semibold">
            {initials}
          </div>

          {/* Name and Details */}
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{patientName}</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>{getPatientAge()} años</span>
              <span>|</span>
              <span>NHC: {getNHC()}</span>
              <span>|</span>
              <span>{getSex()}</span>
            </div>
          </div>
        </div>

        {/* Right section: Controls */}
        <div className="flex items-center space-x-3">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <span
              className={`w-2 h-2 rounded-full ${
                connectionStatus === "connected"
                  ? "bg-green-500"
                  : connectionStatus === "connecting"
                    ? "bg-yellow-500 animate-pulse"
                    : "bg-red-500"
              }`}
            />
            <span className="text-xs text-gray-500">
              {connectionStatus === "connected"
                ? "PIA Conectado"
                : connectionStatus === "connecting"
                  ? "Conectando..."
                  : "Desconectado"}
            </span>
          </div>

          {/* Font Size Button */}
          <FontSizeButton />
          {/* Theme Toggle */}
          <ThemeToggle />
        </div>
      </div>

      {/* Alerts Section */}
      <div className="mt-4 flex flex-wrap gap-6">
        {/* Allergies */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Alergias:</span>
          <div className="flex flex-wrap gap-1">
            {allergies.length > 0 ? (
              allergies.map((allergy) => <AllergyBadge key={allergy.id} allergy={allergy} />)
            ) : (
              <span className="text-sm text-gray-500">Sin alergias conocidas</span>
            )}
          </div>
        </div>

        {/* Medications */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Medicación:</span>
          <div className="flex flex-wrap gap-1">
            {medications.length > 0 ? (
              medications.slice(0, 3).map((med) => (
                <span
                  key={med.id}
                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                >
                  {med.nombre}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-500">Sin medicación activa</span>
            )}
            {medications.length > 3 && (
              <span className="text-xs text-gray-500">+{medications.length - 3} más</span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default PatientHeader;
